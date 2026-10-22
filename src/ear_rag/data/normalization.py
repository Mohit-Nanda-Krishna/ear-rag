"""Deterministic, retriever-safe normalization for local research datasets."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


@dataclass(frozen=True, slots=True)
class NormalizedDocument:
    """Retriever-safe title-level document with sentence provenance."""

    doc_id: str
    title: str
    text: str
    dataset: str
    source_example_id: str
    context_position: int
    sentence_offsets: tuple[tuple[int, int], ...]

    def corpus_record(self) -> dict[str, object]:
        """Return only fields that may be passed to a retriever."""
        return {
            "doc_id": self.doc_id, "title": self.title, "text": self.text,
            "dataset": self.dataset, "source_example_id": self.source_example_id,
            "context_position": self.context_position,
            "sentence_offsets": [{"start": start, "end": end} for start, end in self.sentence_offsets],
        }


@dataclass(frozen=True, slots=True)
class NormalizedExample:
    """Normalized query plus documents and evaluation-only supervision."""

    example_id: str
    dataset: str
    question: str
    answers: tuple[str, ...]
    documents: tuple[NormalizedDocument, ...]
    evaluation: dict[str, object]
    metadata: dict[str, object]

    def example_record(self) -> dict[str, object]:
        """Serialize retriever-safe query/document data, excluding supervision."""
        return {
            "example_id": self.example_id, "dataset": self.dataset,
            "question": self.question,
            "documents": [document.corpus_record() for document in self.documents],
            "metadata": self.metadata,
        }

    def evaluation_record(self) -> dict[str, object]:
        """Serialize answer and support supervision in a separate artifact."""
        return {"example_id": self.example_id, "dataset": self.dataset,
                "answers": list(self.answers), "evaluation": self.evaluation}


class DatasetNormalizer:
    """Schema-specific normalizer with no retrieval or supervision shortcuts."""

    def normalize_hotpotqa_record(self, record: Mapping[str, object]) -> NormalizedExample:
        example_id = _string(record, "_id"); question = _string(record, "question")
        answer = _string(record, "answer")
        contexts = _list(record, "context")
        documents = tuple(self._context_document("hotpotqa", example_id, index, item)
                          for index, item in enumerate(contexts))
        supporting_facts = _list(record, "supporting_facts")
        return NormalizedExample(example_id, "hotpotqa", question, (answer,), documents,
            {"supporting_facts": _json_value(supporting_facts)},
            {key: _string(record, key) for key in ("type", "level") if key in record})

    def normalize_2wiki_record(self, record: Mapping[str, object]) -> NormalizedExample:
        example_id = _string(record, "id"); question = _string(record, "question")
        answer = _string(record, "answer"); context = _mapping(record, "context")
        titles, sentence_groups = _list(context, "title"), _list(context, "sentences")
        if len(titles) != len(sentence_groups):
            raise ValueError("2Wiki context.title and context.sentences must have equal lengths")
        documents = tuple(self._title_sentences_document("2wiki", example_id, index, title, sentences)
                          for index, (title, sentences) in enumerate(zip(titles, sentence_groups)))
        return NormalizedExample(example_id, "2wiki", question, (answer,), documents,
            {"supporting_facts": _json_value(_mapping(record, "supporting_facts")),
             "evidences": _json_value(_list(record, "evidences"))},
            {"type": _string(record, "type")})

    def normalize_nq_record(self, record: Mapping[str, object], line_number: int) -> NormalizedExample:
        question = _string(record, "question"); answers = _list(record, "answer")
        if not all(isinstance(answer, str) for answer in answers):
            raise ValueError("NQ answer must contain only strings")
        return NormalizedExample(f"nq_open:{line_number}", "nq_open", question, tuple(answers), (),
            {"requires_external_retrieval_corpus": True},
            {"source_line_number": line_number, "requires_external_retrieval_corpus": True})

    def _context_document(self, dataset: str, example_id: str, position: int, context: object) -> NormalizedDocument:
        if not isinstance(context, list) or len(context) != 2:
            raise ValueError("HotpotQA context entries must be [title, sentences]")
        return self._title_sentences_document(dataset, example_id, position, context[0], context[1])

    def _title_sentences_document(self, dataset: str, example_id: str, position: int,
                                  title: object, sentences: object) -> NormalizedDocument:
        if not isinstance(title, str) or not title:
            raise ValueError("context title must be a non-empty string")
        if not isinstance(sentences, list) or not all(isinstance(sentence, str) for sentence in sentences):
            raise ValueError("context sentences must be a list of strings")
        text, offsets = _join_sentences(sentences)
        return NormalizedDocument(f"{dataset}:{example_id}:{position}", title, text, dataset,
                                  example_id, position, offsets)


class NormalizedCorpusBuilder:
    """Read local raw files and write stable JSONL example/evaluation/corpus artifacts."""

    def __init__(self, normalizer: DatasetNormalizer | None = None) -> None:
        self._normalizer = normalizer or DatasetNormalizer()

    def build(self, *, nq_path: Path, hotpotqa_path: Path, two_wiki_path: Path,
              output_root: Path) -> dict[str, int]:
        datasets = {
            "hotpotqa": self._read_jsonl(hotpotqa_path, self._normalizer.normalize_hotpotqa_record),
            "2wiki": self._read_2wiki(two_wiki_path),
            "nq_open": self._read_nq(nq_path),
        }
        evaluation_root, corpus_root = output_root / "evaluation", output_root / "retrieval_corpus"
        for directory in (output_root, evaluation_root, corpus_root): directory.mkdir(parents=True, exist_ok=True)
        for name, examples in datasets.items():
            self._write_jsonl(output_root / f"{name}_normalized.jsonl", (item.example_record() for item in examples))
            self._write_jsonl(evaluation_root / f"{name}_evaluation.jsonl", (item.evaluation_record() for item in examples))
            if name != "nq_open":
                self._write_jsonl(corpus_root / f"{name}_corpus.jsonl",
                                  (document.corpus_record() for item in examples for document in item.documents))
        return {name: len(examples) for name, examples in datasets.items()}

    def _read_jsonl(self, path: Path, transform: Any) -> list[NormalizedExample]:
        records: list[NormalizedExample] = []
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                if line.strip(): records.append(transform(json.loads(line)))
        return records

    def _read_nq(self, path: Path) -> list[NormalizedExample]:
        records: list[NormalizedExample] = []
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                if line.strip(): records.append(self._normalizer.normalize_nq_record(json.loads(line), line_number))
        return records

    def _read_2wiki(self, path: Path) -> list[NormalizedExample]:
        return [self._normalizer.normalize_2wiki_record(record)
                for record in pq.ParquetFile(path).read().to_pylist()]

    @staticmethod
    def _write_jsonl(path: Path, records: Iterable[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="\n") as output:
            for record in records:
                output.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
                output.write("\n")


def _join_sentences(sentences: Sequence[str]) -> tuple[str, tuple[tuple[int, int], ...]]:
    pieces: list[str] = []; offsets: list[tuple[int, int]] = []; position = 0
    for sentence in sentences:
        if pieces: position += 1
        pieces.append(sentence); offsets.append((position, position + len(sentence))); position += len(sentence)
    return " ".join(pieces), tuple(offsets)


def _string(record: Mapping[str, object], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip(): raise ValueError(f"required field {key} must be a non-empty string")
    return value
def _list(record: Mapping[str, object], key: str) -> list[object]:
    value = record.get(key)
    if not isinstance(value, list): raise ValueError(f"required field {key} must be a list")
    return value
def _mapping(record: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = record.get(key)
    if not isinstance(value, Mapping): raise ValueError(f"required field {key} must be an object")
    return value
def _json_value(value: object) -> object:
    """Validate that supervision is JSON-serializable without changing it."""
    json.dumps(value, ensure_ascii=False)
    return value
