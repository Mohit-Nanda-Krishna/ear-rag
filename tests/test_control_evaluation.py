"""Synthetic offline evaluation infrastructure, never a dataset benchmark."""

import json
from dataclasses import replace

import pytest

from ear_rag.control_evaluation import supporting_evidence_coverage
from ear_rag.core.models import RetrievalResult
from ear_rag.data.hotpotqa_evidence import SupportingEvidenceMatch
from ear_rag.evaluation_metrics import LabelResolution, supporting_document_metrics


def make_dataset(tmp_path, identifiers=("q1",)):
    from ear_rag.data.hotpotqa import read_hotpotqa

    records = [{"_id": q, "question": "Alpha Beta target?", "answer": "ANSWER_SECRET",
                "context": [["Alpha", ["Alpha first.", "Alpha target."]], ["Beta", ["Beta target."]]],
                "supporting_facts": [["Alpha", 0], ["Alpha", 1], ["Beta", 0]],
                "type": "bridge", "level": "hard", "extra": "ANNOTATION_SECRET"} for q in identifiers]
    path = tmp_path / "source.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    return read_hotpotqa(path, source_split="dev"), path


def factory(*, recover=False, final_sufficient=True, missing=False, observed=None, bad_latency=None):
    """Real controller with deterministic synthetic backend/ESA/policy inputs."""
    from ear_rag.core.models import EvidenceAssessment, RecoveryAction
    from ear_rag.retrieval import DocumentChunker
    from ear_rag.routing import RetrievalControlPipeline

    def build(documents):
        if observed is not None:
            observed.append(("documents", documents))

        class Backend:
            def __init__(self, position):
                self.position = position

            def retrieve(self, query, top_k, **kwargs):
                if observed is not None:
                    observed.append(("query", query))
                chunks = DocumentChunker().chunk_document(documents[self.position])
                metadata = {} if missing else {"retrieval_calls": 1, "retrieved_passages": len(chunks),
                                               "retrieval_latency_ms": 3.0}
                if bad_latency is not None:
                    metadata["retrieval_latency_ms"] = bad_latency
                return RetrievalResult(query.query_id, chunks, "synthetic", top_k, metadata)

        class Assessor:
            def __init__(self):
                self.calls = 0

            def assess(self, query, retrieval):
                self.calls += 1
                sufficient = final_sufficient and (not recover or self.calls == 2)
                return EvidenceAssessment(overall_score=.9 if sufficient else .1,
                                          decision="sufficient" if sufficient else "insufficient")

        class Policy:
            def decide(self, query, assessment, result, **kwargs):
                return RecoveryAction("alternative_retriever" if recover else "no_action",
                                      {"backend": "recovery"} if recover else {},
                                      metadata={"recover": recover})

        return RetrievalControlPipeline({"primary": Backend(0), "recovery": Backend(1)},
                                        Assessor(), Policy())
    return build


def evaluate(dataset, cases, build=None):
    from ear_rag.control_evaluation import evaluate_cases
    return evaluate_cases(dataset, cases, build or factory(), initial_backend="primary")


def test_empty_labels_and_empty_evidence_have_null_quality():
    metrics = supporting_document_metrics(RetrievalResult("q"), LabelResolution(frozenset(), 0), 5)
    assert metrics["hit_at_k"] is None and metrics["full_support_recall_at_k"] is None
    empty = SupportingEvidenceMatch(frozenset(), frozenset(), frozenset(), frozenset())
    assert supporting_evidence_coverage(empty) is None


def test_coverage_denominator_is_unique_annotated_sentences():
    match = SupportingEvidenceMatch(
        frozenset({("A", 0), ("A", 1)}), frozenset({("A", 1)}),
        frozenset({("B", 0), ("B", 1)}), frozenset({"A"}),
    )
    assert supporting_evidence_coverage(match) == pytest.approx(1 / 3)


def test_nonempty_labels_with_empty_retrieval_are_zero_not_missing():
    metrics = supporting_document_metrics(
        RetrievalResult("q"), LabelResolution(frozenset({"a", "b"}), 2), 5)
    assert metrics["hit_at_k"] is False and metrics["full_support_recall_at_k"] == 0


def test_initial_and_terminal_metrics_follow_controller_recovery_evidence(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, path = make_dataset(tmp_path)
    before = path.read_bytes()
    report = evaluate(dataset, [EvaluationCase("q1")], factory(recover=True))
    row, = report["per_case"]
    assert row["status"] == "evaluated"
    assert row["initial"]["metrics"]["hit_at_5"] is True
    assert row["initial"]["metrics"]["supporting_document_recall_at_5"] == .5
    assert row["initial"]["metrics"]["supporting_evidence_coverage_at_5"] == pytest.approx(2 / 3)
    assert row["terminal"]["metrics"]["supporting_document_recall_at_5"] == .5
    assert row["terminal"]["metrics"]["supporting_evidence_coverage_at_5"] == pytest.approx(1 / 3)
    assert row["terminal"]["chunks"][0]["location"]["title"] == "Beta"
    assert row["control"]["recovery_count"] == 1 and not row["control"]["abstained"]
    assert row["work"]["retrieval_calls"] == 2
    assert row["work"]["returned_chunks"] == 2
    assert row["work"]["retrieved_passages"] == 2
    assert row["work"]["retrieval_latency_ms"] == 6
    assert path.read_bytes() == before


def test_failures_exclusions_and_backend_rates_reconcile(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path, ("q1", "q2"))
    cases = [EvaluationCase("q1"), EvaluationCase("missing"), EvaluationCase("q2", "explicit test exclusion")]
    report = evaluate(dataset, cases, factory(recover=True, final_sufficient=False))
    aggregate = report["aggregate"]
    assert aggregate["counts"] == {"requested": 3, "evaluated": 1, "failed": 1, "excluded": 1}
    assert aggregate["recovery_trigger_rate"] == {"numerator": 1, "denominator": 1, "rate": 1}
    assert aggregate["recovery_count"] == 1
    assert aggregate["final_abstention_rate"]["rate"] == 1
    assert aggregate["failure_rate"]["rate"] == pytest.approx(1 / 3)
    assert aggregate["initial_backend_selection"] == {"primary": {"count": 1, "frequency": 1}}
    assert aggregate["work"]["retrieval_calls"] == {"observed": 1, "missing": 1, "total": 2, "mean": 2}
    assert report["per_case"][1]["error"]["stage"] == "corpus"
    assert report["per_case"][2]["exclusion_reason"] == "explicit test exclusion"
    assert aggregate["partial"] is True


def test_factory_failure_is_not_abstention(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)

    def broken(_documents):
        raise RuntimeError("synthetic construction failure")

    report = evaluate(dataset, [EvaluationCase("q1")], broken)
    assert report["per_case"][0]["error"] == {
        "stage": "pipeline_factory", "type": "RuntimeError", "message": "synthetic construction failure"}
    assert report["aggregate"]["counts"]["failed"] == 1
    assert report["aggregate"]["final_abstention_rate"]["rate"] is None


def test_missing_cost_and_latency_are_null_despite_controller_defaults(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)
    report = evaluate(dataset, [EvaluationCase("q1")], factory(missing=True))
    row = report["per_case"][0]
    assert row["status"] == "evaluated"
    for key in ["retrieval_calls", "retrieval_latency_ms", "retrieved_passages", "processed_chunks"]:
        assert row["work"][key] is None
        assert report["aggregate"]["work"][key] == {"observed": 0, "missing": 1, "total": None, "mean": None}
    assert row["work"]["returned_chunks"] == 1
    assert row["work"]["controller_latency_ms"] is None
    assert row["work"]["monetary_cost"] is None


def test_zero_cases_and_all_excluded_have_null_rates(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)
    for cases in [[], [EvaluationCase("q1", "explicit reason")]]:
        report = evaluate(dataset, cases)
        assert report["aggregate"]["recovery_trigger_rate"]["rate"] is None
        assert report["aggregate"]["initial"]["hit_at_5"]["mean"] is None
        assert report["aggregate"]["work"]["retrieval_calls"]["observed"] == 0


def test_repeatability_serialization_and_new_directory_only(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase, write_evaluation_report
    dataset, _ = make_dataset(tmp_path)
    cases = [EvaluationCase("q1")]
    first, second = evaluate(dataset, cases), evaluate(dataset, cases)
    assert first == second
    a, b = tmp_path / "report-a", tmp_path / "report-b"
    write_evaluation_report(first, a)
    write_evaluation_report(second, b)
    for name in ["per_case.jsonl", "aggregate.json"]:
        assert (a / name).read_bytes() == (b / name).read_bytes()
    assert json.loads((a / "aggregate.json").read_text()) == first["aggregate"]
    assert [json.loads(line) for line in (a / "per_case.jsonl").read_text().splitlines()] == first["per_case"]
    with pytest.raises(FileExistsError):
        write_evaluation_report(first, a)


def test_runtime_factory_and_queries_receive_no_labels_and_label_changes_do_not_change_trace(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)
    observed = []
    first = evaluate(dataset, [EvaluationCase("q1")], factory(observed=observed))
    altered = replace(dataset, examples=(replace(dataset.examples[0], answers=("OTHER_ANSWER",),
                       evaluation={"supporting_facts": [["Beta", 0]]}, metadata={"secret": "different"}),))
    second = evaluate(altered, [EvaluationCase("q1")], factory(observed=observed))
    a, b = first["per_case"][0], second["per_case"][0]
    assert a["control"] == b["control"] and a["work"] == b["work"]
    assert a["initial"]["chunks"] == b["initial"]["chunks"]
    assert a["initial"]["metrics"] != b["initial"]["metrics"]
    for kind, value in observed:
        representation = repr(value)
        assert "ANSWER_SECRET" not in representation and "ANNOTATION_SECRET" not in representation
        assert "supporting_facts" not in representation and "OTHER_ANSWER" not in representation


def test_duplicate_requested_ids_are_failed_explicitly_without_dispatch(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)
    observed = []
    report = evaluate(dataset, [EvaluationCase("q1"), EvaluationCase("q1")], factory(observed=observed))
    assert not observed
    assert report["aggregate"]["counts"]["failed"] == 2
    assert all("duplicate" in r["error"]["message"] for r in report["per_case"])


@pytest.mark.parametrize("backend,calls", [("local_lexical", 1), ("vector_flat", 1), ("hybrid", 2), ("multihop", 2)])
def test_existing_real_pipeline_and_backend_factory_are_compatible(tmp_path, backend, calls):
    from ear_rag.control_evaluation import EvaluationCase
    from ear_rag.config import load_config
    from ear_rag.demo import build_backends
    from ear_rag.evidence import DeterministicEvidenceAssessor
    from ear_rag.routing import BoundedRecoveryPolicy, RetrievalControlPipeline
    dataset, _ = make_dataset(tmp_path)
    config = load_config()

    def build(documents):
        return RetrievalControlPipeline(build_backends(documents, config),
                                        DeterministicEvidenceAssessor(), BoundedRecoveryPolicy(max_recovery_rounds=0))

    from ear_rag.control_evaluation import evaluate_cases
    report = evaluate_cases(dataset, [EvaluationCase("q1")], build, initial_backend=backend)
    assert report["aggregate"]["counts"]["evaluated"] == 1
    assert report["per_case"][0]["work"]["retrieval_calls"] == calls
    assert report["per_case"][0]["work"]["retrieval_latency_ms"] >= 0


def test_failed_runtime_is_retained_with_unknown_work(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    from ear_rag.routing import RetrievalControlPipeline
    from ear_rag.evidence import DeterministicEvidenceAssessor
    from ear_rag.routing import BoundedRecoveryPolicy
    dataset, _ = make_dataset(tmp_path)
    report = evaluate(dataset, [EvaluationCase("q1")],
                      lambda docs: RetrievalControlPipeline({}, DeterministicEvidenceAssessor(), BoundedRecoveryPolicy()))
    row = report["per_case"][0]
    assert row["status"] == "failed" and row["error"]["stage"] == "runtime"
    assert row["work"] is None


def test_cutoff_is_first_five_chunks_while_work_counts_every_returned_chunk(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    from ear_rag.core.models import EvidenceAssessment, RecoveryAction
    from ear_rag.data.hotpotqa import read_hotpotqa
    from ear_rag.retrieval import DocumentChunker
    from ear_rag.routing import RetrievalControlPipeline
    dataset, path = make_dataset(tmp_path)
    raw = json.loads(path.read_text())
    raw[0]["context"] = [[f"Distractor {i}", ["Unrelated text."]] for i in range(5)] + raw[0]["context"]
    path.write_text(json.dumps(raw))
    dataset = read_hotpotqa(path, source_split="dev")

    def build(documents):
        class Backend:
            def retrieve(self, query, top_k, **kwargs):
                return RetrievalResult(query.query_id, DocumentChunker().chunk_documents(documents),
                                       "ordered", top_k, {"retrieval_calls": 1})
        class Assessor:
            def assess(self, query, result):
                return EvidenceAssessment(decision="sufficient")
        class Policy:
            def decide(self, *args, **kwargs):
                return RecoveryAction(metadata={"recover": False})
        return RetrievalControlPipeline({"primary": Backend()}, Assessor(), Policy(), top_k=7)

    row = evaluate(dataset, [EvaluationCase("q1")], build)["per_case"][0]
    assert row["status"] == "evaluated"
    assert row["initial"]["metrics"]["hit_at_5"] is False
    assert row["initial"]["metrics"]["supporting_document_recall_at_5"] == 0
    assert row["initial"]["metrics"]["supporting_evidence_coverage_at_5"] == 0
    assert row["work"]["returned_chunks"] == 7


def test_offline_failure_keeps_observed_runtime_work(tmp_path, monkeypatch):
    import ear_rag.control_evaluation as module
    dataset, _ = make_dataset(tmp_path)

    def fail(*args):
        raise ValueError("synthetic label join failure")
    monkeypatch.setattr(module, "_quality", fail)
    report = evaluate(dataset, [module.EvaluationCase("q1")])
    assert report["per_case"][0]["error"]["stage"] == "offline_metrics"
    assert report["aggregate"]["counts"]["failed"] == 1
    assert report["aggregate"]["work"]["retrieval_calls"]["total"] == 1
    assert report["aggregate"]["terminal"]["hit_at_5"]["observed"] == 0


@pytest.mark.parametrize("field", ["retrieval_calls", "retrieval_latency_ms"])
def test_missing_recovery_measurement_makes_total_unknown_but_preserves_stage(tmp_path, field):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)

    def build(documents):
        pipeline = factory(recover=True)(documents)
        original = pipeline.run
        def run(query, backend):
            result = original(query, backend)
            result.recovery_retrieval.metadata.pop(field)
            return result
        pipeline.run = run
        return pipeline

    row = evaluate(dataset, [EvaluationCase("q1")], build)["per_case"][0]
    assert row["status"] == "evaluated" and row["work"][field] is None
    assert row["initial"]["work"][field] is not None
    assert row["terminal"]["work"][field] is None


def test_cumulative_counter_is_not_mistaken_for_per_invocation_work(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)

    def build(documents):
        pipeline = factory(missing=True)(documents)
        original = pipeline.run
        def run(query, backend):
            result = original(query, backend)
            result.initial_retrieval.metadata["retrieval_call_count"] = 12
            return result
        pipeline.run = run
        return pipeline

    row = evaluate(dataset, [EvaluationCase("q1")], build)["per_case"][0]
    assert row["status"] == "evaluated" and row["work"]["retrieval_calls"] is None


def test_router_selected_backend_and_esa_decisions_are_recorded(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase, evaluate_cases
    from ear_rag.config import load_config
    from ear_rag.demo import build_backends
    from ear_rag.evidence import DeterministicEvidenceAssessor
    from ear_rag.routing import BoundedRecoveryPolicy, RetrievalControlPipeline
    dataset, _ = make_dataset(tmp_path)

    def build(documents):
        return RetrievalControlPipeline(build_backends(documents, load_config()),
            DeterministicEvidenceAssessor(), BoundedRecoveryPolicy(max_recovery_rounds=0),
            query_analysis={"enabled": True})

    report = evaluate_cases(dataset, [EvaluationCase("q1")], build, initial_backend="vector_flat")
    row = report["per_case"][0]
    assert row["status"] == "evaluated"
    selected = row["control"]["initial_routing"]["selected_strategy"]
    assert row["initial_backend"] == selected
    assert report["aggregate"]["initial_backend_selection"] == {selected: {"count": 1, "frequency": 1}}
    assert sum(report["aggregate"]["initial_esa_decisions"].values()) == 1
    assert sum(report["aggregate"]["terminal_esa_decisions"].values()) == 1


def test_serialized_schema_has_identical_top_level_keys_for_all_statuses(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase, SCHEMA_VERSION, write_evaluation_report
    dataset, _ = make_dataset(tmp_path)
    report = evaluate(dataset, [EvaluationCase("q1"), EvaluationCase("missing"), EvaluationCase("excluded", "reason")])
    rows = report["per_case"]
    assert all(set(row) == set(rows[0]) and row["schema_version"] == SCHEMA_VERSION for row in rows)
    assert sum(report["aggregate"]["counts"][k] for k in ["evaluated", "failed", "excluded"]) == 3
    report["aggregate"]["invalid_float"] = float("nan")
    target = tmp_path / "invalid-output"
    with pytest.raises(ValueError):
        write_evaluation_report(report, target)
    assert not target.exists()


def test_document_recall_deduplicates_titles_with_multiple_retrieved_chunks():
    from ear_rag.core.models import RetrievedChunk
    result = RetrievalResult("q", [RetrievedChunk(str(i), "a", "text", 1, "test") for i in range(5)] +
                             [RetrievedChunk("sixth", "b", "text", 1, "test")])
    metrics = supporting_document_metrics(result, LabelResolution(frozenset({"a", "b"}), 2), 5)
    assert metrics["matched_support_count"] == 1 and metrics["full_support_recall_at_k"] == .5


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True, 1.5])
def test_invalid_processed_chunk_measurements_fail_explicitly(tmp_path, value):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)

    def build(documents):
        pipeline = factory()(documents)
        original = pipeline.run
        def run(query, backend):
            result = original(query, backend)
            result.initial_retrieval.metadata["processed_chunks"] = value
            return result
        pipeline.run = run
        return pipeline

    row = evaluate(dataset, [EvaluationCase("q1")], build)["per_case"][0]
    assert row["status"] == "failed" and row["error"]["stage"] == "runtime_snapshot"
    assert "processed_chunks" in row["error"]["message"]


def test_known_zero_measurements_are_not_missing(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase
    dataset, _ = make_dataset(tmp_path)

    def build(documents):
        pipeline = factory()(documents)
        original = pipeline.run
        def run(query, backend):
            result = original(query, backend)
            result.initial_retrieval.metadata.update(retrieval_latency_ms=0, processed_chunks=0)
            return result
        pipeline.run = run
        return pipeline

    report = evaluate(dataset, [EvaluationCase("q1")], build)
    assert report["aggregate"]["work"]["retrieval_latency_ms"] == {
        "observed": 1, "missing": 0, "total": 0, "mean": 0}
    assert report["per_case"][0]["work"]["processed_chunks"] == 0


def test_unknown_serialization_version_is_rejected_before_writing(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase, write_evaluation_report
    dataset, _ = make_dataset(tmp_path)
    report = evaluate(dataset, [EvaluationCase("q1")])
    report["schema_version"] = "unsupported"
    target = tmp_path / "wrong-version"
    with pytest.raises(ValueError, match="schema"):
        write_evaluation_report(report, target)
    assert not target.exists()


def test_multiple_completed_cases_use_macro_quality_and_completed_rate_denominators(tmp_path):
    from ear_rag.control_evaluation import EvaluationCase, aggregate_cases
    dataset, _ = make_dataset(tmp_path, ("q1", "q2"))

    def mixed(documents):
        second = documents[0].metadata["source_example_id"] == "q2"
        return factory(recover=second, final_sufficient=not second)(documents)

    report = evaluate(dataset, [EvaluationCase("q1"), EvaluationCase("q2")], mixed)
    aggregate = report["aggregate"]
    assert aggregate["counts"] == {"requested": 2, "evaluated": 2, "failed": 0, "excluded": 0}
    assert aggregate["terminal"]["supporting_evidence_coverage_at_5"]["mean"] == .5
    assert aggregate["recovery_trigger_rate"] == {"numerator": 1, "denominator": 2, "rate": .5}
    assert aggregate["final_abstention_rate"]["rate"] == .5
    assert aggregate["work"]["retrieval_calls"] == {"observed": 2, "missing": 0, "total": 3, "mean": 1.5}
    assert aggregate["partial"] is False
    # Pure aggregation also handles different observed router selections.
    report["per_case"][1]["initial_backend"] = "other_observed_selection"
    assert aggregate_cases(report["per_case"])["initial_backend_selection"] == {
        "primary": {"count": 1, "frequency": .5},
        "other_observed_selection": {"count": 1, "frequency": .5}}
