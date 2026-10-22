"""Real runtime regressions, without external data or a simulated generator."""

import subprocess
import sys

import pytest

from ear_rag.config import load_config
from ear_rag.core.models import Document, Query
from ear_rag.demo import _print_evidence, build_backends
from ear_rag.evidence import DeterministicEvidenceAssessor
from ear_rag.routing import BoundedRecoveryPolicy, RetrievalControlPipeline


_DOCUMENTS = [
    Document("solar-a", "solar electricity storage", {"title": "Solar guide"}),
    Document("solar-b", "solar electricity panels", {"title": "Panel guide"}),
    Document("ocean", "ocean tides currents", {"title": "Ocean guide"}),
]


def _tracked_components(monkeypatch, documents):
    """Observe the real leaf retrievers and real configured ESA without faking them."""
    config = load_config()
    backends = build_backends(documents, config)
    events = []
    for name in ("local_lexical", "vector_flat"):
        original = backends[name].retrieve

        def retrieve(query, top_k, _original=original, _name=name, **kwargs):
            result = _original(query, top_k, **kwargs)
            events.append(("retrieve", _name, query, result))
            return result

        monkeypatch.setattr(backends[name], "retrieve", retrieve)
    settings = config["evidence_assessment"]
    assessor = DeterministicEvidenceAssessor(
        sufficient_threshold=settings["sufficient_threshold"],
        uncertain_threshold=settings["uncertain_threshold"], weights=settings["weights"],
    )
    original_assess = assessor.assess

    def assess(query, retrieval):
        assessment = original_assess(query, retrieval)
        events.append(("assess", retrieval.retriever_name, query, assessment))
        return assessment

    monkeypatch.setattr(assessor, "assess", assess)
    return config, backends, assessor, events


def _policy(config, **overrides):
    settings = config["recovery"]
    return BoundedRecoveryPolicy(**{
        "max_recovery_rounds": settings["max_recovery_rounds"],
        "recovery_backends": settings["recovery_backends"],
        "max_retrieved_chunks": settings["max_retrieved_chunks"],
        "cost_awareness": settings["cost_awareness"], **overrides,
    })


def _assert_observed_costs(result, events):
    leaf_calls = [item for item in events if item[0] == "retrieve"]
    assert result.total_retrieval_calls == len(leaf_calls)
    retrievals = [result.initial_retrieval]
    if result.recovery_retrieval is not None:
        retrievals.append(result.recovery_retrieval)
    assert result.total_retrieved_chunks == sum(len(item.chunks) for item in retrievals)
    assert result.total_latency_ms == pytest.approx(
        sum(item.metadata["retrieval_latency_ms"] for item in retrievals)
    )
    for retrieval in retrievals:
        assert retrieval.metadata["returned_chunk_count"] == len(retrieval.chunks)
        assert retrieval.metadata["requested_top_k"] == 5
        assert retrieval.metadata["retrieval_latency_ms"] >= 0
        assert retrieval.metadata["retrieved_passages"] >= len(retrieval.chunks)


def test_evidence_display_uses_preserved_document_title():
    backends = build_backends([
        Document("solar", "solar electricity", {"title": "Solar guide"}),
    ])
    result = backends["local_lexical"].retrieve(Query("q", "solar electricity"), 5)
    output = []
    _print_evidence([result], output.append)
    assert "Title       : Solar guide" in "\n".join(output)
    assert "(untitled)" not in "\n".join(output)


@pytest.mark.parametrize("candidate", [None, object()])
def test_unavailable_recovery_is_excluded_without_another_retrieval(candidate):
    backends = build_backends([])
    if candidate is None:
        del backends["vector_flat"]
    else:
        backends["vector_flat"] = candidate
    policy = BoundedRecoveryPolicy(recovery_backends={"local_lexical": "vector_flat"})
    pipeline = RetrievalControlPipeline(backends, DeterministicEvidenceAssessor(), policy)
    result = pipeline.run(Query("q", "unmatched vocabulary"), "local_lexical")
    assert not result.recovery_decision.metadata["recover"]
    assert result.recovery_retrieval is result.recovery_assessment is None
    assert result.final_state == "abstain"
    assert "unavailable" in result.recovery_decision.metadata["candidate_evaluations"][0]["reason"]
    assert backends["local_lexical"]._retrieval_call_count == 1


@pytest.mark.parametrize("candidate", [None, object()])
def test_dispatch_guard_still_rejects_an_unavailable_action_from_a_custom_policy(candidate):
    from ear_rag.core.models import RecoveryAction

    class InvalidPolicy:
        def decide(self, *args, **kwargs):
            return RecoveryAction("alternative_retriever", {"backend": "vector_flat"}, metadata={"recover": True})

    backends = build_backends([])
    if candidate is None:
        del backends["vector_flat"]
    else:
        backends["vector_flat"] = candidate
    pipeline = RetrievalControlPipeline(backends, DeterministicEvidenceAssessor(), InvalidPolicy())
    with pytest.raises(ValueError, match="Recovery.*vector_flat.*unavailable"):
        pipeline.run(Query("q", "unmatched vocabulary"), "local_lexical")
    assert backends["local_lexical"]._retrieval_call_count == 1


@pytest.mark.parametrize("backend,nonempty_calls", [
    ("local_lexical", 1), ("vector_flat", 1), ("hybrid", 2), ("multihop", 2),
])
@pytest.mark.parametrize("empty", [False, True])
def test_real_backend_pipeline_is_stable_and_counts_executed_work(
    monkeypatch, backend, nonempty_calls, empty,
):
    config, backends, assessor, events = _tracked_components(
        monkeypatch, [] if empty else _DOCUMENTS,
    )
    pipeline = RetrievalControlPipeline(
        backends, assessor, _policy(config, max_recovery_rounds=0 if empty else 1),
        top_k=5, query_analysis={"enabled": False},
    )
    previous = None
    for _ in range(2):
        events.clear()
        result = pipeline.run(Query("q", "solar electricity"), backend)
        retrieval = result.initial_retrieval
        assert retrieval.retriever_name == backend and retrieval.query_id == "q"
        assert result.total_retrieval_calls == (1 if empty and backend == "multihop" else nonempty_calls)
        assert bool(retrieval.chunks) is not empty
        assert result.final_state == ("abstain" if empty else "generate")
        assert result.recovery_retrieval is result.recovery_assessment is None
        if not empty:
            assert "ESA found current evidence sufficient" in result.recovery_decision.reason
        assert [event[0] for event in events].count("assess") == 1
        assert result.initial_assessment.decision == ("insufficient" if empty else "sufficient")
        for component in ("relevance", "coverage", "support", "consistency"):
            assert 0 <= getattr(result.initial_assessment, component) <= 1
        evidence = [(chunk.chunk_id, chunk.document_id, chunk.text, chunk.retrieval_score)
                    for chunk in retrieval.chunks]
        if previous is not None:
            assert evidence == previous
        previous = evidence
        _assert_observed_costs(result, events)


@pytest.mark.parametrize("recovered", [False, True])
def test_real_recovery_reassesses_once_and_uses_actual_esa(monkeypatch, recovered):
    config, backends, assessor, events = _tracked_components(
        monkeypatch, _DOCUMENTS if recovered else [],
    )
    # A deliberately empty initial index; the alternative has evidence only in
    # the success case. Both retrievers and both ESA calls remain real.
    backends["local_lexical"].index([])
    result = RetrievalControlPipeline(
        backends, assessor, _policy(config), top_k=5,
        query_analysis=config["query_analysis"],
    ).run(Query("q", "solar electricity"), config["retrieval"]["backend"])
    assert [(event[0], event[1]) for event in events] == [
        ("retrieve", "local_lexical"), ("assess", "local_lexical"),
        ("retrieve", "vector_flat"), ("assess", "vector_flat"),
    ]
    assert result.initial_routing.selected_strategy == "local_lexical"
    assert result.initial_assessment.overall_score == 0
    assert result.recovery_decision.metadata["recovery_round"] == 1
    assert result.recovery_retrieval.metadata["retrieval_action"] == "recovery"
    assert result.recovery_assessment is events[-1][3]
    assert result.final_state == ("generate" if recovered else "abstain")
    decision = result.recovery_decision.metadata
    assert "estimated_esa_after" not in decision and "expected_evidence_gain" not in decision
    assert decision["evidence_deficiency"] == 1
    assert decision["cas"] == pytest.approx(1 / .11)
    _assert_observed_costs(result, events)


@pytest.mark.parametrize("candidate", ["hybrid", "multihop"])
def test_real_cas_composite_recovery_counts_child_work_and_reassesses(monkeypatch, candidate):
    config, backends, assessor, events = _tracked_components(
        monkeypatch, [Document("seed", "Golden River author Ada writer.")])
    # Restrict only this synthetic test's initial selector, leaving a dependency
    # feature snapshot for CAS and both composite backends executable.
    settings = {**config["query_analysis"], "eligible_backends": ["local_lexical"]}
    controlled = RetrievalControlPipeline(backends, assessor,
        _policy(config, recovery_backends={"default": [candidate]}), top_k=5,
        query_analysis=settings).run(Query("q", "Where was the author of Golden River born?"), "local_lexical")
    assert controlled.initial_routing.selected_strategy == "local_lexical"
    assert controlled.initial_routing.features["dependent"] is True
    assert controlled.recovery_retrieval.retriever_name == candidate
    assert controlled.recovery_assessment is not None
    assert controlled.recovery_decision.metadata["suitability"] == 1
    assert controlled.recovery_decision.metadata["estimated_work"]["retrieval_calls"] == 2
    assert sum(event[0] == "assess" for event in events) == 2
    assert controlled.total_retrieval_calls == 3
    _assert_observed_costs(controlled, events)


@pytest.mark.parametrize("overrides,reason", [
    ({"max_recovery_rounds": 0}, "Recovery-round limit"),
    ({"recovery_backends": {}}, "No configured recovery backend"),
])
def test_real_empty_pipeline_does_not_retry_disabled_or_unconfigured_recovery(
    monkeypatch, overrides, reason,
):
    config, backends, assessor, events = _tracked_components(monkeypatch, [])
    result = RetrievalControlPipeline(
        backends, assessor, _policy(config, **overrides), top_k=5,
        query_analysis=config["query_analysis"],
    ).run(Query("q", "solar electricity"), config["retrieval"]["backend"])
    assert [(event[0], event[1]) for event in events] == [
        ("retrieve", "local_lexical"), ("assess", "local_lexical"),
    ]
    assert result.recovery_retrieval is result.recovery_assessment is None
    assert result.final_state == "abstain"
    assert reason in result.recovery_decision.reason
    _assert_observed_costs(result, events)


@pytest.mark.parametrize("interactive", [False, True])
def test_cli_subprocess_uses_temporary_data_and_reports_control_and_evidence(
    demo_dataset_root, interactive,
):
    # Redirect only input files. This is the real CLI parser/menu/main, running
    # in a separate interpreter without pytest's path setup or any generator.
    script = (
        "from pathlib import Path; import sys; from ear_rag import demo; "
        "demo._PROJECT_ROOT=Path(sys.argv[1]); "
        "raise SystemExit(demo.main(sys.argv[2:]))"
    )
    args = [] if interactive else ["--mode", "ear-rag", "--query-text", "unmatched deterministic vocabulary"]
    completed = subprocess.run(
        [sys.executable, "-I", "-c", script, str(demo_dataset_root), *args],
        cwd=demo_dataset_root, input="1\n0\n2\n0\n3\n5\n" if interactive else None,
        capture_output=True, text=True, timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert "EAR-RAG CONTROLLER" in completed.stdout
    assert "COST SUMMARY" in completed.stdout and "Final decision" in completed.stdout
    assert "evaluation-only-marker" not in completed.stdout + completed.stderr
    if interactive:
        assert "RETRIEVED EVIDENCE" in completed.stdout
        assert "Title       : Solar energy" in completed.stdout
        for label in ("BM25", "Vector Flat", "Hybrid", "Multi-hop"):
            assert label in completed.stdout
    else:
        assert "SECOND ESA" in completed.stdout and "ABSTAIN" in completed.stdout
        assert "Recovery round               : 1 / 1" in completed.stdout
