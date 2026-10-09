"""Explicitly offline initial-selection comparison; recovery is always disabled."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import random
from typing import Any

from ear_rag.config.loader import get_config_path, load_config
from ear_rag.core.interfaces import Retriever
from ear_rag.core.models import Document, Query
from ear_rag.demo import DemoExample, build_backends, load_demo_dataset
from ear_rag.evidence import DeterministicEvidenceAssessor
from ear_rag.evaluation_artifacts import file_fingerprint, provenance, resolve_labels, save_reports
from ear_rag.evaluation_metrics import OBJECTIVE, LabelResolution, analyze_decision, feature_category, retrieval_metrics
from ear_rag.evaluation_report import summarize
from ear_rag.routing import BoundedRecoveryPolicy, RetrievalControlPipeline
from ear_rag.routing.initial import STRATEGIES


def load_smoke_examples() -> list[DemoExample]:
    """Synthetic wiring fixture, never evidence of retrieval-quality improvement."""
    path = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "initial_routing.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    return [DemoExample(record["id"], record["question"],
                        tuple(Document(item["id"], item["text"]) for item in record["documents"]),
                        frozenset(record["supporting_document_ids"])) for record in records]


def evaluate_initial(examples: Sequence[DemoExample], backends: Mapping[str, Retriever],
                     config: Mapping[str, Any], *, count: int = 20,
                     dataset_label: str = "synthetic smoke", seed: int = 1729,
                     sampling: str = "prefix", bootstrap_samples: int = 1000,
                     label_resolutions: Mapping[str, LabelResolution] | None = None) -> dict[str, Any]:
    """Extend the original comparison with query-level, evaluation-only diagnostics.

    Existing arguments and aggregate condition keys are retained. The original
    query-aware pipeline runs before fixed alternatives for each selected query.
    Recovery is disabled in every condition; no observed outcome alters routing.
    """
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("evaluation count must be a positive integer")
    if not examples:
        raise ValueError("initial-selection evaluation requires at least one query")
    if sampling not in {"prefix", "seeded"}:
        raise ValueError("sampling must be prefix or seeded")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if isinstance(bootstrap_samples, bool) or not isinstance(bootstrap_samples, int) or bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be a positive integer")
    if len({example.example_id for example in examples}) != len(examples):
        raise ValueError("evaluation query IDs must be unique")
    available = tuple(name for name in STRATEGIES if name in backends and callable(getattr(backends[name], "retrieve", None)))
    if not available:
        raise ValueError("No supported initial retrieval backend is available for evaluation")
    indices = list(range(len(examples)))
    if sampling == "seeded":
        random.Random(seed).shuffle(indices)
    selected = [examples[index] for index in indices[:count]]
    labels = (dict(label_resolutions) if label_resolutions is not None else
              {example.example_id: LabelResolution(example.supporting_document_ids, len(example.supporting_document_ids)) for example in examples})
    if any(example.example_id not in labels for example in selected):
        raise ValueError("every selected query needs a label-resolution record, including unresolved queries")
    top_k = config["retrieval"]["default_top_k"]
    esa = config["evidence_assessment"]
    conditions = (*available, "query_aware")
    pipelines = {
        condition: RetrievalControlPipeline(
            backends,
            DeterministicEvidenceAssessor(sufficient_threshold=esa["sufficient_threshold"],
                                          uncertain_threshold=esa["uncertain_threshold"], weights=esa["weights"]),
            BoundedRecoveryPolicy(max_recovery_rounds=0),
            top_k=top_k, max_top_k=config["retrieval"]["max_top_k"],
            query_analysis={**config["query_analysis"], "enabled": condition == "query_aware"},
        ) for condition in conditions
    }
    records = []
    order_rng = random.Random(seed)
    for example in selected:
        query = Query(example.example_id, example.question)
        fixed_order = list(available)
        order_rng.shuffle(fixed_order)
        order = ["query_aware", *fixed_order]
        metrics = {}
        routing = None
        for condition in order:
            result = pipelines[condition].run(query, condition if condition != "query_aware" else config["retrieval"]["backend"])
            if result.recovery_retrieval is not None or result.recovery_decision.metadata.get("recover", False):
                raise AssertionError("initial-selection evaluation must not perform recovery")
            if condition == "query_aware":
                routing = result.initial_routing
            # Gold labels enter only the offline metric function after retrieval.
            metrics[condition] = retrieval_metrics(result.initial_retrieval, labels[example.example_id], top_k,
                                                    routing_ms=result.routing_latency_ms)
        if routing is None:
            raise AssertionError("query-aware comparison must record a routing decision")
        decision = {**asdict(routing), "fallback_occurred": routing.fallback_reason is not None}
        analysis = analyze_decision(routing.selected_strategy, {name: metrics[name] for name in available},
                                    metrics["query_aware"], policy_fallback=decision["fallback_occurred"])
        replay = metrics[routing.selected_strategy]
        matches = all(metrics["query_aware"][key] == replay[key]
                      for key in ("retrieved_chunk_ids", "underlying_retrieval_calls", "resolved_support_recall_at_k"))
        if not matches:
            raise ValueError("selected backend replay changed its evidence or call count; deterministic paired comparison is invalid")
        records.append({"query_id": example.example_id, "query": example.question,
                        "category": feature_category(routing.features), "routing": decision,
                        "label_resolution": labels[example.example_id].record(), "per_retriever": metrics,
                        "decision_analysis": analysis, "execution_order": order, "selected_replay_matches_fixed": matches})
    summary = summarize(records, conditions, seed=seed, bootstrap_samples=bootstrap_samples)
    return {
        "schema_version": "initial_validation_v2", "dataset": dataset_label,
        "synthetic": dataset_label == "synthetic smoke", "requested_queries": count,
        "evaluated_queries": len(records), "available_queries": len(examples),
        "settings": {"top_k": top_k, "recovery_enabled": False, "sampling": sampling, "seed": seed,
                     "query_selection": "first N file records" if sampling == "prefix" else "seeded shuffle of available query indices, then first N",
                     "condition_order": "query-aware first; fixed alternatives shuffled per query using recorded seed",
                     "corpus": "all documents from the loaded normalized examples, common to all conditions",
                     "recall": "unique resolved support IDs in first top_k chunks; no resolved labels means null, not zero",
                     "hit": "at least one resolved support retrieved; distinct from all-support coverage",
                     "full_support_recall": "computed only for queries whose complete annotated support set resolves locally",
                     "available_backends": list(available), "corpus_examples": len(examples),
                     "corpus_documents": sum(len(example.documents) for example in examples),
                     "context_tokens": "Unicode lexical tokens, not model tokenizer tokens",
                     "router_configuration": deepcopy(config["query_analysis"]),
                     "chunking": dict(config["chunking"]), "vector": dict(config["vector"]),
                     "hybrid": {**config["hybrid"], "candidate_depth_per_child": top_k},
                     "multihop": {**config["multihop"], "candidate_depth_per_hop": top_k,
                                  "expansion": "first eight lexical tokens of top passage; output capped at top_k"}},
        "objective": dict(OBJECTIVE),
        "provenance": provenance(examples, selected, {example.example_id: labels[example.example_id] for example in selected}, config),
        "limitations": ["Provisional English query features; no entity recognizer, rarity statistics, synonym model or learned calibration.",
                        "BM25-inspired lexical; hashed-token vectors, not learned dense embeddings.",
                        "Multi-hop is bounded expansion; first-hop truncation can discard later-hop evidence.",
                        "No answer EM/F1: no answer generator is implemented.",
                        "Best-of-four is an offline diagnostic upper bound, never a deployable policy or runtime label.",
                        "Backend-limitation flags are hypotheses; observational outcomes cannot identify causal feature versus backend failures.",
                        "No quality-improvement claim; do not tune to test outcomes.",
                        "One timing observation per condition/query; total initial-stage time is router plus retrieval, excluding index construction, ESA, logging and dispatch.",
                        "Missing annotations/supports are excluded from relevant denominators, with resolution coverage reported."],
        **summary, "per_query": records,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="use the tiny synthetic integration fixture")
    parser.add_argument("--dataset", choices=("hotpotqa", "2wiki"), default="hotpotqa")
    parser.add_argument("--examples", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--sampling", choices=("prefix", "seeded"), default="prefix")
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--output-dir", type=Path, help="save aggregate JSON, per-query JSONL/CSV, and retrieval CSV")
    parser.add_argument("--config", type=Path, default=get_config_path(), help="frozen policy and retrieval configuration")
    args = parser.parse_args(argv)
    if args.examples < 1:
        parser.error("--examples must be a positive integer")
    if args.bootstrap_samples < 1:
        parser.error("--bootstrap-samples must be positive")
    config = load_config(args.config)
    examples = load_smoke_examples() if args.smoke else load_demo_dataset(args.dataset)
    processed = Path(__file__).resolve().parents[2] / "data" / "processed"
    evaluation_path = processed / "evaluation" / f"{args.dataset}_evaluation.jsonl"
    labels = None if args.smoke else resolve_labels(examples, evaluation_path, args.dataset)
    backends = build_backends([document for example in examples for document in example.documents], config)
    report = evaluate_initial(examples, backends, config, count=args.examples, seed=args.seed,
                              sampling=args.sampling, bootstrap_samples=args.bootstrap_samples,
                              label_resolutions=labels, dataset_label="synthetic smoke" if args.smoke else args.dataset)
    report["provenance"]["input_files_sha256"] = {str(args.config): file_fingerprint(args.config)}
    paths = ([Path(__file__).resolve().parents[2] / "data" / "fixtures" / "initial_routing.json"] if args.smoke else
             [processed / f"{args.dataset}_normalized.jsonl", evaluation_path])
    report["provenance"]["input_files_sha256"].update({str(path): file_fingerprint(path) for path in paths})
    if args.output_dir:
        save_reports(report, args.output_dir)
    printable = {key: value for key, value in report.items() if key != "per_query"} if args.output_dir else report
    print(json.dumps(printable, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
