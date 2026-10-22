"""Focused deterministic tests for bounded evidence-sufficiency CAS."""
import pytest
from ear_rag.core.models import EvidenceAssessment, EvidenceDecision, Query, RetrievalResult
from ear_rag.routing import BoundedRecoveryPolicy, DeterministicRecoveryEstimator, RetrievalControlPipeline


_CONFIG = {
    "cost_efficiency_threshold": 10.0,
    "incremental_work": {"vector_flat": {"retrieval_calls": 1, "retrieved_chunks": 2, "latency_ms": 3}},
}


def _assessment(score: float = 0.2) -> EvidenceAssessment:
    return EvidenceAssessment(overall_score=score, decision=EvidenceDecision.INSUFFICIENT)


def _result(name: str = "local_lexical") -> RetrievalResult:
    return RetrievalResult("q", retriever_name=name, top_k=5, metadata={"retrieval_call_count": 1})


def test_estimator_calculates_deficiency_cost_and_cas():
    estimate = DeterministicRecoveryEstimator(_CONFIG).estimate(_assessment(), _result(), "vector_flat",
                                                                query=Query("q", "question"))
    assert estimate.evidence_deficiency == .8
    assert estimate.suitability == 1
    assert estimate.incremental_cost == pytest.approx(.073)
    assert estimate.cas == pytest.approx(.8 / .073)


def test_threshold_pass_and_fail_are_explicit():
    def decision(settings):
        return BoundedRecoveryPolicy(recovery_backends={"local_lexical": "vector_flat"},
                                     cost_awareness=settings).decide(
            Query("q", "question"), _assessment(), _result(), available_backends=("vector_flat",))
    passed = decision(_CONFIG)
    assert passed.metadata["recover"] and passed.metadata["cost_aware_decision"] == "recovery_worthwhile"
    failed = decision({**_CONFIG, "cost_efficiency_threshold": 12.0})
    assert not failed.metadata["recover"] and failed.metadata["cost_aware_decision"] == "recovery_not_worthwhile"


class _SpyRetriever:
    def __init__(self, name: str) -> None:
        self.name, self.calls = name, 0

    def retrieve(self, query, top_k, **kwargs):
        self.calls += 1
        return RetrievalResult(query.query_id, retriever_name=self.name, top_k=top_k,
                               metadata={"retrieval_call_count": 1, "retrieval_latency_ms": 0.0})


class _SequentialAssessor:
    def __init__(self, second_sufficient: bool = True) -> None:
        self.calls, self.second_sufficient = 0, second_sufficient

    def assess(self, query, result):
        self.calls += 1
        sufficient = self.calls == 2 and self.second_sufficient
        return EvidenceAssessment(overall_score=0.8 if sufficient else 0.2,
                                  decision=EvidenceDecision.SUFFICIENT if sufficient else EvidenceDecision.INSUFFICIENT)


def test_rejected_recovery_occurs_before_retrieval_and_skips_second_esa():
    initial, candidate, assessor = _SpyRetriever("local_lexical"), _SpyRetriever("vector_flat"), _SequentialAssessor()
    policy = BoundedRecoveryPolicy(recovery_backends={"local_lexical": "vector_flat"},
                                   cost_awareness={**_CONFIG, "cost_efficiency_threshold": 12.0})
    result = RetrievalControlPipeline({"local_lexical": initial, "vector_flat": candidate}, assessor, policy).run(Query("q", "question"), "local_lexical")
    assert initial.calls == 1 and candidate.calls == 0 and assessor.calls == 1
    assert result.recovery_retrieval is None and result.recovery_assessment is None and result.final_state == "abstain"


def test_accepted_recovery_runs_once_then_second_esa_and_can_abstain():
    initial, candidate, assessor = _SpyRetriever("local_lexical"), _SpyRetriever("vector_flat"), _SequentialAssessor(second_sufficient=False)
    policy = BoundedRecoveryPolicy(recovery_backends={"local_lexical": "vector_flat"}, cost_awareness=_CONFIG)
    result = RetrievalControlPipeline({"local_lexical": initial, "vector_flat": candidate}, assessor, policy).run(Query("q", "question"), "local_lexical")
    assert initial.calls == 1 and candidate.calls == 1 and assessor.calls == 2
    assert result.recovery_retrieval is not None and result.recovery_assessment is not None and result.final_state == "abstain"


def test_estimator_never_reads_runtime_labels():
    class LabelGuardResult(RetrievalResult):
        def __getattribute__(self, name):
            if name in {"answer", "answers", "supporting_facts", "evidences", "gold"}:
                raise AssertionError("runtime labels must not be accessed")
            return super().__getattribute__(name)

    estimate = DeterministicRecoveryEstimator(_CONFIG).estimate(_assessment(),
        LabelGuardResult("q", retriever_name="local_lexical", top_k=5), "vector_flat", query=Query("q", "question"))
    assert estimate.cas == pytest.approx(.8 / .073)
