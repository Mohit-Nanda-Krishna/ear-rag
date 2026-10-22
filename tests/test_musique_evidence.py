"""Native paragraph identity and offline adapter into the existing evaluator."""
from copy import deepcopy
from dataclasses import asdict
import json

import pytest

from ear_rag import condition_evaluation as runner
from ear_rag.config.loader import get_config_path, load_config
from ear_rag.control_evaluation import EvaluationCase, write_evaluation_report
from ear_rag.core.models import RetrievalResult
from ear_rag.data.musique import read_musique
from ear_rag.data.musique_evidence import build_question_corpus, paragraph_quality
from ear_rag.retrieval.chunking import DocumentChunker
from test_musique_ingestion import record, write


def test_repeated_title_distractor_is_not_support_and_chunks_deduplicate(tmp_path):
    r = record()
    r["paragraphs"][0]["paragraph_text"] *= 30
    data = read_musique(write(tmp_path, [r]))
    corpus = build_question_corpus(data, "q1")
    chunks = DocumentChunker(40, 5).chunk_documents(corpus.documents)
    gold = [c for c in chunks if c.document_id == corpus.documents[0].document_id]
    distractor = [c for c in chunks if c.document_id == corpus.documents[1].document_id]
    assert all(c.metadata["document_metadata"]["paragraph_idx"] == 0 for c in gold)
    result = RetrievalResult("q1", distractor, "local_lexical", 5)
    assert paragraph_quality(data, corpus, result)["hit_at_5"] is False
    result.chunks = gold[:4] + distractor
    metrics = paragraph_quality(data, corpus, result)
    assert metrics["supporting_document_recall_at_5"] == 1
    assert metrics["matched_supporting_document_count"] == 1
    assert metrics["supporting_evidence_coverage_at_5"] is None
    assert metrics["metric_units"]["supporting_document_recall_at_5"] == "native_paragraph"
    result.chunks[0].document_id = "forged"
    with pytest.raises(ValueError, match="unknown source"):
        paragraph_quality(data, corpus, result)


def test_hand_calculated_first_five_chunk_cutoff_and_native_indices(tmp_path):
    r = record()
    r["paragraphs"] += [{"idx": 2, "title": "Same", "paragraph_text": "Other gold.", "is_supporting": True}]
    r["question_decomposition"] += [{"id": 11, "question": "Other?", "answer": "Secret", "paragraph_support_idx": 2}]
    # Array order differs from idx: mapping must use the native identifier.
    r["paragraphs"] = list(reversed(r["paragraphs"]))
    data = read_musique(write(tmp_path, [r]))
    corpus = build_question_corpus(data, "q1")
    chunks = DocumentChunker().chunk_documents(corpus.documents)
    by_idx = {c.metadata["document_metadata"]["paragraph_idx"]: c for c in chunks}
    result = RetrievalResult("q1", [by_idx[0]] * 5 + [by_idx[2]], "vector_flat", 5)
    metrics = paragraph_quality(data, corpus, result)
    assert metrics["hit_at_5"] is True
    assert metrics["supporting_document_recall_at_5"] == .5
    assert [d.text for d in corpus.documents] == [p["paragraph_text"] for p in r["paragraphs"]]


def without_timing(value):
    if isinstance(value, dict):
        return {k: without_timing(v) for k, v in value.items() if "latency" not in k and "elapsed" not in k}
    if isinstance(value, list): return [without_timing(v) for v in value]
    return value


def test_six_conditions_native_pools_isolation_gold_mutation_and_serialization(tmp_path, monkeypatch):
    records = [record("q1"), record("q2")]
    for r in records:
        r["paragraphs"] += [{"idx": i, "title": "Same", "paragraph_text": "Unrelated background.", "is_supporting": False}
                            for i in range(2, 7)]
    data = read_musique(write(tmp_path, records))
    config = load_config(get_config_path())
    builds = []
    original = runner._pipeline

    def pipeline(documents, settings):
        p = original(documents, settings)
        builds.append((deepcopy(documents), p))
        return p

    monkeypatch.setattr(runner, "_pipeline", pipeline)
    cases = [EvaluationCase("q1"), EvaluationCase("q2"), EvaluationCase("missing"), EvaluationCase("excluded", "synthetic exclusion")]
    first = runner.evaluate_conditions(data, cases, config)
    assert len({id(p) for _, p in builds}) == 12
    for i, (documents, _) in enumerate(builds):
        assert documents == builds[i % 2][0]
        assert all(d.metadata.keys() == {"title", "dataset", "paragraph_idx", "source_example_id"} for d in documents)
    for r in records:
        r.update(answer="DIFFERENT_SECRET", answer_aliases=["PRIVATE"], enriched_gold="HIDDEN")
        for p in r["paragraphs"]: p["is_supporting"] = p["idx"] == 6
        r["question_decomposition"] = [{"id": 99, "question": "HIDDEN DECOMPOSITION", "answer": "PRIVATE", "paragraph_support_idx": 6}]
    changed = read_musique(write(tmp_path, records))
    second = runner.evaluate_conditions(changed, cases, config)
    for name in runner.CONDITIONS:
        a, b = first[name], second[name]
        assert a["aggregate"]["counts"] == {"requested": 4, "evaluated": 2, "failed": 1, "excluded": 1}
        for x, y in zip(a["per_case"][:2], b["per_case"][:2]):
            assert x["status"] == y["status"] == "evaluated", x["error"]
            assert without_timing(x["control"]) == without_timing(y["control"])
            assert x["initial_backend"] == y["initial_backend"]
            for stage in ("initial", "terminal"):
                assert x[stage]["requested_top_k"] == 5
                assert x[stage]["chunks"] == y[stage]["chunks"]
            assert x["control"]["recovery_count"] <= int(name == "adaptive_controller")
            if name.startswith("fixed_"):
                assert x["control"]["initial_routing"] is None
                assert name == f"fixed_{x['initial_backend']}_no_recovery"
        assert a["aggregate"]["terminal"]["supporting_evidence_coverage_at_5"]["missing"] == 2
        write_evaluation_report(a, tmp_path / name)
        assert json.loads((tmp_path / name / "aggregate.json").read_text()) == a["aggregate"]
    assert builds[:12][0][0] == builds[12:][0][0]
    assert first[runner.CONDITIONS[0]]["per_case"][0]["terminal"]["metrics"] != second[runner.CONDITIONS[0]]["per_case"][0]["terminal"]["metrics"]


def test_deterministic_native_output_and_duplicate_request_failure(tmp_path):
    data = read_musique(write(tmp_path, [record()]))
    config = load_config(get_config_path())
    a = runner.evaluate_conditions(data, [EvaluationCase("q1")], config)
    b = runner.evaluate_conditions(data, [EvaluationCase("q1")], config)
    assert without_timing(a) == without_timing(b)
    duplicate = runner.evaluate_conditions(data, [EvaluationCase("q1"), EvaluationCase("q1")], config)
    assert all(r["aggregate"]["counts"]["failed"] == 2 for r in duplicate.values())


@pytest.mark.parametrize("final", ["sufficient", "insufficient"])
def test_native_adaptive_reassesses_once_and_no_recovery_conditions_cannot(tmp_path, monkeypatch, final):
    from test_condition_evaluation import spy_runtime
    data = read_musique(write(tmp_path, [record()]))
    builds, calls, assessments = spy_runtime(monkeypatch, final=final)
    reports = runner.evaluate_conditions(data, [EvaluationCase("q1")], load_config(get_config_path()))
    for i, (name, report) in enumerate(reports.items()):
        row = report["per_case"][0]
        assert row["status"] == "evaluated", row["error"]
        adaptive = name == "adaptive_controller"
        assert assessments[i].calls == 1 + int(adaptive)
        assert row["control"]["recovery_count"] == int(adaptive)
        assert (row["control"]["recovery_assessment"] is not None) == adaptive
        assert row["control"]["final_state"] == ("generate" if adaptive and final == "sufficient" else "abstain")
        assert all(call[3] == 5 for call in calls)
