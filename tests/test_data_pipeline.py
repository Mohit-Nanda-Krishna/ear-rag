"""Tests for local dataset loading and persistent retrieval artifacts."""

from pathlib import Path

from ear_rag.config.loader import load_config
from ear_rag.core.models import Document, Query
from ear_rag.data import (
    DatasetAdapter,
    DocumentPreprocessor,
    LocalJsonlDatasetAdapter,
    RetrievalArtifactStore,
    RetrievalDataPipeline,
    SUPPORTED_DATASETS,
    adapter_from_config,
)
from ear_rag.retrieval import DocumentChunker, LocalLexicalRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = PROJECT_ROOT / "data" / "fixtures" / "tiny_retrieval.jsonl"


def _pipeline(tmp_path: Path, maximum_examples: int | None = None) -> RetrievalDataPipeline:
    adapter = LocalJsonlDatasetAdapter("fixture", "train", FIXTURE_PATH)
    return RetrievalDataPipeline(
        adapter=adapter,
        chunker=DocumentChunker(chunk_size=40, chunk_overlap=5),
        store=RetrievalArtifactStore(tmp_path / "processed", tmp_path / "indexes", "fixture-train-test"),
        subset="test",
        split="train",
        maximum_examples=maximum_examples,
    )


def test_fixture_adapter_loads_configured_subset_and_satisfies_contract() -> None:
    """The normal test path uses a tiny local fixture and no network access."""
    adapter = LocalJsonlDatasetAdapter("fixture", "train", FIXTURE_PATH)

    examples = adapter.load(maximum_examples=2)

    assert isinstance(adapter, DatasetAdapter)
    assert adapter.name == "fixture"
    assert {"natural_questions", "hotpotqa", "2wikimultihopqa"}.issubset(SUPPORTED_DATASETS)
    assert [example.example_id for example in examples] == ["fixture-1", "fixture-2"]
    assert examples[0].query.text.startswith("How do solar panels")
    assert examples[0].documents[0].metadata["title"] == "Solar energy"


def test_adapter_is_selected_from_repository_configuration() -> None:
    """Dataset selection remains configuration-driven rather than hard-coded."""
    adapter = adapter_from_config(load_config(), PROJECT_ROOT)

    assert adapter.name == "fixture"
    assert len(adapter.load(maximum_examples=1)) == 1


def test_preprocessing_is_deterministic_and_preserves_metadata() -> None:
    """Whitespace normalization is stable and retains source provenance."""
    preprocessor = DocumentPreprocessor()
    document = Document("doc", "  Solar\n panels\twork.  ", {"title": "Solar"})

    first = preprocessor.preprocess(document)
    second = preprocessor.preprocess(document)

    assert first == second
    assert first is not None
    assert first.text == "Solar panels work."
    assert first.metadata["title"] == "Solar"
    assert first.metadata["preprocessing"] == {"whitespace_normalized": True}


def test_pipeline_generates_chunks_and_persists_reloadable_artifacts(tmp_path: Path) -> None:
    """Prepared artifacts preserve examples, documents, chunks, and manifest metadata."""
    pipeline = _pipeline(tmp_path, maximum_examples=2)

    artifacts = pipeline.prepare()
    pipeline.persist(artifacts)
    reloaded = pipeline.reload()

    assert artifacts.manifest["example_count"] == 2
    assert artifacts.manifest["document_count"] == len(artifacts.documents)
    assert artifacts.manifest["chunk_count"] == len(artifacts.chunks)
    assert artifacts.chunks
    assert reloaded.documents == artifacts.documents
    assert reloaded.chunks == artifacts.chunks
    assert reloaded.examples[0].documents[0] == reloaded.documents[0]
    assert reloaded.documents[0].metadata["title"] == "Solar energy"
    assert (tmp_path / "processed" / "fixture-train-test" / "manifest.json").is_file()
    assert (tmp_path / "indexes" / "fixture-train-test" / "chunks.jsonl").is_file()
    chunks_path = tmp_path / "indexes" / "fixture-train-test" / "chunks.jsonl"
    first_bytes = chunks_path.read_bytes()
    pipeline.persist(artifacts)
    assert chunks_path.read_bytes() == first_bytes


def test_retrieval_can_resume_from_persisted_chunks(tmp_path: Path) -> None:
    """Reloaded chunk artifacts can be queried without rerunning chunking."""
    pipeline = _pipeline(tmp_path)
    pipeline.persist(pipeline.prepare())
    retriever = pipeline.load_retriever(
        LocalLexicalRetriever(DocumentChunker(chunk_size=1, chunk_overlap=0))
    )

    result = retriever.retrieve(Query("q", "solar electricity"), top_k=1)

    assert result.chunks[0].document_id == "solar-panels"
    assert result.metadata["indexed_chunk_count"] > 0
    assert result.metadata["indexed_document_count"] == 5


def test_pipeline_from_config_uses_chunking_and_persistence_settings(tmp_path: Path) -> None:
    """Configuration values remain portable when a project root is supplied."""
    config = load_config()
    config["data"] = {**config["data"], "maximum_examples": 1}
    config["data"]["paths"] = {
        **config["data"]["paths"],
        "processed": "processed",
        "indexes": "indexes",
        "fixture_file": "fixture.jsonl",
    }
    config["persistence"] = {
        **config["persistence"],
        "processed_path": "processed",
        "index_path": "indexes",
    }
    (tmp_path / "fixture.jsonl").write_text(FIXTURE_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    pipeline = RetrievalDataPipeline.from_config(config, tmp_path)
    artifacts = pipeline.prepare()

    assert artifacts.manifest["example_count"] == 1
    assert artifacts.manifest["chunking"] == {"size": 400, "overlap": 50}
