"""Bounded deterministic evidence-sufficiency CAS recovery selection."""
from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from dataclasses import asdict
from typing import Any

from ear_rag.core.models import EvidenceAssessment, EvidenceDecision, Query, RecoveryAction, RetrievalResult
from .cost_awareness import (
    CAS_POLICY_VERSION, DeterministicRecoveryEstimator, action_suitability, evidence_deficiency,
)
from .initial import STRATEGIES


class BoundedRecoveryPolicy:
    def __init__(self, *, max_recovery_rounds: int = 1,
                 recovery_backends: Mapping[str, str | Sequence[str]] | None = None,
                 max_retrieved_chunks: int | None = None, cost_awareness: Mapping[str, Any] | None = None,
                 multihop_max_hops: int = 2) -> None:
        if isinstance(max_recovery_rounds, bool) or not isinstance(max_recovery_rounds, int) or max_recovery_rounds < 0:
            raise ValueError("max_recovery_rounds must be a non-negative integer")
        self._limit, self._chunk_limit = max_recovery_rounds, max_retrieved_chunks
        self._map = {}
        for name, candidates in (recovery_backends or {}).items():
            values = (candidates,) if isinstance(candidates, str) else tuple(candidates)
            if any(not isinstance(value, str) for value in values) or len(set(values)) != len(values):
                raise ValueError("recovery candidates must be unique backend names")
            self._map[name] = values
        self._estimator = DeterministicRecoveryEstimator(cost_awareness, multihop_max_hops=multihop_max_hops)

    def decide(self, query: Query, assessment: EvidenceAssessment, retrieval_result: RetrievalResult,
               *, recovery_round: int = 0, total_retrieved_chunks: int = 0,
               available_backends: Collection[str] = (), attempted_backends: Collection[str] = (),
               query_features: Mapping[str, object] | None = None) -> RecoveryAction:
        deficiency = evidence_deficiency(assessment)
        metadata: dict[str, Any] = {"recover": False, "policy_version": CAS_POLICY_VERSION,
                                    "evidence_deficiency": deficiency,
                                    "cas_threshold": self._estimator.threshold,
                                    "candidate_evaluations": []}

        def stop(reason: str) -> RecoveryAction:
            return RecoveryAction(reason=reason, metadata=metadata)

        if assessment.decision == EvidenceDecision.SUFFICIENT:
            return stop("ESA found current evidence sufficient.")
        if recovery_round >= self._limit:
            return stop("Recovery-round limit reached.")
        if self._chunk_limit is not None and total_retrieved_chunks >= self._chunk_limit:
            return stop("Retrieved-chunk operational budget reached.")
        candidates = self._map.get(retrieval_result.retriever_name, self._map.get("default", ()))
        if not candidates:
            return stop("No configured recovery backend.")
        eligible = []
        # Candidate input order cannot influence scores or tie-breaking.
        for name in sorted(candidates, key=lambda name: (STRATEGIES.index(name) if name in STRATEGIES else len(STRATEGIES), name)):
            entry: dict[str, Any] = {"backend": name, "eligible": False}
            metadata["candidate_evaluations"].append(entry)
            if name not in available_backends:
                entry["reason"] = "backend unavailable or not callable"
                continue
            suitability, reason = action_suitability(
                query, assessment, retrieval_result, name, query_features=query_features,
                attempted_backends=attempted_backends, multihop_max_hops=self._estimator.max_hops)
            entry.update(suitability=suitability, reason=reason)
            if not suitability:
                continue
            try:
                estimate = self._estimator.estimate(assessment, retrieval_result, name, query=query,
                    query_features=query_features, attempted_backends=attempted_backends)
            except (ValueError, OverflowError) as error:
                entry["reason"] = f"invalid incremental cost: {error}"
                continue
            entry.update(asdict(estimate), eligible=True)
            eligible.append((name, estimate))
        if not eligible:
            return stop("No eligible recovery action remains.")
        # Iteration already follows the fixed tie-break order; max retains first.
        backend, best = max(eligible, key=lambda pair: pair[1].cas)
        metadata.update(asdict(best), candidate_backend=backend)
        if best.cas <= self._estimator.threshold:
            metadata["cost_aware_decision"] = "recovery_not_worthwhile"
            return stop("Best CAS does not strictly exceed the configured threshold.")
        metadata.update(recover=True, cost_aware_decision="recovery_worthwhile", recovery_round=recovery_round + 1)
        return RecoveryAction("alternative_retriever", {"backend": backend},
                              "Observable evidence gap; best eligible CAS exceeds threshold.", metadata)
