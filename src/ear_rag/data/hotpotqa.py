"""Read labelled HotpotQA arrays and project runtime data without supervision.

This module does not download, index, evaluate or infer a trustworthy split.
Existing JSONL readers are intentionally unchanged.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
from typing import Any, cast

from .normalization import DatasetNormalizer, NormalizedExample


class HotpotQAValidationError(ValueError):
    """A rejected input, with record counts and diagnostics for offline reporting."""

    def __init__(self, message: str, report: dict[str, Any]) -> None:
        super().__init__(message)
        self.report = report


@dataclass(frozen=True)
class HotpotQADataset:
    """Validated offline records. Pass projections, not this bundle, to runtime."""

    examples: tuple[NormalizedExample, ...]
    source_id: str
    source_sha256: str
    source_split: str
    setting: str

    @property
    def source(self) -> dict[str, str]:
        return {"dataset": "hotpotqa", "identifier": self.source_id,
                "sha256": self.source_sha256, "source_split": self.source_split,
                "setting": self.setting, "format": "hotpotqa_json_array_v1",
                "authenticity": "not_verified"}

    @property
    def counts(self) -> dict[str, int]:
        # A dataset is returned only if the entire array passed validation.
        return {"total": len(self.examples), "accepted": len(self.examples),
                "rejected": 0, "malformed": 0, "duplicate_ids": 0}


@dataclass(frozen=True)
class HotpotQAInspection:
    """Offline diagnostic examples, not an approved or filtered dataset.

    An earlier duplicate occurrence can appear in examples; require_valid blocks
    release whenever any duplicate or malformed record was found.
    """

    examples: tuple[NormalizedExample, ...]
    source_id: str
    source_sha256: str
    source_split: str
    setting: str
    _report: dict[str, Any]

    @property
    def report(self) -> dict[str, Any]:
        return deepcopy(self._report)

    def require_valid(self) -> HotpotQADataset:
        """Release all records or raise; never silently exclude rejected rows."""
        if self._report["errors"]:
            raise HotpotQAValidationError(
                f"{self.source_id}: " + "; ".join(self._report["errors"]), self.report)
        return HotpotQADataset(self.examples, self.source_id, self.source_sha256,
                              self.source_split, self.setting)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _normalize_record(record: object) -> NormalizedExample:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    contexts = record.get("context")
    if not isinstance(contexts, list) or not contexts:
        raise ValueError("context must be a nonempty list of [title, sentences] pairs")
    titles = {}
    for index, context in enumerate(contexts):
        if not isinstance(context, list) or len(context) != 2:
            raise ValueError(f"context[{index}] must be [title, sentences]")
        title, sentences = context
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"context[{index}] title must be a nonempty string")
        if title in titles:
            raise ValueError(f"context[{index}] has a duplicate candidate title")
        if not isinstance(sentences, list) or not sentences:
            raise ValueError(f"context[{index}] sentences must be a nonempty list")
        if any(not isinstance(sentence, str) or not sentence.strip() for sentence in sentences):
            raise ValueError(f"context[{index}] sentence must be a nonempty string")
        titles[title] = len(sentences)
    facts = record.get("supporting_facts")
    if not isinstance(facts, list) or not facts:
        raise ValueError("supporting_facts must be a nonempty list of [title, sentence_id] pairs")
    for index, fact in enumerate(facts):
        if not isinstance(fact, list) or len(fact) != 2 or not isinstance(fact[0], str):
            raise ValueError(f"supporting_facts[{index}] must be [title, sentence_id]")
        title, sentence = fact
        if title not in titles:
            raise ValueError(f"supporting_facts[{index}] has an unresolved supporting title")
        if isinstance(sentence, bool) or not isinstance(sentence, int) or not 0 <= sentence < titles[title]:
            raise ValueError(f"supporting_facts[{index}] sentence index is invalid or out of range")
    example = DatasetNormalizer().normalize_hotpotqa_record(record)
    # Preserve additional source annotations offline, including nested values.
    core = {"_id", "question", "answer", "context", "supporting_facts"}
    return replace(example, metadata=deepcopy({key: value for key, value in record.items() if key not in core}))


def read_hotpotqa(path: str | Path, *, source_split: str, setting: str = "distractor",
                 source_id: str | None = None) -> HotpotQADataset:
    """Read an entire labelled train/dev JSON array, rejecting it on any error.

    Source bytes remain read-only. Format validation does not authenticate an
    official release, enforce ten candidates, or support unlabelled blind tests.
    Validation errors expose aggregate counts, without returning a partial dataset.
    """
    return inspect_hotpotqa(path, source_split=source_split, setting=setting,
                           source_id=source_id).require_valid()


def inspect_hotpotqa(path: str | Path, *, source_split: str, setting: str = "distractor",
                    source_id: str | None = None) -> HotpotQAInspection:
    """Inspect record validity without repairing, skipping or releasing a subset.

    Unparseable/empty files still raise; record errors include zero-based source
    position, original string ID (or None) and the first strict validation reason.
    The source hash and examples remain offline; no projection is performed.
    """
    if source_split not in {"train", "dev"}:
        raise ValueError("reader supports labelled HotpotQA train/dev sources only")
    if setting not in {"distractor", "fullwiki"}:
        raise ValueError("setting must be distractor or fullwiki")
    path = Path(path)
    identifier = path.name if source_id is None else source_id
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("source_id must be a nonempty identifier")
    content = path.read_bytes()
    report: dict[str, Any] = {
        "source": {"identifier": identifier, "sha256": hashlib.sha256(content).hexdigest(),
                   "source_split": source_split, "setting": setting},
        "counts": {"total": 0, "accepted": 0, "rejected": 0, "malformed": 0, "duplicate_ids": 0},
        "duplicate_question_ids": [], "errors": [], "record_errors": [],
    }
    try:
        records = json.loads(content.decode("utf-8-sig"), object_pairs_hook=_unique_object,
                             parse_constant=_invalid_constant)
    except (ValueError, UnicodeError) as error:
        report["errors"] = [f"invalid UTF-8 JSON: {error}"]
        raise HotpotQAValidationError(f"{identifier}: {report['errors'][0]}", report) from error
    if not isinstance(records, list) or not records:
        report["errors"] = ["expected a nonempty HotpotQA JSON array"]
        raise HotpotQAValidationError(f"{identifier}: {report['errors'][0]}", report)
    report["counts"]["total"] = len(records)
    examples = []
    seen = set()
    duplicates = set()

    def record_error(position: int, question_id: object, reason: str) -> None:
        identifier = question_id if isinstance(question_id, str) else None
        report["record_errors"].append(
            {"position": position, "question_id": identifier, "reason": reason})
        report["errors"].append(f"record[{position}] (_id={identifier!r}): {reason}")

    for position, record in enumerate(records):
        question_id = record.get("_id") if isinstance(record, dict) else None
        if isinstance(question_id, str):
            if question_id in seen:
                report["counts"]["duplicate_ids"] += 1
                duplicates.add(question_id)
                record_error(position, question_id, "duplicate _id")
                continue
            seen.add(question_id)
        try:
            examples.append(_normalize_record(record))
        except ValueError as error:
            report["counts"]["malformed"] += 1
            record_error(position, question_id, str(error))
    report["counts"]["accepted"] = len(examples)
    report["counts"]["rejected"] = len(records) - len(examples)
    report["duplicate_question_ids"] = sorted(duplicates)
    return HotpotQAInspection(tuple(examples), identifier, report["source"]["sha256"],
                             source_split, setting, report)


def runtime_projection(dataset: HotpotQADataset) -> list[dict[str, Any]]:
    """Allowlist safe fields; never copy example annotations or open label files."""
    records = []
    for example in dataset.examples:
        documents = []
        for document in example.documents:
            documents.append({**document.corpus_record(), "source_id": dataset.source_id,
                              "source_split": dataset.source_split,
                              "sentences": [document.text[start:end] for start, end in document.sentence_offsets]})
        records.append({"example_id": example.example_id, "question": example.question,
                        "dataset": "hotpotqa", "source_split": dataset.source_split,
                        "setting": dataset.setting, "documents": documents})
    return records


def evaluation_projection(dataset: HotpotQADataset) -> list[dict[str, Any]]:
    """Offline-only answer/annotations and an exact support-title-to-ID join."""
    records = []
    for example in dataset.examples:
        by_title = {document.title: document.doc_id for document in example.documents}
        facts = cast(list[list[Any]], example.evaluation["supporting_facts"])
        records.append({**deepcopy(example.evaluation_record()), "source_split": dataset.source_split,
                        "source_id": dataset.source_id, "annotations": deepcopy(example.metadata),
                        "supporting_document_ids": sorted({by_title[fact[0]] for fact in facts})})
    return records
