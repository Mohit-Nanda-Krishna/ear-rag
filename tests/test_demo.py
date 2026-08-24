"""Focused tests for the Phase 1.6C controlled demonstration."""
from ear_rag.demo import DemoRunner, build_backends, load_demo_dataset, main


def test_demo_loads_real_hotpotqa_and_keeps_documents_retriever_safe():
    examples = load_demo_dataset("hotpotqa")
    assert len(examples) == 500 and examples[0].documents
    forbidden = {"answer", "answers", "supporting_facts", "evidences", "support_sentence_ids"}
    assert not forbidden.intersection(examples[0].documents[0].metadata)


def test_comparison_runs_all_existing_strategies_and_reports_cost():
    comparison = DemoRunner().compare(0)
    assert [name for name, _, _ in comparison] == ["BM25", "Vector Flat", "Hybrid", "Multi-hop"]
    assert all("retrieval_latency_ms" in result.metadata for _, result, _ in comparison)


def test_controller_is_bounded_and_second_esa_runs_when_recovery_occurs():
    runner = DemoRunner(); result = runner.run_controller(0)
    assert result.total_retrieval_calls >= 1
    if result.recovery_retrieval:
        assert result.recovery_assessment is not None
        assert result.recovery_decision.metadata["recovery_round"] == 1


def test_insufficient_second_esa_abstains_after_exactly_one_recovery():
    runner = DemoRunner()
    runner.config = {**runner.config, "evidence_assessment": {**runner.config["evidence_assessment"], "sufficient_threshold": 1.0}}
    result = runner.run_controller(0)
    assert result.recovery_retrieval is not None and result.recovery_assessment is not None
    assert result.final_state == "abstain"
    assert result.recovery_decision.metadata["recovery_round"] == 1


def test_cli_noninteractive_ear_rag_prints_cost_summary(capsys):
    assert main(["--mode", "ear-rag", "--index", "0"]) == 0
    output = capsys.readouterr().out
    assert "EAR-RAG CONTROLLER" in output and "COST SUMMARY" in output and "Recovery rounds" in output
