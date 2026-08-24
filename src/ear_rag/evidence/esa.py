"""Explainable baseline Evidence Sufficiency Assessment (ESA)."""
from __future__ import annotations
from collections.abc import Mapping
from ear_rag.core.models import EvidenceAssessment, EvidenceDecision, Query, RetrievalResult
from ear_rag.retrieval.local import LocalLexicalRetriever

class DeterministicEvidenceAssessor:
    """Scores explicit retrieval/evidence signals; this is not a learned ESA."""
    def __init__(self, *, sufficient_threshold: float = .7, uncertain_threshold: float = .4,
                 weights: Mapping[str, float] | None = None) -> None:
        self._sufficient, self._uncertain = sufficient_threshold, uncertain_threshold
        self._weights = dict(weights or {"relevance": .25, "coverage": .25, "support": .25, "consistency": .25})
        if not 0 <= uncertain_threshold <= sufficient_threshold <= 1 or sum(self._weights.values()) <= 0:
            raise ValueError("ESA thresholds/weights are invalid")
    def assess(self, query: Query, retrieval_result: RetrievalResult) -> EvidenceAssessment:
        chunks = retrieval_result.chunks; query_terms = set(LocalLexicalRetriever._tokenize(query.text))
        evidence_terms = set().union(*(set(LocalLexicalRetriever._tokenize(chunk.text)) for chunk in chunks)) if chunks else set()
        coverage = len(query_terms & evidence_terms) / len(query_terms) if query_terms else 0.0
        relevance = max((chunk.retrieval_score for chunk in chunks), default=0.0)
        relevance = relevance / (1.0 + relevance) if relevance > 0 else 0.0
        support = min(1.0, len(chunks) / 2.0) * coverage
        unique_texts = {" ".join(LocalLexicalRetriever._tokenize(chunk.text)) for chunk in chunks}
        consistency = len(unique_texts) / len(chunks) if chunks else 0.0
        signals = {"relevance": relevance, "coverage": coverage, "support": support, "consistency": consistency}
        total_weight = sum(self._weights.values())
        overall = sum(signals[name] * self._weights.get(name, 0.0) for name in signals) / total_weight
        decision = EvidenceDecision.SUFFICIENT if overall >= self._sufficient else (EvidenceDecision.UNCERTAIN if overall >= self._uncertain else EvidenceDecision.INSUFFICIENT)
        reasons = [f"{name}={value:.3f}" for name, value in signals.items()]
        return EvidenceAssessment(relevance, coverage, support, consistency, overall, decision,
            f"Deterministic ESA: {decision.value}; " + ", ".join(reasons),
            {"signals": signals, "relevant_chunk_count": len(chunks), "unique_evidence_count": len(unique_texts), "confidence": overall})
