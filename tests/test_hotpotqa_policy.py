"""Auditable exclusion policy, using synthetic records and read-only inputs."""

import hashlib
import json
import subprocess
import sys

import pytest

from ear_rag.data.hotpotqa import HotpotQAValidationError, read_hotpotqa
from ear_rag.data.hotpotqa_policy import POLICY_VERSION, audit_hotpotqa_policy, write_policy_audit


def record(identifier="q"):
    return {"_id": identifier, "question": "Which source?", "answer": "answer",
            "context": [["Alpha", ["First.", "Second."]], ["Beta", ["Other."]]],
            "supporting_facts": [["Alpha", 1]], "type": "bridge", "level": "hard"}


def write_source(tmp_path, records):
    path = tmp_path / "source.json"
    path.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    return path


def assert_partition(report):
    counts = report["counts"]
    assert counts["total_records_inspected"] == counts["valid"] + counts["excluded"] + counts["otherwise_invalid"]
    assert counts["unclassifiable"] <= counts["otherwise_invalid"]
    positions = [r["source_position"] for r in report["excluded_records"] + report["otherwise_invalid_records"]]
    assert len(positions) == len(set(positions))


def test_reproduces_49_blank_pattern_without_approving_other_records(tmp_path):
    records = [record(str(i)) for i in range(50)]
    for r in records[:49]:
        r["context"][0][1][0] = " \t"
    path = write_source(tmp_path, records)
    before = path.read_bytes()
    report = audit_hotpotqa_policy(path)
    assert report["policy_version"] == POLICY_VERSION
    assert report["counts"] == {"total_records_inspected": 50, "valid": 1, "excluded": 49,
                                "otherwise_invalid": 0, "unclassifiable": 0}
    assert report["excluded_reason_counts"] == {"blank_candidate_sentence": 49}
    assert [r["question_id"] for r in report["excluded_records"]] == [str(i) for i in range(49)]
    assert report["evaluation_approval"] == "not_granted"
    assert report["source"]["filename"] == path.name
    assert report["source"]["sha256"] == hashlib.sha256(before).hexdigest()
    assert path.read_bytes() == before
    assert_partition(report)


def test_index_902_has_actionable_bounds_and_does_not_repair_input(tmp_path):
    r = record("index902")
    r["context"][0][1] = [str(i) for i in range(5)]
    r["supporting_facts"] = [["Alpha", 902]]
    path = write_source(tmp_path, [r])
    before = path.read_bytes()
    report = audit_hotpotqa_policy(path)
    row, = report["excluded_records"]
    assert row["question_id"] == "index902" and row["source_position"] == 0
    assert row["reason_codes"] == ["support_sentence_index_out_of_range"]
    assert row["details"][0] == {"code": "support_sentence_index_out_of_range", "supporting_fact_position": 0,
        "title": "Alpha", "sentence_index": 902, "sentence_count": 5, "valid_min": 0, "valid_max": 4}
    assert path.read_bytes() == before
    with pytest.raises(HotpotQAValidationError):
        read_hotpotqa(path, source_split="dev")


def test_overlapping_and_repeated_defects_count_records_once_and_preserve_all_details(tmp_path):
    r = record()
    r["context"][0][1] = ["", " "]
    r["supporting_facts"] = [["Alpha", -1], ["Alpha", 902]]
    report = audit_hotpotqa_policy(write_source(tmp_path, [r]))
    assert report["counts"]["excluded"] == 1
    row, = report["excluded_records"]
    assert row["reason_codes"] == ["blank_candidate_sentence", "support_sentence_index_out_of_range"]
    assert len(row["details"]) == 4
    assert report["excluded_reason_counts"] == {"blank_candidate_sentence": 1,
                                               "support_sentence_index_out_of_range": 1}
    assert_partition(report)


@pytest.mark.parametrize("identifier", [None, "", " ", 5, ["not", "id"]])
def test_missing_or_malformed_ids_are_unclassifiable_not_silently_excluded(tmp_path, identifier):
    r = record()
    r["_id"] = identifier
    r["context"][0][1][0] = ""
    report = audit_hotpotqa_policy(write_source(tmp_path, [r]))
    assert report["counts"]["otherwise_invalid"] == 1 and report["counts"]["unclassifiable"] == 1
    assert not report["excluded_records"]
    row, = report["otherwise_invalid_records"]
    assert "invalid_question_id" in row["reason_codes"] and "blank_candidate_sentence" in row["reason_codes"]
    assert not row["classification_reliable"]
    assert_partition(report)


def test_missing_id_and_duplicate_ids_keep_all_source_positions(tmp_path):
    missing = record()
    del missing["_id"]
    a, b = record("same"), record("same")
    b["supporting_facts"] = [["Alpha", 902]]
    report = audit_hotpotqa_policy(write_source(tmp_path, [a, missing, b]))
    assert report["counts"]["unclassifiable"] == 3
    assert [r["source_position"] for r in report["otherwise_invalid_records"]] == [0, 1, 2]
    assert report["unclassifiable_positions"] == [0, 1, 2]
    assert report["otherwise_invalid_records"][0]["reason_codes"] == ["duplicate_question_id"]
    assert "support_sentence_index_out_of_range" in report["otherwise_invalid_records"][2]["reason_codes"]
    assert_partition(report)


@pytest.mark.parametrize("context,supports", [
    ({}, [["Alpha", 902]]), ([["Alpha", None]], [["Alpha", 902]]),
    ([["Alpha", ["a"]], ["Alpha", ["b", "c"]]], [["Alpha", 902]]),
    ([["Alpha", ["a"]]], [["Unknown", 902]]),
    ([["Alpha", ["a"]]], [["Alpha", True]]),
    ([["Alpha", ["a"]]], [["Alpha", "902"]]),
    ([["Alpha", ["a"]]], {"title": ["Alpha"], "sent_id": [902]}),
])
def test_uncertain_structure_never_invents_bounds_or_out_of_range_findings(tmp_path, context, supports):
    r = record()
    r.update(context=context, supporting_facts=supports)
    report = audit_hotpotqa_policy(write_source(tmp_path, [r]))
    row, = report["otherwise_invalid_records"]
    assert not row["classification_reliable"]
    assert "support_sentence_index_out_of_range" not in row["reason_codes"]
    assert row["strict_validation_error"]
    assert_partition(report)


def test_other_strict_errors_are_not_policy_exclusions(tmp_path):
    r = record()
    r["answer"] = ""
    report = audit_hotpotqa_policy(write_source(tmp_path, [r]))
    assert report["counts"] == {"total_records_inspected": 1, "valid": 0, "excluded": 0,
                                "otherwise_invalid": 1, "unclassifiable": 0}
    assert report["otherwise_invalid_records"][0]["reason_codes"] == ["strict_validation_error"]


def test_determinism_checksum_changes_and_serialization(tmp_path):
    path = write_source(tmp_path, [record()])
    first = audit_hotpotqa_policy(path)
    assert first == audit_hotpotqa_policy(path)
    a, b = tmp_path / "audit-a.json", tmp_path / "audit-b.json"
    write_policy_audit(first, a)
    write_policy_audit(audit_hotpotqa_policy(path), b)
    assert a.read_bytes() == b.read_bytes()
    assert json.loads(a.read_text(encoding="utf-8")) == first
    path.write_bytes(path.read_bytes() + b"\n")
    changed = audit_hotpotqa_policy(path)
    assert changed["source"]["sha256"] != first["source"]["sha256"]
    assert changed["counts"] == first["counts"]


def test_writer_refuses_existing_files_including_raw_input(tmp_path):
    path = write_source(tmp_path, [record()])
    before = path.read_bytes()
    report = audit_hotpotqa_policy(path)
    with pytest.raises(FileExistsError):
        write_policy_audit(report, path)
    assert path.read_bytes() == before


@pytest.mark.parametrize("text", ["{", "{}", "[]", '[{"_id":"a","_id":"b"}]', '[NaN]'])
def test_unparseable_or_unsupported_file_is_explicitly_unclassified(tmp_path, text):
    path = tmp_path / "bad.json"
    path.write_text(text, encoding="utf-8")
    report = audit_hotpotqa_policy(path)
    assert report["status"] == "file_error" and report["file_error"]
    assert not report["excluded_records"]
    assert report["counts"]["total_records_inspected"] in (0, None)


def test_cli_writes_only_the_requested_audit(tmp_path):
    path = write_source(tmp_path, [record()])
    before = path.read_bytes()
    output = tmp_path / "audit.json"
    result = subprocess.run([sys.executable, "-m", "ear_rag.data.hotpotqa_policy", str(path),
                             "--output", str(output)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8")) == audit_hotpotqa_policy(path)
    assert path.read_bytes() == before
