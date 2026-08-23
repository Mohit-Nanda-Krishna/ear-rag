"""Tests for deterministic local document chunking and retrieval."""

from ear_rag.config.loader import load_config
from ear_rag.core.interfaces import Retriever
from ear_rag.core.models import Document, Query
from ear_rag.retrieval import DocumentChunker, LocalLexicalRetriever


def test_chunking_assigns_deterministic_ids_and_preserves_metadata() -> None:
    """Chunk IDs and source metadata are stable across equivalent calls."""
    document = Document(
        document_id="doc-1",
        text="abcdefghij",
        metadata={"title": "Alphabet"},
    )
    chunker = DocumentChunker(chunk_size=4, chunk_overlap=1)

    first = chunker.chunk_document(document)
    second = chunker.chunk_document(document)

    assert [chunk.chunk_id for chunk in first] == [
        "doc-1:chunk:0",
        "doc-1:chunk:1",
        "doc-1:chunk:2",
    ]
    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
    assert [chunk.text for chunk in first] == ["abcd", "defg", "ghij"]
    assert first[1].metadata["character_start"] == 3
    assert first[0].metadata["document_metadata"] == {"title": "Alphabet"}


def test_chunking_handles_short_and_empty_documents() -> None:
    """Short documents yield one chunk and whitespace-only documents yield none."""
    chunker = DocumentChunker(chunk_size=10, chunk_overlap=2)

    short_chunks = chunker.chunk_document(Document(document_id="short", text="brief"))
    empty_chunks = chunker.chunk_document(Document(document_id="empty", text="  \n\t  "))

    assert len(short_chunks) == 1
    assert short_chunks[0].chunk_id == "short:chunk:0"
    assert empty_chunks == []


def test_chunker_rejects_non_progressing_configuration() -> None:
    """Overlap must leave a positive step between chunk starts."""
    try:
        DocumentChunker(chunk_size=4, chunk_overlap=4)
    except ValueError as error:
        assert "chunk_overlap" in str(error)
    else:
        raise AssertionError("invalid chunk configuration was accepted")


def test_local_retrieval_ranks_relevant_chunks_and_respects_top_k() -> None:
    """A relevant in-memory document ranks above unrelated content."""
    retriever = LocalLexicalRetriever(DocumentChunker(chunk_size=100, chunk_overlap=0))
    retriever.index(
        [
            Document(
                "solar",
                "Solar electricity systems generate electricity from solar energy.",
            ),
            Document("ocean", "Ocean currents influence coastal weather."),
            Document("solar-storage", "Solar battery storage retains electricity."),
        ]
    )

    result = retriever.retrieve(Query("q1", "solar electricity"), top_k=2)

    assert result.query_id == "q1"
    assert result.retriever_name == "local_lexical"
    assert len(result.chunks) == 2
    assert result.chunks[0].document_id == "solar"
    assert result.chunks[0].retrieval_score >= result.chunks[1].retrieval_score
    assert all(chunk.retriever_name == "local_lexical" for chunk in result.chunks)


def test_retrieval_scores_and_metadata_are_deterministic() -> None:
    """Repeated retrieval preserves ranking and scores while tracking call cost."""
    retriever = LocalLexicalRetriever(DocumentChunker(chunk_size=100, chunk_overlap=0))
    retriever.index(
        [
            Document("a", "Cats chase mice."),
            Document("b", "Dogs chase balls."),
        ]
    )
    query = Query("q2", "cats chase")

    first = retriever.retrieve(query, top_k=2)
    second = retriever.retrieve(query, top_k=2)

    assert [(chunk.chunk_id, chunk.retrieval_score) for chunk in first.chunks] == [
        (chunk.chunk_id, chunk.retrieval_score) for chunk in second.chunks
    ]
    assert first.metadata["requested_top_k"] == 2
    assert first.metadata["returned_chunk_count"] == len(first.chunks)
    assert first.metadata["indexed_document_count"] == 2
    assert first.metadata["indexed_chunk_count"] == 2
    assert first.metadata["retrieval_call_count"] == 1
    assert second.metadata["retrieval_call_count"] == 2
    assert first.metadata["retrieval_latency_ms"] >= 0.0


def test_retriever_uses_retrieval_configuration_and_satisfies_protocol() -> None:
    """The configured local backend remains a concrete Retriever implementation."""
    retriever = LocalLexicalRetriever.from_config(load_config())

    assert retriever.name == "local_lexical"
    assert isinstance(retriever, Retriever)


def test_document_to_chunk_to_retrieval_smoke_flow() -> None:
    """Exercise the deterministic Document -> Chunk -> Index -> Retrieval flow."""
    retriever = LocalLexicalRetriever(DocumentChunker(chunk_size=12, chunk_overlap=2))
    retriever.index(
        [
            Document("history", "Ada Lovelace wrote notes about computing machines."),
            Document("botany", "Fern spores grow in moist environments."),
        ]
    )

    result = retriever.retrieve(Query("q3", "Lovelace computing"), top_k=1)

    assert len(result.chunks) == 1
    assert result.chunks[0].document_id == "history"
    assert result.chunks[0].metadata["chunk_index"] >= 0
