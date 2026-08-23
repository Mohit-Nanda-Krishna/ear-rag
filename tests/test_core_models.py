"""Tests for core EAR-RAG data models.

Verifies that all data contracts can be instantiated and have the expected
structure and type hints.
"""

import pytest

from ear_rag.core.models import (
    Query,
    Document,
    RetrievedChunk,
    RetrievalResult,
    EvidenceAssessment,
    RecoveryAction,
    GenerationRequest,
    GenerationResponse,
    EvaluationResult,
)


def test_query_instantiation():
    """Query can be instantiated."""
    q = Query(query_id="q1", text="What is AI?")
    assert q.query_id == "q1"
    assert q.text == "What is AI?"
    assert isinstance(q.metadata, dict)


def test_document_instantiation():
    """Document can be instantiated."""
    d = Document(document_id="d1", text="Some document content")
    assert d.document_id == "d1"
    assert d.text == "Some document content"
    assert isinstance(d.metadata, dict)


def test_retrieved_chunk_instantiation():
    """RetrievedChunk can be instantiated."""
    chunk = RetrievedChunk(
        chunk_id="c1",
        document_id="d1",
        text="Evidence text",
        retrieval_score=0.95,
        retriever_name="test_retriever",
    )
    assert chunk.chunk_id == "c1"
    assert chunk.document_id == "d1"
    assert chunk.retrieval_score == 0.95
    assert chunk.retriever_name == "test_retriever"


def test_retrieval_result_instantiation():
    """RetrievalResult can contain retrieved chunks."""
    chunk = RetrievedChunk(
        chunk_id="c1",
        document_id="d1",
        text="Evidence text",
        retrieval_score=0.95,
        retriever_name="test_retriever",
    )
    result = RetrievalResult(
        query_id="q1",
        chunks=[chunk],
        retriever_name="test_retriever",
        top_k=5,
    )
    assert len(result.chunks) == 1
    assert result.chunks[0].chunk_id == "c1"
    assert result.top_k == 5


def test_evidence_assessment_decisions():
    """EvidenceAssessment supports sufficient/uncertain/insufficient decisions."""

    # Sufficient
    assess_sufficient = EvidenceAssessment(
        relevance=0.9,
        coverage=0.8,
        support=0.9,
        consistency=0.85,
        overall_score=0.86,
        decision=EvidenceAssessment.DECISION_SUFFICIENT,
        rationale="Strong evidence supports the answer",
    )
    assert assess_sufficient.decision == "sufficient"

    # Uncertain
    assess_uncertain = EvidenceAssessment(
        relevance=0.5,
        coverage=0.4,
        support=0.5,
        consistency=0.5,
        overall_score=0.46,
        decision=EvidenceAssessment.DECISION_UNCERTAIN,
        rationale="Partial evidence, unsure",
    )
    assert assess_uncertain.decision == "uncertain"

    # Insufficient
    assess_insufficient = EvidenceAssessment(
        relevance=0.2,
        coverage=0.1,
        support=0.2,
        consistency=0.3,
        overall_score=0.15,
        decision=EvidenceAssessment.DECISION_INSUFFICIENT,
        rationale="No sufficient evidence",
    )
    assert assess_insufficient.decision == "insufficient"


def test_recovery_action_types():
    """RecoveryAction can represent different action types."""

    # increase_k
    action_inc = RecoveryAction(
        action_type=RecoveryAction.ACTION_INCREASE_K,
        parameters={"k": 10},
        reason="Insufficient evidence retrieved",
    )
    assert action_inc.action_type == "increase_k"

    # alternative_retriever
    action_alt = RecoveryAction(
        action_type=RecoveryAction.ACTION_ALTERNATIVE_RETRIEVER,
        reason="Current retriever underperforming",
    )
    assert action_alt.action_type == "alternative_retriever"

    # query_reformulation
    action_ref = RecoveryAction(
        action_type=RecoveryAction.ACTION_QUERY_REFORMULATION,
        reason="Query too broad",
    )
    assert action_ref.action_type == "query_reformulation"

    # query_decomposition
    action_decomp = RecoveryAction(
        action_type=RecoveryAction.ACTION_QUERY_DECOMPOSITION,
        reason="Complex query needs breaking down",
    )
    assert action_decomp.action_type == "query_decomposition"

    # hybrid_retrieval
    action_hyb = RecoveryAction(
        action_type=RecoveryAction.ACTION_HYBRID_RETRIEVAL,
        reason="Combine sparse and dense retrievers",
    )
    assert action_hyb.action_type == "hybrid_retrieval"

    # no_action
    action_no = RecoveryAction(
        action_type=RecoveryAction.ACTION_NO_ACTION,
        reason="Assessment found sufficient evidence",
    )
    assert action_no.action_type == "no_action"


def test_generation_request_instantiation():
    """GenerationRequest can be instantiated."""
    from ear_rag.core.models import Query
    q = Query(query_id="q1", text="What is AI?")
    gr = GenerationRequest(query=q)
    assert gr.query.query_id == "q1"


def test_generation_response_instantiation():
    """GenerationResponse can be instantiated."""
    gr = GenerationResponse(answer="AI is...", confidence=0.95)
    assert gr.answer == "AI is..."
    assert gr.confidence == 0.95


def test_evaluation_result_instantiation():
    """EvaluationResult can be instantiated."""
    er = EvaluationResult(metric_name="accuracy", metric_value=0.92, sample_count=100)
    assert er.metric_name == "accuracy"
    assert er.metric_value == 0.92
    assert er.sample_count == 100