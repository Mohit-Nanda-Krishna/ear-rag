"""Comparison integrity rejects mismatches and retains failed/excluded cases."""
from copy import deepcopy

import pytest

from ear_rag.condition_evaluation import CONDITIONS
from ear_rag.musique_experiment import paired_cases, nominal_cost


def reports():
    return {name: {"configuration": {"retrieval": {"default_top_k": 5}}, "per_case": [
        {"question_id": "a", "case_index": 0, "status": "evaluated"},
        {"question_id": "b", "case_index": 1, "status": "failed"},
        {"question_id": "x", "case_index": 2, "status": "excluded", "exclusion_reason": "invalid"}]}
        for name in CONDITIONS}


def test_pairing_has_explicit_failure_and_exclusion_denominators():
    r = reports()
    r[CONDITIONS[0]]["per_case"][1]["status"] = "evaluated"
    result = paired_cases(r)
    assert result["paired_ids"] == ["a"]
    assert result["requested_ids"] == ["a", "b", "x"]
    assert result["unpaired_ids"] == ["b"]
    assert result["excluded_ids"] == ["x"]
    assert result["failed_ids"][CONDITIONS[1]] == ["b"]


@pytest.mark.parametrize("defect", ["missing", "duplicate", "order", "exclusion", "topk", "condition"])
def test_pairing_rejects_silent_cohort_drift(defect):
    r = deepcopy(reports())
    first = r[CONDITIONS[0]]
    if defect == "missing": first["per_case"].pop()
    elif defect == "duplicate": first["per_case"][1]["question_id"] = "a"
    elif defect == "order": first["per_case"].reverse()
    elif defect == "exclusion": first["per_case"][2]["status"] = "failed"
    elif defect == "topk": first["configuration"]["retrieval"]["default_top_k"] = 4
    elif defect == "condition": r.pop(CONDITIONS[0])
    with pytest.raises(ValueError): paired_cases(r)


def test_nominal_cost_is_configured_increment_not_realized_latency():
    config = {"recovery": {"cost_awareness": {"incremental_work": {
        "local_lexical": {"retrieval_calls": 1, "retrieved_chunks": 5, "latency_ms": 10}}}}}
    assert nominal_cost("local_lexical", config) == pytest.approx(.11)


def test_synthetic_cli_run_saved_replay_and_exclusive_writes(tmp_path, monkeypatch):
    """No local benchmark prerequisite: supply a synthetic approved input gate."""
    import json
    import sys
    from ear_rag import musique_experiment as experiment
    from ear_rag.config.loader import get_config_path, load_config
    from ear_rag.data.musique import read_musique
    from test_musique_ingestion import record, write

    data = read_musique(write(tmp_path, [record()]))
    config = load_config(get_config_path())
    paths = ["configs/config.yaml", "docs/evaluation_protocol.md", "data/raw/musique/test.json",
             "data/raw/nq/NQ-open.dev.jsonl", "data/raw/musique/official_v1_0/musique_ans_v1.0_dev.jsonl",
             "data/raw/musique/official_v1_0/acquisition_manifest.json",
             "data/raw/musique/official_v1_0/dev_test_singlehop_questions_v1.0.json"]
    for path in paths:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("synthetic frozen bytes", encoding="utf-8")
    monkeypatch.setattr(experiment, "ROOT", tmp_path)
    monkeypatch.setattr(experiment, "RAW", tmp_path / "data/raw/musique/official_v1_0")
    monkeypatch.setattr(experiment, "get_config_path", lambda: tmp_path / "configs/config.yaml")
    monkeypatch.setattr(experiment, "inputs", lambda: (data, config, {"label": experiment.LABEL, "question_ids": ["q1"]}))
    output = tmp_path / "outputs/synthetic"
    monkeypatch.setattr(sys, "argv", ["musique_experiment", "run", "--output", str(output)])
    experiment.main()
    initial = {p: p.read_bytes() for p in output.rglob("*") if p.is_file()}
    with pytest.raises(FileExistsError): experiment.main()
    monkeypatch.setattr(sys, "argv", ["musique_experiment", "verify", "--output", str(output)])
    experiment.main()
    assert all(p.read_bytes() == raw for p, raw in initial.items())
    validation = json.loads((output / "validation.json").read_text())
    assert validation["verified_stages"] == 12
    path = output / CONDITIONS[0] / "per_case.jsonl"
    path.write_text(path.read_text() + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="artifact checksum"):
        experiment.main()
