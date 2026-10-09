"""Bounded, deterministic multi-hop evidence aggregation."""
from __future__ import annotations
from time import perf_counter
from typing import cast
from ear_rag.core.interfaces import Retriever
from ear_rag.core.models import Query, RetrievedChunk, RetrievalResult
from .local import LocalLexicalRetriever

class MultiHopRetriever:
    def __init__(self, retriever: Retriever, *, max_hops: int = 2, name: str = "multihop") -> None:
        if max_hops < 1: raise ValueError("max_hops must be at least one")
        self._retriever, self._max_hops, self._name, self._calls = retriever, max_hops, name, 0
    @property
    def name(self) -> str: return self._name
    def retrieve(self, query: Query, top_k: int, **kwargs: object) -> RetrievalResult:
        started = perf_counter(); current = query; evidence: dict[str, RetrievedChunk] = {}; source_results = []
        for hop in range(1, self._max_hops + 1):
            result = self._retriever.retrieve(current, top_k, retrieval_action=kwargs.get("retrieval_action", "initial"), hop_count=hop)
            source_results.append(result)
            for chunk in result.chunks: evidence.setdefault(chunk.chunk_id, chunk)
            if not result.chunks: break
            terms = LocalLexicalRetriever._tokenize(result.chunks[0].text)[:8]
            current = Query(query.query_id, query.text + " " + " ".join(terms), dict(query.metadata))
        self._calls += 1; ranked = list(evidence.values())[:top_k]
        return RetrievalResult(query.query_id, ranked, self._name, top_k, {
            "retriever_name": self._name, "backend_name": self._name, "retrieval_action": str(kwargs.get("retrieval_action", "initial")),
            "requested_top_k": top_k, "returned_chunk_count": len(ranked), "retrieval_call_count": len(source_results),
            "retrieval_calls": sum(cast(int, item.metadata.get("retrieval_calls", 1)) for item in source_results),
            "retrieved_passages": sum(len(item.chunks) for item in source_results),
            "retrieval_latency_ms": (perf_counter()-started)*1000, "indexed_document_count": source_results[0].metadata.get("indexed_document_count", 0) if source_results else 0,
            "indexed_chunk_count": source_results[0].metadata.get("indexed_chunk_count", 0) if source_results else 0,
            "hop_count": len(source_results), "max_hops": self._max_hops,
        })
