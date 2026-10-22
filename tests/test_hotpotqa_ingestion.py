"""Synthetic official-shape ingestion tests; no research dataset is required."""

import hashlib
import json

import pytest

from ear_rag.data.hotpotqa import (
    HotpotQAValidationError, evaluation_projection, read_hotpotqa, runtime_projection,
)


def record(identifier="q1", question="Which place?"):
    return {
        "_id": identifier, "question": question, "answer": "LABEL_ONLY_ANSWER",
        "context": [["Alpha", ["First sentence.", "Second sentence."]],
                    ["Beta", ["Another candidate."]]],
        "supporting_facts": [["Alpha", 1]], "type": "bridge", "level": "hard",
        "extra_annotation": {"answer": ["NESTED_LABEL_ONLY"]},
    }


def write_input(tmp_path, records):
    path = tmp_path / "synthetic.json"
    path.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    return path


def test_inspection_separates_diagnostics_and_never_releases_partial_input(tmp_path):
    from ear_rag.data.hotpotqa import inspect_hotpotqa

    blank = record("blank")
    blank["context"][0][1][0] = " "
    invalid = record("index902")
    invalid["supporting_facts"] = [["Alpha", 902]]
    path = write_input(tmp_path, [record("valid"), blank, invalid])
    original = path.read_bytes()
    inspected = inspect_hotpotqa(path, source_split="dev")
    assert [e.example_id for e in inspected.examples] == ["valid"]
    assert inspected.report["counts"] == {
        "total": 3, "accepted": 1, "rejected": 2, "malformed": 2, "duplicate_ids": 0,
    }
    errors = inspected.report["record_errors"]
    assert [(e["position"], e["question_id"]) for e in errors] == [(1, "blank"), (2, "index902")]
    assert "sentence" in errors[0]["reason"] and "out of range" in errors[1]["reason"]
    with pytest.raises(HotpotQAValidationError) as caught:
        inspected.require_valid()
    assert caught.value.report == inspected.report
    assert "index902" in str(caught.value) and "blank" in str(caught.value)
    inspected.report["errors"].clear()
    with pytest.raises(HotpotQAValidationError):
        inspected.require_valid()
    assert path.read_bytes() == original


def test_valid_inspection_releases_the_same_dataset_as_strict_reader(tmp_path):
    from ear_rag.data.hotpotqa import inspect_hotpotqa

    path = write_input(tmp_path, [record()])
    inspected = inspect_hotpotqa(path, source_split="dev")
    assert inspected.report["record_errors"] == []
    assert inspected.require_valid() == read_hotpotqa(path, source_split="dev")


@pytest.mark.parametrize("bad", [{}, {"_id": None}, {"_id": []}, {"_id": ""}, None])
def test_inspection_missing_ids_and_nonobjects_have_record_positions(tmp_path, bad):
    from ear_rag.data.hotpotqa import inspect_hotpotqa

    inspected = inspect_hotpotqa(write_input(tmp_path, [bad]), source_split="dev")
    assert inspected.report["record_errors"][0]["position"] == 0
    assert inspected.report["counts"]["rejected"] == 1
    with pytest.raises(HotpotQAValidationError):
        inspected.require_valid()


def test_inspection_duplicate_id_is_explicit_and_blocks_release(tmp_path):
    from ear_rag.data.hotpotqa import inspect_hotpotqa

    inspected = inspect_hotpotqa(write_input(tmp_path, [record(), record()]), source_split="dev")
    assert inspected.report["record_errors"] == [
        {"position": 1, "question_id": "q1", "reason": "duplicate _id"},
    ]
    with pytest.raises(HotpotQAValidationError):
        inspected.require_valid()


def test_array_preserves_labels_contexts_provenance_and_read_only_source(tmp_path):
    path = write_input(tmp_path, [record()])
    before = path.read_bytes()
    dataset = read_hotpotqa(path, source_split="dev")
    example = dataset.examples[0]
    assert example.example_id == "q1" and example.question == "Which place?"
    assert example.answers == ("LABEL_ONLY_ANSWER",)
    assert example.evaluation["supporting_facts"] == [["Alpha", 1]]
    assert example.documents[0].doc_id == "hotpotqa:q1:0"
    assert example.documents[0].text == "First sentence. Second sentence."
    assert dataset.source["source_split"] == "dev"
    assert dataset.source["sha256"] == hashlib.sha256(before).hexdigest()
    assert dataset.counts == {"total": 1, "accepted": 1, "rejected": 0, "malformed": 0, "duplicate_ids": 0}
    assert path.read_bytes() == before


def test_projections_allowlist_nested_contexts_and_keep_labels_offline(tmp_path):
    dataset = read_hotpotqa(write_input(tmp_path, [record()]), source_split="dev")
    runtime = runtime_projection(dataset)
    labels = evaluation_projection(dataset)
    assert runtime[0]["documents"][0]["sentences"] == ["First sentence.", "Second sentence."]
    assert runtime[0]["documents"][0]["sentence_offsets"] == [{"start": 0, "end": 15}, {"start": 16, "end": 32}]
    assert runtime[0]["source_split"] == "dev"
    assert labels[0]["supporting_document_ids"] == ["hotpotqa:q1:0"]
    assert labels[0]["annotations"]["extra_annotation"] == {"answer": ["NESTED_LABEL_ONLY"]}
    serialized = json.dumps(runtime)
    for forbidden in ("LABEL_ONLY", "answer", "supporting_facts", "supporting_document_ids", '"type"', '"level"'):
        assert forbidden not in serialized
    labels[0]["annotations"]["extra_annotation"]["answer"].append("mutated")
    assert evaluation_projection(dataset)[0]["annotations"]["extra_annotation"]["answer"] == ["NESTED_LABEL_ONLY"]


def test_label_mutation_cannot_change_runtime_projection(tmp_path):
    source = record()
    path = write_input(tmp_path, [source])
    before = read_hotpotqa(path, source_split="dev")
    source.update(answer="DIFFERENT_LABEL", supporting_facts=[["Beta", 0]], type="comparison")
    after = read_hotpotqa(write_input(tmp_path, [source]), source_split="dev")
    assert before.source["sha256"] != after.source["sha256"]
    assert runtime_projection(before) == runtime_projection(after)
    assert evaluation_projection(before) != evaluation_projection(after)


def test_optional_annotations_and_naturally_occurring_answer_text(tmp_path):
    item = record()
    del item["type"], item["level"]
    item["answer"] = "First"
    dataset = read_hotpotqa(write_input(tmp_path, [item]), source_split="train")
    assert "type" not in evaluation_projection(dataset)[0]["annotations"]
    assert "First sentence." in json.dumps(runtime_projection(dataset))


@pytest.mark.parametrize("field,value,message", [
    ("_id", "", "_id"), ("question", " ", "question"), ("answer", [], "answer"),
    ("context", [], "context"), ("context", [["T", []]], "sentences"),
    ("context", [[" ", ["text"]]], "title"),
    ("context", [["T", [" "]]], "sentence"),
    ("context", [["T", [{"text": "text", "answer": "POISON"}]]], "sentence"),
    ("context", {"title": "T", "sentences": ["text"]}, "context"),
    ("context", [["T", ["a"]], ["T", ["b"]]], "duplicate.*title"),
    ("supporting_facts", [], "supporting_facts"),
    ("supporting_facts", [["Absent", 0]], "unresolved.*title"),
    ("supporting_facts", [["Alpha", -1]], "sentence"),
    ("supporting_facts", [["Alpha", 2]], "sentence"),
    ("supporting_facts", [["Alpha", True]], "sentence"),
    ("supporting_facts", [["Alpha", "0"]], "sentence"),
    ("supporting_facts", [["Alpha", 0, "extra"]], "supporting_facts"),
    ("type", [], "type"), ("level", "", "level"),
])
def test_invalid_fields_are_reported_without_silent_acceptance(tmp_path, field, value, message):
    item = record()
    item[field] = value
    with pytest.raises(HotpotQAValidationError, match=message) as error:
        read_hotpotqa(write_input(tmp_path, [item]), source_split="dev")
    assert error.value.report["counts"]["malformed"] == 1
    assert error.value.report["counts"]["rejected"] == 1


@pytest.mark.parametrize("field", ["_id", "question", "answer", "context", "supporting_facts"])
def test_missing_required_fields_fail(tmp_path, field):
    item = record()
    del item[field]
    with pytest.raises(HotpotQAValidationError, match=field):
        read_hotpotqa(write_input(tmp_path, [item]), source_split="dev")


def test_duplicate_ids_and_malformed_counts_are_explicit(tmp_path):
    items = [record(), record(), {"_id": "bad"}]
    with pytest.raises(HotpotQAValidationError) as error:
        read_hotpotqa(write_input(tmp_path, items), source_split="dev")
    assert error.value.report["counts"] == {
        "total": 3, "accepted": 1, "rejected": 2, "malformed": 1, "duplicate_ids": 1,
    }
    assert error.value.report["duplicate_question_ids"] == ["q1"]


@pytest.mark.parametrize("text", ["", "{", "{}", "[]", '[null]', '[1]', '[{"_id":"a","_id":"b"}]'])
def test_invalid_or_empty_files_fail(tmp_path, text):
    path = tmp_path / "bad.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(HotpotQAValidationError):
        read_hotpotqa(path, source_split="dev")


def test_missing_file_and_blind_test_input_are_explicit(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_hotpotqa(tmp_path / "missing.json", source_split="dev")
    with pytest.raises(ValueError, match="labelled.*train.*dev"):
        read_hotpotqa(write_input(tmp_path, [record()]), source_split="test")


def test_reordering_questions_keeps_document_ids_and_source_sentences(tmp_path):
    items = [record("b"), record("a", "Other question?")]
    first = read_hotpotqa(write_input(tmp_path, items), source_split="dev")
    second = read_hotpotqa(write_input(tmp_path, list(reversed(items))), source_split="dev")
    by_id = lambda data: {item["example_id"]: item for item in runtime_projection(data)}
    assert by_id(first) == by_id(second)
