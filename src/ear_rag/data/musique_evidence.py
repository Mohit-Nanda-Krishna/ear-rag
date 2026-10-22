"""Native paragraph corpora and strictly offline MuSiQue support scoring."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from ear_rag.core.models import Document, Query, RetrievalResult
from ear_rag.evaluation_metrics import LabelResolution, supporting_document_metrics
from .hotpotqa_evidence import locate_evidence
from .musique import MuSiQueDataset
from .normalization import NormalizedDocument, NormalizedExample


@dataclass(frozen=True)
class MuSiQueCorpus:
    question_id: str
    question: str
    source_documents: tuple[NormalizedDocument, ...]
    source: dict[str, str]

    @property
    def query(self) -> Query:
        # No metadata, answers, annotations, hop-prefix parsing or decomposition.
        return Query(self.question_id, self.question)

    @property
    def documents(self) -> tuple[Document, ...]:
        return tuple(Document(d.doc_id, d.text, {"title": d.title, "dataset": "musique",
                     "paragraph_idx": d.context_position, "source_example_id": self.question_id})
                     for d in self.source_documents)


def _example(dataset: MuSiQueDataset, question_id: str) -> NormalizedExample:
    if not isinstance(dataset, MuSiQueDataset):
        raise ValueError("MuSiQue evidence requires a fully validated native dataset")
    matches = dataset.example_index.get(question_id, [])
    if len(matches) != 1:
        raise ValueError(f"question {question_id!r} is missing or duplicated in dataset")
    return matches[0]


def build_question_corpus(dataset: MuSiQueDataset, question_id: str) -> MuSiQueCorpus:
    e = _example(dataset, question_id)
    return MuSiQueCorpus(e.example_id, e.question, e.documents, dataset.source)


def paragraph_quality(dataset: MuSiQueDataset, corpus: MuSiQueCorpus, result: RetrievalResult) -> dict[str, Any]:
    """First five chunks, deduplicated by native parent paragraph, never title.

    A hit credits a parent paragraph even when the retrieved window is partial;
    this does not assert complete-paragraph coverage or semantic sufficiency.
    """
    e = _example(dataset, corpus.question_id)
    if corpus.source != dataset.source or corpus.source_documents != e.documents or corpus.question != e.question:
        raise ValueError("corpus source/question does not match labelled MuSiQue dataset")
    if result.query_id != corpus.question_id:
        raise ValueError("retrieval query ID does not match evaluation case")
    locate_evidence(corpus, result.chunks)
    indices = set(cast(list[int], e.evaluation["supporting_paragraph_indices"]))
    ids = frozenset(d.doc_id for d in e.documents if d.context_position in indices)
    if len(ids) != len(indices) or not ids:
        raise ValueError("missing or ambiguous source support paragraph")
    metrics = supporting_document_metrics(result, LabelResolution(ids, len(indices)), 5)
    return {"hit_at_5": metrics["hit_at_k"],
            "supporting_document_recall_at_5": metrics["full_support_recall_at_k"],
            "supporting_evidence_coverage_at_5": None,
            "supporting_document_count": len(ids), "supporting_fact_count": None,
            "matched_supporting_document_count": metrics["matched_support_count"],
            "matched_supporting_fact_count": None,
            "metric_units": {"hit_at_5": "native_paragraph", "supporting_document_recall_at_5": "native_paragraph"},
            "unavailable_metrics": {"supporting_evidence_coverage_at_5": "MuSiQue provides paragraph support, not HotpotQA sentence annotations"}}
