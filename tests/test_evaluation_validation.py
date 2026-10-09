"""Hand-calculated metrics, offline diagnostic comparisons, and artifact isolation."""

from dataclasses import replace
import csv
import json

import pytest

from ear_rag.config.loader import load_config
from ear_rag.core.models import Document, Query, RetrievedChunk, RetrievalResult
from ear_rag.demo import DemoExample, build_backends
from ear_rag.evaluate_initial import evaluate_initial, load_smoke_examples, main
from ear_rag.evaluation_artifacts import resolve_labels, save_reports
from ear_rag.evaluation_metrics import LabelResolution, analyze_decision, mean_interval, retrieval_metrics
from ear_rag.routing import LightweightQueryAnalyzer
from ear_rag.routing.initial import STRATEGIES


def result(ids, calls=1, latency=3):
    return RetrievalResult("q", [RetrievedChunk(str(i), doc, "some evidence", 1, "fake") for i, doc in enumerate(ids)],
                           "fake", 5, {"retrieval_calls": calls, "retrieval_latency_ms": latency,
                                       "retrieval_call_count": 999, "retrieved_passages": len(ids)})


def metrics(ids, calls=1):
    return retrieval_metrics(result(ids, calls), LabelResolution(frozenset({"a", "b"}), 2), 5)


def test_recall_hit_and_full_support_coverage_are_distinct_and_deduplicated():
    m = metrics(["a", "a", "c"])
    assert m["resolved_support_recall_at_k"] == .5
    assert m["hit_at_k"] is True and m["full_support_covered"] is False
    assert m["matched_support_count"] == 1 and m["underlying_retrieval_calls"] == 1
    assert metrics(["a", "b"])["full_support_covered"] is True
    assert metrics(["c"])["hit_at_k"] is False


def test_cutoff_and_total_initial_latency():
    m = retrieval_metrics(result(["a", "c", "b"]), LabelResolution(frozenset({"a", "b"}), 2), 2, routing_ms=.2)
    assert m["resolved_support_recall_at_k"] == .5 and m["final_context_chunks"] == 2
    assert m["initial_stage_latency_ms"] == 3.2


def test_partial_labels_do_not_create_full_recall_or_penalize_missing_support():
    m = retrieval_metrics(result(["a"]), LabelResolution(frozenset({"a"}), 2, ("unavailable title",)), 5)
    assert m["resolved_support_recall_at_k"] == 1 and m["all_resolved_support_covered"] is True
    assert m["full_support_recall_at_k"] is None and m["full_support_covered"] is None


def test_unresolved_labels_produce_null_metrics_and_no_regret():
    m = retrieval_metrics(result(["a"]), LabelResolution(frozenset(), 2), 5)
    assert m["hit_at_k"] is None and m["resolved_support_recall_at_k"] is None and m["utility"] is None
    analysis = analyze_decision("local_lexical", {"local_lexical": m}, m, policy_fallback=True)
    assert analysis["routing_regret"] is None and analysis["outcome"] == "insufficient_labels"


def test_missing_total_annotations_preclude_full_recall():
    labels = LabelResolution(frozenset({"a"}), None)
    assert labels.record()["status"] == "unknown_annotations"
    assert retrieval_metrics(result(["a"]), labels, 5)["full_support_recall_at_k"] is None


def test_efficiency_objective_preserves_ties_and_quality_regret():
    observed = {"local_lexical": metrics(["a"], 1), "hybrid": metrics(["a", "b"], 2)}
    decision = analyze_decision("local_lexical", observed, observed["local_lexical"], policy_fallback=False)
    assert set(decision["best_observed_strategies"]) == {"local_lexical", "hybrid"}
    assert decision["selection_agreement"] and decision["routing_regret"] == 0
    assert decision["quality_regret"] == .5 and decision["tied_best_utility"]


def test_avoidable_calls_require_equal_quality_not_only_faster_timing():
    observed = {"local_lexical": metrics(["a", "b"], 1), "multihop": metrics(["a", "b"], 2)}
    decision = analyze_decision("multihop", observed, observed["multihop"], policy_fallback=False)
    assert decision["unnecessary_cost"] and decision["avoidable_calls"] == 1
    assert decision["routing_regret"] == .5 and decision["outcome"] == "unnecessary_retrieval_cost"
    observed["multihop"] = {**observed["local_lexical"], "retrieval_latency_ms": 999}
    decision = analyze_decision("multihop", observed, observed["multihop"], policy_fallback=False)
    assert not decision["unnecessary_cost"] and decision["routing_regret"] == 0


def test_missed_evidence_is_observed_router_opportunity_with_separate_backend_caveat():
    observed = {"local_lexical": metrics(["a", "b"]), "vector_flat": metrics([])}
    decision = analyze_decision("vector_flat", observed, observed["vector_flat"], policy_fallback=False)
    assert decision["routing_regret"] == 1 and not decision["selection_agreement"]
    assert decision["missed_retrieval_opportunity"] and decision["router_quality_opportunity"]
    assert decision["backend_limitation_possible"] and "cannot isolate" in decision["reason"]


def test_shared_failure_is_not_automatically_a_router_failure():
    observed = {name: metrics([], 1) for name in STRATEGIES}
    decision = analyze_decision("vector_flat", observed, observed["vector_flat"], policy_fallback=False)
    assert decision["outcome"] == "shared_retrieval_failure"
    assert not decision["router_quality_opportunity"] and not decision["missed_retrieval_opportunity"]
    assert decision["selection_agreement"] and decision["routing_regret"] == 0


def test_equal_successful_strategies_are_explicitly_ambiguous():
    observed = {name: metrics(["a", "b"]) for name in ("local_lexical", "vector_flat")}
    decision = analyze_decision("vector_flat", observed, observed["vector_flat"], policy_fallback=False)
    assert decision["outcome"] == "ambiguous_outcome" and decision["tied_best_quality"]
    assert len(decision["best_observed_strategies"]) == 2


def test_bootstrap_reproducibility_empty_values_and_paired_difference():
    values = [-1, 0, -.5, 0, .5]
    first = mean_interval(values, seed=42, samples=200)
    assert first == mean_interval(values, seed=42, samples=200)
    assert first["mean"] == -.2 and first["ci95"][0] <= -.2 <= first["ci95"][1]
    assert mean_interval([], seed=42)["mean"] is None
    assert mean_interval([1, 1], seed=42)["ci95"] == [1, 1]


@pytest.mark.parametrize("calls", [0, -1])
def test_invalid_measured_calls_are_not_fabricated(calls):
    with pytest.raises(ValueError):
        metrics(["a"], calls)


def test_resolve_annotation_coverage_and_ignore_answers(tmp_path):
    examples = [DemoExample("q", "Explain energy", (Document("a", "text", {"title": "A"}),), frozenset({"a"})),
                DemoExample("missing", "question", (), frozenset())]
    path = tmp_path / "labels.jsonl"
    record = {"example_id": "q", "answers": ["TOP SECRET"],
              "evaluation": {"supporting_facts": [["A", 0], ["A", 1], ["B", 0]]}}
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    labels = resolve_labels(examples, path, "hotpotqa")
    assert labels["q"].record()["resolution_coverage"] == .5
    assert labels["q"].annotated_support_count == 2 and labels["q"].unresolved_titles == ("B",)
    assert labels["missing"].record()["status"] == "unknown_annotations"
    assert "SECRET" not in repr(labels)
    record["answers"] = ["different answer"]
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    assert labels == resolve_labels(examples, path, "hotpotqa")


def test_duplicate_annotated_query_ids_raise(tmp_path):
    path = tmp_path / "labels.jsonl"
    row = json.dumps({"example_id": "q", "evaluation": {"supporting_facts": []}})
    path.write_text(row + "\n" + row, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        resolve_labels([], path, "hotpotqa")


class TableRetriever:
    def __init__(self, name, ids, calls):
        self.name, self.ids, self.calls, self.seen = name, ids, calls, []

    def retrieve(self, query, top_k, **kwargs):
        assert query.metadata == {} and kwargs["retrieval_action"] == "initial"
        self.seen.append(query.query_id)
        r = result(self.ids, self.calls)
        r.query_id, r.retriever_name, r.top_k = query.query_id, self.name, top_k
        return r


def small_report(*, unresolved=False, monkeypatch=None):
    examples = [DemoExample("q", "Explain energy", (Document("a", "energy"), Document("b", "power")), frozenset({"a", "b"}))]
    backends = {name: TableRetriever(name, [] if name == "vector_flat" else ["a", "b"], 2 if name in {"hybrid", "multihop"} else 1) for name in STRATEGIES}
    if monkeypatch:
        original = LightweightQueryAnalyzer.analyze
        def guarded(self, query):
            assert query.query_id == "" and query.metadata == {}
            return original(self, query)
        monkeypatch.setattr(LightweightQueryAnalyzer, "analyze", guarded)
    labels = {"q": LabelResolution(frozenset() if unresolved else frozenset({"a", "b"}), 2)}
    report = evaluate_initial(examples, backends, load_config(), label_resolutions=labels, bootstrap_samples=50)
    return report, backends


def test_mocked_offline_analysis_metrics_calls_and_recovery_isolation(monkeypatch):
    report, backends = small_report(monkeypatch=monkeypatch)
    row = report["per_query"][0]
    assert row["routing"]["selected_strategy"] == "vector_flat"
    assert row["decision_analysis"]["routing_regret"] == 1
    assert row["decision_analysis"]["best_observed_strategies"] == ["local_lexical"]
    assert row["execution_order"][0] == "query_aware"
    assert len(backends["vector_flat"].seen) == 2
    assert all(len(backend.seen) == 1 for name, backend in backends.items() if name != "vector_flat")
    assert all(item["recovery_calls"] == 0 for item in report["conditions"].values())
    assert report["paired_comparisons_query_aware_minus_fixed"]["local_lexical"]["resolved_support_recall_at_k_delta"]["mean"] == -1
    assert report["conditions"]["hybrid"]["underlying_retrieval_calls"] == 2


def test_unresolved_queries_excluded_from_denominators_but_included_in_routing():
    report, _ = small_report(unresolved=True)
    assert report["evaluated_queries"] == 1 and report["decision_quality"]["labeled_queries"] == 0
    assert report["decision_quality"]["selection_agreement"] is None
    assert report["fallback_diagnostics"]["queries"] == 1
    assert all(item["hit_at_k"] is None and item["labeled_questions"] == 0 for item in report["conditions"].values())


def test_corpus_and_runtime_decisions_do_not_change_with_gold_labels():
    before, _ = small_report()
    after, _ = small_report(unresolved=True)
    assert before["provenance"]["corpus_sha256"] == after["provenance"]["corpus_sha256"]
    assert before["provenance"]["evidence_labels_sha256"] != after["provenance"]["evidence_labels_sha256"]
    a, b = before["per_query"][0]["routing"], after["per_query"][0]["routing"]
    a.pop("routing_latency_ms"); b.pop("routing_latency_ms")
    assert a == b


def test_json_csv_outputs_roundtrip_query_level_records(tmp_path):
    report, _ = small_report()
    save_reports(report, tmp_path)
    aggregate = json.loads((tmp_path / "aggregate.json").read_text(encoding="utf-8"))
    assert "per_query" not in aggregate and aggregate["evaluated_queries"] == 1
    row = json.loads((tmp_path / "per_query.jsonl").read_text(encoding="utf-8"))
    assert row["query_id"] == "q" and row["decision_analysis"]["routing_regret"] == 1
    with (tmp_path / "per_query.csv").open(encoding="utf-8", newline="") as f:
        csv_row = next(csv.DictReader(f))
    assert json.loads(csv_row["scores"])["vector_flat"] == 3
    with (tmp_path / "retrievals.csv").open(encoding="utf-8", newline="") as f:
        assert len(list(csv.DictReader(f))) == 5


def test_seeded_sampling_and_provenance_reproducible():
    examples = load_smoke_examples()
    config = load_config()
    backends = build_backends([doc for ex in examples for doc in ex.documents], config)
    first = evaluate_initial(examples, backends, config, count=3, sampling="seeded", seed=17, bootstrap_samples=20)
    second = evaluate_initial(examples, backends, config, count=3, sampling="seeded", seed=17, bootstrap_samples=20)
    assert first["provenance"] == second["provenance"]
    assert [row["execution_order"] for row in first["per_query"]] == [row["execution_order"] for row in second["per_query"]]
    assert first["decision_quality"] == second["decision_quality"]


def test_command_writes_smoke_artifacts(tmp_path, capsys):
    assert main(["--smoke", "--examples", "5", "--bootstrap-samples", "20", "--output-dir", str(tmp_path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["evaluated_queries"] == 5 and report["provenance"]["input_files_sha256"]
    assert report["fallback_diagnostics"]["primary_reason_counts"] == {"no_routing_signals": 1}
    assert (tmp_path / "per_query.csv").is_file()


def test_invalid_sampling_missing_labels_and_duplicate_query_ids():
    examples = load_smoke_examples()
    backends = build_backends([doc for ex in examples for doc in ex.documents])
    config = load_config()
    for kwargs in ({"sampling": "random_unseeded"}, {"bootstrap_samples": 0}, {"label_resolutions": {}}):
        with pytest.raises(ValueError):
            evaluate_initial(examples, backends, config, **kwargs)
    with pytest.raises(ValueError, match="unique"):
        evaluate_initial([examples[0], replace(examples[1], example_id=examples[0].example_id)], backends, config)
