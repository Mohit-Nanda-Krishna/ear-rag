"""Deterministic document chunking for local retrieval backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ear_rag.core.models import Document, RetrievedChunk


@dataclass(frozen=True, slots=True)
class DocumentChunker:
    """Split documents into overlapping character windows.

    Chunk IDs are stable for the same document identifier and text. The chunker
    deliberately performs no semantic analysis so that it is reproducible and
    can later be replaced or complemented by a semantic chunker.
    """

    chunk_size: int = 400
    chunk_overlap: int = 50

    def __post_init__(self) -> None:
        """Validate a chunking configuration that always makes progress."""
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size")

    def chunk_document(self, document: Document) -> list[RetrievedChunk]:
        """Return non-empty chunks for one document in source order."""
        chunks: list[RetrievedChunk] = []
        step = self.chunk_size - self.chunk_overlap
        start = 0
        chunk_index = 0

        while start < len(document.text):
            end = min(start + self.chunk_size, len(document.text))
            chunk_text = document.text[start:end].strip()
            if chunk_text:
                chunks.append(
                    RetrievedChunk(
                        chunk_id=f"{document.document_id}:chunk:{chunk_index}",
                        document_id=document.document_id,
                        text=chunk_text,
                        retrieval_score=0.0,
                        retriever_name="unindexed",
                        metadata={
                            "chunk_index": chunk_index,
                            "character_start": start,
                            "character_end": end,
                            "document_metadata": dict(document.metadata),
                        },
                    )
                )
                chunk_index += 1

            if end == len(document.text):
                break
            start += step

        return chunks

    def chunk_documents(self, documents: Iterable[Document]) -> list[RetrievedChunk]:
        """Return chunks for documents in the supplied order."""
        return [chunk for document in documents for chunk in self.chunk_document(document)]
