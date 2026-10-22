"""Offline bounded-controller evaluation infrastructure; no benchmark entry point."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
from typing import Any

from ear_rag.core.models import Document, RetrievalResult
from ear_rag.data.hotpotqa import HotpotQADataset
from ear_rag.data.musique import MuSiQueDataset
from ear_rag.data.musique_evidence import (
    MuSiQueCorpus, build_question_corpus as build_musique_corpus, paragraph_quality,
)
from ear_rag.data.hotpotqa_evidence import (
    HotpotQACorpus, SupportingEvidenceMatch, build_question_corpus,
    locate_evidence, match_supporting_evidence,
)
from ear_rag.evaluation_metrics import LabelResolution, supporting_document_metrics
from ear_rag.routing.initial import finite_number
from ear_rag.routing.pipeline import RetrievalControlPipeline, underlying_calls


SCHEMA_VERSION = "ear_rag_control_evaluation_v1"
QUALITY_FIELDS = ("hit_at_5", "supporting_document_recall_at_5", "supporting_evidence_coverage_at_5")
WORK_FIELDS = ("retrieval_calls", "returned_chunks", "retrieved_passages", "processed_chunks",
               "retrieval_latency_ms", "routing_latency_ms", "controller_latency_ms", "monetary_cost")


@dataclass(frozen=True)
class EvaluationCase:
    """Explicit request or auditable exclusion; never an automatic dataset split."""

    question_id: str
    exclusion_reason: str | None = None


def supporting_evidence_coverage(match: SupportingEvidenceMatch) -> float | None:
    """Fraction of unique annotated sentences completely covered by evidence."""
    denominator = len(match.matched_supports | match.missing_supports)
    return len(match.matched_supports) / denominator if denominator else None


def _json_snapshot(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True))


def _optional_measurement(metadata: Mapping[str, Any], key: str, *, count: bool = False) -> int | float | None:
    value = metadata.get(key)
    if value is None:
        return None
    number = finite_number(value, key, nonnegative=True)
    if count and not number.is_integer():
        raise ValueError(f"{key} must be an integer count")
    return int(number) if count else number


def _runtime_stage(corpus: HotpotQACorpus | MuSiQueCorpus, result: RetrievalResult) -> dict[str, Any]:
    if result.query_id != corpus.question_id:
        raise ValueError("retrieval query ID does not match evaluation case")
    calls = _optional_measurement(result.metadata, "retrieval_calls", count=True)
    # A legacy cumulative counter (or a controller's default zero) does not prove
    # how many child/hop calls this invocation made.
    work = {"retrieval_calls": underlying_calls(result) if calls is not None else None,
            "returned_chunks": len(result.chunks),
            "retrieved_passages": _optional_measurement(result.metadata, "retrieved_passages", count=True),
            "processed_chunks": _optional_measurement(result.metadata, "processed_chunks", count=True),
            "retrieval_latency_ms": _optional_measurement(result.metadata, "retrieval_latency_ms")}
    locations = locate_evidence(corpus, result.chunks)
    return _json_snapshot({
        "retriever_name": result.retriever_name, "requested_top_k": result.top_k,
        "retrieval_metadata": result.metadata, "work": work,
        "chunks": [{"chunk_id": chunk.chunk_id, "document_id": chunk.document_id,
                    "retrieval_score": chunk.retrieval_score, "retriever_name": chunk.retriever_name,
                    "location": asdict(location)} for chunk, location in zip(result.chunks, locations, strict=True)],
        "metrics": None,
    })


def _quality(dataset: HotpotQADataset | MuSiQueDataset, corpus: HotpotQACorpus | MuSiQueCorpus,
             result: RetrievalResult) -> dict[str, Any]:
    if isinstance(dataset, MuSiQueDataset) and isinstance(corpus, MuSiQueCorpus):
        return paragraph_quality(dataset, corpus, result)
    if not isinstance(dataset, HotpotQADataset) or not isinstance(corpus, HotpotQACorpus):
        raise ValueError("dataset and evidence adapter do not match")
    cutoff = replace(result, chunks=result.chunks[:5])
    match = match_supporting_evidence(dataset, corpus, cutoff.chunks)
    facts = match.matched_supports | match.missing_supports
    titles = {title for title, _ in facts}
    ids = frozenset(document.doc_id for document in corpus.source_documents if document.title in titles)
    documents = supporting_document_metrics(cutoff, LabelResolution(ids, len(titles)), 5)
    return {"hit_at_5": documents["hit_at_k"],
            "supporting_document_recall_at_5": documents["full_support_recall_at_k"],
            "supporting_evidence_coverage_at_5": supporting_evidence_coverage(match),
            "supporting_document_count": len(titles), "supporting_fact_count": len(facts),
            "matched_supporting_document_count": documents["matched_support_count"],
            "matched_supporting_fact_count": len(match.matched_supports)}


def _sum_observations(stages: Sequence[Mapping[str, Any]], field: str) -> int | float | None:
    values = [stage["work"][field] for stage in stages]
    return sum(values) if all(value is not None for value in values) else None


def evaluate_cases(dataset: HotpotQADataset | MuSiQueDataset, cases: Sequence[EvaluationCase],
                   pipeline_factory: Callable[[Sequence[Document]], RetrievalControlPipeline],
                   *, initial_backend: str) -> dict[str, Any]:
    """Run explicit requests in order; retain errors/exclusions and join labels offline.

    Factory receives only fresh runtime documents and must return a fresh pipeline
    for each case. It receives neither labels, the dataset nor the offline corpus.
    Strict ingestion/exposure approval remains the caller's responsibility. This
    function does not ingest partial inspections, apply exclusion policy or split.
    """
    if not isinstance(dataset, (HotpotQADataset, MuSiQueDataset)):
        raise ValueError("evaluation requires a fully validated HotpotQA dataset or native MuSiQue dataset")
    requests = tuple(cases)
    counts = Counter(case.question_id for case in requests)
    records = []
    for index, case in enumerate(requests):
        row: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "case_index": index,
            "question_id": case.question_id, "source": dataset.source, "status": "failed",
            "requested_initial_backend": initial_backend, "initial_backend": None,
            "initial": None, "terminal": None, "control": None, "work": None,
            "error": None, "exclusion_reason": None}
        stage = "request"
        try:
            if counts[case.question_id] != 1:
                raise ValueError(f"duplicate requested question ID: {case.question_id!r}")
            if case.exclusion_reason is not None:
                if not case.exclusion_reason.strip():
                    raise ValueError("exclusion requires a nonblank reason")
                row.update(status="excluded", exclusion_reason=case.exclusion_reason)
                records.append(row)
                continue
            stage = "corpus"
            corpus = (build_musique_corpus(dataset, case.question_id) if isinstance(dataset, MuSiQueDataset)
                      else build_question_corpus(dataset, case.question_id))
            stage = "pipeline_factory"
            pipeline = pipeline_factory(corpus.documents)
            stage = "runtime"
            trace = pipeline.run(corpus.query, initial_backend)
            stage = "runtime_snapshot"
            row["initial_backend"] = (trace.initial_routing.selected_strategy if trace.initial_routing
                                      else initial_backend)
            recovered = trace.recovery_retrieval is not None
            triggered = bool(trace.recovery_decision.metadata.get("recover", False))
            if triggered != recovered:
                raise ValueError("recovery decision and completed recovery trace disagree")
            if trace.final_state not in {"generate", "abstain"}:
                raise ValueError("unknown controller final state")
            initial = _runtime_stage(corpus, trace.initial_retrieval)
            terminal = (_runtime_stage(corpus, trace.recovery_retrieval) if trace.recovery_retrieval
                        else _json_snapshot(initial))
            row["initial"], row["terminal"] = initial, terminal
            row["control"] = _json_snapshot({
                "initial_assessment": asdict(trace.initial_assessment),
                "recovery_decision": asdict(trace.recovery_decision),
                "recovery_assessment": asdict(trace.recovery_assessment) if trace.recovery_assessment else None,
                "initial_routing": asdict(trace.initial_routing) if trace.initial_routing else None,
                "recovery_triggered": triggered, "recovery_count": int(recovered),
                "final_state": trace.final_state, "abstained": trace.final_state == "abstain"})
            retrievals = [initial, terminal] if recovered else [initial]
            row["work"] = {field: _sum_observations(retrievals, field) for field in initial["work"]}
            row["work"].update(
                routing_latency_ms=finite_number(trace.initial_routing.routing_latency_ms,
                    "routing_latency_ms", nonnegative=True) if trace.initial_routing else 0.0,
                controller_latency_ms=None, monetary_cost=None)
            stage = "offline_metrics"
            initial["metrics"] = _quality(dataset, corpus, trace.initial_retrieval)
            terminal["metrics"] = _quality(dataset, corpus, trace.recovery_retrieval or trace.initial_retrieval)
            row["status"] = "evaluated"
        except Exception as error:
            row["error"] = {"stage": stage, "type": type(error).__name__, "message": str(error)}
        records.append(row)
    return {"schema_version": SCHEMA_VERSION, "per_case": records,
            "aggregate": aggregate_cases(records)}


def _summary(values: Sequence[int | float | None]) -> dict[str, Any]:
    observed = [value for value in values if value is not None]
    total = sum(observed) if observed else None
    return {"observed": len(observed), "missing": len(values) - len(observed),
            "total": total, "mean": total / len(observed) if total is not None else None}


def _rate(numerator: int, denominator: int) -> dict[str, Any]:
    return {"numerator": numerator, "denominator": denominator,
            "rate": numerator / denominator if denominator else None}


def aggregate_cases(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Quality/rates over evaluated cases; known work includes failed cases too."""
    if any(row["status"] not in {"evaluated", "failed", "excluded"} for row in records):
        raise ValueError("unknown evaluation case status")
    completed = [row for row in records if row["status"] == "evaluated"]
    attempted = [row for row in records if row["status"] != "excluded"]
    n = len(completed)
    failed = sum(row["status"] == "failed" for row in records)
    excluded = len(records) - n - failed
    selections = Counter(row["initial_backend"] for row in completed)
    return {"schema_version": SCHEMA_VERSION,
        "counts": {"requested": len(records), "evaluated": n, "failed": failed, "excluded": excluded},
        "partial": bool(failed or excluded), "quality_scope": "evaluated_cases_only",
        **{stage: {field: _summary([row[stage]["metrics"][field] for row in completed])
                   for field in QUALITY_FIELDS} for stage in ("initial", "terminal")},
        "initial_backend_selection": {name: {"count": count, "frequency": count / n}
                                      for name, count in sorted(selections.items())},
        "recovery_trigger_rate": _rate(sum(row["control"]["recovery_triggered"] for row in completed), n),
        "recovery_count": sum(row["control"]["recovery_count"] for row in completed),
        "final_abstention_rate": _rate(sum(row["control"]["abstained"] for row in completed), n),
        "failure_rate": _rate(failed, len(records)), "exclusion_rate": _rate(excluded, len(records)),
        "initial_esa_decisions": dict(sorted(Counter(row["control"]["initial_assessment"]["decision"]
                                                     for row in completed).items())),
        "terminal_esa_decisions": dict(sorted(Counter((row["control"]["recovery_assessment"] or
                      row["control"]["initial_assessment"])["decision"] for row in completed).items())),
        "work": {field: _summary([row["work"][field] if row["work"] else None for row in attempted])
                 for field in WORK_FIELDS}}


def write_evaluation_report(report: Mapping[str, Any], directory: str | Path) -> None:
    """Write deterministic JSONL/JSON to a new directory; never overwrite results.

    Pre-serialize before touching disk. A later disk failure can leave an
    incomplete directory; this writer does not publish a benchmark manifest.
    """
    if (report["schema_version"] != SCHEMA_VERSION or
            report["aggregate"]["schema_version"] != SCHEMA_VERSION or
            any(row["schema_version"] != SCHEMA_VERSION for row in report["per_case"])):
        raise ValueError("unsupported evaluation report schema")
    aggregate = json.dumps(report["aggregate"], ensure_ascii=False, sort_keys=True, allow_nan=False, indent=2) + "\n"
    per_case = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
                       for row in report["per_case"])
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "per_case.jsonl").write_text(per_case, encoding="utf-8", newline="\n")
    (directory / "aggregate.json").write_text(aggregate, encoding="utf-8", newline="\n")
