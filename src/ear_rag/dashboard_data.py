"""Read-only dashboard adapters over existing controller and saved reports."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from ear_rag.condition_evaluation import CONDITIONS, _pipeline
from ear_rag.data.musique import MuSiQueDataset
from ear_rag.data.musique_evidence import build_question_corpus
from ear_rag.routing.cost_awareness import DEFAULT_WORK, incremental_cost

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / 'data/raw/musique/official_v1_0/musique_ans_v1.0_dev.jsonl'
EXAMPLE = '2hop__152700_141308'
SOURCES = {
    'HotpotQA / revised CAS / known exposure': ('phase5-revised-cas-development-internal-known-exposure-20261022T125412Z-0e6adb98', 'aggregate'),
    'MuSiQue / Phase 5 / official development': ('phase5-musique-development-internal-20261022T153801Z-cfdcea73', 'aggregate'),
    'MuSiQue / Phase 6A / trained-router development': ('phase6a-router-development-20261022T155210Z-95732e1d', 'trained'),
}


def run_question(dataset: MuSiQueDataset, question_id: str, config: dict[str, Any]) -> dict[str, Any]:
    """Build fresh safe corpus/index/controller; gold stays outside runtime."""
    corpus = build_question_corpus(dataset, question_id)
    result = _pipeline(corpus.documents, deepcopy(config)).run(corpus.query, config['retrieval']['backend'])

    def stage(retrieval: Any, assessment: Any) -> dict[str, Any]:
        evidence = []
        for chunk in retrieval.chunks:
            source = chunk.metadata.get('document_metadata', {})
            evidence.append({'paragraph_idx': source.get('paragraph_idx'), 'title': source.get('title'),
                             'document_id': chunk.document_id, 'chunk_id': chunk.chunk_id,
                             'score': chunk.retrieval_score, 'text': chunk.text})
        return {'backend': retrieval.retriever_name, 'assessment': asdict(assessment), 'evidence': evidence,
                'work': retrieval.metadata}

    work = config['recovery']['cost_awareness'].get('incremental_work', DEFAULT_WORK)
    initial_cost = incremental_cost(work[result.initial_retrieval.retriever_name])[1]
    recovery_cost = (result.recovery_decision.metadata.get('incremental_cost')
                     if result.recovery_retrieval is not None else 0.0)
    return {'question_id': question_id, 'question': corpus.question,
            'routing': asdict(result.initial_routing) if result.initial_routing else None,
            'initial': stage(result.initial_retrieval, result.initial_assessment),
            'decision': asdict(result.recovery_decision),
            'recovery': stage(result.recovery_retrieval, result.recovery_assessment) if result.recovery_retrieval else None,
            'final_status': 'ANSWERABLE' if result.final_state == 'generate' else 'ABSTAIN',
            'calls': result.total_retrieval_calls, 'chunks': result.total_retrieved_chunks,
            'retrieval_latency_ms': result.total_latency_ms,
            'nominal_initial_cost': initial_cost, 'nominal_recovery_cost': recovery_cost,
            'configuration': deepcopy(config)}


def load_benchmarks(output_root: Path, sources: dict[str, tuple[str, str]] | None = None
                    ) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    """Display artifacts without running any evaluation or filling missing metrics."""
    tables: dict[str, list[dict[str, Any]]] = {}
    errors = []
    for label, (directory, kind) in (SOURCES if sources is None else sources).items():
        rows: list[dict[str, Any]] = []
        tables[label] = rows
        base = output_root / directory
        paths = [(name, base / name / 'aggregate.json') for name in CONDITIONS] if kind == 'aggregate' else [('trained', base / 'results.json')]
        for name, path in paths:
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                if kind == 'aggregate':
                    counts, metrics = data['counts'], data['terminal']
                    rows.append({'Condition': name, 'Hit@5': metrics['hit_at_5']['mean'],
                                 'Recall@5': metrics['supporting_document_recall_at_5']['mean'],
                                 'Retrieval calls': data['work']['retrieval_calls']['total'],
                                 'Requested': counts['requested'], 'Evaluated': counts['evaluated'],
                                 'Failed': counts['failed'], 'Excluded': counts['excluded'], 'Source': str(path)})
                else:
                    for condition, item in data['results'].items():
                        rows.append({'Condition': condition, 'Hit@5': item['hit_at_5'],
                                     'Recall@5': item['paragraph_recall_at_5'], 'Retrieval calls': item['retrieval_calls'],
                                     'Requested': item['requested'], 'Evaluated': item['evaluated'],
                                     'Failed': len(item['failed_ids']),
                                     'Excluded': item['requested'] - item['evaluated'] - len(item['failed_ids']),
                                     'Source': str(path)})
            except (OSError, ValueError, KeyError, TypeError) as exc:
                errors.append(f'{path}: {type(exc).__name__}: {exc}')
    return tables, errors
