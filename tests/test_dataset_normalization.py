"""Tests for deterministic, retriever-safe Phase 1.6B normalization."""
import json
from pathlib import Path
import pytest
from ear_rag.data import DatasetNormalizer, NormalizedCorpusBuilder

def _hotpot():
    return {"_id":"h1","question":"Which city?","answer":"Paris","type":"bridge","level":"easy",
            "context":[["France",["Paris is in France.","France is in Europe."]]],
            "supporting_facts":[["France",0]]}
def _two_wiki():
    return {"id":"w1","question":"Who?","answer":"Ada","type":"compositional",
            "context":{"title":["Ada Lovelace","Charles Babbage"],"sentences":[["Ada wrote notes."],["Charles designed engines."]]},
            "supporting_facts":{"title":["Ada Lovelace"],"sent_id":[0]},"evidences":[["Ada","wrote","notes"]]} 

def test_hotpot_normalization_preserves_order_and_separates_support():
    example = DatasetNormalizer().normalize_hotpotqa_record(_hotpot())
    document = example.documents[0]
    assert example.example_id == "h1" and document.doc_id == "hotpotqa:h1:0"
    assert document.text == "Paris is in France. France is in Europe."
    assert document.sentence_offsets == ((0, 19), (20, 40))
    assert example.evaluation["supporting_facts"] == [["France", 0]]
    assert "supporting_facts" not in document.corpus_record()

def test_2wiki_normalization_zips_titles_and_sentences_without_supervision():
    example = DatasetNormalizer().normalize_2wiki_record(_two_wiki())
    assert [document.doc_id for document in example.documents] == ["2wiki:w1:0", "2wiki:w1:1"]
    assert [document.title for document in example.documents] == ["Ada Lovelace", "Charles Babbage"]
    assert example.evaluation["supporting_facts"]["sent_id"] == [0]
    assert "evidences" not in example.documents[0].corpus_record()

def test_nq_is_explicitly_qa_only_and_deterministic():
    normalizer = DatasetNormalizer(); record = {"question":"When?","answer":["1972","December 1972"]}
    first, second = normalizer.normalize_nq_record(record, 4), normalizer.normalize_nq_record(record, 4)
    assert first == second and first.example_id == "nq_open:4" and first.documents == ()
    assert first.metadata["requires_external_retrieval_corpus"] is True

def test_retriever_record_never_contains_answer_or_evaluation_labels():
    example = DatasetNormalizer().normalize_hotpotqa_record(_hotpot())
    serialized = json.dumps(example.documents[0].corpus_record())
    assert "supporting_facts" not in serialized and "answer" not in serialized and "Paris" in serialized

@pytest.mark.parametrize("record, method, message", [
    ({"_id":"x"}, "normalize_hotpotqa_record", "question"),
    ({"id":"x","question":"q","answer":"a","type":"t","context":{"title":["T"],"sentences":[]},"supporting_facts":{},"evidences":[]}, "normalize_2wiki_record", "equal lengths"),
])
def test_malformed_required_fields_fail_clearly(record, method, message):
    with pytest.raises(ValueError, match=message): getattr(DatasetNormalizer(), method)(record)

def test_builder_writes_equivalent_safe_records_on_repeat(tmp_path: Path):
    nq, hotpot = tmp_path / "nq.jsonl", tmp_path / "hotpot.jsonl"
    nq.write_text(json.dumps({"question":"When?","answer":["then"]}) + "\n", encoding="utf-8")
    hotpot.write_text(json.dumps(_hotpot()) + "\n", encoding="utf-8")
    import pyarrow as pa, pyarrow.parquet as pq
    wiki = tmp_path / "wiki.parquet"; pq.write_table(pa.Table.from_pylist([_two_wiki()]), wiki)
    builder = NormalizedCorpusBuilder(); output = tmp_path / "processed"
    assert builder.build(nq_path=nq, hotpotqa_path=hotpot, two_wiki_path=wiki, output_root=output) == {"hotpotqa":1,"2wiki":1,"nq_open":1}
    first = (output / "retrieval_corpus" / "hotpotqa_corpus.jsonl").read_bytes()
    builder.build(nq_path=nq, hotpotqa_path=hotpot, two_wiki_path=wiki, output_root=output)
    assert (output / "retrieval_corpus" / "hotpotqa_corpus.jsonl").read_bytes() == first
    assert not (output / "retrieval_corpus" / "nq_open_corpus.jsonl").exists()
    evaluation = (output / "evaluation" / "hotpotqa_evaluation.jsonl").read_text(encoding="utf-8")
    corpus = (output / "retrieval_corpus" / "hotpotqa_corpus.jsonl").read_text(encoding="utf-8")
    assert "supporting_facts" in evaluation and "supporting_facts" not in corpus and "answer" not in corpus
