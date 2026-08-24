"""Dataset, preprocessing, and persistence components for EAR-RAG."""

from .datasets import (
    SUPPORTED_DATASETS,
    DatasetAdapter,
    DatasetExample,
    LocalJsonlDatasetAdapter,
    adapter_from_config,
)
from .persistence import RetrievalArtifactStore, RetrievalArtifacts
from .pipeline import RetrievalDataPipeline
from .preprocessing import DocumentPreprocessor
from .normalization import DatasetNormalizer, NormalizedCorpusBuilder, NormalizedDocument, NormalizedExample

__all__ = [
    "SUPPORTED_DATASETS",
    "DatasetAdapter",
    "DatasetExample",
    "DocumentPreprocessor",
    "LocalJsonlDatasetAdapter",
    "RetrievalArtifactStore",
    "RetrievalArtifacts",
    "RetrievalDataPipeline",
    "adapter_from_config",
    "DatasetNormalizer",
    "NormalizedCorpusBuilder",
    "NormalizedDocument",
    "NormalizedExample",
]
