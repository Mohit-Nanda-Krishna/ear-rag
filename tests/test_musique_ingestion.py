"""Native synthetic MuSiQue validation, independent of ignored local sources."""
from copy import deepcopy
import json

import pytest

from ear_rag.data.musique import inspect_musique, read_musique


def record(qid="q1"):
    return {"id": qid, "question": "Where did Alpha begin?", "answer": "SECRET",
            "answer_aliases": [], "answerable": True,
            "paragraphs": [{"idx": 0, "title": "Same", "paragraph_text": "Alpha began in Paris.", "is_supporting": True},
                           {"idx": 1, "title": "Same", "paragraph_text": "Alpha other place.", "is_supporting": False}],
            "question_decomposition": [{"id": 10, "question": "Private step?", "answer": "SECRET", "paragraph_support_idx": 0}]}


def write(tmp_path, records):
    path = tmp_path / "native.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return path


def test_preservation_manifest_determinism_and_checksum(tmp_path):
    original = record()
    path = write(tmp_path, [original])
    raw = path.read_bytes()
    data = read_musique(path)
    assert data.records == (original,)
    assert inspect_musique(path) == inspect_musique(path) == data.manifest
    assert data.manifest["counts"] == {"total": 1, "valid": 1, "excluded": 0, "unclassifiable": 0, "unique_ids": 1}
    assert path.read_bytes() == raw
    original["answer"] = "Changed gold"
    write(tmp_path, [original])
    assert inspect_musique(path)["source"]["sha256"] != data.source_sha256


@pytest.mark.parametrize("defect", ["id", "question", "answer", "answer_aliases", "answerable", "paragraphs", "question_decomposition",
                                    "support_idx", "flag", "duplicate_idx", "blank_text", "bool_idx", "duplicate_step", "bad_alias"])
def test_invalid_native_records_are_explicit_and_not_evaluable(tmp_path, defect):
    r = record()
    if defect in r:
        del r[defect]
    elif defect == "support_idx": r["question_decomposition"][0]["paragraph_support_idx"] = 99
    elif defect == "flag": r["paragraphs"][0]["is_supporting"] = False
    elif defect == "duplicate_idx": r["paragraphs"][1]["idx"] = 0
    elif defect == "blank_text": r["paragraphs"][0]["paragraph_text"] = " "
    elif defect == "bool_idx": r["paragraphs"][0]["idx"] = False
    elif defect == "duplicate_step": r["question_decomposition"].append(deepcopy(r["question_decomposition"][0]))
    elif defect == "bad_alias": r["answer_aliases"] = [1]
    path = write(tmp_path, [r])
    report = inspect_musique(path)
    assert report["counts"]["excluded"] + report["counts"]["unclassifiable"] == 1
    assert report["issues"][0]["position"] == 1
    assert report["issues"][0]["reason_codes"]
    with pytest.raises(ValueError, match="not fully valid"):
        read_musique(path)


@pytest.mark.parametrize("content", ['{bad}\n', '{"id":"a","id":"b"}\n', '{"x":NaN}\n', '{"extra":1e999}\n', '\n'])
def test_strict_jsonl(tmp_path, content):
    path = tmp_path / "bad.jsonl"
    path.write_text(content, encoding="utf-8")
    report = inspect_musique(path)
    assert report["counts"]["unclassifiable"] == 1
    with pytest.raises(ValueError): read_musique(path)


def test_duplicate_ids_exclude_every_occurrence_not_first_wins(tmp_path):
    report = inspect_musique(write(tmp_path, [record(), record()]))
    assert report["counts"]["excluded"] == 2
    assert report["counts"]["valid"] == 0
    assert all("duplicate_question_id" in issue["reason_codes"] for issue in report["issues"])


def test_acquisition_metadata_requires_matching_source(tmp_path):
    path = write(tmp_path, [record()])
    acquisition = tmp_path / "acquisition.json"
    acquisition.write_text(json.dumps({"artifacts": [{"sha256": "wrong"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="acquisition"):
        read_musique(path, acquisition_path=acquisition)
