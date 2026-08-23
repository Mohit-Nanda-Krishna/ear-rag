"""Core data models for EAR-RAG.

Defines the data structures that all later components will use.
All algorithms and implementation logic are intentionally omitted —
these are pure data contracts with type hints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import ClassVar


Metadata = dict[str, object]
"""Extensible, serializable metadata attached to a core contract."""


class EvidenceDecision(StrEnum):
    """Valid outcomes of evidence sufficiency assessment."""

    SUFFICIENT = "sufficient"
    UNCERTAIN = "uncertain"
    INSUFFICIENT = "insufficient"


class RecoveryActionType(StrEnum):
    """Recovery operations available to a future recovery policy."""

    NO_ACTION = "no_action"
    INCREASE_K = "increase_k"
    ALTERNATIVE_RETRIEVER = "alternative_retriever"
    QUERY_REFORMULATION = "query_reformulation"
    QUERY_DECOMPOSITION = "query_decomposition"
    HYBRID_RETRIEVAL = "hybrid_retrieval"


@dataclass
class Query:
    """Represents an incoming user question.

    Attributes:
        query_id: Unique identifier for this query.
        text: The user's question or request.
        metadata: Additional key-value metadata (e.g., source, timestamp).
    """

    query_id: str
    text: str
    metadata: Metadata = field(default_factory=dict)


@dataclass
class Document:
    """Represents a source document.

    Attributes:
        document_id: Unique identifier for this document.
        text: The full document text content.
        metadata: Additional key-value metadata (e.g., source, title, URL).
    """

    document_id: str
    text: str
    metadata: Metadata = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    """Represents a retrieved piece of evidence.

    Attributes:
        chunk_id: Unique identifier for this chunk.
        document_id: Identifier of the source document.
        text: The extracted text chunk.
        retrieval_score: Score assigned by the retriever (higher = more relevant).
        retriever_name: Name of the retriever that produced this result.
        metadata: Additional key-value metadata (e.g., position, section).
    """

    chunk_id: str
    document_id: str
    text: str
    retrieval_score: float
    retriever_name: str
    metadata: Metadata = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """Represents the output of a retrieval operation.

    Attributes:
        query_id: The query this result corresponds to.
        chunks: List of retrieved chunks, sorted by relevance.
        retriever_name: Name of the retriever that produced this result.
        top_k: Number of chunks retrieved.
        metadata: Additional key-value metadata.
    """

    query_id: str
    chunks: list[RetrievedChunk] = field(default_factory=list)
    retriever_name: str = ""
    top_k: int = 0
    metadata: Metadata = field(default_factory=dict)


@dataclass
class EvidenceAssessment:
    """Represents the output of Evidence Sufficiency Assessment.

    Attributes:
        relevance: How relevant the retrieved evidence is to the query.
        coverage: How much of the query is covered by the evidence.
        support: How well the evidence supports a potential answer.
        consistency: Whether the evidence is consistent with itself.
        overall_score: Composite score indicating sufficiency.
        decision: Final determination (sufficient / uncertain / insufficient).
        rationale: Human-readable explanation for the decision.
        metadata: Additional key-value metadata.
    """

    relevance: float = 0.0
    coverage: float = 0.0
    support: float = 0.0
    consistency: float = 0.0
    overall_score: float = 0.0
    decision: EvidenceDecision | str = EvidenceDecision.INSUFFICIENT
    rationale: str = ""
    metadata: Metadata = field(default_factory=dict)

    DECISION_SUFFICIENT: ClassVar[EvidenceDecision] = EvidenceDecision.SUFFICIENT
    DECISION_UNCERTAIN: ClassVar[EvidenceDecision] = EvidenceDecision.UNCERTAIN
    DECISION_INSUFFICIENT: ClassVar[EvidenceDecision] = EvidenceDecision.INSUFFICIENT

    def __post_init__(self) -> None:
        """Normalize and validate a decision supplied by a caller."""
        self.decision = EvidenceDecision(self.decision)


@dataclass
class RecoveryAction:
    """Represents a recovery action selected by the adaptive policy.

    Attributes:
        action_type: Type of recovery action.
        parameters: Parameters specific to the action type.
        reason: Why this action was selected.
        metadata: Additional key-value metadata.
    """

    ACTION_INCREASE_K: ClassVar[RecoveryActionType] = RecoveryActionType.INCREASE_K
    ACTION_ALTERNATIVE_RETRIEVER: ClassVar[RecoveryActionType] = (
        RecoveryActionType.ALTERNATIVE_RETRIEVER
    )
    ACTION_QUERY_REFORMULATION: ClassVar[RecoveryActionType] = (
        RecoveryActionType.QUERY_REFORMULATION
    )
    ACTION_QUERY_DECOMPOSITION: ClassVar[RecoveryActionType] = (
        RecoveryActionType.QUERY_DECOMPOSITION
    )
    ACTION_HYBRID_RETRIEVAL: ClassVar[RecoveryActionType] = (
        RecoveryActionType.HYBRID_RETRIEVAL
    )
    ACTION_NO_ACTION: ClassVar[RecoveryActionType] = RecoveryActionType.NO_ACTION

    action_type: RecoveryActionType | str = RecoveryActionType.NO_ACTION
    parameters: Metadata = field(default_factory=dict)
    reason: str = ""
    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize and validate a recovery action supplied by a caller."""
        self.action_type = RecoveryActionType(self.action_type)


@dataclass
class GenerationRequest:
    """Represents input to the generation component.

    Attributes:
        query: The original user query.
        evidence: The retrieved evidence/chunks to ground generation.
        metadata: Additional key-value metadata.
    """

    query: Query
    evidence: list[RetrievedChunk] = field(default_factory=list)
    metadata: Metadata = field(default_factory=dict)


@dataclass
class GenerationResponse:
    """Represents model output.

    Attributes:
        answer: The generated answer text.
        confidence: Confidence score or classification.
        citations: List of source citations.
        metadata: Additional key-value metadata.
    """

    answer: str = ""
    confidence: float = 0.0
    citations: list[str] = field(default_factory=list)
    metadata: Metadata = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Represents evaluation output.

    Attributes:
        metric_name: Name of the evaluation metric.
        metric_value: The computed metric value.
        sample_count: Number of samples used for this metric.
        metadata: Additional key-value metadata.
    """

    metric_name: str
    metric_value: float
    sample_count: int = 0
    metadata: Metadata = field(default_factory=dict)


__all__ = [
    "Document",
    "EvidenceAssessment",
    "EvidenceDecision",
    "EvaluationResult",
    "GenerationRequest",
    "GenerationResponse",
    "Metadata",
    "Query",
    "RecoveryAction",
    "RecoveryActionType",
    "RetrievedChunk",
    "RetrievalResult",
]
