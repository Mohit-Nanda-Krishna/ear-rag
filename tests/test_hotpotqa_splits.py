"""Synthetic split/exposure integrity and artifact consistency checks."""

import hashlib
import json
from pathlib import Path

import pytest

from ear_rag.data.hotpotqa import read_hotpotqa
from ear_rag.data.hotpotqa_splits import (
    ExposureInventory, SplitIntegrityError, plan_splits, validate_split_integrity,
    write_split_artifacts,
)


def make_dataset(tmp_path, questions=None):
    questions = questions or {f"q{i}": f"Question {i}?" for i in range(8)}
    records = [{"_id": key, "question": text, "answer": "PRIVATE_ANSWER",
                "context": [["A", ["Candidate sentence."]]],
                "supporting_facts": [["A", 0]],
                "annotation": {"nested": ["PRIVATE_ANNOTATION"]}}
               for key, text in questions.items()]
    path = tmp_path / "synthetic.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    return read_hotpotqa(path, source_split="dev")


def inventory(questions=None):
    return ExposureInventory("explicit-synthetic-inventory", {} if questions is None else questions)


def test_selection_manifest_is_deterministic_and_not_input_order_dependent(tmp_path):
    dataset = make_dataset(tmp_path)
    kwargs = {"development_count": 2, "holdout_count": 2, "prior_exposure": inventory()}
    first = plan_splits(dataset, **kwargs)
    assert first == plan_splits(dataset, **kwargs)
    questions = {item.example_id: item.question for item in reversed(dataset.examples)}
    reordered = plan_splits(make_dataset(tmp_path, questions), **kwargs)
    assert first["roles"] == reordered["roles"]
    assert first["source"]["sha256"] != reordered["source"]["sha256"]
    assert first["counts"]["accepted"] == 8
    assert first["counts"]["development"] == first["counts"]["holdout"] == 2
    assert first["integrity"]["prior_exposure"]["status"] == "supplied"
    assert first["selection"]["seed"] == 1729


def test_selection_ignores_answers_and_annotations(tmp_path):
    dataset = make_dataset(tmp_path)
    kwargs = {"development_count": 2, "holdout_count": 2, "prior_exposure": inventory()}
    before = plan_splits(dataset, **kwargs)["roles"]
    source = tmp_path / "synthetic.json"
    records = json.loads(source.read_text())
    for item in records:
        item["answer"] = "CHANGED_LABEL"
        item["annotation"] = {"type": "changed", "gold": ["another"]}
    source.write_text(json.dumps(records), encoding="utf-8")
    assert before == plan_splits(read_hotpotqa(source, source_split="dev"), **kwargs)["roles"]


def test_normalized_alias_exposure_excludes_representative_even_if_alias_id_exposed(tmp_path):
    questions = {"a": "Ｃｉｔｙ   name?", "z": "city name?", "b": "Other?", "c": "Third?"}
    dataset = make_dataset(tmp_path, questions)
    manifest = plan_splits(dataset, development_count=0, holdout_count=2,
                           prior_exposure=inventory({"z": None}))
    assert manifest["roles"]["holdout"] == sorted(["b", "c"], key=lambda key: hashlib.sha256(f"1729:{key}".encode()).hexdigest())
    assert manifest["aliases"] == {"a": ["a", "z"]}
    assert manifest["counts"]["normalized_text_duplicates"] == 1
    assert "a" in manifest["holdout_exclusions"]
    assert manifest["integrity"]["semantic_near_duplicates"] == "not_checked"


def test_exposed_text_outside_source_is_checked_without_fuzzy_matching(tmp_path):
    dataset = make_dataset(tmp_path, {"a": "City name?", "b": "Different?"})
    manifest = plan_splits(dataset, development_count=0, holdout_count=1,
                           prior_exposure=inventory({"external-id": " CITY  NAME? "}))
    assert manifest["roles"]["holdout"] == ["b"]


def test_missing_inventory_is_unavailable_and_blocks_holdout(tmp_path):
    dataset = make_dataset(tmp_path)
    with pytest.raises(SplitIntegrityError, match="exposure") as error:
        plan_splits(dataset, development_count=1, holdout_count=1, prior_exposure=None)
    assert error.value.report["prior_exposure"]["status"] == "unavailable"
    development_only = plan_splits(dataset, development_count=1, holdout_count=0, prior_exposure=None)
    assert development_only["integrity"]["prior_exposure"]["status"] == "unavailable"


def test_unmatched_exposure_ids_need_text_before_holdout_claim(tmp_path):
    with pytest.raises(SplitIntegrityError, match="exposure") as error:
        plan_splits(make_dataset(tmp_path), development_count=1, holdout_count=1,
                    prior_exposure=inventory({"unknown-old-id": None}))
    assert error.value.report["prior_exposure"]["status"] == "partial"


@pytest.mark.parametrize("dev,held,message", [
    (["q0"], ["q0"], "overlap"), (["q0", "q0"], [], "duplicate"),
    ([], ["q0", "q0"], "duplicate"), (["missing"], [], "unknown"),
])
def test_explicit_id_overlap_duplicates_and_unknown_ids_fail(tmp_path, dev, held, message):
    with pytest.raises(SplitIntegrityError, match=message):
        validate_split_integrity(make_dataset(tmp_path), dev, held, prior_exposure=inventory())


def test_explicit_normalized_text_overlap_and_prior_exposure_fail(tmp_path):
    dataset = make_dataset(tmp_path, {"a": "City name?", "b": " CITY name? "})
    with pytest.raises(SplitIntegrityError, match="normalized.*overlap"):
        validate_split_integrity(dataset, ["a"], ["b"], prior_exposure=inventory())
    with pytest.raises(SplitIntegrityError, match="expos"):
        validate_split_integrity(dataset, [], ["b"], prior_exposure=inventory({"a": None}))


@pytest.mark.parametrize("kwargs", [
    {"development_count": -1, "holdout_count": 1},
    {"development_count": True, "holdout_count": 1},
    {"development_count": 1, "holdout_count": 1.5},
    {"development_count": 0, "holdout_count": 0},
    {"development_count": 1, "holdout_count": 1, "seed": True},
])
def test_invalid_selection_configuration_fails(tmp_path, kwargs):
    with pytest.raises(ValueError):
        plan_splits(make_dataset(tmp_path), prior_exposure=inventory(), **kwargs)


def test_insufficient_records_or_exposure_constraints_never_silently_shrink(tmp_path):
    dataset = make_dataset(tmp_path, {"a": "A?", "b": "B?"})
    with pytest.raises(SplitIntegrityError, match="development"):
        plan_splits(dataset, development_count=3, holdout_count=0, prior_exposure=inventory())
    with pytest.raises(SplitIntegrityError, match="eligible"):
        plan_splits(dataset, development_count=1, holdout_count=1,
                    prior_exposure=inventory({"a": None, "b": None}))


def test_exports_are_reproducible_separate_checksums_match_and_do_not_overwrite(tmp_path, monkeypatch):
    dataset = make_dataset(tmp_path)
    source_bytes = (tmp_path / "synthetic.json").read_bytes()
    kwargs = {"development_count": 2, "holdout_count": 2, "prior_exposure": inventory()}
    destinations = [tmp_path / "first", tmp_path / "second"]
    for destination in destinations:
        manifest = write_split_artifacts(dataset, destination, **kwargs)
        assert json.loads((destination / "manifest.json").read_text()) == manifest
        for name, info in manifest["artifacts"].items():
            payload = (destination / name).read_bytes()
            assert info["sha256"] == hashlib.sha256(payload).hexdigest()
            records = [json.loads(line) for line in payload.decode().splitlines()]
            assert len(records) == info["records"] == 2
            role = name.split(".")[0]
            assert [item["example_id"] for item in records] == manifest["roles"][role]
            assert all(item["role"] == role for item in records)
            if ".runtime." in name:
                assert b"PRIVATE_" not in payload and b'"answer' not in payload
            else:
                assert b"PRIVATE_ANSWER" in payload and b"PRIVATE_ANNOTATION" in payload
    assert {p.name: p.read_bytes() for p in destinations[0].iterdir()} == {p.name: p.read_bytes() for p in destinations[1].iterdir()}
    assert (tmp_path / "synthetic.json").read_bytes() == source_bytes
    with pytest.raises(FileExistsError):
        write_split_artifacts(dataset, destinations[0], **kwargs)
    original_open = Path.open

    def deny_labels(path, *args, **kwargs):
        if ".labels." in path.name:
            raise AssertionError("runtime must not open labels")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", deny_labels)
    runtime = [json.loads(line) for line in (destinations[0] / "development.runtime.jsonl").read_text().splitlines()]
    assert len(runtime) == 2 and runtime[0]["documents"]


def test_failed_preflight_creates_no_artifact_directory(tmp_path):
    target = tmp_path / "must-not-exist"
    with pytest.raises(SplitIntegrityError):
        write_split_artifacts(make_dataset(tmp_path), target,
                              development_count=1, holdout_count=1, prior_exposure=None)
    assert not target.exists()
