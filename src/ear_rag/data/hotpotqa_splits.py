"""Explicit split planning and small, separately labelled data artifacts.

No default role counts, automatic exposure discovery, retrieval or indexing.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any
import unicodedata

from .hotpotqa import HotpotQADataset, evaluation_projection, runtime_projection


@dataclass(frozen=True)
class ExposureInventory:
    """Caller-supplied history: exposed ID -> question text, or None if unknown.

    Source-matched IDs can recover text from the current source. Unmatched IDs
    need supplied text before an exact normalized-text check is possible.
    An explicitly supplied empty mapping is distinct from unavailable history.
    """

    identifier: str
    questions: Mapping[str, str | None]


class SplitIntegrityError(ValueError):
    def __init__(self, message: str, report: dict[str, Any]) -> None:
        super().__init__(message)
        self.report = report


def normalized_question(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).lower().split())


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _exposure(dataset: HotpotQADataset, inventory: ExposureInventory | None) -> tuple[dict[str, Any], set[str], set[str]]:
    if inventory is None:
        return {"status": "unavailable", "identifier": None, "sha256": None}, set(), set()
    if not isinstance(inventory.identifier, str) or not inventory.identifier.strip():
        raise ValueError("exposure inventory needs a nonempty identifier")
    if not isinstance(inventory.questions, Mapping):
        raise ValueError("exposure questions must map IDs to text or None")
    current = {example.example_id: example.question for example in dataset.examples}
    ids, texts, unresolved = set(), set(), []
    for question_id, text in inventory.questions.items():
        if not isinstance(question_id, str) or not question_id.strip():
            raise ValueError("exposure question IDs must be nonempty strings")
        if text is not None and (not isinstance(text, str) or not text.strip()):
            raise ValueError("exposure question text must be nonempty or None")
        ids.add(question_id)
        if question_id in current:
            texts.add(normalized_question(current[question_id]))
        if text is not None:
            texts.add(normalized_question(text))
        elif question_id not in current:
            unresolved.append(question_id)
    info = {"status": "partial" if unresolved else "supplied", "identifier": inventory.identifier,
            "sha256": _digest(dict(inventory.questions)), "question_ids": sorted(ids),
            "normalized_question_count": len(texts), "unresolved_text_ids": sorted(unresolved),
            "scope": "exact IDs and NFKC/lower/whitespace text against supplied history only"}
    return info, ids, texts


def validate_split_integrity(dataset: HotpotQADataset, development_ids: Sequence[str],
                             holdout_ids: Sequence[str], *,
                             prior_exposure: ExposureInventory | None) -> dict[str, Any]:
    """Validate explicit roles; unavailable/partial history cannot certify holdout."""
    source = {example.example_id: example.question for example in dataset.examples}
    if len(source) != len(dataset.examples):
        raise ValueError("dataset contains duplicate source IDs")
    dev, held = list(development_ids), list(holdout_ids)
    if any(not isinstance(key, str) or not key for key in dev + held):
        raise ValueError("role question IDs must be nonempty strings")
    info, exposed_ids, exposed_texts = _exposure(dataset, prior_exposure)
    report: dict[str, Any] = {"prior_exposure": info, "semantic_near_duplicates": "not_checked",
                              "normalized_text_method": "nfkc_lower_whitespace_v1"}
    errors = []
    if len(set(dev)) != len(dev) or len(set(held)) != len(held):
        errors.append("duplicate IDs inside a split role")
    unknown = sorted((set(dev) | set(held)) - source.keys())
    if unknown:
        errors.append("unknown question IDs in split roles")
    report["unknown_ids"] = unknown
    report["id_overlap"] = sorted(set(dev) & set(held))
    if report["id_overlap"]:
        errors.append("development/holdout ID overlap")
    dev_texts = {normalized_question(source[key]) for key in dev if key in source}
    held_texts = {normalized_question(source[key]) for key in held if key in source}
    report["normalized_text_overlap"] = sorted(dev_texts & held_texts)
    if report["normalized_text_overlap"]:
        errors.append("development/holdout normalized-text overlap")
    # Also reject duplicate text within either role, even when IDs differ.
    if len(dev_texts) != len(set(dev) & source.keys()) or len(held_texts) != len(set(held) & source.keys()):
        errors.append("duplicate normalized question text inside a split role")
    report["exposed_holdout_ids"] = sorted(key for key in held if key in exposed_ids or
                                          (key in source and normalized_question(source[key]) in exposed_texts))
    if held and info["status"] != "supplied":
        errors.append("prior exposure inventory is unavailable or partial; holdout cannot be validated")
    if report["exposed_holdout_ids"]:
        errors.append("holdout overlaps prior exposure by ID or normalized text")
    if errors:
        report["errors"] = errors
        raise SplitIntegrityError("; ".join(errors), report)
    return report


def plan_splits(dataset: HotpotQADataset, *, development_count: int, holdout_count: int,
                prior_exposure: ExposureInventory | None, seed: int = 1729) -> dict[str, Any]:
    """Plan explicit sizes without writing; never silently shrink or infer history."""
    for name, value in (("development_count", development_count), ("holdout_count", holdout_count)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    if development_count + holdout_count == 0:
        raise ValueError("at least one split role must be nonempty")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    groups: dict[str, list[str]] = {}
    for example in dataset.examples:
        groups.setdefault(normalized_question(example.question), []).append(example.example_id)
    aliases = {min(ids): sorted(ids) for ids in groups.values()}
    rank = lambda key: (hashlib.sha256(f"{seed}:{key}".encode("utf-8")).hexdigest(), key)
    ranked = sorted(aliases, key=rank)
    info, exposed_ids, exposed_texts = _exposure(dataset, prior_exposure)
    preflight = {"prior_exposure": info, "unique_questions": len(ranked),
                 "requested_development": development_count, "requested_holdout": holdout_count}
    if development_count > len(ranked):
        raise SplitIntegrityError("not enough unique questions for requested development count", preflight)
    if holdout_count and info["status"] != "supplied":
        raise SplitIntegrityError("prior exposure inventory is unavailable or partial; cannot select holdout", preflight)
    development = ranked[:development_count]
    by_id = {example.example_id: example for example in dataset.examples}
    exclusions = {}
    eligible = []
    for representative in ranked:
        reasons = []
        if representative in development:
            reasons.append("development_role")
        if set(aliases[representative]) & exposed_ids:
            reasons.append("prior_exposure_id")
        if normalized_question(by_id[representative].question) in exposed_texts:
            reasons.append("prior_exposure_normalized_text")
        if reasons:
            for key in aliases[representative]:
                exclusions[key] = reasons
        else:
            eligible.append(representative)
    if holdout_count > len(eligible):
        raise SplitIntegrityError("not enough eligible questions for requested holdout count",
                                  {**preflight, "eligible_holdout": len(eligible)})
    holdout = eligible[:holdout_count]
    integrity = validate_split_integrity(dataset, development, holdout, prior_exposure=prior_exposure)
    return {
        "schema_version": "ear_rag_hotpotqa_splits_v1", "dataset": "hotpotqa",
        "source": dataset.source, "corpus_scope": "per_question_candidates",
        "selection": {"algorithm": "sha256_seed_id_v1", "seed": seed,
                      "normalized_text": "nfkc_lower_whitespace_v1",
                      "representative": "lexicographically smallest ID per exact normalized-text group"},
        "roles": {"development": development, "holdout": holdout},
        "counts": {**dataset.counts, "unique_questions": len(ranked),
                   "normalized_text_duplicates": len(dataset.examples) - len(ranked),
                   "development": len(development), "holdout": len(holdout)},
        "aliases": {key: value for key, value in sorted(aliases.items()) if len(value) > 1},
        "holdout_exclusions": dict(sorted(exclusions.items())), "integrity": integrity,
    }


def write_split_artifacts(dataset: HotpotQADataset, destination: str | Path,
                          **selection: Any) -> dict[str, Any]:
    """Preflight, then write a new directory only; publish checksummed manifest last.

    A successful preflight is not evidence that a supplied inventory is exhaustive
    or that the source is authentic. Callers authorize sizes and inventory scope.
    """
    manifest = plan_splits(dataset, **selection)
    runtime = {record["example_id"]: record for record in runtime_projection(dataset)}
    labels = {record["example_id"]: record for record in evaluation_projection(dataset)}
    payloads = {}
    artifacts = {}
    for role, ids in manifest["roles"].items():
        for view, records in (("runtime", runtime), ("labels", labels)):
            name = f"{role}.{view}.jsonl"
            content = b"".join(_json_bytes({**records[key], "role": role}) + b"\n" for key in ids)
            payloads[name] = content
            artifacts[name] = {"sha256": hashlib.sha256(content).hexdigest(), "records": len(ids)}
    manifest["artifacts"] = artifacts
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name, content in payloads.items():
        with (destination / name).open("xb") as output:
            output.write(content)
    with (destination / "manifest.json").open("xb") as output:
        output.write(_json_bytes(manifest) + b"\n")
    return manifest
