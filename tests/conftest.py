"""Local test inputs; never depend on ignored research datasets."""

import json

import pytest

from ear_rag import demo
from ear_rag.data import DatasetNormalizer


@pytest.fixture
def demo_dataset_root(tmp_path, monkeypatch):
    """Exercise the real loader with 500 synthetic, separately labelled records."""
    processed = tmp_path / "data" / "processed"
    evaluation = processed / "evaluation"
    evaluation.mkdir(parents=True)
    normalizer = DatasetNormalizer()
    with (processed / "hotpotqa_normalized.jsonl").open("w", encoding="utf-8") as data_file, (
        evaluation / "hotpotqa_evaluation.jsonl"
    ).open("w", encoding="utf-8") as label_file:
        for index in range(500):
            example = normalizer.normalize_hotpotqa_record({
                "_id": f"synthetic-{index}",
                "question": "How do solar panels generate electricity?",
                "answer": "photovoltaic cells",
                "type": "bridge", "level": "easy",
                "context": [
                    ["Solar energy", ["Solar panels convert sunlight into electricity using photovoltaic cells."]],
                    ["Oceanography", ["Ocean currents influence coastal weather patterns."]],
                ],
                "supporting_facts": [["Solar energy", 0]],
            })
            record = example.example_record()
            # Unexpected supervision fields must still be filtered by the loader.
            for document in record["documents"]:
                for field in ("answer", "answers", "supporting_facts", "evidences", "support_sentence_ids"):
                    document[field] = "evaluation-only-marker"
            data_file.write(json.dumps(record) + "\n")
            label_file.write(json.dumps(example.evaluation_record()) + "\n")
    monkeypatch.setattr(demo, "_PROJECT_ROOT", tmp_path)
    return tmp_path
