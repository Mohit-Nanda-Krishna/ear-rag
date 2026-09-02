"""Configurable, bounded cost-aware recovery policy skeleton."""
from __future__ import annotations
from collections.abc import Mapping
from ear_rag.core.models import EvidenceAssessment, EvidenceDecision, Query, RecoveryAction, RetrievalResult
from .cost_awareness import DeterministicRecoveryEstimator

class BoundedRecoveryPolicy:
    def __init__(self, *, max_recovery_rounds: int = 1, recovery_backends: Mapping[str, str] | None = None,
                 max_retrieved_chunks: int | None = None, cost_awareness: Mapping[str, object] | None = None,
                 estimator: object | None = None) -> None:
        if max_recovery_rounds < 0: raise ValueError("max_recovery_rounds cannot be negative")
        self._limit, self._map, self._chunk_limit = max_recovery_rounds, dict(recovery_backends or {}), max_retrieved_chunks
        self._estimator = estimator or DeterministicRecoveryEstimator(cost_awareness)
    def decide(self, query: Query, assessment: EvidenceAssessment, retrieval_result: RetrievalResult,
               *, recovery_round: int = 0, total_retrieved_chunks: int = 0) -> RecoveryAction:
        if assessment.decision is EvidenceDecision.SUFFICIENT:
            return RecoveryAction(reason="ESA found current evidence sufficient.", metadata={"recover": False})
        if recovery_round >= self._limit:
            return RecoveryAction(reason="Recovery-round limit reached.", metadata={"recover": False})
        if self._chunk_limit is not None and total_retrieved_chunks >= self._chunk_limit:
            return RecoveryAction(reason="Retrieved-chunk operational budget reached.", metadata={"recover": False})
        backend = self._map.get(retrieval_result.retriever_name, self._map.get("default"))
        if not backend:
            return RecoveryAction(reason="No configured recovery backend.", metadata={"recover": False})
        estimate = self._estimator.estimate(assessment, retrieval_result, backend)
        estimate_metadata = {
            "candidate_backend": backend,
            "estimated_esa_after": estimate.estimated_esa_after,
            "expected_evidence_gain": estimate.expected_evidence_gain,
            "expected_additional_cost": estimate.expected_additional_cost,
            "expected_cost_efficiency": estimate.expected_cost_efficiency,
            "cost_efficiency_threshold": self._estimator.threshold,
            "expected_work": estimate.expected_work,
        }
        if estimate.expected_cost_efficiency < self._estimator.threshold:
            return RecoveryAction(
                reason="Recovery is not worthwhile under the configured cost-efficiency threshold.",
                metadata={"recover": False, "cost_aware_decision": "recovery_not_worthwhile", **estimate_metadata},
            )
        return RecoveryAction("alternative_retriever", {"backend": backend},
            f"ESA is {assessment.decision.value}; bounded recovery uses configured {backend} backend.",
            {"recover": True, "recovery_round": recovery_round + 1, "cost_aware_decision": "recovery_worthwhile", **estimate_metadata,
             "cost_proxies": {"prior_calls": retrieval_result.metadata.get("retrieval_call_count", 0), "prior_chunks": total_retrieved_chunks}})
