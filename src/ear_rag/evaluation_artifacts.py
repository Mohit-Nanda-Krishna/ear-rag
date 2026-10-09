"""Offline annotation resolution, provenance and report serialization."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
from typing import Any

from ear_rag.demo import DemoExample
from ear_rag.evaluation_metrics import LabelResolution


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_labels(examples: Sequence[DemoExample], evaluation_path: Path,
                   dataset: str) -> dict[str, LabelResolution]:
    """Resolve unique annotated titles within each original example's context.

    This keeps the established local-ID metric comparable. Unresolved or duplicate
    titles are recorded, not converted into negative retrieval outcomes. Answers
    are neither retained in this mapping nor sent to any runtime component.
    """
    annotations = {}
    with evaluation_path.open(encoding="utf-8-sig") as source:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            query_id = record["example_id"]
            if query_id in annotations:
                raise ValueError(f"duplicate evaluation query ID: {query_id}")
            annotations[query_id] = record.get("evaluation", {}).get("supporting_facts")
    resolved = {}
    for example in examples:
        facts = annotations.get(example.example_id)
        if facts is None:
            resolved[example.example_id] = LabelResolution(frozenset(), None)
            continue
        if dataset == "hotpotqa" and isinstance(facts, list):
            if not all(isinstance(item, list) and item and isinstance(item[0], str) for item in facts):
                raise ValueError("HotpotQA supporting facts must contain title/sentence entries")
            titles = {item[0] for item in facts}
        elif dataset == "2wiki" and isinstance(facts, dict) and isinstance(facts.get("title"), list):
            if not all(isinstance(title, str) for title in facts["title"]):
                raise ValueError("2Wiki support titles must be strings")
            titles = set(facts["title"])
        else:
            raise ValueError(f"unsupported supporting-fact schema for {dataset}")
        title_ids: dict[str, list[str]] = {}
        for doc in example.documents:
            title_ids.setdefault(str(doc.metadata.get("title", "")), []).append(doc.document_id)
        ids = frozenset(title_ids[title][0] for title in titles if len(title_ids.get(title, [])) == 1)
        unresolved = tuple(sorted(title for title in titles if len(title_ids.get(title, [])) != 1))
        resolved[example.example_id] = LabelResolution(ids, len(titles), unresolved)
    return resolved


def provenance(examples: Sequence[DemoExample], selected: Sequence[DemoExample],
               labels: Mapping[str, LabelResolution], config: Mapping[str, Any]) -> dict[str, Any]:
    documents = sorted((doc for example in examples for doc in example.documents), key=lambda doc: doc.document_id)
    if len({doc.document_id for doc in documents}) != len(documents):
        raise ValueError("evaluation corpus document IDs must be unique")
    root = Path(__file__).resolve().parents[2]
    sources = [
        "src/ear_rag/routing/query_analysis.py", "src/ear_rag/routing/initial.py",
        "src/ear_rag/routing/pipeline.py", "src/ear_rag/demo.py",
        "src/ear_rag/retrieval/local.py", "src/ear_rag/retrieval/vector.py",
        "src/ear_rag/retrieval/hybrid.py", "src/ear_rag/retrieval/multihop.py",
        "src/ear_rag/retrieval/chunking.py", "src/ear_rag/evidence/esa.py",
        "src/ear_rag/data/normalization.py", "src/ear_rag/evaluate_initial.py",
        "src/ear_rag/evaluation_metrics.py", "src/ear_rag/evaluation_artifacts.py",
    ]
    return {
        "query_ids": [example.example_id for example in selected],
        "query_sha256": fingerprint([(example.example_id, example.question) for example in selected]),
        "corpus_sha256": fingerprint([(doc.document_id, doc.text, doc.metadata) for doc in documents]),
        "evidence_labels_sha256": fingerprint({key: {**value.record(), "resolved_ids": sorted(value.resolved_ids)}
                                               for key, value in labels.items()}),
        "configuration_sha256": fingerprint(config), "source_sha256": {path: file_fingerprint(root / path) for path in sources},
        "python": sys.version, "platform": platform.platform(),
        "corpus_examples": len(examples), "corpus_documents": len(documents),
        "annotation_scope": "unique support titles mapped to IDs within original example context; corpus is unchanged",
    }


def save_reports(report: Mapping[str, Any], directory: Path) -> None:
    """Write UTF-8 JSON and CSV; query text appears only in offline artifacts."""
    directory.mkdir(parents=True, exist_ok=True)
    aggregate = {key: value for key, value in report.items() if key != "per_query"}
    (directory / "aggregate.json").write_text(json.dumps(aggregate, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    records = report["per_query"]
    with (directory / "per_query.jsonl").open("w", encoding="utf-8", newline="\n") as output:
        for row in records:
            output.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    fields = ["query_id", "query", "category", "selected_strategy", "fallback_occurred", "fallback_code",
              "fallback_reason", "selection_code", "score_margin", "routing_latency_ms", "features", "scores",
              "label_resolution", "per_retriever", "best_observed_strategies", "routing_regret", "outcome", "reason"]
    with (directory / "per_query.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in records:
            routing, analysis = row["routing"], row["decision_analysis"]
            item = {key: row[key] for key in ("query_id", "query", "category")}
            item.update({key: routing[key] for key in ("selected_strategy", "fallback_occurred", "fallback_code", "fallback_reason", "selection_code", "score_margin", "routing_latency_ms")})
            item.update({"features": routing["features"], "scores": routing["suitability_scores"],
                         "label_resolution": row["label_resolution"], "per_retriever": row["per_retriever"]})
            item.update({key: analysis[key] for key in ("best_observed_strategies", "routing_regret", "outcome", "reason")})
            writer.writerow({key: json.dumps(value, ensure_ascii=False, allow_nan=False) if isinstance(value, (dict, list)) else value
                             for key, value in item.items()})
    with (directory / "retrievals.csv").open("w", encoding="utf-8", newline="") as output:
        fields = ["query_id", "strategy", "resolved_support_recall_at_k", "hit_at_k", "full_support_recall_at_k",
                  "full_support_covered", "utility", "underlying_retrieval_calls", "retrieval_latency_ms",
                  "router_latency_ms", "initial_stage_latency_ms", "retrieved_passages", "final_context_chunks"]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in records:
            for strategy, metrics in row["per_retriever"].items():
                writer.writerow({"query_id": row["query_id"], "strategy": strategy,
                                 **{key: metrics[key] for key in fields[2:]}})
