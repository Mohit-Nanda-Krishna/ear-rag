"""Dispatch, privacy, bounds, and real offline wiring for initial selection."""

import logging

import pytest

from ear_rag.config.loader import load_config
from ear_rag.core.models import EvidenceAssessment, Query, RetrievedChunk, RetrievalResult
from ear_rag.demo import DemoRunner, build_backends
from ear_rag.evaluate_initial import load_smoke_examples
from ear_rag.routing import BoundedRecoveryPolicy, LightweightQueryAnalyzer, RetrievalControlPipeline
from ear_rag.routing.initial import STRATEGIES


class SpyRetriever:
    def __init__(self, name):
        self.name, self.calls, self.results = name, [], []

    def retrieve(self, query, top_k, **kwargs):
        self.calls.append((query, top_k, kwargs))
        result = RetrievalResult(query.query_id,
                                 [RetrievedChunk("c", "d", "solar power", 1, self.name)], self.name, top_k,
                                 {"retrieval_calls": 1, "retrieval_call_count": len(self.calls), "retrieval_latency_ms": 1.5})
        self.results.append(result)
        return result


class SpyAssessor:
    def __init__(self, sufficient=True):
        self.calls, self.sufficient = [], sufficient

    def assess(self, query, result):
        self.calls.append((query, result))
        return EvidenceAssessment(overall_score=.9 if self.sufficient else .1,
                                  decision="sufficient" if self.sufficient else "insufficient")


@pytest.mark.parametrize("question,selected", [
    ("Find XJ-42", "local_lexical"), ("Explain solar power", "vector_flat"),
    ("Explain XJ-42", "hybrid"), ("Where was the author of Golden River born?", "multihop"),
])
def test_one_initial_dispatch_original_query_parameters_and_evidence(question, selected):
    backends = {name: SpyRetriever(name) for name in STRATEGIES}
    assessor = SpyAssessor()
    query = Query("identity", question, {"source": "user"})
    result = RetrievalControlPipeline(backends, assessor, BoundedRecoveryPolicy(), top_k=3,
                                      query_analysis={"enabled": True}).run(query, "local_lexical")
    assert {name: len(backend.calls) for name, backend in backends.items()} == {name: int(name == selected) for name in STRATEGIES}
    received, top_k, parameters = backends[selected].calls[0]
    assert received is query and top_k == 3 and parameters == {"retrieval_action": "initial"}
    assert assessor.calls[0][0] is query
    assert assessor.calls[0][1] is backends[selected].results[0] is result.initial_retrieval
    assert result.initial_strategy_selections == 1 and result.total_retrieval_calls == 1
    assert result.recovery_retrieval is None and result.routing_latency_ms >= 0
    assert result.total_latency_ms == 1.5  # Routing is a separate metric.


def test_disabled_preserves_explicit_backend_without_analyzing(monkeypatch):
    def fail(*args):
        raise AssertionError("disabled analyzer called")
    monkeypatch.setattr(LightweightQueryAnalyzer, "analyze", fail)
    backends = {name: SpyRetriever(name) for name in STRATEGIES}
    result = RetrievalControlPipeline(backends, SpyAssessor(), BoundedRecoveryPolicy(),
                                      query_analysis={"enabled": False}).run(Query("q", "Find XJ-42"), "hybrid")
    assert len(backends["hybrid"].calls) == 1 and result.initial_routing is None
    assert result.routing_latency_ms == 0


def test_availability_and_resource_limits_do_not_probe_backends():
    backends = {"local_lexical": SpyRetriever("local_lexical")}
    pipeline = RetrievalControlPipeline(backends, SpyAssessor(), BoundedRecoveryPolicy(), top_k=2,
                                         max_top_k=2, query_analysis={"enabled": True})
    assert backends["local_lexical"].calls == []
    result = pipeline.run(Query("q", "Explain energy"), "local_lexical")
    assert result.initial_routing.fallback_reason and len(backends["local_lexical"].calls) == 1
    with pytest.raises(ValueError, match="max_top_k"):
        RetrievalControlPipeline(backends, SpyAssessor(), BoundedRecoveryPolicy(), top_k=3, max_top_k=2)
    with pytest.raises(ValueError, match="unavailable"):
        RetrievalControlPipeline(backends, SpyAssessor(), BoundedRecoveryPolicy()).run(Query("q", "energy"), "hybrid")
    with pytest.raises(ValueError, match="No eligible"):
        RetrievalControlPipeline({}, SpyAssessor(), BoundedRecoveryPolicy(), query_analysis={"enabled": True}).run(Query("q", "energy"), "hybrid")


@pytest.mark.parametrize("round_limit", [0, 1, 5])
def test_existing_recovery_stays_at_most_one_round(round_limit):
    backends = {name: SpyRetriever(name) for name in STRATEGIES}
    assessor = SpyAssessor(sufficient=False)
    policy = BoundedRecoveryPolicy(max_recovery_rounds=round_limit, recovery_backends={"vector_flat": "hybrid"})
    result = RetrievalControlPipeline(backends, assessor, policy, query_analysis={"enabled": True}).run(Query("q", "Explain energy"), "local_lexical")
    assert len(backends["vector_flat"].calls) == 1
    assert len(backends["hybrid"].calls) == int(round_limit > 0)
    assert len(assessor.calls) == 1 + int(round_limit > 0)
    assert not backends["local_lexical"].calls and not backends["multihop"].calls
    assert result.final_state == "abstain"
    if round_limit:
        assert backends["hybrid"].calls[0][2] == {"retrieval_action": "recovery"}
        assert result.recovery_decision.metadata["recovery_round"] == 1


def test_router_analyzer_boundary_drops_all_metadata_and_logs_no_query(monkeypatch, caplog):
    original = LightweightQueryAnalyzer.analyze
    received = []
    def guarded(self, query):
        assert query.metadata == {} and query.query_id == ""
        received.append(query)
        return original(self, query)
    monkeypatch.setattr(LightweightQueryAnalyzer, "analyze", guarded)
    backend = SpyRetriever("local_lexical")
    pipeline = RetrievalControlPipeline({"local_lexical": backend}, SpyAssessor(), BoundedRecoveryPolicy(), query_analysis={"enabled": True})
    with caplog.at_level(logging.INFO, logger="ear_rag.routing.pipeline"):
        a = pipeline.run(Query("q", "PRIVATE-XJ42", {"gold": "secret", "answer": "secret", "supporting_facts": ["secret"]}), "local_lexical")
        b = pipeline.run(Query("different id", "PRIVATE-XJ42", {"answers": ["other"], "supporting_document_ids": ["other"]}), "local_lexical")
    assert len(received) == 2
    assert a.initial_routing.features == b.initial_routing.features
    assert a.initial_routing.suitability_scores == b.initial_routing.suitability_scores
    assert a.initial_routing.selected_strategy == b.initial_routing.selected_strategy
    assert "PRIVATE-XJ42" not in caplog.text and "secret" not in caplog.text
    assert "routing_latency_ms" in caplog.text and "query_features_v1" in caplog.text


@pytest.mark.parametrize("question,strategy,calls", [
    ("Explain how XJ-42 regulates solar power", "hybrid", 2),
    ("Where was the author of Golden River born?", "multihop", 2),
])
def test_real_composite_strategy_calls_and_repeated_run_accounting(question, strategy, calls):
    examples = load_smoke_examples()
    config = load_config()
    backends = build_backends([doc for example in examples for doc in example.documents], config)
    pipeline = RetrievalControlPipeline(backends, SpyAssessor(), BoundedRecoveryPolicy(max_recovery_rounds=0),
                                         top_k=3, query_analysis=config["query_analysis"])
    for _ in range(2):
        result = pipeline.run(Query("q", question), "local_lexical")
        assert result.initial_routing.selected_strategy == strategy
        assert result.initial_strategy_selections == 1
        assert result.total_retrieval_calls == calls
        assert result.initial_retrieval.chunks and len(result.initial_retrieval.chunks) <= 3
        assert result.recovery_retrieval is None


def test_real_pipeline_esa_wiring_with_synthetic_fixture():
    from ear_rag.evidence import DeterministicEvidenceAssessor
    examples = load_smoke_examples()
    config = load_config()
    backends = build_backends([doc for example in examples for doc in example.documents], config)
    pipeline = RetrievalControlPipeline(backends, DeterministicEvidenceAssessor(), BoundedRecoveryPolicy(max_recovery_rounds=0),
                                         top_k=5, query_analysis=config["query_analysis"])
    result = pipeline.run(Query("q", examples[0].question), "local_lexical")
    assert result.initial_routing.selected_strategy == "local_lexical"
    assert "manual" in {chunk.document_id for chunk in result.initial_retrieval.chunks}
    assert result.initial_assessment == DeterministicEvidenceAssessor().assess(result.query, result.initial_retrieval)


def test_main_demo_honors_disabled_configured_backend():
    runner = DemoRunner()
    runner.config["query_analysis"]["enabled"] = False
    runner.config["retrieval"]["backend"] = "vector_flat"
    result = runner.run_controller(0)
    assert result.initial_routing is None
    assert result.initial_retrieval.retriever_name == "vector_flat"


def test_retrieval_failure_propagates_without_hidden_retry_or_other_strategy():
    class BrokenRetriever(SpyRetriever):
        def retrieve(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            raise RuntimeError("backend failed")
    backends = {name: SpyRetriever(name) for name in STRATEGIES}
    backends["vector_flat"] = BrokenRetriever("vector_flat")
    pipeline = RetrievalControlPipeline(backends, SpyAssessor(), BoundedRecoveryPolicy(), query_analysis={"enabled": True})
    with pytest.raises(RuntimeError, match="backend failed"):
        pipeline.run(Query("q", "Explain electricity"), "local_lexical")
    assert len(backends["vector_flat"].calls) == 1
    assert all(not backend.calls for name, backend in backends.items() if name != "vector_flat")


def test_registry_placeholder_is_not_treated_as_available():
    working = SpyRetriever("local_lexical")
    result = RetrievalControlPipeline({"local_lexical": working, "vector_flat": object()},
                                      SpyAssessor(), BoundedRecoveryPolicy(), query_analysis={"enabled": True}).run(Query("q", "Explain energy"), "local_lexical")
    assert result.initial_routing.selected_strategy == "local_lexical"
    assert "vector_flat" not in result.initial_routing.eligible_strategies
    assert result.initial_routing.fallback_reason


def test_real_shared_children_count_initial_and_recovery_calls_once_each():
    examples = load_smoke_examples()
    backends = build_backends([doc for example in examples for doc in example.documents])
    policy = BoundedRecoveryPolicy(recovery_backends={"hybrid": "local_lexical"})
    pipeline = RetrievalControlPipeline(backends, SpyAssessor(sufficient=False), policy,
                                         query_analysis={"enabled": True})
    result = pipeline.run(Query("q", "Explain XJ-42"), "local_lexical")
    assert result.initial_routing.selected_strategy == "hybrid"
    assert result.recovery_retrieval.retriever_name == "local_lexical"
    assert result.recovery_retrieval.metadata["retrieval_call_count"] == 2  # Legacy cumulative counter.
    assert result.total_retrieval_calls == 3  # Two hybrid children + one recovery.
    assert result.recovery_decision.metadata["recovery_round"] == 1
