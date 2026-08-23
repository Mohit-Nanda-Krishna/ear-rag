"""Core data models and interfaces for EAR-RAG.

This package provides the foundational data structures and type contracts
that all later components (retrieval, ESA, recovery, generation) will use.

DO NOT implement algorithmic logic here — only data contracts and interfaces.
"""

from .interfaces import (
    Evaluator,
    EvidenceAssessor,
    Generator,
    QueryAnalyzer,
    RecoveryPolicy,
    Retriever,
)
from .models import (
    Document,
    EvidenceAssessment,
    EvidenceDecision,
    EvaluationResult,
    GenerationRequest,
    GenerationResponse,
    Query,
    RecoveryAction,
    RecoveryActionType,
    RetrievedChunk,
    RetrievalResult,
)

__all__ = [
    "Document",
    "EvidenceAssessment",
    "EvidenceAssessor",
    "EvidenceDecision",
    "EvaluationResult",
    "Evaluator",
    "GenerationRequest",
    "GenerationResponse",
    "Generator",
    "Query",
    "QueryAnalyzer",
    "RecoveryAction",
    "RecoveryActionType",
    "RecoveryPolicy",
    "RetrievedChunk",
    "Retriever",
    "RetrievalResult",
]
