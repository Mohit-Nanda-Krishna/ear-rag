"""Local retrieval building blocks for EAR-RAG."""

from .chunking import DocumentChunker
from .local import LocalLexicalRetriever

__all__ = ["DocumentChunker", "LocalLexicalRetriever"]
