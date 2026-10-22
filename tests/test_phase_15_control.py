"""Focused deterministic tests for Phase 1.5 retrieval/control architecture."""
from ear_rag.core.models import Document, EvidenceDecision, Query
from ear_rag.evidence import DeterministicEvidenceAssessor
from ear_rag.retrieval import DocumentChunker, DeterministicVectorRetriever, HybridRetriever, LocalLexicalRetriever, MultiHopRetriever
from ear_rag.routing import BoundedRecoveryPolicy, RetrievalControlPipeline

def _backends():
    docs = [Document("solar", "Solar panels generate electricity from sunlight."), Document("wind", "Wind turbines generate electricity using wind."), Document("history", "Ada Lovelace wrote computing notes.")]
    chunker = DocumentChunker(200, 0); lexical = LocalLexicalRetriever(chunker); vector = DeterministicVectorRetriever(chunker)
    lexical.index(docs); vector.index(docs)
    hybrid = HybridRetriever(lexical, vector); multihop = MultiHopRetriever(lexical, max_hops=2)
    return {"local_lexical": lexical, "vector_flat": vector, "hybrid": hybrid, "multihop": multihop}

def test_vector_hybrid_and_cost_metadata_contracts():
    backends = _backends(); query = Query("q", "solar electricity")
    vector = backends["vector_flat"].retrieve(query, 2)
    hybrid = backends["hybrid"].retrieve(query, 2)
    for result in (vector, hybrid):
        assert result.chunks and result.metadata["backend_name"] == result.retriever_name
        assert result.metadata["requested_top_k"] == 2 and result.metadata["returned_chunk_count"] == len(result.chunks)
        assert result.metadata["retrieval_latency_ms"] >= 0 and result.metadata["indexed_chunk_count"] == 3
    assert hybrid.chunks[0].document_id == "solar"

def test_multihop_is_explicitly_bounded():
    result = _backends()["multihop"].retrieve(Query("q", "solar electricity"), 2)
    assert 1 <= result.metadata["hop_count"] <= 2
    assert result.metadata["max_hops"] == 2

def test_esa_distinguishes_clear_and_inadequate_evidence():
    assessor = DeterministicEvidenceAssessor(sufficient_threshold=.5, uncertain_threshold=.2)
    good = _backends()["local_lexical"].retrieve(Query("q", "solar electricity"), 2)
    assert assessor.assess(Query("q", "solar electricity"), good).decision is EvidenceDecision.SUFFICIENT
    empty = _backends()["local_lexical"].retrieve(Query("q", "unrelated zebras"), 2)
    assert assessor.assess(Query("q", "unrelated zebras"), empty).decision is EvidenceDecision.INSUFFICIENT

def test_sufficient_evidence_skips_recovery():
    backends = _backends(); assessor = DeterministicEvidenceAssessor(sufficient_threshold=.5, uncertain_threshold=.2)
    pipeline = RetrievalControlPipeline(backends, assessor, BoundedRecoveryPolicy(recovery_backends={"local_lexical": "vector_flat"}), top_k=2)
    result = pipeline.run(Query("q", "solar electricity"), "local_lexical")
    assert not result.recovery_decision.metadata["recover"] and result.recovery_retrieval is None and result.final_state == "generate"

def test_recovery_runs_once_then_second_esa_terminates():
    backends = _backends(); assessor = DeterministicEvidenceAssessor(sufficient_threshold=.99, uncertain_threshold=.5)
    policy = BoundedRecoveryPolicy(max_recovery_rounds=1, recovery_backends={"local_lexical": "vector_flat"})
    pipeline = RetrievalControlPipeline(backends, assessor, policy, top_k=2)
    # Include an observable query-term gap: a high ESA threshold alone no longer
    # establishes applicability of an alternative recovery action.
    result = pipeline.run(Query("q", "solar electricity missing"), "local_lexical")
    assert result.recovery_decision.metadata["recover"]
    assert result.recovery_retrieval is not None and result.recovery_assessment is not None
    assert result.final_state == "abstain" and result.total_retrieval_calls >= 2
    follow_up = policy.decide(result.query, result.recovery_assessment, result.recovery_retrieval, recovery_round=1, total_retrieved_chunks=result.total_retrieved_chunks)
    assert not follow_up.metadata["recover"]
