"""Offline-only initial-router labels and development training workflow."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import platform
from typing import Any

from ear_rag.condition_evaluation import CONDITIONS, evaluate_conditions
from ear_rag.config.loader import get_config_path, load_config
from ear_rag.control_evaluation import EvaluationCase, write_evaluation_report
from ear_rag.data.musique import MuSiQueDataset, read_musique
from ear_rag.evaluation_metrics import mean_interval
from ear_rag.musique_experiment import LABEL, normalized, nominal_cost, sha, dump
from ear_rag.routing.initial import STRATEGIES
from ear_rag.routing.learned import POLICY, FEATURES, feature_values, fit_tree, predict, save_artifact, load_router

ROOT = Path(__file__).resolve().parents[2]


def choose_target(outcomes: dict[str, Any]) -> dict[str, Any]:
    if set(outcomes) != set(STRATEGIES): raise ValueError("four backend outcomes required")
    failed = [n for n in STRATEGIES if outcomes[n]["status"] != "evaluated"]
    if failed: return {"action": None, "reason": "incomplete_fixed_outcomes", "failed_actions": failed}
    for o in outcomes.values():
        if (type(o["recall"]) not in (int, float) or not math.isfinite(o["recall"]) or
                not 0 <= o["recall"] <= 1 or type(o["calls"]) is not int or o["calls"] < 1):
            raise ValueError("invalid label quality/call observation")
    action = min(STRATEGIES, key=lambda n: (-outcomes[n]["recall"], outcomes[n]["calls"], STRATEGIES.index(n)))
    best = outcomes[action]
    tied = [n for n in STRATEGIES if outcomes[n]["recall"] == best["recall"]]
    return {"action": action, "quality_tied_actions": tied, "zero_evidence": best["recall"] == 0,
            "objective": "max_paragraph_recall_then_min_measured_calls_then_action_order_v1"}


def validate_separation(train: MuSiQueDataset, dev: MuSiQueDataset) -> dict[str, Any]:
    if train.source_split != "train" or dev.source_split != "dev": raise ValueError("explicit train/dev split roles required")
    ids = sorted({e.example_id for e in train.examples} & {e.example_id for e in dev.examples})
    texts = sorted({normalized(e.question) for e in train.examples} & {normalized(e.question) for e in dev.examples})
    if ids or texts: raise ValueError(f"train/dev overlap: IDs={ids}, normalized questions={texts}")
    train_steps = {s['id'] for r in train.records for s in r['question_decomposition']}
    dev_steps = {s['id'] for r in dev.records for s in r['question_decomposition']}
    train_paragraphs = {normalized(d.text) for e in train.examples for d in e.documents}
    dev_paragraphs = {normalized(d.text) for e in dev.examples for d in e.documents}
    return {"question_id_overlap": ids, "normalized_question_overlap": texts,
            "shared_decomposition_ids": len(train_steps & dev_steps),
            "shared_normalized_paragraph_texts": len(train_paragraphs & dev_paragraphs),
            "train_count": len(train.examples), "dev_count": len(dev.examples),
            "train_sha256": train.source_sha256, "dev_sha256": dev.source_sha256}


def fixed_labels(dataset: MuSiQueDataset, config: dict[str, Any], directory: Path) -> list[dict[str, Any]]:
    """Bounded-memory batches through the existing condition evaluator, not a new retriever loop."""
    directory.mkdir(exist_ok=False)
    streams = {n: (directory/f"{n}.jsonl").open("x",encoding="utf-8",newline="\n") for n in STRATEGIES}
    labels = []
    try:
        for start in range(0,len(dataset.examples),64):
            examples = dataset.examples[start:start+64]
            reports = evaluate_conditions(dataset,[EvaluationCase(e.example_id) for e in examples],config,
                conditions=CONDITIONS[:4])
            for j,e in enumerate(examples):
                outcomes = {}
                for n,condition in zip(STRATEGIES,CONDITIONS[:4]):
                    row = reports[condition]["per_case"][j]
                    row["case_index"] = start+j
                    # Cache offline outcomes only; complete runtime trace retained below.
                    streams[n].write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
                    outcomes[n] = {"status":row["status"], "error":row["error"],
                        "recall":row["terminal"]["metrics"]["supporting_document_recall_at_5"] if row["status"]=="evaluated" else None,
                        "calls":row["work"]["retrieval_calls"] if row["work"] else None}
                labels.append({"question_id":e.example_id,"features":feature_values(e.question),
                               "target":choose_target(outcomes),"outcomes":outcomes})
            print(f"{dataset.source_split} fixed labels {min(start+64,len(dataset.examples))}/{len(dataset.examples)}",flush=True)
    finally:
        for stream in streams.values(): stream.close()
    with (directory/"labels.jsonl").open("x",encoding="utf-8",newline="\n") as stream:
        for row in labels: stream.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
    return labels


def select_tree(train: list[dict[str, Any]], dev: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fitted = [r for r in train if r["target"]["action"] is not None]
    valid = [r for r in dev if r["target"]["action"] is not None]
    if not fitted or not valid: raise ValueError("no complete training/development targets")
    search = []
    for depth in (0,1,2,3):
        tree = fit_tree([r["features"] for r in fitted],[r["target"]["action"] for r in fitted],max_depth=depth,min_leaf=64)
        selections = [predict(tree,r["features"]) for r in valid]
        recall = sum(r["outcomes"][p]["recall"] for r,p in zip(valid,selections))/len(valid)
        calls = sum(r["outcomes"][p]["calls"] for r,p in zip(valid,selections))
        search.append({"depth":depth,"tree":tree,"dev_recall":recall,"dev_calls":calls,
                       "dev_agreement":sum(p==r["target"]["action"] for r,p in zip(valid,selections))/len(valid),
                       "selection_counts":dict(sorted(Counter(selections).items()))})
    best = min(search,key=lambda r:(-r["dev_recall"],r["dev_calls"],r["depth"]))
    return best,search


def run(output: Path) -> None:
    if not output.is_dir() or (output/"model.json").exists(): raise ValueError("new prepared output directory required")
    train_dir=ROOT/"data/raw/musique/official_v1_0_train"
    dev_dir=ROOT/"data/raw/musique/official_v1_0"
    train=read_musique(train_dir/"musique_ans_v1.0_train.jsonl",acquisition_path=train_dir/"acquisition_manifest.json",source_split="train")
    dev=read_musique(dev_dir/"musique_ans_v1.0_dev.jsonl",acquisition_path=dev_dir/"acquisition_manifest.json")
    separation=validate_separation(train,dev)
    config=load_config(get_config_path())
    if config['retrieval']['default_top_k']!=5 or config['recovery']['max_recovery_rounds']!=1:
        raise ValueError('Phase 6A requires frozen top-k 5 and one recovery round')
    paths=list((ROOT/"src/ear_rag").rglob("*.py"))+[get_config_path(),output/"PROTOCOL.md",
        ROOT/'docs/evaluation_protocol.md', ROOT/'tests/test_learned_router.py',
        train_dir/'musique_ans_v1.0_train.jsonl',train_dir/'acquisition_manifest.json',
        dev_dir/'musique_ans_v1.0_dev.jsonl',dev_dir/'acquisition_manifest.json']
    dump(output/"frozen.json",{"label":LABEL,"python":platform.python_version(),"seed":0,
        "configuration":config,"hashes":{str(p.relative_to(ROOT)):sha(p) for p in paths}})
    dump(output/"input_validation.json",{"label":LABEL,"separation":separation,
        "train":train.manifest,"dev":dev.manifest,
        "exposure":"31 dev decomposition-text NQ matches remain potential indicators, not proof of training; no protected test"})
    train_labels=fixed_labels(train,config,output/"training")
    dev_labels=fixed_labels(dev,config,output/"development")
    best,search=select_tree(train_labels,dev_labels)
    dump(output/"model_selection.json",{"label":LABEL,"candidates":search,"selected_depth":best["depth"],
        "training_targets":dict(sorted(Counter(r["target"]["action"] for r in train_labels if r["target"]["action"]).items())),
        "train_excluded_ids":[r["question_id"] for r in train_labels if r["target"]["action"] is None],
        "dev_excluded_ids":[r["question_id"] for r in dev_labels if r["target"]["action"] is None]})
    model_sha=save_artifact(output/"model.json",best["tree"],{"depth":best["depth"],"min_leaf":64,"seed":0,
        "data":separation,"training_objective":train_labels[0]["target"].get("objective"),"feature_schema":FEATURES})
    selected=deepcopy(config)
    selected["query_analysis"]={"enabled":True,"policy":POLICY,"artifact_path":str(output/"model.json"),"artifact_sha256":model_sha}
    dump(output/"selected_config.json",selected)
    cases=[EvaluationCase(e.example_id) for e in dev.examples]
    reports={}
    for key,settings,condition in (("original_router",config,"query_aware_no_recovery"),
            ("trained_router",selected,"query_aware_no_recovery"),("trained_adaptive",selected,"adaptive_controller")):
        report=evaluate_conditions(dev,cases,settings,conditions=[condition])[condition]
        report["aggregate"]["evaluation_label"]=LABEL
        for row in report["per_case"]: row["evaluation_label"]=LABEL
        write_evaluation_report(report,output/key)
        reports[key]=report["per_case"]
        print(f"Completed {key}: {report['aggregate']['counts']}",flush=True)
    # Fixed outcomes are already measured under the same frozen settings/cases.
    for n in STRATEGIES:
        reports[n]=[json.loads(line) for line in (output/"development"/f"{n}.jsonl").read_text(encoding="utf-8").splitlines()]
    ids=[e.example_id for e in dev.examples]
    if any([r["question_id"] for r in rows]!=ids for rows in reports.values()): raise ValueError("unpaired requested IDs")
    target_counts = Counter(r['target']['action'] for r in train_labels if r['target']['action'] is not None)
    majority = min(STRATEGIES,key=lambda n:(-target_counts[n],STRATEGIES.index(n)))
    reports['training_majority'] = reports[majority]
    by_id={name:{r["question_id"]:r for r in rows} for name,rows in reports.items()}
    common=[q for q in ids if all(by_id[name][q]['status']=='evaluated' for name in reports)]
    paired={}
    for baseline in ("original_router",*STRATEGIES):
        paired[baseline]={metric:mean_interval([float(by_id['trained_router'][q]['terminal']['metrics'][metric])-float(by_id[baseline][q]['terminal']['metrics'][metric]) for q in common],seed=1729,samples=10000)
            for metric in ("hit_at_5","supporting_document_recall_at_5")}
    summary={}
    for name,rows in reports.items():
        good=[r for r in rows if r['status']=='evaluated']
        summary[name]={"requested":len(rows),"evaluated":len(good),"failed_ids":[r['question_id'] for r in rows if r['status']=='failed'],
            "hit_at_5":sum(r['terminal']['metrics']['hit_at_5'] for r in good)/len(good) if good else None,
            "paragraph_recall_at_5":sum(r['terminal']['metrics']['supporting_document_recall_at_5'] for r in good)/len(good) if good else None,
            "retrieval_calls":sum(r['work']['retrieval_calls'] for r in good),"returned_chunks":sum(r['work']['returned_chunks'] for r in good),
            "retrieval_latency_ms":sum(r['work']['retrieval_latency_ms'] for r in good),
            "nominal_initial_cost":sum(nominal_cost(r['initial_backend'],config) for r in good),
            "nominal_recovery_increment":sum(r['control']['recovery_decision']['metadata']['incremental_cost'] for r in good if r['control']['recovery_count']),
            "selection_counts":dict(sorted(Counter(r['initial_backend'] for r in good).items())),
            "recovery_count":sum(r['control']['recovery_count'] for r in good),
            "abstained":sum(r['control']['abstained'] for r in good)}
    agreements = {}
    for split,labels in (('train',train_labels),('development',dev_labels)):
        valid=[r for r in labels if r['target']['action'] is not None]
        predictions=[predict(best['tree'],r['features']) for r in valid]
        agreements[split]={'eligible':len(valid),'excluded_ids':[r['question_id'] for r in labels if r['target']['action'] is None],
            'agreement':sum(p==r['target']['action'] for p,r in zip(predictions,valid))/len(valid),
            'selection_counts':dict(sorted(Counter(predictions).items())),
            'zero_evidence_targets':sum(r['target'].get('zero_evidence',False) for r in valid)}
    groups: dict[str, Any]={}
    for group in ('dependent_signal','conceptual_without_dependent','remaining'):
        def group_for(row: dict[str, Any]) -> str:
            features=dict(zip(FEATURES,row['features']))
            return 'dependent_signal' if features['dependent'] else 'conceptual_without_dependent' if features['conceptual'] else 'remaining'
        members=[r['question_id'] for r in dev_labels if group_for(r)==group and r['question_id'] in common]
        groups[group]={'n':len(members),'reported':len(members)>=30}
        if len(members)>=30:
            groups[group]['paragraph_recall']={name:sum(by_id[name][q]['terminal']['metrics']['supporting_document_recall_at_5'] for q in members)/len(members) for name in reports}
    dump(output/"results.json",{"label":LABEL,"model_sha256":model_sha,"results":summary,"paired_count":len(common),
        "paired_ids":common,"unpaired_ids":[q for q in ids if q not in common],"trained_minus_baselines":paired,
        "label_agreement":agreements,"training_majority_action":majority,"predeclared_groups":groups})
    frozen=json.loads((output/"frozen.json").read_text(encoding='utf-8'))
    if any(sha(ROOT/p)!=s for p,s in frozen['hashes'].items()): raise ValueError('frozen sources changed during training')
    print(f"Training and development complete: {output}",flush=True)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'outputs'): raise ValueError('output must be under outputs/')
    run(output)


if __name__=='__main__': main()
