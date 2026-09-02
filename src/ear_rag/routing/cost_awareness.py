"""Deterministic, pre-recovery estimates for bounded recovery control.

The estimator deliberately consumes only the current ESA, current retrieval
instrumentation, and configuration.  It never receives recovered documents or
evaluation labels, so it can later be replaced by a learned implementation
behind the same ``estimate`` method.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

from ear_rag.core.models import EvidenceAssessment, RetrievalResult


@dataclass(frozen=True, slots=True)
class RecoveryEstimate:
    """Inspectable expected benefit and operational cost of one candidate."""

    estimated_esa_after: float
    expected_evidence_gain: float
    expected_additional_cost: float
    expected_cost_efficiency: float
    expected_work: dict[str, float]


class DeterministicRecoveryEstimator:
    """Configuration-driven baseline estimator for a candidate recovery action."""

    def __init__(self, config: Mapping[str, object] | None = None) -> None:
        config = dict(config or {})
        self._gains = dict(config.get("estimated_esa_gain", {"default": 0.25}))
        self._work = dict(config.get("expected_work", {"default": {"retrieval_calls": 1, "retrieved_chunks": 5, "latency_ms": 10}}))
        self._weights = dict(config.get("cost_weights", {"retrieval_calls": 0.05, "retrieved_chunks": 0.01, "latency_ms": 0.001}))
        self.threshold = float(config.get("cost_efficiency_threshold", 0.0))
        if self.threshold < 0:
            raise ValueError("cost_efficiency_threshold cannot be negative")

    def estimate(
        self,
        assessment: EvidenceAssessment,
        retrieval_result: RetrievalResult,
        candidate_backend: str,
    ) -> RecoveryEstimate:
        """Estimate using only pre-recovery signals and configured expectations."""
        del retrieval_result  # Contract guard: no candidate/recovered evidence is inspected.
        gain = float(self._by_backend(self._gains, candidate_backend, 0.25))
        if gain < 0:
            raise ValueError("estimated ESA gain cannot be negative")
        current = float(assessment.overall_score)
        estimated_after = min(1.0, current + gain)
        expected_gain = estimated_after - current
        work = self._by_backend(self._work, candidate_backend, {})
        if not isinstance(work, Mapping):
            raise ValueError("expected recovery work must be a mapping")
        expected_work = {
            "retrieval_calls": float(work.get("retrieval_calls", 1)),
            "retrieved_chunks": float(work.get("retrieved_chunks", 0)),
            "latency_ms": float(work.get("latency_ms", 0)),
        }
        if any(value < 0 for value in expected_work.values()):
            raise ValueError("expected recovery work cannot be negative")
        cost = sum(expected_work[name] * float(self._weights.get(name, 0.0)) for name in expected_work)
        if cost <= 0:
            raise ValueError("expected additional recovery cost must be positive")
        return RecoveryEstimate(estimated_after, expected_gain, cost, expected_gain / cost, expected_work)

    @staticmethod
    def _by_backend(values: Mapping[str, object], backend: str, default: object) -> object:
        return values.get(backend, values.get("default", default))
