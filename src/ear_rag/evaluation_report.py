"""Aggregate the existing evaluator's per-query offline observations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from statistics import mean
from typing import Any

from ear_rag.evaluation_metrics import group_summary, mean_interval


def summarize(records: Sequence[dict[str, Any]], conditions: Sequence[str], *,
              seed: int, bootstrap_samples: int) -> dict[str, Any]:
    def interval(values: Sequence[float]) -> dict[str, Any]:
        return mean_interval(values, seed=seed, samples=bootstrap_samples)

    aggregates = {}
    for name in conditions:
        metrics = [row["per_retriever"][name] for row in records]
        recall = [item["resolved_support_recall_at_k"] for item in metrics if item["resolved_support_recall_at_k"] is not None]
        hits = [int(item["hit_at_k"]) for item in metrics if item["hit_at_k"] is not None]
        full = [item["full_support_recall_at_k"] for item in metrics if item["full_support_recall_at_k"] is not None]
        full_covered = [int(item["full_support_covered"]) for item in metrics if item["full_support_covered"] is not None]
        distribution = Counter(row["routing"]["selected_strategy"] if name == "query_aware" else name for row in records)
        recall_ci, hit_ci = interval(recall), interval(hits)
        aggregates[name] = {
            "questions": len(records), "labeled_questions": len(recall), "fully_resolved_questions": len(full),
            "support_document_recall_at_k": recall_ci["mean"], "hit_at_k": hit_ci["mean"],
            "full_support_recall_at_k": mean(full) if full else None,
            "full_support_coverage_at_k": mean(full_covered) if full_covered else None,
            "all_resolved_support_coverage_at_k": mean([int(item["all_resolved_support_covered"]) for item in metrics if item["all_resolved_support_covered"] is not None]) if recall else None,
            "recall_interval": recall_ci, "hit_interval": hit_ci, "full_support_recall_interval": interval(full),
            "initial_strategy_distribution": dict(distribution), "initial_strategy_selections": len(records),
            "fallback_rate": mean([int(row["routing"]["fallback_occurred"]) for row in records]) if name == "query_aware" else 0.0,
            "mean_router_ms": mean([item["router_latency_ms"] for item in metrics]),
            "mean_retrieval_ms": mean([item["retrieval_latency_ms"] for item in metrics]),
            "mean_initial_stage_ms": mean([item["initial_stage_latency_ms"] for item in metrics]),
            "underlying_retrieval_calls": sum(item["underlying_retrieval_calls"] for item in metrics),
            "mean_underlying_calls": mean([item["underlying_retrieval_calls"] for item in metrics]),
            "mean_retrieved_passages": mean([item["retrieved_passages"] for item in metrics]),
            "mean_final_context_chunks": mean([item["final_context_chunks"] for item in metrics]),
            "mean_final_context_characters": mean([item["final_context_characters"] for item in metrics]),
            "mean_final_context_tokens": mean([item["final_context_tokens"] for item in metrics]),
            "mean_utility": mean([item["utility"] for item in metrics if item["utility"] is not None]) if recall else None,
            "recovery_calls": 0,
        }
    by_category = {key: group_summary([row for row in records if row["category"] == key])
                   for key in sorted({row["category"] for row in records})}
    by_backend = {key: group_summary([row for row in records if row["routing"]["selected_strategy"] == key])
                  for key in sorted({row["routing"]["selected_strategy"] for row in records})}
    by_feature = {key: group_summary([row for row in records if row["routing"]["features"][key]])
                  for key in ("exact_anchor", "conceptual", "mixed", "dependent", "comparison", "number_count", "date_count")}
    labeled = [row for row in records if row["decision_analysis"]["routing_regret"] is not None]
    paired = {}
    for name in conditions:
        if name == "query_aware":
            continue
        paired[name] = {key + "_delta": interval([float(row["per_retriever"]["query_aware"][key]) - float(row["per_retriever"][name][key]) for row in labeled])
                        for key in ("resolved_support_recall_at_k", "hit_at_k", "utility")}
    fallback = [row for row in records if row["routing"]["fallback_occurred"]]
    no_signals = sum(not row["routing"]["recognized_signals"] for row in records)
    ambiguous = sum(row["routing"]["ambiguous_scores"] for row in records)
    decision_summary = group_summary(records)
    decision_summary.update({
        "regret_interval": interval([row["decision_analysis"]["routing_regret"] for row in labeled]),
        "agreement_interval": interval([float(row["decision_analysis"]["selection_agreement"]) for row in labeled]),
        "quality_regret_interval": interval([row["decision_analysis"]["quality_regret"] for row in labeled]),
        "agreement_when_any_support_retrievable": group_summary([row for row in labeled if row["decision_analysis"]["best_observed_recall"] > 0]),
        "offline_best_observed_mean_recall": mean([row["decision_analysis"]["best_observed_recall"] for row in labeled]) if labeled else None,
        "offline_best_observed_mean_utility": mean([row["decision_analysis"]["best_observed_utility"] for row in labeled]) if labeled else None,
        "shared_incomplete_evidence_count": sum(row["decision_analysis"].get("shared_incomplete_evidence", False) for row in labeled),
    })
    annotations = [row["label_resolution"] for row in records]
    total = sum(item["annotated_support_count"] for item in annotations if item["annotated_support_count"] is not None)
    resolved = sum(item["resolved_support_count"] for item in annotations if item["annotated_support_count"] is not None)
    return {
        "conditions": aggregates,
        "label_resolution": {"queries": len(records), "queries_with_resolved_labels": len(labeled),
                             "fully_resolved_queries": sum(item["fully_resolved"] for item in annotations),
                             "status_counts": dict(Counter(item["status"] for item in annotations)),
                             "annotated_support_documents": total, "resolved_support_documents": resolved,
                             "support_label_resolution_coverage": resolved / total if total else None},
        "query_category_distribution": dict(Counter(row["category"] for row in records)),
        "fallback_diagnostics": {
            "queries": len(records), "fallback_count": len(fallback), "fallback_rate": len(fallback) / len(records),
            "fallback_rate_interval": interval([float(row["routing"]["fallback_occurred"]) for row in records]),
            "primary_reason_counts": dict(Counter(row["routing"]["fallback_code"] for row in fallback)),
            "substitution_reason_counts": dict(Counter(row["routing"]["fallback_substitution_code"] for row in fallback if row["routing"]["fallback_substitution_code"])),
            "selection_code_counts": dict(Counter(row["routing"]["selection_code"] for row in records)),
            "no_recognized_signal_count": no_signals, "no_recognized_signal_rate": no_signals / len(records),
            "ambiguous_score_count": ambiguous, "ambiguous_score_rate": ambiguous / len(records),
            "note": "Ambiguous-score flag can overlap no-signal fallback; primary reasons follow existing branch precedence. Configuration/execution errors raise and are not counted as fallback.",
            "fallback_queries": group_summary(fallback),
            "nonfallback_queries": group_summary([row for row in records if not row["routing"]["fallback_occurred"]]),
        },
        "decision_quality": decision_summary, "by_query_category": by_category,
        "by_selected_backend": by_backend, "by_feature": by_feature,
        "paired_comparisons_query_aware_minus_fixed": paired,
        "uncertainty": {"method": "paired question-level percentile bootstrap, 95% intervals", "samples": bootstrap_samples, "seed": seed,
                        "limitations": "Descriptive local development sample, not an independent test result. Corpus overlap can violate question independence; timings are single observations."},
    }
