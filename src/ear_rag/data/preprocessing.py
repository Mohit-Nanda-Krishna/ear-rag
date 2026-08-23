"""Deterministic document preprocessing for local retrieval datasets."""

from __future__ import annotations

from collections.abc import Iterable

from ear_rag.core.models import Document


class DocumentPreprocessor:
    """Normalize whitespace while preserving document identity and metadata."""

    def preprocess(self, document: Document) -> Document | None:
        """Return a normalized document, or ``None`` when it has no text."""
        normalized_text = " ".join(document.text.split())
        if not normalized_text:
            return None
        return Document(
            document_id=document.document_id,
            text=normalized_text,
            metadata={
                **document.metadata,
                "preprocessing": {"whitespace_normalized": True},
            },
        )

    def preprocess_documents(self, documents: Iterable[Document]) -> list[Document]:
        """Normalize, deduplicate, and preserve source order for documents."""
        processed_documents: list[Document] = []
        by_document_id: dict[str, Document] = {}
        for document in documents:
            processed = self.preprocess(document)
            if processed is None:
                continue
            existing = by_document_id.get(processed.document_id)
            if existing is None:
                by_document_id[processed.document_id] = processed
                processed_documents.append(processed)
            elif existing != processed:
                raise ValueError(
                    f"Conflicting text or metadata for document ID: {processed.document_id}"
                )
        return processed_documents
