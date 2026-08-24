"""A lightweight deterministic lexical retriever for EAR-RAG."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from math import log
import re
from time import perf_counter
from typing import Self

from ear_rag.core.models import Document, Query, RetrievedChunk, RetrievalResult

from .chunking import DocumentChunker


_TOKEN_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)


class LocalLexicalRetriever:
    """In-memory BM25-inspired lexical retrieval over deterministic chunks.

    Calling :meth:`index` replaces the current corpus, which keeps experiments
    reproducible and prevents hidden state from previous runs. The class has no
    external service or model dependency.
    """

    def __init__(
        self,
        chunker: DocumentChunker | None = None,
        *,
        name: str = "local_lexical",
        max_top_k: int | None = None,
    ) -> None:
        if not name:
            raise ValueError("name must not be empty")
        if max_top_k is not None and max_top_k <= 0:
            raise ValueError("max_top_k must be greater than zero when provided")

        self._chunker = chunker or DocumentChunker()
        self._name = name
        self._max_top_k = max_top_k
        self._chunks: list[RetrievedChunk] = []
        self._term_frequencies: list[Counter[str]] = []
        self._document_frequencies: Counter[str] = Counter()
        self._average_chunk_length = 0.0
        self._indexed_document_count = 0
        self._retrieval_call_count = 0

    @property
    def name(self) -> str:
        """Return the stable name recorded in retrieval results."""
        return self._name

    @classmethod
    def from_config(cls, config: Mapping[str, object]) -> Self:
        """Create a retriever from the portable ``retrieval`` configuration section."""
        retrieval_config = config.get("retrieval")
        if not isinstance(retrieval_config, Mapping):
            raise ValueError("retrieval configuration must be a mapping")

        chunking_config = config.get("chunking", retrieval_config)
        if not isinstance(chunking_config, Mapping):
            raise ValueError("chunking configuration must be a mapping")
        chunk_size = chunking_config.get("size", retrieval_config.get("chunk_size"))
        chunk_overlap = chunking_config.get("overlap", retrieval_config.get("chunk_overlap"))
        max_top_k = retrieval_config.get("max_top_k")
        backend_name = retrieval_config.get("backend")
        if (
            not isinstance(chunk_size, int)
            or isinstance(chunk_size, bool)
            or not isinstance(chunk_overlap, int)
            or isinstance(chunk_overlap, bool)
            or not isinstance(max_top_k, int)
            or isinstance(max_top_k, bool)
            or not isinstance(backend_name, str)
        ):
            raise ValueError("retrieval configuration has invalid local backend values")

        return cls(
            chunker=DocumentChunker(chunk_size, chunk_overlap),
            name=backend_name,
            max_top_k=max_top_k,
        )

    def index(self, documents: Sequence[Document]) -> None:
        """Chunk and replace the in-memory corpus with ``documents``."""
        document_ids = [document.document_id for document in documents]
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("document identifiers must be unique within an index")

        self.index_chunks(
            self._chunker.chunk_documents(documents), document_count=len(documents)
        )

    def index_chunks(
        self,
        chunks: Sequence[RetrievedChunk],
        *,
        document_count: int,
    ) -> None:
        """Replace the index from persisted chunks without re-chunking documents."""
        if document_count < 0:
            raise ValueError("document_count must be non-negative")
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError("chunk identifiers must be unique within an index")

        chunks = list(chunks)
        term_frequencies = [Counter(self._tokenize(chunk.text)) for chunk in chunks]
        document_frequencies: Counter[str] = Counter()
        for frequencies in term_frequencies:
            document_frequencies.update(frequencies.keys())

        self._chunks = chunks
        self._term_frequencies = term_frequencies
        self._document_frequencies = document_frequencies
        self._average_chunk_length = (
            sum(sum(frequencies.values()) for frequencies in term_frequencies)
            / len(term_frequencies)
            if term_frequencies
            else 0.0
        )
        self._indexed_document_count = document_count
        self._retrieval_call_count = 0

    def retrieve(
        self,
        query: Query,
        top_k: int,
        **kwargs: object,
    ) -> RetrievalResult:
        """Return deterministic ranked chunks for a query.

        Additional keyword arguments are accepted for compatibility with the
        retrieval protocol but intentionally unused by this local backend.
        """
        retrieval_action = str(kwargs.get("retrieval_action", "initial"))
        hop_count = kwargs.get("hop_count", 1)
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")
        if self._max_top_k is not None and top_k > self._max_top_k:
            raise ValueError(f"top_k must not exceed configured maximum of {self._max_top_k}")

        started_at = perf_counter()
        query_terms = self._tokenize(query.text)
        ranked = self._rank(query_terms)[:top_k] if query_terms else []
        self._retrieval_call_count += 1
        latency_ms = (perf_counter() - started_at) * 1_000

        result_chunks = [
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                retrieval_score=score,
                retriever_name=self._name,
                metadata=dict(chunk.metadata),
            )
            for score, chunk in ranked
        ]
        return RetrievalResult(
            query_id=query.query_id,
            chunks=result_chunks,
            retriever_name=self._name,
            top_k=top_k,
            metadata={
                "retriever_name": self._name,
                "backend_name": self._name,
                "retrieval_action": retrieval_action,
                "requested_top_k": top_k,
                "returned_chunk_count": len(result_chunks),
                "retrieval_call_count": self._retrieval_call_count,
                "retrieval_latency_ms": latency_ms,
                "indexed_document_count": self._indexed_document_count,
                "indexed_chunk_count": len(self._chunks),
                "hop_count": hop_count,
            },
        )

    def _rank(self, query_terms: list[str]) -> list[tuple[float, RetrievedChunk]]:
        """Score chunks with a deterministic BM25-inspired lexical function."""
        corpus_size = len(self._chunks)
        if corpus_size == 0 or self._average_chunk_length == 0:
            return []

        query_frequencies = Counter(query_terms)
        scored_chunks: list[tuple[float, RetrievedChunk]] = []
        for chunk, term_frequencies in zip(self._chunks, self._term_frequencies):
            chunk_length = sum(term_frequencies.values())
            score = 0.0
            for term, query_frequency in query_frequencies.items():
                term_frequency = term_frequencies.get(term, 0)
                if term_frequency == 0:
                    continue
                document_frequency = self._document_frequencies[term]
                inverse_document_frequency = log(
                    1.0 + (corpus_size - document_frequency + 0.5) / (document_frequency + 0.5)
                )
                normalized_term_frequency = term_frequency * 2.5 / (
                    term_frequency + 1.5 * (1.0 - 0.75 + 0.75 * chunk_length / self._average_chunk_length)
                )
                score += query_frequency * inverse_document_frequency * normalized_term_frequency
            if score > 0.0:
                scored_chunks.append((score, chunk))

        return sorted(
            scored_chunks,
            key=lambda item: (-item[0], item[1].document_id, item[1].chunk_id),
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Normalize text into deterministic lexical tokens."""
        return _TOKEN_PATTERN.findall(text.lower())
