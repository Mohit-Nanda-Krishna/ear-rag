"""Synthetic corpus/evidence contracts; no ignored datasets or research scoring."""

import json

import pytest

from ear_rag.core.models import Query, RetrievedChunk
from ear_rag.data.hotpotqa import HotpotQAValidationError, inspect_hotpotqa, read_hotpotqa
from ear_rag.data.hotpotqa_evidence import (
    build_question_corpus, locate_evidence, match_supporting_evidence,
)
from ear_rag.retrieval import (
    DeterministicVectorRetriever, DocumentChunker, HybridRetriever,
    LocalLexicalRetriever, MultiHopRetriever,
)


def source_record(identifier="q1"):
    return {"_id": identifier, "question": "Alpha target?", "answer": "LABEL_SECRET",
            "context": [["Alpha", ["Alpha first.", "Target second."]],
                        ["Beta", ["Beta distractor."]]],
            "supporting_facts": [["Alpha", 1]], "type": "bridge", "level": "hard",
            "extra": {"nested": "ANNOTATION_SECRET"}}


def load(tmp_path, records=None):
    path = tmp_path / "source.json"
    path.write_text(json.dumps(records or [source_record()], ensure_ascii=False), encoding="utf-8")
    return read_hotpotqa(path, source_split="dev"), path


def window(corpus, start, end, *, position=0, identifier="window"):
    document = corpus.documents[position]
    return RetrievedChunk(identifier, document.document_id, document.text[start:end].strip(),
                          1.0, "synthetic", {"character_start": start, "character_end": end})


def test_corpus_scopes_candidates_and_preserves_source_and_stable_ids(tmp_path):
    dataset, path = load(tmp_path, [source_record(), source_record("q2")])
    original = path.read_bytes()
    corpus = build_question_corpus(dataset, "q1")
    assert corpus.query == Query("q1", "Alpha target?")
    assert [d.document_id for d in corpus.documents] == ["hotpotqa:q1:0", "hotpotqa:q1:1"]
    assert corpus.documents[0].text == "Alpha first. Target second."
    assert corpus.documents[0].metadata["sentence_offsets"] == [
        {"start": 0, "end": 12}, {"start": 13, "end": 27},
    ]
    assert corpus.source == dataset.source
    assert corpus.documents == build_question_corpus(dataset, "q1").documents
    assert corpus.documents != build_question_corpus(dataset, "q2").documents
    assert path.read_bytes() == original
    serialized = json.dumps([d.metadata for d in corpus.documents])
    assert "LABEL_SECRET" not in serialized and "ANNOTATION_SECRET" not in serialized
    assert "supporting_facts" not in serialized and '"level"' not in serialized


def test_corpus_runtime_views_are_fresh_and_label_independent(tmp_path):
    source = source_record()
    first, _ = load(tmp_path, [source])
    source.update(answer="CHANGED", supporting_facts=[["Beta", 0]], type="comparison")
    second, _ = load(tmp_path, [source])
    a, b = build_question_corpus(first, "q1"), build_question_corpus(second, "q1")
    assert a.query == b.query and a.documents == b.documents
    a.documents[0].metadata["title"] = "modified caller copy"
    a.query.text = "modified caller copy"
    assert a.documents == b.documents and a.query == b.query
    assert a.source["sha256"] != b.source["sha256"]


def test_diagnostic_inspection_cannot_become_a_corpus_implicitly(tmp_path):
    invalid = source_record()
    invalid["supporting_facts"] = [["Alpha", 902]]
    _, path = load(tmp_path)
    path.write_text(json.dumps([source_record("valid"), invalid]), encoding="utf-8")
    inspected = inspect_hotpotqa(path, source_split="dev")
    with pytest.raises(ValueError, match="validated.*dataset"):
        build_question_corpus(inspected, "valid")
    with pytest.raises(HotpotQAValidationError):
        inspected.require_valid()


def test_unknown_question_fails_explicitly(tmp_path):
    dataset, _ = load(tmp_path)
    with pytest.raises(ValueError, match="question.*missing"):
        build_question_corpus(dataset, "missing")


def test_title_hit_is_not_a_sentence_hit(tmp_path):
    dataset, _ = load(tmp_path)
    corpus = build_question_corpus(dataset, "q1")
    first_sentence = window(corpus, 0, 12)
    located, = locate_evidence(corpus, [first_sentence])
    assert (located.question_id, located.context_position, located.title) == ("q1", 0, "Alpha")
    assert located.sentence_indices == (0,) and located.complete_sentence_indices == (0,)
    match = match_supporting_evidence(dataset, corpus, [first_sentence])
    assert match.matched_support_titles == frozenset({"Alpha"})
    assert match.matched_supports == frozenset()
    assert match.missing_supports == frozenset({("Alpha", 1)})


def test_partial_sentence_overlap_does_not_count_as_complete_support(tmp_path):
    dataset, _ = load(tmp_path)
    corpus = build_question_corpus(dataset, "q1")
    partial = window(corpus, 13, 19)
    located, = locate_evidence(corpus, [partial])
    assert located.sentence_indices == (1,) and located.complete_sentence_indices == ()
    assert not match_supporting_evidence(dataset, corpus, [partial]).matched_supports


def test_union_of_chunks_covers_support_once_and_missing_character_does_not(tmp_path):
    dataset, _ = load(tmp_path)
    corpus = build_question_corpus(dataset, "q1")
    left, right = window(corpus, 13, 18), window(corpus, 18, 27)
    match = match_supporting_evidence(dataset, corpus, [right, left, left])
    assert match.matched_supports == frozenset({("Alpha", 1)})
    assert not match.missing_supports
    assert not match_supporting_evidence(dataset, corpus, [left, window(corpus, 19, 27)]).matched_supports


def test_chunker_trimming_maps_to_actual_text_and_whitespace_gaps_are_harmless(tmp_path):
    source = source_record()
    source["context"][0][1] = ["  Alpha first. ", " Target second.  "]
    dataset, _ = load(tmp_path, [source])
    corpus = build_question_corpus(dataset, "q1")
    chunks = DocumentChunker(chunk_size=100, chunk_overlap=0).chunk_documents(corpus.documents)
    locations = locate_evidence(corpus, chunks)
    for location, chunk in zip(locations, chunks):
        doc = corpus.documents[location.context_position]
        assert doc.text[location.character_start:location.character_end] == chunk.text
    assert locations[0].complete_sentence_indices == (0, 1)
    assert match_supporting_evidence(dataset, corpus, chunks).matched_supports == frozenset({("Alpha", 1)})
    original, _ = load(tmp_path)
    c = build_question_corpus(original, "q1")
    assert match_supporting_evidence(original, c, [window(c, 13, 19), window(c, 20, 27)]).matched_supports


@pytest.mark.parametrize("mutation", [
    {"document_id": "unknown"}, {"text": "altered"},
    {"metadata": {}}, {"metadata": {"character_start": True, "character_end": 12}},
    {"metadata": {"character_start": -1, "character_end": 12}},
    {"metadata": {"character_start": 12, "character_end": 0}},
    {"metadata": {"character_start": 0, "character_end": 1000}},
])
def test_unknown_or_inconsistent_evidence_is_not_silently_matched(tmp_path, mutation):
    dataset, _ = load(tmp_path)
    corpus = build_question_corpus(dataset, "q1")
    chunk = window(corpus, 0, 12)
    for key, value in mutation.items():
        setattr(chunk, key, value)
    with pytest.raises(ValueError):
        locate_evidence(corpus, [chunk])


def test_same_title_from_other_question_or_source_cannot_match(tmp_path):
    dataset, _ = load(tmp_path, [source_record(), source_record("q2")])
    corpus = build_question_corpus(dataset, "q1")
    other = build_question_corpus(dataset, "q2")
    with pytest.raises(ValueError, match="document"):
        match_supporting_evidence(dataset, corpus, [window(other, 0, 12)])
    changed, _ = load(tmp_path, [source_record()])
    with pytest.raises(ValueError, match="source"):
        match_supporting_evidence(changed, corpus, [])


def test_empty_evidence_and_duplicate_support_annotations_are_sets(tmp_path):
    source = source_record()
    source["supporting_facts"].append(["Alpha", 1])
    dataset, _ = load(tmp_path, [source])
    match = match_supporting_evidence(dataset, build_question_corpus(dataset, "q1"), [])
    assert not match.matched_supports and not match.matched_support_titles
    assert match.missing_supports == frozenset({("Alpha", 1)})


def test_overlapping_real_chunks_recover_unicode_sentence_coverage(tmp_path):
    source = source_record()
    source["context"][0][1] = ["Caf\u00e9 \U0001f600 alpha.", "Target second sentence continues."]
    dataset, _ = load(tmp_path, [source])
    corpus = build_question_corpus(dataset, "q1")
    chunks = DocumentChunker(chunk_size=12, chunk_overlap=4).chunk_documents(corpus.documents)
    locations = locate_evidence(corpus, chunks)
    assert all(location.character_end <= len(corpus.documents[location.context_position].text)
               for location in locations)
    match = match_supporting_evidence(dataset, corpus, reversed(chunks))
    assert match.matched_supports == frozenset({("Alpha", 1)})
    assert not match.missing_supports


def test_forged_chunk_title_and_sentence_metadata_cannot_supply_support(tmp_path):
    dataset, _ = load(tmp_path)
    corpus = build_question_corpus(dataset, "q1")
    chunk = window(corpus, 0, len(corpus.documents[1].text), position=1)
    chunk.metadata.update(title="Alpha", sentence_indices=[1], supporting_facts=[["Alpha", 1]])
    located, = locate_evidence(corpus, [chunk])
    assert located.title == "Beta" and located.context_position == 1
    match = match_supporting_evidence(dataset, corpus, [chunk])
    assert not match.matched_support_titles and not match.matched_supports


@pytest.mark.parametrize("backend", ["lexical", "vector_flat", "hybrid", "multihop"])
def test_four_existing_backends_preserve_resolvable_evidence(tmp_path, backend):
    dataset, path = load(tmp_path)
    before = path.read_bytes()
    corpus = build_question_corpus(dataset, "q1")
    lexical, vector = LocalLexicalRetriever(), DeterministicVectorRetriever()
    if backend == "hybrid":
        retriever = HybridRetriever(lexical, vector)
        retriever.index(corpus.documents)
    elif backend == "multihop":
        lexical.index(corpus.documents)
        retriever = MultiHopRetriever(lexical)
    else:
        retriever = lexical if backend == "lexical" else vector
        retriever.index(corpus.documents)
    result = retriever.retrieve(corpus.query, 2)
    assert result.chunks
    locations = locate_evidence(corpus, result.chunks)
    assert all(location.question_id == "q1" for location in locations)
    assert match_supporting_evidence(dataset, corpus, result.chunks).matched_supports == frozenset({("Alpha", 1)})
    assert path.read_bytes() == before
