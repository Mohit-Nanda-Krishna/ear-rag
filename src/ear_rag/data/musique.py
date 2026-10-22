"""Strict, all-or-nothing native MuSiQue-Ans JSONL ingestion. No split approval."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .normalization import NormalizedDocument, NormalizedExample

POLICY = "musique_official_jsonl_v1"


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite JSON number: {value}")
    return number


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _integer(value: Any) -> bool:
    return type(value) is int and value >= 0


def _defects(record: dict[str, Any]) -> list[str]:
    errors = [f"invalid_{key}" for key in ("id", "question", "answer") if not _text(record.get(key))]
    aliases = record.get("answer_aliases")
    if not isinstance(aliases, list) or not all(_text(a) for a in aliases):
        errors.append("invalid_answer_aliases")
    if record.get("answerable") is not True:
        errors.append("not_answerable_ans_record")
    paragraphs = record.get("paragraphs")
    indices: list[int] = []
    support: set[int] = set()
    if not isinstance(paragraphs, list) or not paragraphs:
        errors.append("invalid_paragraphs")
    else:
        for position, p in enumerate(paragraphs):
            if (not isinstance(p, dict) or not _integer(p.get("idx")) or
                    not _text(p.get("title")) or not _text(p.get("paragraph_text")) or
                    type(p.get("is_supporting")) is not bool):
                errors.append(f"invalid_paragraph:{position}")
                continue
            indices.append(p["idx"])
            if p["is_supporting"]:
                support.add(p["idx"])
        if len(indices) != len(set(indices)):
            errors.append("duplicate_paragraph_idx")
        # Official native indices identify the candidate array, not titles.
        if set(indices) != set(range(len(paragraphs))):
            errors.append("paragraph_idx_out_of_range")
    steps = record.get("question_decomposition")
    refs: list[int] = []
    step_ids: list[int] = []
    if not isinstance(steps, list) or not steps:
        errors.append("invalid_question_decomposition")
    else:
        for position, step in enumerate(steps):
            if (not isinstance(step, dict) or not _integer(step.get("id")) or
                    not _integer(step.get("paragraph_support_idx")) or
                    not _text(step.get("question")) or not _text(step.get("answer"))):
                errors.append(f"invalid_decomposition:{position}")
                continue
            refs.append(step["paragraph_support_idx"])
            step_ids.append(step["id"])
        if len(step_ids) != len(set(step_ids)):
            errors.append("duplicate_decomposition_id")
        if not set(refs).issubset(indices):
            errors.append("missing_support_paragraph")
        if set(refs) != support or not support:
            errors.append("support_flag_reference_disagreement")
    return sorted(set(errors))


@dataclass(frozen=True)
class MuSiQueDataset:
    examples: tuple[NormalizedExample, ...]
    records: tuple[dict[str, Any], ...]
    source_sha256: str
    manifest: dict[str, Any]
    source_split: str = "dev"

    @cached_property
    def example_index(self) -> dict[str, list[NormalizedExample]]:
        index: dict[str, list[NormalizedExample]] = {}
        for example in self.examples:
            index.setdefault(example.example_id, []).append(example)
        return index

    @property
    def source(self) -> dict[str, str]:
        return {"dataset": "musique", "identifier": f"musique_ans_v1.0_{self.source_split}",
                "sha256": self.source_sha256, "source_split": self.source_split, "setting": "native_candidates",
                "format": POLICY}


def _inspect(path: str | Path, acquisition_path: str | Path | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = Path(path)
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    parsed: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    # splitlines preserves interior blank records; one terminal newline is normal.
    for position, line in enumerate(raw.splitlines(), 1):
        record: dict[str, Any] | None = None
        error = None
        try:
            value = json.loads(line.decode("utf-8"), object_pairs_hook=_object,
                               parse_constant=_constant, parse_float=_float)
            if not isinstance(value, dict):
                raise ValueError("record must be an object")
            record = value
            parsed.append(record)
            reasons = _defects(record)
        except (ValueError, UnicodeError) as exc:
            reasons, error = ["unparseable_record"], str(exc)
        qid = record.get("id") if record and _text(record.get("id")) else None
        entries.append({"position": position, "question_id": qid, "reason_codes": reasons, "detail": error})
    ids = Counter(e["question_id"] for e in entries if e["question_id"] is not None)
    for entry in entries:
        if entry["question_id"] is not None and ids[entry["question_id"]] > 1:
            entry["reason_codes"] = sorted(set(entry["reason_codes"] + ["duplicate_question_id"]))
    issues = [e for e in entries if e["reason_codes"]]
    unclassifiable = sum(e["question_id"] is None for e in issues)
    report: dict[str, Any] = {
        "schema_version": POLICY, "source": {"path": path.resolve().as_posix(), "sha256": sha, "bytes": len(raw)},
        "counts": {"total": len(entries), "valid": len(entries) - len(issues),
                   "excluded": len(issues) - unclassifiable, "unclassifiable": unclassifiable, "unique_ids": len(ids)},
        "exclusion_policy": {"id": POLICY, "mode": "reject_entire_input_if_any_defect",
                             "definitions": "valid: no defects; excluded: defective with reliable ID; unclassifiable: defective without reliable ID. Disjoint record counts."},
        "issues": issues, "evaluation_approval": "not_granted_by_validation", "acquisition": None}
    if acquisition_path is not None:
        acquisition_path = Path(acquisition_path)
        acquisition_raw = acquisition_path.read_bytes()
        acquisition = json.loads(acquisition_raw.decode("utf-8"), object_pairs_hook=_object,
                                 parse_constant=_constant, parse_float=_float)
        matches = [a for a in acquisition.get("artifacts", []) if a.get("sha256") == sha]
        if len(matches) != 1:
            raise ValueError("acquisition manifest does not uniquely match input checksum")
        report["acquisition"] = {"path": acquisition_path.resolve().as_posix(),
                                 "sha256": hashlib.sha256(acquisition_raw).hexdigest(), "artifact": matches[0]}
    return parsed, report


def inspect_musique(path: str | Path, *, acquisition_path: str | Path | None = None) -> dict[str, Any]:
    """Deterministic diagnostics. Invalid inspections cannot enter the evaluator."""
    return _inspect(path, acquisition_path)[1]


def read_musique(path: str | Path, *, acquisition_path: str | Path | None = None,
                 source_split: str = "dev") -> MuSiQueDataset:
    if source_split not in {"train", "dev"}:
        raise ValueError("labelled MuSiQue source_split must explicitly be train or dev")
    records, report = _inspect(path, acquisition_path)
    if report["issues"] or not records:
        raise ValueError(f"MuSiQue input not fully valid: {report['counts']}; issues={report['issues']}")
    examples = []
    for record in records:
        qid = record["id"]
        docs = tuple(NormalizedDocument(
            f"musique:ans_v1.0:{source_split}:{qid}:paragraph:{p['idx']}", p["title"], p["paragraph_text"],
            "musique", qid, p["idx"], ()) for p in record["paragraphs"])
        examples.append(NormalizedExample(qid, "musique", record["question"],
            (record["answer"], *record["answer_aliases"]), docs,
            {"supporting_paragraph_indices": [p["idx"] for p in record["paragraphs"] if p["is_supporting"]]}, {}))
    return MuSiQueDataset(tuple(examples), tuple(records), report["source"]["sha256"], report, source_split)
