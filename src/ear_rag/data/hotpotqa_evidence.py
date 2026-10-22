"""Per-question runtime corpora and offline, exact sentence-evidence matching.

No indexing policy, scoring experiment, artifact writer or source repair lives
here. Only fully validated labelled input can build a corpus through this API.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Protocol, cast

from ear_rag.core.models import Document, Query, RetrievedChunk

from .hotpotqa import HotpotQADataset
from .normalization import NormalizedDocument, NormalizedExample


@dataclass(frozen=True)
class HotpotQACorpus:
    """One question's candidate pool; source checksum is offline provenance.

    Pass query/documents to existing backends. Fresh runtime objects prevent
    backend/caller mutation from altering the canonical sentence map. No answer,
    support annotations or arbitrary example metadata enter these runtime views.
    """

    question_id: str
    question: str
    source_documents: tuple[NormalizedDocument, ...]
    source: dict[str, str]

    @property
    def query(self) -> Query:
        return Query(self.question_id, self.question)

    @property
    def documents(self) -> tuple[Document, ...]:
        documents = []
        for original in self.source_documents:
            record = original.corpus_record()
            metadata = {key: value for key, value in record.items() if key not in {"doc_id", "text"}}
            metadata.update({"source_id": self.source["identifier"],
                             "source_split": self.source["source_split"],
                             "setting": self.source["setting"]})
            documents.append(Document(original.doc_id, original.text, metadata))
        return tuple(documents)


@dataclass(frozen=True)
class EvidenceLocation:
    """Actual chunk text range and source sentence positions (zero-based).

    sentence_indices means overlap; complete_sentence_indices means this single
    chunk contains every non-whitespace character of that sentence.
    """

    chunk_id: str
    document_id: str
    question_id: str
    context_position: int
    title: str
    character_start: int
    character_end: int
    sentence_indices: tuple[int, ...]
    complete_sentence_indices: tuple[int, ...]


@dataclass(frozen=True)
class SupportingEvidenceMatch:
    """Offline set joins of (exact title, sentence index), scoped to one source.

    Title hits are separate from sentence hits. No numeric research metric or
    semantic entailment is inferred; a sentence hit requires complete text cover.
    """

    retrieved_sentences: frozenset[tuple[str, int]]
    matched_supports: frozenset[tuple[str, int]]
    missing_supports: frozenset[tuple[str, int]]
    matched_support_titles: frozenset[str]


def _get_example(dataset: HotpotQADataset, question_id: str) -> NormalizedExample:
    if not isinstance(dataset, HotpotQADataset):
        raise ValueError("corpus/evidence requires a fully validated HotpotQA dataset")
    matches = [example for example in dataset.examples if example.example_id == question_id]
    if len(matches) != 1:
        raise ValueError(f"question {question_id!r} is missing or duplicated in dataset")
    return matches[0]


def build_question_corpus(dataset: HotpotQADataset, question_id: str) -> HotpotQACorpus:
    """Adapt validated records without pooling other questions or changing IDs.

    Source + setting + question/context position scopes the normalizer's stable
    local IDs. No inspection result or silently filtered subset is accepted.
    """
    example = _get_example(dataset, question_id)
    return HotpotQACorpus(example.example_id, example.question, example.documents, dataset.source)


def _sentence_ranges(document: NormalizedDocument) -> Iterable[tuple[int, int, int]]:
    for index, (start, end) in enumerate(document.sentence_offsets):
        sentence = document.text[start:end]
        yield index, start + len(sentence) - len(sentence.lstrip()), end - len(sentence) + len(sentence.rstrip())


class EvidenceCorpus(Protocol):
    """Source-only structure shared by exact chunk-window validation."""

    @property
    def question_id(self) -> str: ...

    @property
    def source_documents(self) -> tuple[NormalizedDocument, ...]: ...


def locate_evidence(corpus: EvidenceCorpus,
                    chunks: Iterable[RetrievedChunk]) -> tuple[EvidenceLocation, ...]:
    """Resolve unmodified backend chunks using source IDs and character windows.

    Unknown documents, absent/invalid offsets or inconsistent text raise instead
    of guessing. Bounds describe the existing chunker's untrimmed window; actual
    returned text can have stripped boundary whitespace. Nested chunk metadata
    is not trusted to supply titles, sentence indices or gold annotations.
    """
    documents = {document.doc_id: document for document in corpus.source_documents}
    locations = []
    for chunk in chunks:
        if chunk.document_id not in documents:
            raise ValueError(f"chunk {chunk.chunk_id!r}: unknown source document {chunk.document_id!r}")
        document = documents[chunk.document_id]
        start, end = chunk.metadata.get("character_start"), chunk.metadata.get("character_end")
        if (isinstance(start, bool) or not isinstance(start, int) or
                isinstance(end, bool) or not isinstance(end, int) or
                not 0 <= start < end <= len(document.text)):
            raise ValueError(f"chunk {chunk.chunk_id!r}: invalid or missing character window")
        window = document.text[start:end]
        if not chunk.text or window.strip() != chunk.text:
            raise ValueError(f"chunk {chunk.chunk_id!r}: text does not match its source window")
        actual_start = start + len(window) - len(window.lstrip())
        actual_end = end - len(window) + len(window.rstrip())
        ranges = tuple(_sentence_ranges(document))
        overlapping = tuple(i for i, a, b in ranges if actual_start < b and a < actual_end)
        complete = tuple(i for i, a, b in ranges if actual_start <= a and b <= actual_end)
        locations.append(EvidenceLocation(chunk.chunk_id, document.doc_id, corpus.question_id,
                                          document.context_position, document.title,
                                          actual_start, actual_end, overlapping, complete))
    return tuple(locations)


def match_supporting_evidence(dataset: HotpotQADataset, corpus: HotpotQACorpus,
                              chunks: Iterable[RetrievedChunk]) -> SupportingEvidenceMatch:
    """Join labels offline, after resolving exact retrieved text to its source.

    Union chunk ranges per document. Overlap, adjacency and whitespace-only gaps
    can cover a sentence collectively; missing non-whitespace characters cannot.
    Repeated chunks/support annotations count once. Source mismatches raise.
    """
    example = _get_example(dataset, corpus.question_id)
    if (corpus.source != dataset.source or corpus.source_documents != example.documents or
            corpus.question != example.question):
        raise ValueError("corpus source/question does not match the labelled dataset")
    locations = locate_evidence(corpus, chunks)
    retrieved: set[tuple[str, int]] = set()
    for document in corpus.source_documents:
        intervals = sorted((location.character_start, location.character_end)
                           for location in locations if location.document_id == document.doc_id)
        merged: list[tuple[int, int]] = []
        for start, end in intervals:
            if merged and (start <= merged[-1][1] or not document.text[merged[-1][1]:start].strip()):
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        for index, start, end in _sentence_ranges(document):
            if any(a <= start and end <= b for a, b in merged):
                retrieved.add((document.title, index))
    facts = cast(list[list[Any]], example.evaluation["supporting_facts"])
    supports = {(title, index) for title, index in facts}
    retrieved_titles = {location.title for location in locations}
    return SupportingEvidenceMatch(frozenset(retrieved), frozenset(retrieved & supports),
                                   frozenset(supports - retrieved),
                                   frozenset(retrieved_titles & {title for title, _ in supports}))
