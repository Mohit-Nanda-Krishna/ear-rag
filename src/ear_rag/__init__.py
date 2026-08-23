"""Evidence-Aware Adaptive Retrieval with Selective Query Recovery (EAR-RAG).

Research-grade Python project for investigating evidence-aware adaptive
retrieval policies that improve answer quality and reduce hallucinated answers.

This package exposes the core data models, interface contracts, and configuration
loader that all later components will use.
"""

__version__ = "0.1.0"
__author__ = "EAR-RAG Research Project"

# Core data models - import directly from the core package
from ear_rag.core.models import (
    Query,
    Document,
    RetrievedChunk,
    RetrievalResult,
    EvidenceAssessment,
    EvidenceDecision,
    RecoveryAction,
    RecoveryActionType,
    GenerationRequest,
    GenerationResponse,
    EvaluationResult,
)

# Core interface contracts
from ear_rag.core.interfaces import (
    Retriever,
    QueryAnalyzer,
    EvidenceAssessor,
    RecoveryPolicy,
    Generator,
    Evaluator,
)

# Configuration loader - will be loaded on demand
from ear_rag.config.loader import load_config, get_config_path, get_config_value, get_project_name, \
    get_project_version, get_default_top_k, get_max_top_k, get_sufficient_threshold, \
    get_uncertain_threshold

# Local retrieval foundation
from ear_rag.retrieval import DocumentChunker, LocalLexicalRetriever

__all__ = [
    "Query",
    "Document",
    "RetrievedChunk",
    "RetrievalResult",
    "EvidenceAssessment",
    "EvidenceDecision",
    "RecoveryAction",
    "RecoveryActionType",
    "GenerationRequest",
    "GenerationResponse",
    "EvaluationResult",
    "Retriever",
    "QueryAnalyzer",
    "EvidenceAssessor",
    "RecoveryPolicy",
    "Generator",
    "Evaluator",
    "load_config",
    "get_config_path",
    "get_config_value",
    "get_project_name",
    "get_project_version",
    "get_default_top_k",
    "get_max_top_k",
    "get_sufficient_threshold",
    "get_uncertain_threshold",
    "DocumentChunker",
    "LocalLexicalRetriever",
]
