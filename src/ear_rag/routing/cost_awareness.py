"""Deterministic evidence-state CAS and nominal incremental work-cost proxy.

No future evidence score, quality, success or gain is predicted here. Nominal
work is an explicit engineering configuration, separate from realized telemetry.
"""
from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from typing import Any

from ear_rag.core.models import EvidenceAssessment, EvidenceDecision, Query, RetrievalResult
from ear_rag.retrieval.local import LocalLexicalRetriever
from .initial import STRATEGIES, finite_number

CAS_POLICY_VERSION = "evidence_sufficiency_cas_v1"
MINIMUM_COST = .05  # Abstract work-cost units; engineering safeguard, not calibration.
DEFAULT_WORK = {
    "local_lexical": {"retrieval_calls": 1, "retrieved_chunks": 5, "latency_ms": 10},
    "vector_flat": {"retrieval_calls": 1, "retrieved_chunks": 5, "latency_ms": 10},
    "hybrid": {"retrieval_calls": 2, "retrieved_chunks": 5, "latency_ms": 20},
    "multihop": {"retrieval_calls": 2, "retrieved_chunks": 5, "latency_ms": 20},
}


def evidence_deficiency(assessment: EvidenceAssessment) -> float:
    score = finite_number(assessment.overall_score, "current ESA")
    if not 0 <= score <= 1:
        raise ValueError("current ESA must be in [0, 1]")
    return 1.0 - score


def incremental_cost(work: Mapping[str, Any]) -> tuple[float, float]:
    """Validate complete nominal work; zero work gets the explicit .05 floor.

    retrieved_chunks means final returned context chunks, not processed chunks or
    hybrid child passages. Never read prior retrieval telemetry as candidate cost.
    """
    values = {}
    for key in ("retrieval_calls", "retrieved_chunks", "latency_ms"):
        if key not in work:
            raise ValueError(f"incremental cost missing {key}")
        value = finite_number(work[key], f"incremental cost {key}", nonnegative=True)
        if key != "latency_ms" and not value.is_integer():
            raise ValueError(f"incremental cost {key} must be an integer")
        values[key] = value
    raw = finite_number(.05 * values["retrieval_calls"] + .01 * values["retrieved_chunks"]
                        + .001 * values["latency_ms"], "incremental cost", nonnegative=True)
    return raw, max(raw, MINIMUM_COST)


def action_suitability(query: Query, assessment: EvidenceAssessment, result: RetrievalResult,
                       action: str, *, query_features: Mapping[str, object] | None = None,
                       attempted_backends: Collection[str] = (),
                       multihop_max_hops: int = 2) -> tuple[float, str]:
    """Binary applicability, not a probability that an action will help.

    Gap: missing literal query tokens OR duplicate normalized texts OR fewer than
    min(k,2) chunks. Two is the existing ESA support-saturation count. Multi-hop
    additionally needs a dependency flag, a partial lexical seed and novel seed
    tokens. It starts fresh retrieval; this gate does not claim semantic coverage.
    """
    evidence_deficiency(assessment)
    if action not in STRATEGIES:
        return 0.0, "unsupported action"
    if assessment.decision == EvidenceDecision.SUFFICIENT:
        return 0.0, "ESA already sufficient"
    if action in set(attempted_backends) | {result.retriever_name}:
        return 0.0, "backend already attempted"
    if isinstance(result.top_k, bool) or not isinstance(result.top_k, int) or result.top_k < 1:
        return 0.0, "missing or invalid requested top_k"
    tokenize = LocalLexicalRetriever._tokenize
    query_terms = set(tokenize(query.text))
    if not query_terms:
        return 0.0, "no query tokens"
    normalized = [tuple(tokenize(chunk.text)) for chunk in result.chunks]
    evidence_terms = set().union(*(set(tokens) for tokens in normalized))
    reasons = []
    if query_terms - evidence_terms:
        reasons.append("missing query tokens")
    if len(set(normalized)) < len(normalized):
        reasons.append("duplicate normalized evidence")
    if len(normalized) < min(result.top_k, 2):
        reasons.append("small evidence set under ESA support rule")
    if not reasons:
        return 0.0, "no supported observable evidence gap"
    if action == "multihop":
        if not query_features or query_features.get("dependent") is not True:
            return 0.0, "dependency indicator absent or false"
        if multihop_max_hops < 2:
            return 0.0, "multi-hop requires at least two configured hops"
        # Conservative gate: no claim that a vector/hybrid chunk is the lexical
        # seed. A full lexical first hop already occupies all terminal positions.
        if result.retriever_name != "local_lexical" or not 0 < len(normalized) < result.top_k:
            return 0.0, "multi-hop requires a nonempty partial lexical seed"
        if not set(normalized[0][:8]) - query_terms:
            return 0.0, "no novel lexical seed tokens"
        reasons.append("dependent query with lexical expansion seed")
    return 1.0, "; ".join(reasons)


@dataclass(frozen=True, slots=True)
class RecoveryEstimate:
    evidence_deficiency: float
    suitability: float
    suitability_reason: str
    raw_incremental_cost: float
    incremental_cost: float
    cas: float
    estimated_work: dict[str, float]


class DeterministicRecoveryEstimator:
    """Compute CAS from present evidence and configured nominal next-action work."""

    def __init__(self, config: Mapping[str, Any] | None = None, *, multihop_max_hops: int = 2) -> None:
        config = {} if config is None else config
        unknown = set(config) - {"policy", "cost_efficiency_threshold", "incremental_work"}
        if unknown:
            raise ValueError(f"unsupported CAS configuration: {sorted(unknown)}")
        if config.get("policy", CAS_POLICY_VERSION) != CAS_POLICY_VERSION:
            raise ValueError("unsupported CAS policy")
        self.threshold = finite_number(config.get("cost_efficiency_threshold", 0.0), "CAS threshold", nonnegative=True)
        if isinstance(multihop_max_hops, bool) or not isinstance(multihop_max_hops, int) or multihop_max_hops < 1:
            raise ValueError("multihop_max_hops must be a positive integer")
        self.max_hops = multihop_max_hops
        work = config.get("incremental_work", DEFAULT_WORK)
        if not isinstance(work, Mapping):
            raise ValueError("incremental_work must be a mapping")
        # Detach caller state. Missing action/measurement stays missing.
        self._work = {key: dict(value) if isinstance(value, Mapping) else value for key, value in work.items()}

    def estimate(self, assessment: EvidenceAssessment, retrieval_result: RetrievalResult,
                 candidate_backend: str, *, query: Query,
                 query_features: Mapping[str, object] | None = None,
                 attempted_backends: Collection[str] = ()) -> RecoveryEstimate:
        deficiency = evidence_deficiency(assessment)
        suitability, reason = action_suitability(
            query, assessment, retrieval_result, candidate_backend, query_features=query_features,
            attempted_backends=attempted_backends, multihop_max_hops=self.max_hops)
        work = self._work.get(candidate_backend)
        if not isinstance(work, Mapping):
            raise ValueError("incremental cost missing action work configuration")
        raw, cost = incremental_cost(work)
        # Invocation budgets of audited real backends. Multi-hop can terminate
        # early; H is a reserved upper bound, not predicted realized work.
        calls = {"local_lexical": 1, "vector_flat": 1, "hybrid": 2, "multihop": self.max_hops}
        if candidate_backend not in calls or work["retrieval_calls"] != calls[candidate_backend]:
            raise ValueError("incremental cost call budget does not match backend structure")
        nominal = {name: float(work[name]) for name in ("retrieval_calls", "retrieved_chunks", "latency_ms")}
        return RecoveryEstimate(deficiency, suitability, reason, raw, cost,
                                deficiency * suitability / cost, nominal)
