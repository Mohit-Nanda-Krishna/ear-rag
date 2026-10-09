"""Query-aware initial dispatch followed by the existing bounded ESA/recovery."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import logging
from typing import Protocol

from ear_rag.core.interfaces import EvidenceAssessor, Retriever
from ear_rag.core.models import EvidenceAssessment, EvidenceDecision, Query, RecoveryAction, RetrievalResult
from .initial import InitialRetrievalRouter, InitialRoutingDecision, finite_number


_LOGGER = logging.getLogger(__name__)


class ControlRecoveryPolicy(Protocol):
    def decide(self, query: Query, assessment: EvidenceAssessment, retrieval_result: RetrievalResult,
               *, total_retrieved_chunks: int = 0) -> RecoveryAction: ...


@dataclass
class RetrievalControlResult:
    query: Query
    initial_retrieval: RetrievalResult
    initial_assessment: EvidenceAssessment
    recovery_decision: RecoveryAction
    recovery_retrieval: RetrievalResult | None = None
    recovery_assessment: EvidenceAssessment | None = None
    final_state: str = "abstain"
    total_retrieval_calls: int = 0
    total_retrieved_chunks: int = 0
    total_latency_ms: float = 0.0
    initial_routing: InitialRoutingDecision | None = None
    routing_latency_ms: float = 0.0
    initial_strategy_selections: int = 1


def underlying_calls(result: RetrievalResult) -> int:
    """Prefer per-invocation calls; retain compatibility with existing fakes."""
    return int(finite_number(result.metadata.get("retrieval_calls", result.metadata.get("retrieval_call_count", 0)),
                             "retrieval_calls", nonnegative=True))


class RetrievalControlPipeline:
    def __init__(self, backends: Mapping[str, Retriever], assessor: EvidenceAssessor,
                 policy: ControlRecoveryPolicy, *, top_k: int = 5,
                 query_analysis: Mapping[str, object] | None = None,
                 max_top_k: int | None = None) -> None:
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        if max_top_k is not None and (isinstance(max_top_k, bool) or not isinstance(max_top_k, int)
                                      or max_top_k < 1 or top_k > max_top_k):
            raise ValueError("top_k must not exceed a positive integer max_top_k")
        self._backends, self._assessor, self._policy, self._top_k = dict(backends), assessor, policy, top_k
        self._available = tuple(name for name, backend in self._backends.items()
                                if callable(getattr(backend, "retrieve", None)))
        settings = {} if query_analysis is None else query_analysis
        router = InitialRetrievalRouter(settings)
        self._router = router if settings.get("enabled", False) else None

    def run(self, query: Query, initial_backend: str) -> RetrievalControlResult:
        routing = self._router.select(query.text, self._available) if self._router else None
        backend_name = routing.selected_strategy if routing else initial_backend
        if backend_name not in self._available:
            raise ValueError(f"Initial retrieval backend {backend_name!r} is unavailable")
        if routing:
            _LOGGER.info("initial_routing policy=%s selected=%s scores=%s features=%s reason=%s fallback=%s routing_latency_ms=%.3f",
                         routing.policy_version, routing.selected_strategy, routing.suitability_scores,
                         routing.features, routing.reason, routing.fallback_reason, routing.routing_latency_ms)
        # Dispatch exactly one selected strategy. Composite backends own their calls.
        initial = self._backends[backend_name].retrieve(query, self._top_k, retrieval_action="initial")
        assessment = self._assessor.assess(query, initial)
        decision = self._policy.decide(query, assessment, initial, total_retrieved_chunks=len(initial.chunks))
        result = RetrievalControlResult(query, initial, assessment, decision, initial_routing=routing,
                                        routing_latency_ms=routing.routing_latency_ms if routing else 0.0)
        if not decision.metadata.get("recover", False):
            return self._finish(result)
        recovery_backend = str(decision.parameters["backend"])
        recovery = self._backends[recovery_backend].retrieve(query, self._top_k, retrieval_action="recovery")
        result.recovery_retrieval = recovery
        result.recovery_assessment = self._assessor.assess(query, recovery)
        return self._finish(result)

    def _finish(self, result: RetrievalControlResult) -> RetrievalControlResult:
        retrievals = [result.initial_retrieval] + ([result.recovery_retrieval] if result.recovery_retrieval else [])
        result.total_retrieval_calls = sum(underlying_calls(item) for item in retrievals)
        result.total_retrieved_chunks = sum(len(item.chunks) for item in retrievals)
        result.total_latency_ms = sum(finite_number(item.metadata.get("retrieval_latency_ms", 0.0),
                                                    "retrieval_latency_ms", nonnegative=True) for item in retrievals)
        final = result.recovery_assessment or result.initial_assessment
        result.final_state = "generate" if final.decision == EvidenceDecision.SUFFICIENT else "abstain"
        return result
