"""Synthetic condition orchestration; no benchmark files or network."""

from copy import deepcopy
from dataclasses import asdict
import json

import pytest

from ear_rag.config.loader import get_config_path, load_config
from ear_rag.control_evaluation import EvaluationCase, write_evaluation_report
from ear_rag.core.models import EvidenceAssessment
from ear_rag.data.hotpotqa import read_hotpotqa
from ear_rag.routing.initial import InitialRetrievalRouter
from ear_rag import condition_evaluation as runner


@pytest.fixture
def inputs(tmp_path):
    records = [{"_id": q, "question": "Alpha target?", "answer": "GOLD_SECRET",
                "context": [["Alpha", [f"Alpha target {q}."]], ["Beta", [f"Beta {q}."]]],
                "supporting_facts": [["Alpha", 0]], "type": "bridge", "level": "hard"}
               for q in ("q1", "q2")]
    path = tmp_path / "synthetic.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    return read_hotpotqa(path, source_split="dev"), load_config(get_config_path()), path


def spy_runtime(monkeypatch, *, final="insufficient"):
    """Keep real backends/policy/controller; observe fresh factories and calls."""
    builds, calls, assessments = [], [], []
    original = runner.build_backends

    def build(documents, config):
        backends = original(documents, config)
        index = len(builds)
        builds.append((deepcopy(documents), backends, deepcopy(config)))
        for name, backend in backends.items():
            retrieve = backend.retrieve

            def wrapped(query, top_k, _retrieve=retrieve, _name=name, **kwargs):
                calls.append((index, _name, deepcopy(query), top_k, deepcopy(kwargs)))
                return _retrieve(query, top_k, **kwargs)

            monkeypatch.setattr(backend, "retrieve", wrapped)
        return backends

    class Assessor:
        def __init__(self, **kwargs):
            self.calls = 0
            assessments.append(self)

        def assess(self, query, retrieval):
            self.calls += 1
            decision = final if self.calls == 2 else "insufficient"
            return EvidenceAssessment(overall_score=.9 if decision == "sufficient" else .1,
                                      decision=decision)

    monkeypatch.setattr(runner, "build_backends", build)
    monkeypatch.setattr(runner, "DeterministicEvidenceAssessor", Assessor)
    return builds, calls, assessments


@pytest.mark.parametrize("backend", ["local_lexical", "vector_flat", "hybrid", "multihop"])
def test_fixed_dispatch_bypasses_selector_and_cannot_recover(inputs, monkeypatch, backend):
    dataset, config, _ = inputs
    builds, calls, assessments = spy_runtime(monkeypatch)

    def forbidden(*args):
        raise AssertionError("fixed condition called query-aware selection")

    monkeypatch.setattr(InitialRetrievalRouter, "select", forbidden)
    name = f"fixed_{backend}_no_recovery"
    report = runner.evaluate_conditions(dataset, [EvaluationCase("q1")], config,
                                        conditions=[name])[name]
    row, = report["per_case"]
    assert row["status"] == "evaluated", row["error"]
    assert row["initial_backend"] == backend
    assert row["control"]["initial_routing"] is None
    assert row["control"]["recovery_count"] == 0
    assert row["control"]["final_state"] == "abstain"
    assert calls[0][1] == backend
    assert all(call[4].get("retrieval_action") != "recovery" for call in calls)
    assert assessments[0].calls == 1
    assert builds[0][2]["recovery"]["max_recovery_rounds"] == 0


def test_query_aware_uses_existing_selector_without_recovery(inputs, monkeypatch):
    dataset, config, _ = inputs
    config["query_analysis"]["enabled"] = False  # condition explicitly enables it
    _, calls, assessments = spy_runtime(monkeypatch)
    selected = []
    original = InitialRetrievalRouter.select

    def select(self, text, available):
        selected.append(text)
        return original(self, text, available)

    monkeypatch.setattr(InitialRetrievalRouter, "select", select)
    report = runner.evaluate_conditions(dataset, [EvaluationCase("q1")], config,
        conditions=["query_aware_no_recovery"])["query_aware_no_recovery"]
    row, = report["per_case"]
    assert row["status"] == "evaluated"
    assert selected == ["Alpha target?"]
    assert row["control"]["initial_routing"] is not None
    assert row["control"]["recovery_count"] == 0 and assessments[0].calls == 1
    assert all(call[4].get("retrieval_action") != "recovery" for call in calls)


@pytest.mark.parametrize("final", ["sufficient", "insufficient"])
@pytest.mark.parametrize("limit", [0, 1, 3])
def test_adaptive_preserves_limit_and_mandatory_reassessment(inputs, monkeypatch, final, limit):
    dataset, config, _ = inputs
    config["recovery"]["max_recovery_rounds"] = limit
    builds, calls, assessments = spy_runtime(monkeypatch, final=final)
    report = runner.evaluate_conditions(dataset, [EvaluationCase("q1")], config,
        conditions=["adaptive_controller"])["adaptive_controller"]
    row, = report["per_case"]
    assert row["status"] == "evaluated", row["error"]
    assert builds[0][2]["recovery"] == config["recovery"]
    assert row["control"]["initial_routing"] is not None
    assert row["control"]["recovery_count"] == int(limit > 0)
    assert assessments[0].calls == 1 + int(limit > 0)
    assert (row["control"]["recovery_assessment"] is not None) == (limit > 0)
    assert row["control"]["final_state"] == (
        "generate" if limit > 0 and final == "sufficient" else "abstain")


def test_same_pools_settings_and_fresh_state_for_every_question_condition(inputs, monkeypatch):
    dataset, config, path = inputs
    before, raw = deepcopy(config), path.read_bytes()
    builds, calls, assessments = spy_runtime(monkeypatch)
    pipelines = []
    original = runner.RetrievalControlPipeline

    def pipeline(*args, **kwargs):
        instance = original(*args, **kwargs)
        pipelines.append(instance)
        return instance

    monkeypatch.setattr(runner, "RetrievalControlPipeline", pipeline)
    cases = [EvaluationCase("q1"), EvaluationCase("q2")]
    reports = runner.evaluate_conditions(dataset, cases, config)
    assert tuple(reports) == runner.CONDITIONS
    assert len(builds) == len(assessments) == 12
    assert len({id(instance) for instance in pipelines}) == 12
    for position, (name, report) in enumerate(reports.items()):
        assert [row["question_id"] for row in report["per_case"]] == ["q1", "q2"]
        assert report["aggregate"]["counts"]["evaluated"] == 2
        for offset, row in enumerate(report["per_case"]):
            assert builds[position * 2 + offset][0] == builds[offset][0]
            assert row["condition"] == name
            assert row["configuration"] == report["aggregate"]["configuration"]
            assert row["initial"]["requested_top_k"] == config["retrieval"]["default_top_k"]
            assert row["source"]["sha256"] == dataset.source_sha256
        for section in ("chunking", "vector", "hybrid", "multihop", "evidence_assessment"):
            assert report["configuration"][section] == config[section]
    for backend in ("local_lexical", "vector_flat", "hybrid", "multihop"):
        assert len({id(build[1][backend]) for build in builds}) == 12
    for index, _, query, top_k, _ in calls:
        assert query.query_id == cases[index % 2].question_id
        assert top_k == config["retrieval"]["default_top_k"]
        assert "GOLD_SECRET" not in repr(query)
        runtime = json.dumps([asdict(query), [asdict(d) for d in builds[index][0]]])
        for key in ('"answer"', '"supporting_facts"', '"level"', '"type"'):
            assert key not in runtime
    assert builds[0][0] != builds[1][0]
    assert config == before and path.read_bytes() == raw


def test_failures_exclusions_and_duplicate_ids_remain_in_every_condition(inputs, monkeypatch):
    dataset, config, _ = inputs
    original = runner.build_backends

    def build(documents, settings):
        if settings["retrieval"]["backend"] == "vector_flat":
            raise RuntimeError("synthetic index failure")
        return original(documents, settings)

    monkeypatch.setattr(runner, "build_backends", build)
    cases = [EvaluationCase("q1"), EvaluationCase("missing"), EvaluationCase("q2", "test exclusion")]
    reports = runner.evaluate_conditions(dataset, cases, config)
    for name, report in reports.items():
        counts = report["aggregate"]["counts"]
        assert counts["requested"] == sum(counts[k] for k in ("evaluated", "failed", "excluded")) == 3
        assert counts["failed"] == (2 if name == "fixed_vector_flat_no_recovery" else 1)
        assert counts["excluded"] == 1
    duplicate = runner.evaluate_conditions(dataset, [EvaluationCase("q1"), EvaluationCase("q1")], config)
    assert all(report["aggregate"]["counts"]["failed"] == 2 for report in duplicate.values())


def test_gold_changes_only_affect_offline_metrics(inputs, monkeypatch):
    dataset, config, path = inputs
    config["retrieval"]["default_top_k"] = 1
    builds, calls, _ = spy_runtime(monkeypatch)
    first = runner.evaluate_conditions(dataset, [EvaluationCase("q1")], config)
    first_builds, first_calls = len(builds), len(calls)
    records = json.loads(path.read_text(encoding="utf-8"))
    for record in records:
        record["answer"] = "DIFFERENT_GOLD_SECRET"
        record["supporting_facts"] = [["Beta", 0]]
        record["type"], record["level"] = "comparison", "easy"
    path.write_text(json.dumps(records), encoding="utf-8")
    changed = read_hotpotqa(path, source_split="dev")
    second = runner.evaluate_conditions(changed, [EvaluationCase("q1")], config)
    assert [build[0] for build in builds[:first_builds]] == [build[0] for build in builds[first_builds:]]
    assert [call[1:] for call in calls[:first_calls]] == [call[1:] for call in calls[first_calls:]]
    for name in first:
        a, b = first[name]["per_case"][0], second[name]["per_case"][0]
        assert a["status"] == b["status"] == "evaluated"
        assert a["initial_backend"] == b["initial_backend"]
        assert a["control"]["recovery_count"] == b["control"]["recovery_count"]
    name = "fixed_local_lexical_no_recovery"
    assert first[name]["per_case"][0]["initial"]["metrics"] != second[name]["per_case"][0]["initial"]["metrics"]


def test_repeatable_definitions_structure_and_existing_serialization(inputs, tmp_path):
    dataset, config, _ = inputs
    first = runner.evaluate_conditions(dataset, [EvaluationCase("q1")], config)
    second = runner.evaluate_conditions(dataset, [EvaluationCase("q1")], config)

    def structure(value):
        if isinstance(value, dict):
            return {k: structure(v) for k, v in value.items()}
        if isinstance(value, list):
            return [structure(v) for v in value]
        return type(value).__name__

    assert structure(first) == structure(second)
    for name in first:
        assert first[name]["configuration"] == second[name]["configuration"]
        write_evaluation_report(first[name], tmp_path / name)
        row = json.loads((tmp_path / name / "per_case.jsonl").read_text(encoding="utf-8"))
        aggregate = json.loads((tmp_path / name / "aggregate.json").read_text(encoding="utf-8"))
        assert row == first[name]["per_case"][0]
        assert aggregate == first[name]["aggregate"]
        with pytest.raises(FileExistsError):
            write_evaluation_report(first[name], tmp_path / name)


@pytest.mark.parametrize("names", [["unknown"], ["adaptive_controller", "adaptive_controller"]])
def test_invalid_condition_requests_fail_before_execution(inputs, monkeypatch, names):
    dataset, config, _ = inputs
    def forbidden(*args):
        raise AssertionError("should not build")
    monkeypatch.setattr(runner, "build_backends", forbidden)
    with pytest.raises(ValueError):
        runner.evaluate_conditions(dataset, [EvaluationCase("q1")], config, conditions=names)
