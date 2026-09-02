"""Focused tests for deterministic pre-recovery cost-aware control."""
import pytest
from ear_rag.core.models import EvidenceAssessment, EvidenceDecision, Query, RetrievalResult
from ear_rag.routing import BoundedRecoveryPolicy, DeterministicRecoveryEstimator, RetrievalControlPipeline


_CONFIG = {
    "cost_efficiency_threshold": 2.0,
    "estimated_esa_gain": {"candidate": 0.30},
    "expected_work": {"candidate": {"retrieval_calls": 1, "retrieved_chunks": 2, "latency_ms": 3}},
    "cost_weights": {"retrieval_calls": 0.1, "retrieved_chunks": 0.01, "latency_ms": 0.001},
}


def _assessment(score: float = 0.2) -> EvidenceAssessment:
    return EvidenceAssessment(overall_score=score, decision=EvidenceDecision.INSUFFICIENT)


def _result(name: str = "initial") -> RetrievalResult:
    return RetrievalResult("q", retriever_name=name, metadata={"retrieval_call_count": 1})


def test_estimator_calculates_gain_cost_and_cost_efficiency():
    estimate = DeterministicRecoveryEstimator(_CONFIG).estimate(_assessment(), _result(), "candidate")
    assert estimate.estimated_esa_after == 0.5
    assert estimate.expected_evidence_gain == 0.3
    assert estimate.expected_additional_cost == pytest.approx(0.123)
    assert round(estimate.expected_cost_efficiency, 6) == round(0.3 / 0.123, 6)


def test_threshold_pass_and_fail_are_explicit():
    policy = BoundedRecoveryPolicy(recovery_backends={"initial": "candidate"}, cost_awareness=_CONFIG)
    passed = policy.decide(Query("q", "question"), _assessment(), _result())
    assert passed.metadata["recover"] and passed.metadata["cost_aware_decision"] == "recovery_worthwhile"
    failed_config = {**_CONFIG, "cost_efficiency_threshold": 3.0}
    failed = BoundedRecoveryPolicy(recovery_backends={"initial": "candidate"}, cost_awareness=failed_config).decide(Query("q", "question"), _assessment(), _result())
    assert not failed.metadata["recover"] and failed.metadata["cost_aware_decision"] == "recovery_not_worthwhile"


class _SpyRetriever:
    def __init__(self, name: str) -> None:
        self.name, self.calls = name, 0

    def retrieve(self, query, top_k, **kwargs):
        self.calls += 1
        return RetrievalResult(query.query_id, retriever_name=self.name, top_k=top_k, metadata={"retrieval_call_count": 1, "retrieval_latency_ms": 0.0})


class _SequentialAssessor:
    def __init__(self, second_sufficient: bool = True) -> None:
        self.calls, self.second_sufficient = 0, second_sufficient

    def assess(self, query, result):
        self.calls += 1
        sufficient = self.calls == 2 and self.second_sufficient
        return EvidenceAssessment(overall_score=0.8 if sufficient else 0.2, decision=EvidenceDecision.SUFFICIENT if sufficient else EvidenceDecision.INSUFFICIENT)


def test_rejected_recovery_occurs_before_retrieval_and_skips_second_esa():
    initial, candidate, assessor = _SpyRetriever("initial"), _SpyRetriever("candidate"), _SequentialAssessor()
    policy = BoundedRecoveryPolicy(recovery_backends={"initial": "candidate"}, cost_awareness={**_CONFIG, "cost_efficiency_threshold": 3.0})
    result = RetrievalControlPipeline({"initial": initial, "candidate": candidate}, assessor, policy).run(Query("q", "question"), "initial")
    assert initial.calls == 1 and candidate.calls == 0 and assessor.calls == 1
    assert result.recovery_retrieval is None and result.recovery_assessment is None and result.final_state == "abstain"


def test_accepted_recovery_runs_once_then_second_esa_and_can_abstain():
    initial, candidate, assessor = _SpyRetriever("initial"), _SpyRetriever("candidate"), _SequentialAssessor(second_sufficient=False)
    policy = BoundedRecoveryPolicy(recovery_backends={"initial": "candidate"}, cost_awareness=_CONFIG)
    result = RetrievalControlPipeline({"initial": initial, "candidate": candidate}, assessor, policy).run(Query("q", "question"), "initial")
    assert initial.calls == 1 and candidate.calls == 1 and assessor.calls == 2
    assert result.recovery_retrieval is not None and result.recovery_assessment is not None and result.final_state == "abstain"


def test_estimator_never_reads_runtime_labels():
    class LabelGuardResult:
        def __getattribute__(self, name):
            if name in {"answer", "answers", "supporting_facts", "evidences", "gold"}:
                raise AssertionError("runtime labels must not be accessed")
            return super().__getattribute__(name)

    estimate = DeterministicRecoveryEstimator(_CONFIG).estimate(_assessment(), LabelGuardResult(), "candidate")
    assert estimate.expected_evidence_gain == 0.3
