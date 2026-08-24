"""Explicit finite-state retrieval/ESA/recovery demonstrator."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Mapping
from ear_rag.core.models import EvidenceAssessment, Query, RecoveryAction, RetrievalResult

@dataclass
class RetrievalControlResult:
    query: Query; initial_retrieval: RetrievalResult; initial_assessment: EvidenceAssessment
    recovery_decision: RecoveryAction; recovery_retrieval: RetrievalResult | None = None
    recovery_assessment: EvidenceAssessment | None = None; final_state: str = "abstain"
    total_retrieval_calls: int = 0; total_retrieved_chunks: int = 0; total_latency_ms: float = 0.0

class RetrievalControlPipeline:
    def __init__(self, backends: Mapping[str, object], assessor: object, policy: object, *, top_k: int = 5) -> None:
        self._backends, self._assessor, self._policy, self._top_k = dict(backends), assessor, policy, top_k
    def run(self, query: Query, initial_backend: str) -> RetrievalControlResult:
        initial = self._backends[initial_backend].retrieve(query, self._top_k, retrieval_action="initial")
        assessment = self._assessor.assess(query, initial)
        total_chunks = len(initial.chunks); decision = self._policy.decide(query, assessment, initial, total_retrieved_chunks=total_chunks)
        result = RetrievalControlResult(query, initial, assessment, decision)
        if not decision.metadata.get("recover", False):
            return self._finish(result)
        backend = str(decision.parameters["backend"])
        recovery = self._backends[backend].retrieve(query, self._top_k, retrieval_action="recovery")
        second = self._assessor.assess(query, recovery)
        result.recovery_retrieval, result.recovery_assessment = recovery, second
        return self._finish(result)
    def _finish(self, result: RetrievalControlResult) -> RetrievalControlResult:
        retrievals = [result.initial_retrieval] + ([result.recovery_retrieval] if result.recovery_retrieval else [])
        result.total_retrieval_calls = sum(int(item.metadata.get("retrieval_call_count", 0)) for item in retrievals)
        result.total_retrieved_chunks = sum(len(item.chunks) for item in retrievals)
        result.total_latency_ms = sum(float(item.metadata.get("retrieval_latency_ms", 0.0)) for item in retrievals)
        final = result.recovery_assessment or result.initial_assessment
        result.final_state = "generate" if final.decision.value == "sufficient" else "abstain"
        return result
