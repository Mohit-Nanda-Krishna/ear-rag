"""Isolated offline evaluation and supervision boundaries."""

from dataclasses import replace
import json

import pytest

from ear_rag.config.loader import load_config
from ear_rag.demo import build_backends
from ear_rag.evaluate_initial import evaluate_initial, load_smoke_examples, main


def _run(examples=None, count=5):
    examples = load_smoke_examples() if examples is None else examples
    config = load_config()
    backends = build_backends([doc for example in examples for doc in example.documents], config)
    return evaluate_initial(examples, backends, config, count=count)


def test_offline_smoke_isolates_initial_selection_and_reports_metrics():
    report = _run()
    assert report["synthetic"] and report["settings"]["recovery_enabled"] is False
    conditions = report["conditions"]
    assert set(conditions) == {"local_lexical", "vector_flat", "hybrid", "multihop", "query_aware"}
    for condition in conditions.values():
        assert condition["questions"] == condition["labeled_questions"] == 5
        assert 0 <= condition["support_document_recall_at_k"] <= 1
        assert condition["recovery_calls"] == 0
        assert condition["initial_strategy_selections"] == 5
        assert condition["mean_retrieved_passages"] >= condition["mean_final_context_chunks"]
        assert condition["mean_final_context_tokens"] > 0 and condition["mean_final_context_characters"] > 0
    assert conditions["local_lexical"]["underlying_retrieval_calls"] == 5
    assert conditions["vector_flat"]["underlying_retrieval_calls"] == 5
    assert conditions["hybrid"]["underlying_retrieval_calls"] == 10
    assert conditions["multihop"]["underlying_retrieval_calls"] == 10
    assert conditions["query_aware"]["initial_strategy_distribution"] == {"local_lexical": 2, "vector_flat": 1, "hybrid": 1, "multihop": 1}
    assert conditions["query_aware"]["fallback_rate"] == .2
    assert conditions["query_aware"]["mean_router_ms"] > 0
    assert conditions["hybrid"]["mean_router_ms"] == 0


def test_changing_only_gold_labels_does_not_change_routing_or_calls():
    examples = load_smoke_examples()
    before = _run(examples)
    after = _run([replace(example, supporting_document_ids=frozenset({"wrong-gold-label"})) for example in examples])
    for name, original in before["conditions"].items():
        modified = after["conditions"][name]
        for key in ("initial_strategy_distribution", "fallback_rate", "underlying_retrieval_calls", "mean_final_context_characters"):
            assert original[key] == modified[key]
        assert modified["support_document_recall_at_k"] == 0


def test_unlabeled_queries_are_reported_without_fabricated_quality():
    examples = [replace(example, supporting_document_ids=frozenset()) for example in load_smoke_examples()]
    report = _run(examples)
    assert all(item["support_document_recall_at_k"] is None and item["labeled_questions"] == 0 for item in report["conditions"].values())


def test_small_command_prints_json_and_uses_deterministic_prefix(capsys):
    assert main(["--smoke", "--examples", "2"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["synthetic"] and report["conditions"]["query_aware"]["questions"] == 2


@pytest.mark.parametrize("count", [0, -1, True])
def test_invalid_evaluation_count(count):
    with pytest.raises(ValueError, match="positive integer"):
        _run(count=count)


def test_empty_dataset_has_clear_error():
    with pytest.raises(ValueError, match="at least one query"):
        _run([])
