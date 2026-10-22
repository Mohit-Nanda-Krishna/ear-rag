"""Versioned invalid-record audit only: no filtering, repair or approval.

Reads one byte snapshot, reuses strict JSON/record validation, and collects all
instances of the two policy predicates instead of relying on first-error text.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from .hotpotqa import _invalid_constant, _normalize_record, _unique_object


POLICY_VERSION = "hotpotqa_initial_release_invalid_records_v1"
SCHEMA_VERSION = "hotpotqa_policy_audit_v1"
POLICY_CODES = frozenset({"blank_candidate_sentence", "support_sentence_index_out_of_range"})


def _policy_findings(record: object) -> tuple[list[dict[str, Any]], bool]:
    """Collect every decidable policy finding and mark incomplete checks."""
    details: list[dict[str, Any]] = []
    reliable = True

    def unknown(path: str, reason: str) -> None:
        nonlocal reliable
        reliable = False
        details.append({"code": "unclassifiable_policy_input", "path": path, "reason": reason})

    if not isinstance(record, dict):
        unknown("$", "record must be an object")
        return details, reliable
    contexts = record.get("context")
    title_lengths: dict[str, list[int | None]] = defaultdict(list)
    if not isinstance(contexts, list):
        unknown("context", "expected a list of candidate pairs")
    else:
        for position, context in enumerate(contexts):
            path = f"context[{position}]"
            if not isinstance(context, list) or len(context) != 2:
                unknown(path, "expected [title, sentences]")
                continue
            title, sentences = context
            usable_title = isinstance(title, str) and bool(title.strip())
            if not usable_title:
                unknown(path, "title must be a nonblank string")
            valid_sentences = isinstance(sentences, list) and bool(sentences)
            if not valid_sentences:
                unknown(path, "sentences must be a nonempty list")
            elif any(not isinstance(sentence, str) for sentence in sentences):
                unknown(path, "sentence values must be strings")
                valid_sentences = False
            if usable_title:
                title_lengths[title].append(len(sentences) if valid_sentences else None)
                if len(title_lengths[title]) > 1:
                    unknown(path, "duplicate title prevents unique support resolution")
            if isinstance(sentences, list):
                for index, sentence in enumerate(sentences):
                    if isinstance(sentence, str) and not sentence.strip():
                        details.append({"code": "blank_candidate_sentence", "context_position": position,
                                        "title": title if usable_title else None,
                                        "sentence_index": index, "sentence_value": sentence})
    facts = record.get("supporting_facts")
    if not isinstance(facts, list):
        unknown("supporting_facts", "expected a list of supporting-fact pairs")
    else:
        for position, fact in enumerate(facts):
            path = f"supporting_facts[{position}]"
            if not isinstance(fact, list) or len(fact) != 2:
                unknown(path, "expected [title, sentence_index]")
                continue
            title, index = fact
            if not isinstance(title, str) or not title.strip():
                unknown(path, "support title must be a nonblank string")
                continue
            if isinstance(index, bool) or not isinstance(index, int):
                unknown(path, "sentence index must be an integer, excluding bool")
                continue
            lengths = title_lengths.get(title, [])
            if len(lengths) != 1 or lengths[0] is None:
                unknown(path, "no unique valid context sentence count for this title")
                continue
            count = lengths[0]
            if not 0 <= index < count:
                details.append({"code": "support_sentence_index_out_of_range",
                                "supporting_fact_position": position, "title": title,
                                "sentence_index": index, "sentence_count": count,
                                "valid_min": 0, "valid_max": count - 1})
    return details, reliable


def audit_hotpotqa_policy(path: str | Path) -> dict[str, Any]:
    """Return a deterministic audit, never a dataset or list of approved IDs.

    Identity/structural uncertainty takes precedence over policy exclusion and
    remains otherwise-invalid with all decidable policy findings retained.
    Unreadable files raise; unparseable/unsupported files return file_error with
    unknown counts (or known zero for an empty array), not invented records.
    """
    path = Path(path)
    content = path.read_bytes()
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "policy_version": POLICY_VERSION,
        "source": {"filename": path.name, "sha256": hashlib.sha256(content).hexdigest(),
                   "size_bytes": len(content), "format": "hotpotqa_json_array_v1"},
        "status": "inspected", "file_error": None, "evaluation_approval": "not_granted",
        "definitions": {
            "valid": "Passes existing strict per-record validation and unique usable ID checks; not evaluation approval.",
            "excluded": "Reliably identified, structurally classifiable record with at least one policy exclusion finding.",
            "otherwise_invalid": "All remaining invalid or unclassifiable records; disjoint from valid and excluded.",
            "unclassifiable": "Subset of otherwise_invalid with ambiguous identity or incomplete policy checks; not additive.",
            "excluded_reason_counts": "Excluded records per code, once per code per record; overlapping codes are not additive.",
        },
        "counts": {key: None for key in ("total_records_inspected", "valid", "excluded", "otherwise_invalid", "unclassifiable")},
        "excluded_reason_counts": {}, "excluded_records": [], "otherwise_invalid_records": [],
        "unclassifiable_positions": [],
    }
    try:
        records = json.loads(content.decode("utf-8-sig"), object_pairs_hook=_unique_object,
                             parse_constant=_invalid_constant)
        if not isinstance(records, list) or not records:
            if isinstance(records, list):
                report["counts"] = dict.fromkeys(report["counts"], 0)
            raise ValueError("expected a nonempty HotpotQA JSON array")
    except (ValueError, UnicodeError) as error:
        report.update(status="file_error", file_error={"type": type(error).__name__, "message": str(error)})
        return report
    positions: dict[str, list[int]] = defaultdict(list)
    for position, record in enumerate(records):
        identifier = record.get("_id") if isinstance(record, dict) else None
        if isinstance(identifier, str) and identifier.strip():
            positions[identifier].append(position)
    counts = dict.fromkeys(report["counts"], 0)
    counts["total_records_inspected"] = len(records)
    reason_counts: Counter[str] = Counter()
    for position, record in enumerate(records):
        identifier = record.get("_id") if isinstance(record, dict) else None
        details, reliable = _policy_findings(record)
        if not isinstance(identifier, str) or not identifier.strip():
            reliable = False
            details.append({"code": "invalid_question_id", "reason": "missing, nonstring or blank _id"})
        elif len(positions[identifier]) > 1:
            reliable = False
            details.append({"code": "duplicate_question_id", "source_positions": positions[identifier]})
        strict_error = None
        try:
            _normalize_record(record)
        except ValueError as error:
            strict_error = str(error)
        if strict_error and not details:
            details.append({"code": "strict_validation_error", "reason": strict_error})
        codes = sorted({detail["code"] for detail in details})
        classification = ("otherwise_invalid" if not reliable else "excluded" if POLICY_CODES.intersection(codes)
                          else "otherwise_invalid" if strict_error else "valid")
        counts[classification] += 1
        if classification == "valid":
            continue
        row = {"question_id": identifier if isinstance(identifier, str) else None,
               "source_position": position, "classification": classification,
               "classification_reliable": reliable, "reason_codes": codes,
               "details": details, "strict_validation_error": strict_error}
        report[f"{classification}_records"].append(row)
        if not reliable:
            counts["unclassifiable"] += 1
            report["unclassifiable_positions"].append(position)
        if classification == "excluded":
            reason_counts.update(POLICY_CODES.intersection(codes))
    report["counts"] = counts
    report["excluded_reason_counts"] = dict(sorted(reason_counts.items()))
    return report


def write_policy_audit(report: dict[str, Any], path: str | Path) -> None:
    """Write finite, sorted UTF-8 JSON only to a new file; never overwrite raw data."""
    if report["schema_version"] != SCHEMA_VERSION or report["policy_version"] != POLICY_VERSION:
        raise ValueError("unsupported policy audit version")
    serialized = json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False, indent=2) + "\n"
    with Path(path).open("x", encoding="utf-8", newline="\n") as output:
        output.write(serialized)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = audit_hotpotqa_policy(args.source)
        write_policy_audit(report, args.output)
    except OSError as error:
        parser.error(str(error))
    return 0 if report["status"] == "inspected" else 2


if __name__ == "__main__":
    raise SystemExit(main())
