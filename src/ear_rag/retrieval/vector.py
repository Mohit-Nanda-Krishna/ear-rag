"""Dependency-free deterministic flat vector retrieval for architecture tests."""

from __future__ import annotations

from collections.abc import Sequence
from math import sqrt
from time import perf_counter

from ear_rag.core.models import Document, Query, RetrievedChunk, RetrievalResult

from .chunking import DocumentChunker
from .local import LocalLexicalRetriever


class DeterministicVectorRetriever:
    """Flat cosine search using stable hashed token vectors.

    This deliberately stands in for an embedding encoder: it is reproducible,
    requires no model download, and can later be replaced behind this contract.
    """

    def __init__(self, chunker: DocumentChunker | None = None, *, name: str = "vector_flat",
                 dimensions: int = 64, max_top_k: int | None = None) -> None:
        if dimensions <= 0 or max_top_k is not None and max_top_k <= 0:
            raise ValueError("dimensions and max_top_k must be positive")
        self._chunker, self._name = chunker or DocumentChunker(), name
        self._dimensions, self._max_top_k = dimensions, max_top_k
        self._chunks: list[RetrievedChunk] = []
        self._vectors: list[list[float]] = []
        self._indexed_document_count = self._retrieval_call_count = 0

    @property
    def name(self) -> str:
        return self._name

    def index(self, documents: Sequence[Document]) -> None:
        self.index_chunks(self._chunker.chunk_documents(documents), document_count=len(documents))

    def index_chunks(self, chunks: Sequence[RetrievedChunk], *, document_count: int) -> None:
        self._chunks = list(chunks)
        self._vectors = [self._encode(chunk.text) for chunk in self._chunks]
        self._indexed_document_count, self._retrieval_call_count = document_count, 0

    def retrieve(self, query: Query, top_k: int, **kwargs: object) -> RetrievalResult:
        if top_k <= 0 or self._max_top_k is not None and top_k > self._max_top_k:
            raise ValueError("top_k is outside configured bounds")
        started = perf_counter(); query_vector = self._encode(query.text)
        ranked = sorted(
            ((self._cosine(query_vector, vector), chunk) for chunk, vector in zip(self._chunks, self._vectors)),
            key=lambda item: (-item[0], item[1].document_id, item[1].chunk_id),
        )[:top_k]
        self._retrieval_call_count += 1
        chunks = [RetrievedChunk(chunk.chunk_id, chunk.document_id, chunk.text, score, self._name, dict(chunk.metadata))
                  for score, chunk in ranked if score > 0.0]
        return RetrievalResult(query.query_id, chunks, self._name, top_k, {
            "retriever_name": self._name, "backend_name": self._name,
            "retrieval_action": str(kwargs.get("retrieval_action", "initial")),
            "requested_top_k": top_k, "returned_chunk_count": len(chunks),
            "retrieval_call_count": self._retrieval_call_count,
            "retrieval_latency_ms": (perf_counter() - started) * 1000,
            "indexed_document_count": self._indexed_document_count,
            "indexed_chunk_count": len(self._chunks), "hop_count": kwargs.get("hop_count", 1),
            "encoder": "deterministic_hashed_tokens",
        })

    def _encode(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        for token in LocalLexicalRetriever._tokenize(text):
            # Stable, process-independent token hash (unlike Python hash()).
            value = sum((position + 1) * ord(char) for position, char in enumerate(token))
            vector[value % self._dimensions] += 1.0 if value % 2 else -1.0
        norm = sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector

    @staticmethod
    def _cosine(first: list[float], second: list[float]) -> float:
        return sum(left * right for left, right in zip(first, second))
