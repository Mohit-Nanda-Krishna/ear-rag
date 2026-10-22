"""Frozen MuSiQue development orchestration over the existing condition runner.

No retrieval/controller policy lives here. Run only after synthetic/regression
checks pass; verify replays saved evidence/analysis without retrieving again.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import platform
from typing import Any, cast
import unicodedata

from ear_rag.condition_evaluation import CONDITIONS, evaluate_conditions
from ear_rag.config.loader import get_config_path, load_config
from ear_rag.control_evaluation import EvaluationCase, aggregate_cases, write_evaluation_report
from ear_rag.core.models import RetrievalResult, RetrievedChunk
from ear_rag.data.musique import read_musique
from ear_rag.data.musique_evidence import build_question_corpus, paragraph_quality
from ear_rag.evaluation_metrics import mean_interval
from ear_rag.routing.cost_awareness import incremental_cost

LABEL = "development/internal \u2014 exposure limitations apply"
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/musique/official_v1_0"
SOURCE_SHA = "15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b"
DERIVATIVE_SHA = "b8a2f97c09f666cccf9663550eab73bbecc72af4f44f75af15c84b646f49cc38"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    # Exclusive writes, finite JSON, and explicit label on every new report.
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, indent=2) + "\n")


def normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).lower().split())


def nominal_cost(backend: str, config: dict[str, Any]) -> float:
    return incremental_cost(config["recovery"]["cost_awareness"]["incremental_work"][backend])[1]


def paired_cases(reports: dict[str, Any]) -> dict[str, Any]:
    """Reject missing/duplicate/reordered requests; failures remain explicit."""
    if set(reports) != set(CONDITIONS):
        raise ValueError("all six condition outputs are required")
    reference = reports[CONDITIONS[0]]["per_case"]
    ids = [r["question_id"] for r in reference]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate requested IDs")
    exclusions = {r["question_id"]: r.get("exclusion_reason") for r in reference if r["status"] == "excluded"}
    failed: dict[str, list[str]] = {}
    completed = []
    for name in CONDITIONS:
        report = reports[name]
        rows = report["per_case"]
        if [r["question_id"] for r in rows] != ids or [r["case_index"] for r in rows] != list(range(len(ids))):
            raise ValueError(f"{name}: missing, duplicate or reordered cases")
        if report["configuration"]["retrieval"]["default_top_k"] != 5:
            raise ValueError("MuSiQue metric protocol requires frozen top-k 5")
        if {r["question_id"]: r.get("exclusion_reason") for r in rows if r["status"] == "excluded"} != exclusions:
            raise ValueError("condition exclusions disagree")
        if any(r["status"] not in {"evaluated", "failed", "excluded"} for r in rows):
            raise ValueError("unknown case status")
        failed[name] = [r["question_id"] for r in rows if r["status"] == "failed"]
        completed.append({r["question_id"] for r in rows if r["status"] == "evaluated"})
    common = set.intersection(*completed)
    return {"label": LABEL, "requested_ids": ids, "paired_ids": [q for q in ids if q in common],
            "excluded_ids": [q for q in ids if q in exclusions], "failed_ids": failed,
            "unpaired_ids": [q for q in ids if q not in common and q not in exclusions]}


def analyze(reports: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    pairing = paired_cases(reports)
    rows = {n: {r["question_id"]: r for r in reports[n]["per_case"]} for n in CONDITIONS}
    comparisons = {}
    for name in CONDITIONS[:-1]:
        metrics = {}
        for metric in ("hit_at_5", "supporting_document_recall_at_5"):
            values = []
            for q in pairing["paired_ids"]:
                a = rows["adaptive_controller"][q]["terminal"]["metrics"][metric]
                b = rows[name][q]["terminal"]["metrics"][metric]
                if a is not None and b is not None:
                    values.append(float(a) - float(b))
            metrics[metric] = {**mean_interval(values, seed=1729, samples=10000),
                               "missing_pairs": len(pairing["paired_ids"]) - len(values)}
        comparisons[name] = metrics
    conditions = {}
    for name in CONDITIONS:
        report = reports[name]
        good = [r for r in report["per_case"] if r["status"] == "evaluated"]
        recovered = [r for r in good if r["control"]["recovery_count"]]
        changes: Counter[str] = Counter()
        for r in recovered:
            delta = r["terminal"]["metrics"]["supporting_document_recall_at_5"] - r["initial"]["metrics"]["supporting_document_recall_at_5"]
            changes["improved" if delta > 0 else "worsened" if delta < 0 else "tied"] += 1
        initial_nominal = sum(nominal_cost(r["initial_backend"], config) for r in good)
        recovery_nominal = sum(r["control"]["recovery_decision"]["metadata"]["incremental_cost"] for r in recovered)
        conditions[name] = {"aggregate": report["aggregate"],
            "nominal_cost": {"units": "configured abstract work proxy; evaluated cases only",
                             "initial": initial_nominal, "recovery_increment": recovery_nominal,
                             "total": initial_nominal + recovery_nominal},
            "recovery_paragraph_recall_changes": {key: changes[key] for key in ("improved", "tied", "worsened")},
            "recovery_backend_counts": dict(sorted(Counter(r["terminal"]["retriever_name"] for r in recovered).items())),
            "reassessed_esa_decisions": dict(sorted(Counter(r["control"]["recovery_assessment"]["decision"] for r in recovered).items())),
            "final_states": dict(sorted(Counter(r["control"]["final_state"] for r in good).items())),
            "sufficient_but_incomplete_paragraph_recall": sum(r["control"]["final_state"] == "generate" and r["terminal"]["metrics"]["supporting_document_recall_at_5"] < 1 for r in good)}
    return {"label": LABEL, "pairing": pairing, "conditions": conditions,
            "adaptive_minus_baseline": comparisons,
            "uncertainty": "95% percentile paired question bootstrap; B=10000, seed=1729. Descriptive development intervals; repeated questions/components create dependence; secondary comparisons uncorrected.",
            "unavailable": ["HotpotQA sentence coverage", "answer quality/generation", "hallucination rate", "processed chunks", "controller latency", "monetary cost"]}


def validate(reports: dict[str, Any], dataset: Any, config: dict[str, Any]) -> dict[str, Any]:
    """Replay stored native paragraph matches; no retriever or router runs."""
    pairing = paired_cases(reports)
    if pairing["requested_ids"] != [e.example_id for e in dataset.examples]:
        raise ValueError("requested IDs differ from complete validated cohort")
    stages = 0
    for name in CONDITIONS:
        report = reports[name]
        settings = deepcopy(config)
        settings["query_analysis"]["enabled"] = not name.startswith("fixed_")
        if name.startswith("fixed_"):
            settings["retrieval"]["backend"] = name[len("fixed_"):-len("_no_recovery")]
        if name != "adaptive_controller": settings["recovery"]["max_recovery_rounds"] = 0
        if report["configuration"] != settings:
            raise ValueError("condition configuration differs from frozen definition")
        rebuilt = aggregate_cases(report["per_case"])
        if any(report["aggregate"][k] != value for k, value in rebuilt.items()):
            raise ValueError("saved aggregates do not match case accounting")
        for row in report["per_case"]:
            if row["configuration"] != settings or row["condition"] != name or row["source"] != dataset.source:
                raise ValueError("case source/configuration/condition mismatch")
            if row["status"] != "evaluated": continue
            corpus = build_question_corpus(dataset, row["question_id"])
            control = row["control"]
            recovered = control["recovery_count"]
            if recovered not in (0, 1) or bool(recovered) != control["recovery_triggered"]:
                raise ValueError("invalid recovery accounting")
            if name != "adaptive_controller" and recovered:
                raise ValueError("recovery ran in disabled condition")
            if bool(recovered) != (control["recovery_assessment"] is not None):
                raise ValueError("missing or spurious mandatory reassessment")
            if name.startswith("fixed_") and (control["initial_routing"] is not None or row["initial_backend"] != settings["retrieval"]["backend"]):
                raise ValueError("fixed condition did not bypass routing")
            final = control["recovery_assessment"] or control["initial_assessment"]
            if (control["final_state"] == "generate") != (final["decision"] == "sufficient"):
                raise ValueError("final sufficiency/abstention mismatch")
            for stage in ("initial", "terminal"):
                saved = row[stage]
                if saved["requested_top_k"] != 5: raise ValueError("stage top-k mismatch")
                documents = {d.doc_id: d for d in corpus.source_documents}
                chunks = []
                for c in saved["chunks"]:
                    d, location = documents[c["document_id"]], c["location"]
                    if location["context_position"] != d.context_position: raise ValueError("native paragraph idx mismatch")
                    a, b = location["character_start"], location["character_end"]
                    chunks.append(RetrievedChunk(c["chunk_id"], c["document_id"], d.text[a:b],
                        c["retrieval_score"], c["retriever_name"], {"character_start": a, "character_end": b}))
                replay = RetrievalResult(row["question_id"], chunks, saved["retriever_name"], 5)
                if paragraph_quality(dataset, corpus, replay) != saved["metrics"]:
                    raise ValueError("saved paragraph metrics fail source replay")
                stages += 1
            if recovered:
                metadata = control["recovery_decision"]["metadata"]
                if not math.isclose(metadata["cas"], (1 - control["initial_assessment"]["overall_score"]) * metadata["suitability"] / metadata["incremental_cost"]):
                    raise ValueError("CAS arithmetic mismatch")
                if metadata["cas"] <= metadata["cas_threshold"]: raise ValueError("strict CAS threshold violated")
    # Query-aware ablation and adaptive must have identical initial evidence/ESA.
    a = reports["query_aware_no_recovery"]["per_case"]
    b = reports["adaptive_controller"]["per_case"]
    for x, y in zip(a, b, strict=True):
        if x["status"] == y["status"] == "evaluated":
            if x["initial"]["chunks"] != y["initial"]["chunks"] or x["control"]["initial_assessment"] != y["control"]["initial_assessment"]:
                raise ValueError("router-only/adaptive initial states differ")
    return {"label": LABEL, "verified_stages": stages, "paired_count": len(pairing["paired_ids"]), "passed": True}


def inputs() -> tuple[Any, dict[str, Any], dict[str, Any]]:
    dataset = read_musique(RAW / "musique_ans_v1.0_dev.jsonl", acquisition_path=RAW / "acquisition_manifest.json")
    if dataset.source_sha256 != SOURCE_SHA or len(dataset.examples) != 2417:
        raise ValueError("official dev differs materially from acquisition audit")
    derivative_path = ROOT / "data/raw/musique/test.json"
    if sha(derivative_path) != DERIVATIVE_SHA: raise ValueError("third-party derivative differs from audit")
    derivative = json.loads(derivative_path.read_text(encoding="utf-8"))
    fields = ["id", "question", "answer", "answer_aliases", "answerable", "paragraphs"]
    if len(derivative) != len(dataset.records) or any(any(a[k] != b[k] for k in fields) for a, b in zip(dataset.records, derivative, strict=True)):
        raise ValueError("derivative identity/candidate/label comparison differs from audit")
    acquisition = json.loads((RAW / "acquisition_manifest.json").read_text(encoding="utf-8"))
    inventory_path = RAW / "dev_test_singlehop_questions_v1.0.json"
    expected_inventory = next(a["sha256"] for a in acquisition["artifacts"] if a["filename"] == inventory_path.name)
    if sha(inventory_path) != expected_inventory: raise ValueError("single-hop inventory checksum mismatch")
    nq_path = ROOT / "data/raw/nq/NQ-open.dev.jsonl"
    nq = {normalized(json.loads(line)["question"]) for line in nq_path.read_text(encoding="utf-8").splitlines()}
    matches = sorted({r["id"] for r in dataset.records if any(normalized(s["question"]) in nq for s in r["question_decomposition"])})
    expected = sorted({m["question_id"] for m in acquisition["verification"]["additional_exposure_check"]["official_dev_step_matches"]})
    if matches != expected or len(matches) != 31: raise ValueError("NQ matching records differ from audit")
    groups: dict[str, list[str]] = defaultdict(list)
    for r in dataset.records: groups[normalized(r["question"])].append(r["id"])
    duplicates = sorted((ids for ids in groups.values() if len(ids) > 1), key=lambda ids: ids[0])
    config = load_config(get_config_path())
    if config["retrieval"]["default_top_k"] != 5 or config["recovery"]["max_recovery_rounds"] != 1:
        raise ValueError("configuration differs from approved top-k/recovery protocol")
    identity = {"label": LABEL, "nq_potential_exposure_ids": matches,
                "nq_limit": "matching decomposition text, not proof of training use",
                "normalized_duplicate_question_groups": duplicates, "derivative_equivalent_fields": fields,
                "candidate_paragraphs": sum(len(e.documents) for e in dataset.examples),
                "support_paragraphs": sum(len(cast(list[int], e.evaluation["supporting_paragraph_indices"])) for e in dataset.examples),
                "question_ids": [e.example_id for e in dataset.examples],
                "pools": [{"question_id": e.example_id, "pool_sha256": hashlib.sha256(json.dumps(
                    [asdict(d) for d in e.documents], sort_keys=True, ensure_ascii=False).encode()).hexdigest()} for e in dataset.examples]}
    return dataset, config, identity


def report_text(analysis: dict[str, Any]) -> str:
    def number(value: Any, digits: int = 6) -> str:
        return f"{value:.{digits}f}" if value is not None else "unavailable"

    lines = ["# MuSiQue official-dev development/internal evaluation", "", LABEL, "",
        f"All {len(analysis['pairing']['requested_ids'])} validated official-dev IDs requested; {len(analysis['pairing']['excluded_ids'])} explicit exclusions. No tuning or router training.",
        "Paragraph metrics use unique parent IDs among the first five CHUNKS; title joins are forbidden.",
        "HotpotQA sentence coverage is unavailable (null), not replaced by paragraph recall.", "",
        "| Condition | Evaluated / failed / excluded | Hit@5 | Paragraph Recall@5 | Calls | Chunks | Retrieval ms (sum) | Recoveries | Abstain |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, c in analysis["conditions"].items():
        a = c["aggregate"]
        n, q, w = a["counts"], a["terminal"], a["work"]
        lines.append(f"| {name} | {n['evaluated']} / {n['failed']} / {n['excluded']} | {number(q['hit_at_5']['mean'])} | {number(q['supporting_document_recall_at_5']['mean'])} | {w['retrieval_calls']['total']} | {w['returned_chunks']['total']} | {number(w['retrieval_latency_ms']['total'], 2)} | {a['recovery_count']} | {a['final_abstention_rate']['numerator']} |")
    lines += ["", f"Common paired denominator: {len(analysis['pairing']['paired_ids'])}; unpaired: {len(analysis['pairing']['unpaired_ids'])}.",
              "", "Adaptive minus baseline (paragraph recall; paired 95% intervals):", ""]
    for name, metrics in analysis["adaptive_minus_baseline"].items():
        m = metrics["supporting_document_recall_at_5"]
        lines.append(f"- {name}: {number(m['mean'])}, CI {m['ci95']}, n={m['n']}.")
    lines += ["", "See analysis.json for Hit intervals, nominal cost, ESA/backend frequencies, recovery gains/ties/losses, missing values and complete failure/paired accounting.",
              "", analysis["uncertainty"], "", "## Limitations", "",
              "31 decomposition-text matches with local NQ indicate potential exposure; they do not establish training use. No exposure-cleared holdout or verified public labelled official-test/scoring access exists.",
              "Six duplicate normalized-question groups and shared components limit independence. All candidates/order retained; no clearance inferred from validation.",
              "BM25-inspired lexical, hashed-token vector, hybrid and lexical-expansion multi-hop are prototypes. No learned embeddings/router or generated answers are evaluated.",
              "ESA generate means evidence judged sufficient, not a verified answer. No hallucination reduction, unseen generalization or published-method superiority is established.",
              "One fixed-order timing pass measures retrieval work only; loading/index creation/controller overhead are excluded. Calls/chunks/latency are work proxies, not equal compute or money. Nominal CAS cost is separate and uncalibrated.",
              "", "## Reproduce", "", "Frozen source/config/protocol/input hashes: frozen.json. Input manifest: dataset_manifest.json; ordered IDs/pool fingerprints/NQ caveat: cohort.json. Each condition has per_case.jsonl and aggregate.json.",
              "Run `python -B -m ear_rag.musique_experiment verify --output <this-directory>` to replay saved paragraph metrics and reproduce analysis without retrieval. A new run requires a new directory and unchanged approved configuration.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "verify"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dataset, config, identity = inputs()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / "outputs").resolve()): raise ValueError("output must be under project outputs/")
    if args.mode == "run":
        output.mkdir(parents=True, exist_ok=False)
        paths = list((ROOT / "src/ear_rag").rglob("*.py")) + [get_config_path(), ROOT / "docs/evaluation_protocol.md",
            RAW / "musique_ans_v1.0_dev.jsonl", RAW / "acquisition_manifest.json", RAW / "dev_test_singlehop_questions_v1.0.json",
            ROOT / "data/raw/musique/test.json", ROOT / "data/raw/nq/NQ-open.dev.jsonl"]
        frozen: dict[str, Any] = {"label": LABEL, "python": platform.python_version(), "configuration": config,
                  "hashes": {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}}
        dump(output / "frozen.json", frozen)
        dump(output / "dataset_manifest.json", {"label": LABEL, **dataset.manifest})
        dump(output / "cohort.json", identity)
        reports = {}
        cases = [EvaluationCase(e.example_id) for e in dataset.examples]
        for name in CONDITIONS:
            print(f"Running {name}: {len(cases)} cases", flush=True)
            report = evaluate_conditions(dataset, cases, config, conditions=[name])[name]
            report["aggregate"]["evaluation_label"] = LABEL
            for row in report["per_case"]: row["evaluation_label"] = LABEL
            write_evaluation_report(report, output / name)
            reports[name] = report
            print(f"Completed {name}: {report['aggregate']['counts']}", flush=True)
        validation = validate(reports, dataset, config)
        analysis = analyze(reports, config)
        dump(output / "validation.json", validation)
        dump(output / "analysis.json", analysis)
        with (output / "REPORT.md").open("x", encoding="utf-8", newline="\n") as stream: stream.write(report_text(analysis))
        if any(sha(ROOT / p) != expected for p, expected in frozen["hashes"].items()): raise ValueError("frozen inputs changed during run")
        dump(output / "artifact_checksums.json", {p.relative_to(output).as_posix(): sha(p) for p in output.rglob("*") if p.is_file()})
        print(f"Completed: {output / 'REPORT.md'}", flush=True)
    else:
        frozen = json.loads((output / "frozen.json").read_text(encoding="utf-8"))
        if config != frozen["configuration"] or identity != json.loads((output / "cohort.json").read_text(encoding="utf-8")):
            raise ValueError("frozen configuration/cohort differs")
        if any(sha(ROOT / p) != expected for p, expected in frozen["hashes"].items()): raise ValueError("frozen source/input mismatch")
        checksums = json.loads((output / "artifact_checksums.json").read_text(encoding="utf-8"))
        if any(sha(output / p) != expected for p, expected in checksums.items()): raise ValueError("artifact checksum mismatch")
        reports = {name: {"configuration": json.loads((output / name / "aggregate.json").read_text(encoding="utf-8"))["configuration"],
                    "aggregate": json.loads((output / name / "aggregate.json").read_text(encoding="utf-8")),
                    "per_case": [json.loads(line) for line in (output / name / "per_case.jsonl").read_text(encoding="utf-8").splitlines()]} for name in CONDITIONS}
        if validate(reports, dataset, config) != json.loads((output / "validation.json").read_text(encoding="utf-8")): raise ValueError("validation replay differs")
        analysis = analyze(reports, config)
        if analysis != json.loads((output / "analysis.json").read_text(encoding="utf-8")) or report_text(analysis) != (output / "REPORT.md").read_text(encoding="utf-8"):
            raise ValueError("saved analysis/report does not reproduce")
        print("Verified frozen inputs, all artifact hashes, saved stage metrics and exact analysis/report reproduction (no retrieval).")


if __name__ == "__main__":
    main()
