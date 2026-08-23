"""Tests for EAR-RAG interface contracts (Protocols)."""

from ear_rag.core.interfaces import (
    Retriever,
    QueryAnalyzer,
    EvidenceAssessor,
    RecoveryPolicy,
    Generator,
    Evaluator,
)
from ear_rag.core.models import Query, RetrievedChunk, RetrievalResult, EvidenceAssessment, RecoveryAction


def test_retriever_importable():
    """Retriever protocol can be imported."""
    assert Retriever is not None


def test_mock_retriever():
    """Mock retriever can satisfy the Retriever protocol."""

    class MockRetriever:
        def retrieve(self, query, top_k=3, **kwargs):
            return RetrievalResult(
                query_id="q1",
                chunks=[
                    RetrievedChunk(
                        chunk_id="c1", document_id="d1", text="Evidence",
                        retrieval_score=0.9, retriever_name="mock",
                    )
                ],
                retriever_name="mock", top_k=top_k,
            )

    mock = MockRetriever()
    from ear_rag.core.models import Query
    q = Query(query_id="q1", text="Test")
    result = mock.retrieve(q, top_k=3)
    assert result.query_id == "q1"
    assert isinstance(result.chunks, list)
    assert result.retriever_name == "mock"


def test_query_analyzer_importable():
    """QueryAnalyzer protocol can be imported."""
    assert QueryAnalyzer is not None


def test_mock_query_analyzer():
    """Mock query analyzer can satisfy the protocol."""

    class MockQueryAnalyzer:
        def analyze(self, query):
            return {"intent": "question", "entities": [], "length": len(query.text)}

    mock = MockQueryAnalyzer()
    from ear_rag.core.models import Query
    q = Query(query_id="q1", text="What is AI?")
    result = mock.analyze(q)
    assert isinstance(result, dict)


def test_evidence_assessor_importable():
    """EvidenceAssessor protocol can be imported."""
    assert EvidenceAssessor is not None


def test_mock_evidence_assessor():
    """Mock evidence assessor can satisfy the protocol."""

    from ear_rag.core.models import (
        Query, RetrievedChunk, RetrievalResult, EvidenceAssessment,
    )

    class MockEvidenceAssessor:
        def assess(self, query, retrieval_result):
            chunks = retrieval_result.chunks
            n = len(chunks)
            if n >= 3:
                decision = "sufficient"
                rationale = "Good chunk coverage"
            elif n >= 1:
                decision = "uncertain"
                rationale = "Limited evidence"
            else:
                decision = "insufficient"
                rationale = "No evidence"
            return EvidenceAssessment(
                relevance=0.8 if n > 0 else 0.0,
                coverage=0.5 * n, support=0.7 if n > 0 else 0.0,
                consistency=0.8, overall_score=0.6 * n,
                decision=decision, rationale=rationale,
            )

    mock = MockEvidenceAssessor()
    from ear_rag.core.models import Query, RetrievedChunk, RetrievalResult
    q = Query(query_id="q1", text="Test")
    rr = RetrievalResult(query_id="q1", chunks=[], retriever_name="test")
    result = mock.assess(q, rr)
    assert isinstance(result, EvidenceAssessment)
    assert result.decision in ("sufficient", "uncertain", "insufficient")