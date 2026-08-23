"""Local, normalized dataset adapters for reproducible EAR-RAG experiments."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Protocol, runtime_checkable

from ear_rag.core.models import Document, Metadata, Query


SUPPORTED_DATASETS = frozenset({"fixture", "natural_questions", "hotpotqa", "2wikimultihopqa"})


@dataclass(frozen=True, slots=True)
class DatasetExample:
    """A query, its local supporting documents, and an optional reference answer."""

    example_id: str
    query: Query
    documents: tuple[Document, ...]
    answer: str | None = None
    metadata: Metadata = field(default_factory=dict)


@runtime_checkable
class DatasetAdapter(Protocol):
    """Contract for local dataset adapters used by the data pipeline."""

    @property
    def name(self) -> str:
        """Return the configured dataset identifier."""
        ...

    def load(self, maximum_examples: int | None = None) -> list[DatasetExample]:
        """Load a deterministic development subset without network access."""
        ...


class LocalJsonlDatasetAdapter:
    """Load a normalized JSONL dataset stored locally.

    Each line must contain ``example_id``, ``question``, and ``contexts``. A
    context contains ``document_id`` and ``text`` and may carry ``metadata``.
    This compact interchange format is intentionally shared by local fixtures
    and future adapters that normalize Natural Questions, HotpotQA, or 2Wiki.
    """

    def __init__(self, dataset_name: str, split: str, source_path: Path) -> None:
        if dataset_name not in SUPPORTED_DATASETS:
            raise ValueError(f"Unsupported dataset: {dataset_name}")
        self._dataset_name = dataset_name
        self._split = split
        self._source_path = source_path

    @property
    def name(self) -> str:
        """Return the configured dataset identifier."""
        return self._dataset_name

    def load(self, maximum_examples: int | None = None) -> list[DatasetExample]:
        """Load up to ``maximum_examples`` records in source-file order."""
        if maximum_examples is not None and maximum_examples < 0:
            raise ValueError("maximum_examples must be non-negative")
        if not self._source_path.is_file():
            raise FileNotFoundError(f"Dataset file not found: {self._source_path}")

        examples: list[DatasetExample] = []
        with self._source_path.open("r", encoding="utf-8") as source_file:
            for line_number, line in enumerate(source_file, start=1):
                if not line.strip():
                    continue
                examples.append(self._parse_record(json.loads(line), line_number))
                if maximum_examples is not None and len(examples) >= maximum_examples:
                    break
        return examples

    def _parse_record(self, record: object, line_number: int) -> DatasetExample:
        """Convert one normalized JSON record into existing core contracts."""
        if not isinstance(record, dict):
            raise ValueError(f"Dataset record at line {line_number} must be an object")

        example_id = record.get("example_id")
        question = record.get("question")
        contexts = record.get("contexts")
        answer = record.get("answer")
        metadata = record.get("metadata", {})
        if not isinstance(example_id, str) or not example_id:
            raise ValueError(f"Dataset record at line {line_number} has no example_id")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Dataset record at line {line_number} has no question")
        if not isinstance(contexts, list):
            raise ValueError(f"Dataset record at line {line_number} has no contexts list")
        if answer is not None and not isinstance(answer, str):
            raise ValueError(f"Dataset record at line {line_number} has an invalid answer")
        if not isinstance(metadata, dict):
            raise ValueError(f"Dataset record at line {line_number} has invalid metadata")

        documents = tuple(
            self._parse_context(context, example_id, context_index, line_number)
            for context_index, context in enumerate(contexts)
        )
        shared_metadata: Metadata = {
            **metadata,
            "dataset": self._dataset_name,
            "split": self._split,
            "example_id": example_id,
        }
        return DatasetExample(
            example_id=example_id,
            query=Query(query_id=example_id, text=question, metadata=dict(shared_metadata)),
            documents=documents,
            answer=answer,
            metadata=shared_metadata,
        )

    def _parse_context(
        self,
        context: object,
        example_id: str,
        context_index: int,
        line_number: int,
    ) -> Document:
        """Convert one context object into a document with provenance metadata."""
        if not isinstance(context, dict):
            raise ValueError(f"Context at line {line_number} must be an object")
        document_id = context.get("document_id", f"{example_id}:context:{context_index}")
        text = context.get("text")
        metadata = context.get("metadata", {})
        if not isinstance(document_id, str) or not document_id:
            raise ValueError(f"Context at line {line_number} has an invalid document_id")
        if not isinstance(text, str):
            raise ValueError(f"Context at line {line_number} has invalid text")
        if not isinstance(metadata, dict):
            raise ValueError(f"Context at line {line_number} has invalid metadata")
        return Document(
            document_id=document_id,
            text=text,
            metadata={
                **metadata,
                "dataset": self._dataset_name,
                "split": self._split,
            },
        )


def adapter_from_config(
    config: Mapping[str, object], project_root: Path
) -> LocalJsonlDatasetAdapter:
    """Build a local adapter from repository-relative data configuration."""
    data_config = config.get("data")
    if not isinstance(data_config, Mapping):
        raise ValueError("data configuration must be a mapping")
    dataset_name = data_config.get("dataset")
    split = data_config.get("split")
    paths = data_config.get("paths")
    if not isinstance(dataset_name, str) or not isinstance(split, str) or not isinstance(paths, Mapping):
        raise ValueError("data configuration has invalid dataset, split, or paths values")

    if dataset_name == "fixture":
        fixture_file = paths.get("fixture_file")
        if not isinstance(fixture_file, str):
            raise ValueError("fixture data configuration requires paths.fixture_file")
        source_path = _repository_path(project_root, fixture_file)
    else:
        raw_directory = paths.get("raw")
        if not isinstance(raw_directory, str):
            raise ValueError("dataset data configuration requires paths.raw")
        source_path = _repository_path(project_root, raw_directory) / f"{dataset_name}_{split}.jsonl"

    return LocalJsonlDatasetAdapter(dataset_name, split, source_path)


def _repository_path(project_root: Path, configured_path: str) -> Path:
    """Resolve a configured path only when it remains repository-relative."""
    path = Path(configured_path)
    if path.is_absolute():
        raise ValueError("dataset paths must be repository-relative")
    return project_root / path
