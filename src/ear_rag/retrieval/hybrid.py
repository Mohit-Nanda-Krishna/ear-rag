"""Deterministic score-fusion retrieval backend."""
from __future__ import annotations
from collections.abc import Sequence
from time import perf_counter
from typing import cast
from ear_rag.core.interfaces import IndexableRetriever
from ear_rag.core.models import Document, Query, RetrievedChunk, RetrievalResult

class HybridRetriever:
    def __init__(self, lexical: IndexableRetriever, vector: IndexableRetriever, *, lexical_weight: float = .5,
                 vector_weight: float = .5, name: str = "hybrid") -> None:
        if lexical_weight < 0 or vector_weight < 0 or lexical_weight + vector_weight == 0:
            raise ValueError("hybrid weights must be non-negative and non-zero together")
        self._lexical, self._vector, self._name = lexical, vector, name
        total = lexical_weight + vector_weight
        self._lexical_weight, self._vector_weight = lexical_weight / total, vector_weight / total
        self._calls = 0
    @property
    def name(self) -> str: return self._name
    def index(self, documents: Sequence[Document]) -> None:
        self._lexical.index(documents); self._vector.index(documents); self._calls = 0
    def retrieve(self, query: Query, top_k: int, **kwargs: object) -> RetrievalResult:
        started = perf_counter()
        lexical = self._lexical.retrieve(query, top_k, **kwargs)
        vector = self._vector.retrieve(query, top_k, **kwargs)
        scores: dict[str, float] = {}; evidence: dict[str, RetrievedChunk] = {}
        for result, weight in ((lexical, self._lexical_weight), (vector, self._vector_weight)):
            maximum = max((chunk.retrieval_score for chunk in result.chunks), default=0.0)
            for chunk in result.chunks:
                evidence[chunk.chunk_id] = chunk
                scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + weight * (chunk.retrieval_score / maximum if maximum else 0.0)
        self._calls += 1
        ranked = sorted(evidence.values(), key=lambda chunk: (-scores[chunk.chunk_id], chunk.document_id, chunk.chunk_id))[:top_k]
        chunks = [RetrievedChunk(chunk.chunk_id, chunk.document_id, chunk.text, scores[chunk.chunk_id], self._name, dict(chunk.metadata)) for chunk in ranked]
        return RetrievalResult(query.query_id, chunks, self._name, top_k, {
            "retriever_name": self._name, "backend_name": self._name, "retrieval_action": str(kwargs.get("retrieval_action", "initial")),
            "requested_top_k": top_k, "returned_chunk_count": len(chunks), "retrieval_call_count": self._calls * 2,
            "retrieval_calls": cast(int, lexical.metadata.get("retrieval_calls", 1)) + cast(int, vector.metadata.get("retrieval_calls", 1)),
            "retrieved_passages": len(lexical.chunks) + len(vector.chunks),
            "retrieval_latency_ms": (perf_counter()-started)*1000, "indexed_document_count": lexical.metadata["indexed_document_count"],
            "indexed_chunk_count": lexical.metadata["indexed_chunk_count"], "hop_count": kwargs.get("hop_count", 1),
            "fusion": {"lexical_weight": self._lexical_weight, "vector_weight": self._vector_weight},
        })
