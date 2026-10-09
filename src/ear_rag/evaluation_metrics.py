"""Pure offline metrics and decision diagnostics. Never imported by runtime routing."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import isclose
import random
from statistics import mean
from typing import Any

from ear_rag.core.models import RetrievalResult
from ear_rag.retrieval.local import LocalLexicalRetriever
from ear_rag.routing.initial import finite_number
from ear_rag.routing.pipeline import underlying_calls


OBJECTIVE = {
    "id": "resolved_recall_per_call_v1",
    "utility": "resolved supporting-document recall@k / measured underlying retrieval calls",
    "quality": "unique resolved supporting-document recall, not binary Hit@k",
    "cost": "actual backend child/hop calls; no latency-to-quality conversion coefficient",
    "ties": "all utilities equal within absolute tolerance 1e-12 are retained",
    "scope": "offline diagnostic over available fixed strategies; not runtime ground truth",
    "caveat": "Efficiency objective can tie partial recall at one call with full recall at two; quality-only regret is also reported.",
}


@dataclass(frozen=True)
class LabelResolution:
    resolved_ids: frozenset[str]
    annotated_support_count: int | None
    unresolved_titles: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.annotated_support_count is not None and self.annotated_support_count < len(self.resolved_ids):
            raise ValueError("annotated support count cannot be smaller than resolved support count")

    @property
    def complete(self) -> bool:
        return bool(self.resolved_ids) and self.annotated_support_count == len(self.resolved_ids)

    def record(self) -> dict[str, Any]:
        count = self.annotated_support_count
        status = ("unknown_annotations" if count is None else "no_annotations" if count == 0 else
                  "unresolved" if not self.resolved_ids else "complete" if self.complete else "partial")
        return {"status": status, "annotated_support_count": count,
                "resolved_support_count": len(self.resolved_ids),
                "resolution_coverage": len(self.resolved_ids) / count if count else None,
                "fully_resolved": self.complete, "unresolved_titles": list(self.unresolved_titles)}


def retrieval_metrics(result: RetrievalResult, labels: LabelResolution, top_k: int,
                      *, routing_ms: float = 0.0) -> dict[str, Any]:
    if top_k < 1:
        raise ValueError("metric cutoff must be positive")
    calls = underlying_calls(result)
    if calls < 1:
        raise ValueError("observed retrieval_calls must be positive for efficiency evaluation")
    chunks = result.chunks[:top_k]
    found = {chunk.document_id for chunk in chunks}
    matched = found & labels.resolved_ids
    recall = len(matched) / len(labels.resolved_ids) if labels.resolved_ids else None
    latency = finite_number(result.metadata.get("retrieval_latency_ms", 0), "retrieval_latency_ms", nonnegative=True)
    return {
        "resolved_support_recall_at_k": recall,
        "hit_at_k": bool(matched) if labels.resolved_ids else None,
        "all_resolved_support_covered": recall == 1 if recall is not None else None,
        "full_support_recall_at_k": recall if labels.complete else None,
        "full_support_covered": recall == 1 if labels.complete else None,
        "matched_support_count": len(matched), "matched_support_ids": sorted(matched),
        "retrieved_document_ids": sorted(found), "retrieved_chunk_ids": [chunk.chunk_id for chunk in chunks],
        "utility": recall / calls if recall is not None else None,
        "underlying_retrieval_calls": calls, "retrieval_latency_ms": latency,
        "router_latency_ms": routing_ms, "initial_stage_latency_ms": routing_ms + latency,
        "retrieved_passages": int(finite_number(result.metadata.get("retrieved_passages", len(result.chunks)), "retrieved_passages", nonnegative=True)),
        "final_context_chunks": len(chunks), "final_context_characters": sum(len(chunk.text) for chunk in chunks),
        "final_context_tokens": sum(len(LocalLexicalRetriever._tokenize(chunk.text)) for chunk in chunks),
    }


def feature_category(features: Mapping[str, Any]) -> str:
    """Mutually exclusive observed signal group, not a semantic ground-truth label."""
    for feature, category in (("dependent", "dependent_signal"), ("mixed", "mixed_signal"),
                              ("exact_anchor", "exact_anchor_signal"), ("conceptual", "conceptual_signal"),
                              ("comparison", "comparison_only")):
        if features.get(feature):
            return category
    if features.get("number_count") or features.get("date_count"):
        return "numeric_or_date_only"
    return "no_recognized_routing_signal"


def analyze_decision(selected: str, observed: Mapping[str, Mapping[str, Any]],
                     chosen: Mapping[str, Any], *, policy_fallback: bool) -> dict[str, Any]:
    """Compare fixed outcomes after retrieval. Causal attribution stays qualified."""
    base: dict[str, Any] = {"objective": OBJECTIVE["id"], "best_observed_strategies": [],
                           "best_quality_strategies": [], "selection_agreement": None,
                           "routing_regret": None, "quality_regret": None,
                           "unnecessary_cost": None, "avoidable_calls": None,
                           "cheaper_equivalent_strategies": [], "missed_retrieval_opportunity": None,
                           "tied_best_utility": None, "tied_best_quality": None,
                           "backend_limitation_possible": False, "router_quality_opportunity": None}
    if chosen["utility"] is None:
        return {**base, "outcome": "insufficient_labels", "reason": "No resolved supports; retrieval quality and regret are undefined, not zero."}
    best_utility = max(item["utility"] for item in observed.values())
    best_recall = max(item["resolved_support_recall_at_k"] for item in observed.values())
    best = [name for name, item in observed.items() if isclose(item["utility"], best_utility, rel_tol=0, abs_tol=1e-12)]
    best_quality = [name for name, item in observed.items() if isclose(item["resolved_support_recall_at_k"], best_recall, rel_tol=0, abs_tol=1e-12)]
    equivalent = {name: item for name, item in observed.items()
                  if isclose(item["resolved_support_recall_at_k"], chosen["resolved_support_recall_at_k"], rel_tol=0, abs_tol=1e-12)
                  and item["underlying_retrieval_calls"] < chosen["underlying_retrieval_calls"]}
    cheaper_calls = min((item["underlying_retrieval_calls"] for item in equivalent.values()), default=chosen["underlying_retrieval_calls"])
    missed = not chosen["hit_at_k"] and any(item["hit_at_k"] for item in observed.values())
    quality_regret = max(0.0, best_recall - chosen["resolved_support_recall_at_k"])
    backend_flag = (selected in {"vector_flat", "hybrid", "multihop"}
                    and chosen["resolved_support_recall_at_k"] < 1 and not policy_fallback)
    if best_recall == 0:
        outcome, reason = "shared_retrieval_failure", "None of the observed strategies retrieved any resolved support."
    elif missed:
        outcome, reason = "missed_retrieval_opportunity", "Selected strategy retrieved no support; an available alternative retrieved support."
    elif quality_regret > 1e-12:
        outcome, reason = "lower_quality_selection", "An available alternative recovered a larger fraction of resolved supports."
    elif equivalent:
        outcome, reason = "unnecessary_retrieval_cost", "Equivalent resolved-support recall was available using fewer underlying calls."
    elif len(best) > 1:
        outcome, reason = "ambiguous_outcome", "Multiple strategies share the best observed efficiency utility."
    else:
        outcome, reason = "selected_best_observed", "Selected strategy achieves the best observed efficiency utility."
    if backend_flag:
        reason += " The selected prototype follows its configured query heuristic; a backend limitation is possible, but this comparison cannot isolate the causal contribution of features versus backend implementation."
    return {**base, "best_observed_strategies": best, "best_quality_strategies": best_quality,
            "best_observed_utility": best_utility, "best_observed_recall": best_recall,
            "selection_agreement": selected in best,
            "routing_regret": max(0.0, best_utility - chosen["utility"]), "quality_regret": quality_regret,
            "unnecessary_cost": bool(equivalent), "avoidable_calls": chosen["underlying_retrieval_calls"] - cheaper_calls,
            "cheaper_equivalent_strategies": list(equivalent), "missed_retrieval_opportunity": missed,
            "tied_best_utility": len(best) > 1, "tied_best_quality": len(best_quality) > 1,
            "backend_limitation_possible": backend_flag, "router_quality_opportunity": quality_regret > 1e-12,
            "shared_incomplete_evidence": best_recall < 1, "outcome": outcome, "reason": reason}


def mean_interval(values: Sequence[float], *, seed: int, samples: int = 1000) -> dict[str, Any]:
    """Seeded percentile bootstrap over questions; describes this local sample only."""
    if samples < 1:
        raise ValueError("bootstrap samples must be positive")
    if not values:
        return {"n": 0, "mean": None, "ci95": None}
    estimate = mean(values)
    if min(values) == max(values):
        return {"n": len(values), "mean": estimate, "ci95": [estimate, estimate]}
    rng = random.Random(seed)
    draws = sorted(sum(rng.choices(values, k=len(values))) / len(values) for _ in range(samples))
    return {"n": len(values), "mean": estimate,
            "ci95": [draws[int(.025 * (samples - 1))], draws[int(.975 * (samples - 1))]]}


def group_summary(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Fallback and decision quality summaries with explicit denominators."""
    labeled = [row for row in records if row["decision_analysis"]["routing_regret"] is not None]
    def average(key: str) -> float | None:
        values = [row["decision_analysis"][key] for row in labeled if row["decision_analysis"].get(key) is not None]
        return mean(values) if values else None
    chosen = [row["per_retriever"]["query_aware"] for row in labeled]
    return {"queries": len(records), "labeled_queries": len(labeled),
            "fallback_count": sum(row["routing"]["fallback_occurred"] for row in records),
            "fallback_rate": mean([int(row["routing"]["fallback_occurred"]) for row in records]) if records else None,
            "mean_recall": mean([item["resolved_support_recall_at_k"] for item in chosen]) if chosen else None,
            "hit_rate": mean([int(item["hit_at_k"]) for item in chosen]) if chosen else None,
            "selection_agreement": average("selection_agreement"), "mean_regret": average("routing_regret"),
            "mean_quality_regret": average("quality_regret"), "missed_opportunity_rate": average("missed_retrieval_opportunity"),
            "unnecessary_cost_rate": average("unnecessary_cost"), "mean_avoidable_calls": average("avoidable_calls"),
            "utility_tie_rate": average("tied_best_utility"), "quality_tie_rate": average("tied_best_quality"),
            "outcomes": dict(Counter(row["decision_analysis"]["outcome"] for row in records)),
            "possible_backend_limitations": sum(row["decision_analysis"]["backend_limitation_possible"] for row in records)}
