"""Dataset-to-persistent-retrieval pipeline for local experiments."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Self

from ear_rag.core.models import Document
from ear_rag.retrieval import DocumentChunker, LocalLexicalRetriever

from .datasets import DatasetAdapter, DatasetExample, adapter_from_config
from .persistence import ARTIFACT_SCHEMA_VERSION, RetrievalArtifactStore, RetrievalArtifacts
from .preprocessing import DocumentPreprocessor


class RetrievalDataPipeline:
    """Prepare, persist, reload, and re-index deterministic local dataset artifacts."""

    def __init__(
        self,
        adapter: DatasetAdapter,
        chunker: DocumentChunker,
        store: RetrievalArtifactStore,
        preprocessor: DocumentPreprocessor | None = None,
        *,
        subset: str,
        split: str,
        maximum_examples: int | None,
    ) -> None:
        self._adapter = adapter
        self._chunker = chunker
        self._store = store
        self._preprocessor = preprocessor or DocumentPreprocessor()
        self._subset = subset
        self._split = split
        self._maximum_examples = maximum_examples

    @classmethod
    def from_config(cls, config: Mapping[str, object], project_root: Path) -> Self:
        """Construct a pipeline from portable repository configuration."""
        data_config = _mapping(config, "data")
        chunking_config = _mapping(config, "chunking")
        persistence_config = _mapping(config, "persistence")
        paths = _mapping(data_config, "paths")
        dataset_name = _string(data_config, "dataset")
        subset = _string(data_config, "subset")
        split = _string(data_config, "split")
        maximum_examples = _optional_non_negative_int(data_config, "maximum_examples")
        chunk_size = _positive_int(chunking_config, "size")
        chunk_overlap = _non_negative_int(chunking_config, "overlap")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunking overlap must be smaller than size")
        if persistence_config.get("enabled") is not True:
            raise ValueError("persistence must be enabled for the persistent data pipeline")

        processed_path = _repository_path(project_root, _string(persistence_config, "processed_path"))
        index_path = _repository_path(project_root, _string(persistence_config, "index_path"))
        if paths.get("processed") != persistence_config.get("processed_path"):
            raise ValueError("data.paths.processed must match persistence.processed_path")
        if paths.get("indexes") != persistence_config.get("index_path"):
            raise ValueError("data.paths.indexes must match persistence.index_path")

        artifact_name = f"{dataset_name}-{split}-{subset}"
        return cls(
            adapter=adapter_from_config(config, project_root),
            chunker=DocumentChunker(chunk_size, chunk_overlap),
            store=RetrievalArtifactStore(processed_path, index_path, artifact_name),
            subset=subset,
            split=split,
            maximum_examples=maximum_examples,
        )

    def prepare(self) -> RetrievalArtifacts:
        """Load, preprocess, chunk, and describe the configured local subset."""
        examples = tuple(self._adapter.load(self._maximum_examples))
        documents = tuple(self._preprocess_examples(examples))
        chunks = tuple(self._chunker.chunk_documents(documents))
        manifest: dict[str, object] = {
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "dataset": self._adapter.name,
            "subset": self._subset,
            "split": self._split,
            "example_count": len(examples),
            "document_count": len(documents),
            "chunk_count": len(chunks),
            "chunking": {
                "size": self._chunker.chunk_size,
                "overlap": self._chunker.chunk_overlap,
            },
        }
        return RetrievalArtifacts(examples, documents, chunks, manifest)

    def persist(self, artifacts: RetrievalArtifacts) -> None:
        """Save prepared documents and chunk-index artifacts locally."""
        self._store.save(artifacts)

    def reload(self) -> RetrievalArtifacts:
        """Reload previously persisted artifacts without re-chunking documents."""
        return self._store.load()

    def load_retriever(self, retriever: LocalLexicalRetriever) -> LocalLexicalRetriever:
        """Populate an existing local retriever from persisted chunk artifacts."""
        artifacts = self.reload()
        retriever.index_chunks(artifacts.chunks, document_count=len(artifacts.documents))
        return retriever

    def _preprocess_examples(self, examples: tuple[DatasetExample, ...]) -> list[Document]:
        documents = (document for example in examples for document in example.documents)
        return self._preprocessor.preprocess_documents(documents)


def _mapping(config: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = config.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"configuration section {key} must be a mapping")
    return value


def _string(config: Mapping[str, object], key: str) -> str:
    value = config.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"configuration value {key} must be a non-empty string")
    return value


def _positive_int(config: Mapping[str, object], key: str) -> int:
    value = config.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"configuration value {key} must be a positive integer")
    return value


def _non_negative_int(config: Mapping[str, object], key: str) -> int:
    value = config.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"configuration value {key} must be a non-negative integer")
    return value


def _optional_non_negative_int(config: Mapping[str, object], key: str) -> int | None:
    value = config.get(key)
    if value is None:
        return None
    return _non_negative_int(config, key)


def _repository_path(project_root: Path, configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        raise ValueError("pipeline paths must be repository-relative")
    return project_root / path
