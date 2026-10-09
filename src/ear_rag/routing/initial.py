"""Transparent, provisional query-only initial strategy selection."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from math import isfinite
from time import perf_counter

from ear_rag.core.interfaces import QueryAnalyzer
from ear_rag.core.models import Query
from .query_analysis import FEATURE_NAMES, LightweightQueryAnalyzer


STRATEGIES = ("local_lexical", "vector_flat", "hybrid", "multihop")
POLICY_VERSION = "query_features_v1"
DEFAULT_WEIGHTS: dict[str, dict[str, float]] = {
    "local_lexical": {"exact_anchor": 4.0},
    "vector_flat": {"conceptual": 3.0},
    "hybrid": {"exact_anchor": 1.0, "conceptual": 1.0, "mixed": 4.0},
    "multihop": {"dependent": 8.0},
}


@dataclass(frozen=True)
class InitialRoutingDecision:
    selected_strategy: str
    features: dict[str, object]
    suitability_scores: dict[str, float]
    reason: str
    fallback_reason: str | None
    policy_version: str
    routing_latency_ms: float
    eligible_strategies: tuple[str, ...]
    # Additive diagnostics; existing constructor arguments and selection stay valid.
    fallback_code: str | None = None
    fallback_substitution_code: str | None = None
    selection_code: str = "score_winner"
    score_margin: float = 0.0
    top_score: float = 0.0
    tied_top_strategies: tuple[str, ...] = ()
    recognized_signals: tuple[str, ...] = ()
    ambiguous_scores: bool = False


def finite_number(value: object, name: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if nonnegative and value < 0:
        raise ValueError(f"{name} must be non-negative")
    return float(value)


class InitialRetrievalRouter:
    """Score query features without consulting retrieval, ESA, recovery or labels.

    Scores are heuristic suitability scores, not calibrated probabilities. Unknown
    settings fail early. Backend availability is a static registry-key intersection.
    """

    def __init__(self, config: Mapping[str, object] | None = None, *, analyzer: QueryAnalyzer | None = None) -> None:
        config = {} if config is None else config
        if not isinstance(config, Mapping):
            raise ValueError("query_analysis must be a mapping")
        unknown = set(config) - {"enabled", "policy", "fallback_backend", "eligible_backends", "weights", "biases", "minimum_score", "minimum_margin", "tie_break_order"}
        if unknown:
            raise ValueError(f"unknown query_analysis settings: {sorted(unknown)}")
        if "enabled" in config and not isinstance(config["enabled"], bool):
            raise ValueError("query_analysis.enabled must be a boolean")
        if config.get("policy", POLICY_VERSION) != POLICY_VERSION:
            raise ValueError(f"unsupported query-analysis policy; expected {POLICY_VERSION}")
        fallback = config.get("fallback_backend", "local_lexical")
        if fallback not in STRATEGIES:
            raise ValueError(f"unknown fallback backend: {fallback}")
        self.fallback_backend = str(fallback)
        self.eligible_backends = self._names(config.get("eligible_backends", list(STRATEGIES)), "eligible_backends")
        self.tie_break_order = self._names(config.get("tie_break_order", list(STRATEGIES)), "tie_break_order")
        if set(self.tie_break_order) != set(STRATEGIES):
            raise ValueError("tie_break_order must contain each supported strategy exactly once")
        self.minimum_score = finite_number(config.get("minimum_score", 1.0), "minimum_score", nonnegative=True)
        self.minimum_margin = finite_number(config.get("minimum_margin", .25), "minimum_margin", nonnegative=True)
        self.weights = {name: dict(weights) for name, weights in DEFAULT_WEIGHTS.items()}
        raw_weights = config.get("weights", {})
        if not isinstance(raw_weights, Mapping) or set(raw_weights) - set(STRATEGIES):
            raise ValueError("weights must map supported strategies to feature weights")
        for strategy, weights in raw_weights.items():
            if not isinstance(weights, Mapping) or set(weights) - FEATURE_NAMES:
                raise ValueError(f"unknown features or invalid weight mapping for {strategy}")
            # A provided row replaces that strategy's entire default row.
            self.weights[strategy] = {key: finite_number(value, f"{strategy}.{key}") for key, value in weights.items()}
        raw_biases = config.get("biases", {})
        if not isinstance(raw_biases, Mapping) or set(raw_biases) - set(STRATEGIES):
            raise ValueError("biases must map supported strategies to finite numbers")
        self.biases = {name: finite_number(raw_biases.get(name, 0.0), f"biases.{name}") for name in STRATEGIES}
        self.analyzer = analyzer or LightweightQueryAnalyzer()

    @staticmethod
    def _names(value: object, name: str) -> tuple[str, ...]:
        if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"{name} must be a list of backend identifiers")
        if len(set(value)) != len(value) or set(value) - set(STRATEGIES):
            raise ValueError(f"{name} contains duplicate or unknown backends")
        return tuple(value)

    def select(self, query_text: str, available_backends: Collection[str]) -> InitialRoutingDecision:
        started = perf_counter()
        available = frozenset(available_backends)
        eligible = tuple(name for name in self.tie_break_order if name in self.eligible_backends and name in available)
        if not eligible:
            raise ValueError("No eligible initial retrieval strategy is available; check backend registry and query_analysis.eligible_backends")
        # Neither query ID nor arbitrary query metadata crosses the analyzer boundary.
        features = dict(self.analyzer.analyze(Query("", query_text)))
        if set(features) != FEATURE_NAMES:
            raise ValueError("query analyzer must return the documented scalar feature schema")
        values = {key: float(value) if isinstance(value, bool) else finite_number(value, f"feature.{key}")
                  for key, value in features.items()}
        scores = {name: self.biases[name] + sum(weight * values[key] for key, weight in self.weights[name].items())
                  for name in STRATEGIES}
        if not all(isfinite(value) for value in scores.values()):
            raise ValueError("routing suitability scores must be finite")
        # Ranking all hypotheses is cheap arithmetic, never retrieval/backend probing.
        ranking = sorted(STRATEGIES, key=lambda name: (-scores[name], self.tie_break_order.index(name)))
        preferred = ranking[0]
        top_score = scores[preferred]
        margin = top_score - scores[ranking[1]]
        tied = tuple(name for name in ranking if scores[name] == top_score)
        recognized = tuple(key for key in ("exact_anchor", "conceptual", "mixed", "dependent") if values[key])
        fallback_reason = None
        fallback_code = None
        substitution_code = None
        if not values["token_count"] or scores[preferred] < self.minimum_score:
            fallback_reason = "Insufficient query signals for an initial strategy."
            fallback_code = ("empty_query" if not values["token_count"] else
                             "no_routing_signals" if not recognized else "low_score")
        elif margin < self.minimum_margin:
            fallback_reason = "Ambiguous heuristic suitability scores."
            fallback_code = "ambiguous_scores"
        elif preferred not in eligible:
            fallback_reason = f"Preferred strategy {preferred} is unavailable or ineligible."
            fallback_code = "preferred_unavailable" if preferred not in available else "preferred_ineligible"
        selected = preferred
        selection_code = "tie_break" if len(tied) > 1 else "score_winner"
        if fallback_reason:
            selection_code = "configured_fallback"
            selected = self.fallback_backend
            if selected not in eligible:
                substitution_code = "fallback_unavailable" if selected not in available else "fallback_ineligible"
                selection_code = "eligible_substitute"
                selected = eligible[0]
                fallback_reason += f" Configured fallback {self.fallback_backend} is unavailable or ineligible; using first eligible strategy in tie-break order."
        signals = ", ".join(key for key in ("exact_anchor", "conceptual", "mixed", "dependent") if values[key]) or "none"
        reason = f"{selected}: heuristic suitability score {scores[selected]:g}; signals: {signals}."
        return InitialRoutingDecision(selected, features, scores, reason, fallback_reason, POLICY_VERSION,
                                      (perf_counter() - started) * 1000, eligible,
                                      fallback_code, substitution_code, selection_code, margin, top_score,
                                      tied, recognized, margin < self.minimum_margin)
