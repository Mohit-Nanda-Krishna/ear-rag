"""Phase 1.2 tests for stable configuration and core contracts."""

from pathlib import Path

import pytest

from ear_rag.config.loader import get_config_path, load_config
from ear_rag.core.interfaces import (
    Evaluator,
    EvidenceAssessor,
    Generator,
    QueryAnalyzer,
    RecoveryPolicy,
    Retriever,
)
from ear_rag.core.models import (
    EvidenceAssessment,
    EvidenceDecision,
    EvaluationResult,
    GenerationRequest,
    GenerationResponse,
    Query,
    RecoveryAction,
    RecoveryActionType,
    RetrievedChunk,
    RetrievalResult,
)


def test_mutable_defaults_are_independent() -> None:
    """Mutable contract defaults must never be shared across instances."""
    first_query = Query(query_id="q1", text="First")
    second_query = Query(query_id="q2", text="Second")
    first_query.metadata["source"] = "test"

    first_action = RecoveryAction()
    second_action = RecoveryAction()
    first_action.parameters["k"] = 10

    first_request = GenerationRequest(query=first_query)
    second_request = GenerationRequest(query=second_query)
    first_request.evidence.append(
        RetrievedChunk(
            chunk_id="c1",
            document_id="d1",
            text="Evidence",
            retrieval_score=1.0,
            retriever_name="test",
        )
    )

    assert second_query.metadata == {}
    assert second_action.parameters == {}
    assert second_request.evidence == []


def test_evidence_decision_is_normalized_and_validated() -> None:
    """Evidence decisions accept valid strings and reject invalid values."""
    assessment = EvidenceAssessment(decision="sufficient")

    assert assessment.decision is EvidenceDecision.SUFFICIENT
    with pytest.raises(ValueError, match="unsupported"):
        EvidenceAssessment(decision="unsupported")


def test_recovery_action_is_normalized_and_validated() -> None:
    """Recovery actions accept every defined action and reject invalid values."""
    for action_type in RecoveryActionType:
        assert RecoveryAction(action_type=action_type.value).action_type is action_type

    with pytest.raises(ValueError, match="unsupported"):
        RecoveryAction(action_type="unsupported")


def test_minimal_implementations_satisfy_runtime_protocols() -> None:
    """The contracts remain implementation-independent and runtime checkable."""

    class MinimalRetriever:
        def retrieve(self, query: Query, top_k: int, **kwargs: object) -> RetrievalResult:
            return RetrievalResult(query_id=query.query_id, top_k=top_k)

    class MinimalQueryAnalyzer:
        def analyze(self, query: Query) -> dict[str, object]:
            return {"query_length": len(query.text)}

    class MinimalEvidenceAssessor:
        def assess(
            self, query: Query, retrieval_result: RetrievalResult
        ) -> EvidenceAssessment:
            return EvidenceAssessment()

    class MinimalRecoveryPolicy:
        def decide(
            self,
            query: Query,
            assessment: EvidenceAssessment,
            retrieval_result: RetrievalResult,
        ) -> RecoveryAction:
            return RecoveryAction()

    class MinimalGenerator:
        def generate(self, request: GenerationRequest) -> GenerationResponse:
            return GenerationResponse()

    class MinimalEvaluator:
        def evaluate(self, **kwargs: object) -> EvaluationResult:
            return EvaluationResult(metric_name="placeholder", metric_value=0.0)

    assert isinstance(MinimalRetriever(), Retriever)
    assert isinstance(MinimalQueryAnalyzer(), QueryAnalyzer)
    assert isinstance(MinimalEvidenceAssessor(), EvidenceAssessor)
    assert isinstance(MinimalRecoveryPolicy(), RecoveryPolicy)
    assert isinstance(MinimalGenerator(), Generator)
    assert isinstance(MinimalEvaluator(), Evaluator)


def test_hardened_configuration_sections_and_values() -> None:
    """Initial research configuration exposes every required section."""
    config = load_config()

    assert {
        "project",
        "data",
        "query_analysis",
        "retrieval",
        "evidence_assessment",
        "recovery",
        "generation",
        "evaluation",
        "logging",
    }.issubset(config)
    assert config["retrieval"]["default_top_k"] < config["retrieval"]["max_top_k"]
    assert sum(config["evidence_assessment"]["weights"].values()) == pytest.approx(1.0)
    assert config["recovery"]["max_attempts"] > 0


def test_default_config_path_is_derived_from_repository_root() -> None:
    """The default path is portable and stays inside the repository."""
    repository_root = Path(__file__).resolve().parents[1]

    assert get_config_path() == repository_root / "configs" / "config.yaml"
