"""Deterministic local persistence for processed retrieval artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from ear_rag.core.models import Document, Query, RetrievedChunk

from .datasets import DatasetExample


ARTIFACT_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class RetrievalArtifacts:
    """Reloadable local records required to resume lexical retrieval."""

    examples: tuple[DatasetExample, ...]
    documents: tuple[Document, ...]
    chunks: tuple[RetrievedChunk, ...]
    manifest: dict[str, object]


class RetrievalArtifactStore:
    """Persist processed records and chunk-index artifacts in separate roots."""

    def __init__(self, processed_root: Path, index_root: Path, artifact_name: str) -> None:
        if not artifact_name or Path(artifact_name).name != artifact_name:
            raise ValueError("artifact_name must be a single directory name")
        self._processed_directory = processed_root / artifact_name
        self._index_directory = index_root / artifact_name

    def save(self, artifacts: RetrievalArtifacts) -> None:
        """Write stable JSONL/JSON artifacts that can be reloaded in another run."""
        self._processed_directory.mkdir(parents=True, exist_ok=True)
        self._index_directory.mkdir(parents=True, exist_ok=True)
        self._write_jsonl(
            self._processed_directory / "examples.jsonl",
            (_example_to_record(example) for example in artifacts.examples),
        )
        self._write_jsonl(
            self._processed_directory / "documents.jsonl",
            (_document_to_record(document) for document in artifacts.documents),
        )
        self._write_jsonl(
            self._index_directory / "chunks.jsonl",
            (_chunk_to_record(chunk) for chunk in artifacts.chunks),
        )
        self._write_json(self._processed_directory / "manifest.json", artifacts.manifest)
        self._write_json(self._index_directory / "manifest.json", artifacts.manifest)

    def load(self) -> RetrievalArtifacts:
        """Reload processed examples, documents, chunks, and their shared manifest."""
        manifest = self._read_json(self._processed_directory / "manifest.json")
        index_manifest = self._read_json(self._index_directory / "manifest.json")
        if manifest != index_manifest:
            raise ValueError("processed and index manifests do not match")
        if manifest.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
            raise ValueError("unsupported retrieval artifact schema version")

        documents = tuple(
            _document_from_record(record)
            for record in self._read_jsonl(self._processed_directory / "documents.jsonl")
        )
        documents_by_id = {document.document_id: document for document in documents}
        examples = tuple(
            _example_from_record(record, documents_by_id)
            for record in self._read_jsonl(self._processed_directory / "examples.jsonl")
        )
        chunks = tuple(
            _chunk_from_record(record)
            for record in self._read_jsonl(self._index_directory / "chunks.jsonl")
        )
        return RetrievalArtifacts(examples, documents, chunks, manifest)

    @staticmethod
    def _write_jsonl(path: Path, records: object) -> None:
        with path.open("w", encoding="utf-8", newline="\n") as output_file:
            for record in records:
                output_file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
                output_file.write("\n")

    @staticmethod
    def _write_json(path: Path, record: dict[str, object]) -> None:
        with path.open("w", encoding="utf-8", newline="\n") as output_file:
            json.dump(record, output_file, ensure_ascii=False, indent=2, sort_keys=True)
            output_file.write("\n")

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, object]]:
        if not path.is_file():
            raise FileNotFoundError(f"Retrieval artifact not found: {path}")
        with path.open("r", encoding="utf-8") as input_file:
            return [json.loads(line) for line in input_file if line.strip()]

    @staticmethod
    def _read_json(path: Path) -> dict[str, object]:
        if not path.is_file():
            raise FileNotFoundError(f"Retrieval artifact not found: {path}")
        with path.open("r", encoding="utf-8") as input_file:
            record = json.load(input_file)
        if not isinstance(record, dict):
            raise ValueError(f"Retrieval artifact must be an object: {path}")
        return record


def _document_to_record(document: Document) -> dict[str, object]:
    return {"document_id": document.document_id, "text": document.text, "metadata": document.metadata}


def _document_from_record(record: dict[str, object]) -> Document:
    return Document(
        document_id=_required_string(record, "document_id"),
        text=_required_string(record, "text"),
        metadata=_metadata(record, "metadata"),
    )


def _chunk_to_record(chunk: RetrievedChunk) -> dict[str, object]:
    return {
        "chunk_id": chunk.chunk_id,
        "document_id": chunk.document_id,
        "text": chunk.text,
        "retrieval_score": chunk.retrieval_score,
        "retriever_name": chunk.retriever_name,
        "metadata": chunk.metadata,
    }


def _chunk_from_record(record: dict[str, object]) -> RetrievedChunk:
    score = record.get("retrieval_score")
    if not isinstance(score, (float, int)) or isinstance(score, bool):
        raise ValueError("chunk retrieval_score must be numeric")
    return RetrievedChunk(
        chunk_id=_required_string(record, "chunk_id"),
        document_id=_required_string(record, "document_id"),
        text=_required_string(record, "text"),
        retrieval_score=float(score),
        retriever_name=_required_string(record, "retriever_name"),
        metadata=_metadata(record, "metadata"),
    )


def _example_to_record(example: DatasetExample) -> dict[str, object]:
    return {
        "example_id": example.example_id,
        "query": {
            "query_id": example.query.query_id,
            "text": example.query.text,
            "metadata": example.query.metadata,
        },
        "document_ids": [document.document_id for document in example.documents],
        "answer": example.answer,
        "metadata": example.metadata,
    }


def _example_from_record(
    record: dict[str, object], documents_by_id: dict[str, Document]
) -> DatasetExample:
    query_record = record.get("query")
    document_ids = record.get("document_ids")
    answer = record.get("answer")
    if not isinstance(query_record, dict) or not isinstance(document_ids, list):
        raise ValueError("example artifact has invalid query or document_ids")
    if answer is not None and not isinstance(answer, str):
        raise ValueError("example artifact has invalid answer")
    resolved_document_ids = [document_id for document_id in document_ids if isinstance(document_id, str)]
    if len(resolved_document_ids) != len(document_ids):
        raise ValueError("example artifact document_ids must contain only strings")
    try:
        documents = tuple(documents_by_id[document_id] for document_id in resolved_document_ids)
    except KeyError as error:
        raise ValueError(f"example artifact references missing document: {error.args[0]}") from error
    return DatasetExample(
        example_id=_required_string(record, "example_id"),
        query=Query(
            query_id=_required_string(query_record, "query_id"),
            text=_required_string(query_record, "text"),
            metadata=_metadata(query_record, "metadata"),
        ),
        documents=documents,
        answer=answer,
        metadata=_metadata(record, "metadata"),
    )


def _required_string(record: dict[str, object], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str):
        raise ValueError(f"artifact field {key} must be a string")
    return value


def _metadata(record: dict[str, object], key: str) -> dict[str, object]:
    value = record.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"artifact field {key} must be an object")
    return value
