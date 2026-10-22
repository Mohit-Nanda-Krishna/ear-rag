"""Synthetic specification for evidence-state CAS; never use benchmark files."""
from copy import deepcopy
from dataclasses import asdict
import math

import pytest

from ear_rag.core.models import EvidenceAssessment, Query, RetrievedChunk, RetrievalResult
from ear_rag.routing import BoundedRecoveryPolicy, DeterministicRecoveryEstimator
from ear_rag.routing.cost_awareness import action_suitability, incremental_cost


def assessment(score=.2):
    return EvidenceAssessment(overall_score=score, decision="insufficient")


def result(backend="local_lexical", texts=(), top_k=5):
    return RetrievalResult("q", [RetrievedChunk(str(i), str(i), text, .5, backend)
                                  for i, text in enumerate(texts)], backend, top_k,
                           {"retrieval_calls": 1000, "retrieval_latency_ms": 999999})


def config(threshold=1, work=None):
    return {"cost_efficiency_threshold": threshold, "incremental_work": work or {
        "local_lexical": {"retrieval_calls": 1, "retrieved_chunks": 5, "latency_ms": 10},
        "vector_flat": {"retrieval_calls": 1, "retrieved_chunks": 5, "latency_ms": 10},
        "hybrid": {"retrieval_calls": 2, "retrieved_chunks": 5, "latency_ms": 20},
        "multihop": {"retrieval_calls": 2, "retrieved_chunks": 5, "latency_ms": 20}}}


def decide(candidates, *, current=None, settings=None, available=None, **kwargs):
    policy = BoundedRecoveryPolicy(recovery_backends={"default": candidates},
                                   cost_awareness=settings or config())
    return policy.decide(Query("q", "alpha beta"), assessment(), current or result(),
                         available_backends=candidates if available is None else available, **kwargs)


def test_exact_formula_floor_and_recovery_only_cost():
    estimator = DeterministicRecoveryEstimator(config())
    first = estimator.estimate(assessment(), result(), "vector_flat", query=Query("q", "alpha beta"))
    assert first.evidence_deficiency == .8
    assert first.suitability == 1
    assert first.raw_incremental_cost == pytest.approx(.11)
    assert first.incremental_cost == pytest.approx(.11)
    assert first.cas == pytest.approx(.8 / .11)
    other = result(); other.metadata = {"retrieval_calls": 1, "retrieval_latency_ms": 0}
    assert first == estimator.estimate(assessment(), other, "vector_flat", query=Query("q", "alpha beta"))
    assert incremental_cost({"retrieval_calls": 0, "retrieved_chunks": 0, "latency_ms": 0}) == (0, .05)
    assert incremental_cost({"retrieval_calls": 1, "retrieved_chunks": 2, "latency_ms": 3}) == pytest.approx((.073, .073))


@pytest.mark.parametrize("score", [-.1, 1.1, float("nan"), float("inf"), True])
def test_invalid_current_esa_is_rejected(score):
    with pytest.raises(ValueError, match="ESA"):
        DeterministicRecoveryEstimator(config()).estimate(assessment(score), result(), "vector_flat",
                                                         query=Query("q", "alpha"))


def test_deficiency_is_current_state_not_a_future_gain():
    estimator = DeterministicRecoveryEstimator(config())
    low = estimator.estimate(assessment(.2), result(), "vector_flat", query=Query("q", "alpha"))
    high = estimator.estimate(assessment(.6), result(), "vector_flat", query=Query("q", "alpha"))
    assert low.cas == pytest.approx(2 * high.cas)
    assert not any("gain" in key or "esa_after" in key for key in asdict(low))
    with pytest.raises(ValueError, match="unsupported"):
        DeterministicRecoveryEstimator({**config(), "estimated_esa_gain": {"default": .9}})


@pytest.mark.parametrize("backend", ["local_lexical", "vector_flat", "hybrid"])
def test_binary_suitability_for_alternative_rankings(backend):
    state = result("multihop", ("alpha", "unrelated"))
    args = (Query("q", "alpha beta"), assessment(), state, backend)
    assert action_suitability(*args) == action_suitability(*args)
    assert action_suitability(*args)[0] == 1
    assert action_suitability(*args, attempted_backends=(backend,))[0] == 0


@pytest.mark.parametrize("text", ["", "???"])
def test_empty_query_does_not_trigger_recovery(text):
    assert action_suitability(Query("q", text), assessment(), result(), "vector_flat")[0] == 0


def test_complete_diverse_evidence_has_no_suitability_gap():
    state = result("local_lexical", ("alpha beta", "gamma delta"))
    assert action_suitability(Query("q", "alpha beta"), assessment(), state, "vector_flat")[0] == 0
    # Duplicate text and the existing ESA's two-chunk support saturation are observable proxies.
    assert action_suitability(Query("q", "alpha beta"), assessment(), result(texts=("alpha beta",) * 2), "vector_flat")[0] == 1
    assert action_suitability(Query("q", "alpha beta"), assessment(), result(texts=("alpha beta",)), "vector_flat")[0] == 1


def test_multihop_needs_observed_dependency_seed_and_room_for_new_chunks():
    query = Query("q", "alpha beta")
    state = result(texts=("alpha bridge",))
    args = (query, assessment(), state, "multihop")
    assert action_suitability(*args, query_features={"dependent": True})[0] == 1
    assert action_suitability(*args)[0] == 0
    assert action_suitability(*args, query_features={"dependent": False})[0] == 0
    assert action_suitability(*args, query_features={"dependent": True}, multihop_max_hops=1)[0] == 0
    assert action_suitability(query, assessment(), result(), "multihop", query_features={"dependent": True})[0] == 0
    assert action_suitability(query, assessment(), result(texts=("alpha bridge",), top_k=1), "multihop", query_features={"dependent": True})[0] == 0
    assert action_suitability(query, assessment(), result(texts=("alpha",)), "multihop", query_features={"dependent": True})[0] == 0


def test_ranking_tie_breaking_and_cost_changes():
    current = result("hybrid")
    a = decide(["vector_flat", "local_lexical"], current=current)
    assert a.parameters["backend"] == "local_lexical"
    settings = config(); settings["incremental_work"]["local_lexical"]["latency_ms"] = 100
    b = decide(["local_lexical", "vector_flat"], current=current, settings=settings)
    assert b.parameters["backend"] == "vector_flat"
    assert a == decide(["local_lexical", "vector_flat"], current=current)
    c = decide(["local_lexical", "vector_flat"], current=current, attempted_backends=("local_lexical",))
    assert c.parameters["backend"] == "vector_flat"


def test_strict_boundary_equal_cas_does_not_recover():
    work = {"vector_flat": {"retrieval_calls": 1, "retrieved_chunks": 0, "latency_ms": 0}}
    boundary = .8 / .05
    assert not decide(["vector_flat"], settings=config(boundary, work)).metadata["recover"]
    assert decide(["vector_flat"], settings=config(math.nextafter(boundary, 0), work)).metadata["recover"]


@pytest.mark.parametrize("field", ["retrieval_calls", "retrieved_chunks", "latency_ms"])
@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), None, True])
def test_invalid_cost_components_exclude_candidate(field, value):
    settings = config(); settings["incremental_work"]["vector_flat"][field] = value
    action = decide(["vector_flat"], settings=settings)
    assert not action.metadata["recover"]
    assert "cost" in action.metadata["candidate_evaluations"][0]["reason"]


def test_missing_costs_unknown_actions_and_unavailable_actions_stop_safely():
    settings = config(); del settings["incremental_work"]["vector_flat"]["latency_ms"]
    assert not decide(["vector_flat"], settings=settings).metadata["recover"]
    settings = config(); settings["incremental_work"] = {}
    assert not decide(["vector_flat"], settings=settings).metadata["recover"]
    assert not decide(["vector_flat"], available=[]).metadata["recover"]
    assert not decide(["unknown"], available=["unknown"]).metadata["recover"]
    assert not decide(["local_lexical"]).metadata["recover"]


def test_structural_call_estimates_must_match_the_backend_budget():
    settings = config(); settings["incremental_work"]["hybrid"]["retrieval_calls"] = 1
    assert not decide(["hybrid"], settings=settings).metadata["recover"]


def test_repeatability_input_immutability_and_gold_isolation():
    settings = config(); original = deepcopy(settings)
    state = result(); query = Query("q", "alpha beta", {"answer": "SECRET", "supporting_facts": ["SECRET"]})
    policy = BoundedRecoveryPolicy(recovery_backends={"default": ["vector_flat", "hybrid"]}, cost_awareness=settings)
    first = policy.decide(query, assessment(), state, available_backends=("vector_flat", "hybrid"))
    query.metadata = {"answer": "CHANGED"}; state.metadata["gold"] = "OTHER"
    second = policy.decide(query, assessment(), state, available_backends=("hybrid", "vector_flat"))
    assert first == second and settings == original
    assert "SECRET" not in repr(first)
    assert not any(key in repr(first) for key in ("estimated_esa_after", "expected_evidence_gain"))


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), None, True])
def test_invalid_threshold_is_rejected(value):
    with pytest.raises(ValueError, match="threshold"):
        DeterministicRecoveryEstimator(config(value))


@pytest.mark.parametrize("component", ["retrieval_calls", "retrieved_chunks"])
def test_fractional_work_counts_are_invalid(component):
    work = {"retrieval_calls": 1, "retrieved_chunks": 5, "latency_ms": 10}
    work[component] = .5
    with pytest.raises(ValueError, match="integer"):
        incremental_cost(work)


def test_limits_stop_before_ranking_and_missing_topk_does_not_fabricate_state():
    policy = BoundedRecoveryPolicy(recovery_backends={"default": ["vector_flat"]}, max_retrieved_chunks=5)
    for kwargs, reason in [({"recovery_round": 1}, "Recovery-round"),
                           ({"total_retrieved_chunks": 5}, "operational budget")]:
        action = policy.decide(Query("q", "alpha"), assessment(), result(),
                               available_backends=("vector_flat",), **kwargs)
        assert not action.metadata["recover"] and reason in action.reason
        assert action.metadata["candidate_evaluations"] == []
    assert action_suitability(Query("q", "alpha"), assessment(), result(top_k=0), "vector_flat")[0] == 0


def test_sufficient_evidence_cannot_be_overridden_by_low_cost():
    sufficient = EvidenceAssessment(overall_score=.8, decision="sufficient")
    policy = BoundedRecoveryPolicy(recovery_backends={"default": ["vector_flat"]}, cost_awareness=config(0))
    action = policy.decide(Query("q", "alpha"), sufficient, result(), available_backends=("vector_flat",))
    assert not action.metadata["recover"] and action.metadata["candidate_evaluations"] == []
