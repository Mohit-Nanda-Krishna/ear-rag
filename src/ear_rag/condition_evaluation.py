"""Small condition matrix over the existing offline control evaluator.

This API requires an explicit dataset and case list; it neither approves inputs
nor prepares splits. Each returned report can use write_evaluation_report as-is.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import json
from typing import Any

from ear_rag.control_evaluation import EvaluationCase, evaluate_cases
from ear_rag.core.models import Document
from ear_rag.data.hotpotqa import HotpotQADataset
from ear_rag.data.musique import MuSiQueDataset
from ear_rag.demo import build_backends
from ear_rag.evidence import DeterministicEvidenceAssessor
from ear_rag.routing import BoundedRecoveryPolicy, RetrievalControlPipeline


_FIXED_BACKENDS = ("local_lexical", "vector_flat", "hybrid", "multihop")
CONDITIONS = tuple(f"fixed_{backend}_no_recovery" for backend in _FIXED_BACKENDS) + (
    "query_aware_no_recovery", "adaptive_controller")
CONDITION_VERSION = "ear_rag_conditions_v2_cas"


def _pipeline(documents: Sequence[Document], config: dict[str, Any]) -> RetrievalControlPipeline:
    """Fresh factory/index, assessor, policy and pipeline for one case only."""
    assessment, recovery, retrieval = (
        config["evidence_assessment"], config["recovery"], config["retrieval"])
    return RetrievalControlPipeline(
        build_backends(list(documents), config),
        DeterministicEvidenceAssessor(
            sufficient_threshold=float(assessment["sufficient_threshold"]),
            uncertain_threshold=float(assessment["uncertain_threshold"]), weights=assessment["weights"]),
        BoundedRecoveryPolicy(
            max_recovery_rounds=int(recovery["max_recovery_rounds"]),
            recovery_backends=recovery["recovery_backends"],
            max_retrieved_chunks=int(recovery["max_retrieved_chunks"]),
            cost_awareness=recovery["cost_awareness"], multihop_max_hops=config["multihop"]["max_hops"]),
        top_k=retrieval["default_top_k"], max_top_k=retrieval["max_top_k"],
        query_analysis=config["query_analysis"])


def evaluate_conditions(
    dataset: HotpotQADataset | MuSiQueDataset, cases: Sequence[EvaluationCase], config: Mapping[str, Any], *,
    conditions: Sequence[str] = CONDITIONS,
) -> dict[str, dict[str, Any]]:
    """Evaluate identical requested cases using isolated condition configurations.

    Fixed conditions disable initial selection; query-aware and adaptive enable
    the configured selector. Only adaptive retains the supplied recovery settings
    (including a zero limit). All other conditions set the round limit to zero.
    Backend scoring, top-k and ESA settings remain identical. Existing pipeline
    semantics cap adaptive recovery at one call and require reassessment.

    Definitions/order are deterministic; observed latency values need not be.
    Gold labels remain inside evaluate_cases' offline scoring boundary.
    """
    names, requested = tuple(conditions), tuple(cases)
    if len(set(names)) != len(names) or any(name not in CONDITIONS for name in names):
        raise ValueError("condition names must be supported and unique")
    # Require a finite JSON configuration before executing; detach caller state.
    base = json.loads(json.dumps(dict(config), allow_nan=False))
    reports = {}
    for name in names:
        settings = deepcopy(base)
        fixed = name.startswith("fixed_")
        settings["query_analysis"]["enabled"] = not fixed
        if fixed:
            settings["retrieval"]["backend"] = _FIXED_BACKENDS[CONDITIONS.index(name)]
        if name != "adaptive_controller":
            settings["recovery"]["max_recovery_rounds"] = 0

        def factory(documents: Sequence[Document]) -> RetrievalControlPipeline:
            return _pipeline(documents, deepcopy(settings))

        report = evaluate_cases(dataset, requested, factory,
                                initial_backend=str(settings["retrieval"]["backend"]))
        definition = {"condition": name, "condition_version": CONDITION_VERSION,
                      "candidate_pool": "question_scoped_source_context_v1",
                      "configuration": settings}
        report.update(deepcopy(definition))
        report["aggregate"].update(deepcopy(definition))
        for row in report["per_case"]:
            row.update(deepcopy(definition))
        reports[name] = report
    return reports
