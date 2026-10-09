"""Interface contracts (Protocols) for EAR-RAG components.

These Protocol definitions establish the contracts that all later implementations
must satisfy. They deliberately depend only on Python standard library and the
core data models defined in this package.

DO NOT implement algorithmic logic here — only interface contracts.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from .models import (
    Query,
    Document,
    RetrievalResult,
    EvidenceAssessment,
    RecoveryAction,
    GenerationRequest,
    GenerationResponse,
    EvaluationResult,
)


@runtime_checkable
class Retriever(Protocol):
    """Protocol for retrieval components.

    Conceptual signature:
        retrieve(query, top_k, ...) -> RetrievalResult
    """

    def retrieve(
        self,
        query: Query,
        top_k: int,
        **kwargs: object,
    ) -> RetrievalResult:
        """Retrieve evidence for a given query.

        Args:
            query: The query to retrieve for.
            top_k: Number of results to return.
            **kwargs: Additional retriever-specific parameters.

        Returns:
            RetrievalResult containing the retrieved chunks.
        """
        ...


class IndexableRetriever(Retriever, Protocol):
    """A retriever whose in-memory corpus can be replaced before queries run."""

    def index(self, documents: Sequence[Document]) -> None: ...


@runtime_checkable
class QueryAnalyzer(Protocol):
    """Protocol for query analysis components.

    Conceptual signature:
        analyze(query) -> analysis_result
    """

    def analyze(self, query: Query) -> Mapping[str, object]:
        """Analyze a query to extract intent, entities, etc.

        Args:
            query: The query to analyze.

        Returns:
            Dictionary containing analysis results.
        """
        ...


@runtime_checkable
class EvidenceAssessor(Protocol):
    """Protocol for evidence sufficiency assessment components.

    Conceptual signature:
        assess(query, retrieval_result) -> EvidenceAssessment
    """

    def assess(
        self,
        query: Query,
        retrieval_result: RetrievalResult,
    ) -> EvidenceAssessment:
        """Assess whether the retrieved evidence is sufficient.

        Args:
            query: The original query.
            retrieval_result: The retrieval results to assess.

        Returns:
            EvidenceAssessment containing relevance, coverage, support,
            consistency, and a decision.
        """
        ...


@runtime_checkable
class RecoveryPolicy(Protocol):
    """Protocol for recovery policy components.

    Conceptual signature:
        decide(query, assessment, retrieval_result) -> RecoveryAction
    """

    def decide(
        self,
        query: Query,
        assessment: EvidenceAssessment,
        retrieval_result: RetrievalResult,
    ) -> RecoveryAction:
        """Decide on a recovery action given the assessment.

        Args:
            query: The original query.
            assessment: The ESA result.
            retrieval_result: The current retrieval results.

        Returns:
            RecoveryAction describing what to do next.
        """
        ...


@runtime_checkable
class Generator(Protocol):
    """Protocol for generation components.

    Conceptual signature:
        generate(request) -> GenerationResponse
    """

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate an answer based on a request.

        Args:
            request: The generation request containing query and evidence.

        Returns:
            GenerationResponse containing the answer and metadata.
        """
        ...


@runtime_checkable
class Evaluator(Protocol):
    """Protocol for evaluation components.

    Conceptual signature:
        evaluate(...) -> EvaluationResult or collection of results
    """

    def evaluate(
        self,
        **kwargs: object,
    ) -> EvaluationResult:
        """Evaluate system performance.

        Args:
            **kwargs: Evaluation-specific parameters.

        Returns:
            EvaluationResult containing metric name, value, and sample count.
        """
        ...
