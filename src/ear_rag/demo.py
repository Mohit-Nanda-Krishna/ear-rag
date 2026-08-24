"""Executable controlled demonstration for the bounded EAR-RAG prototype.

This module intentionally demonstrates retrieval and evidence control only; it
does not generate answers or use evaluation supervision as retriever input.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from ear_rag.config.loader import get_config_path, load_config
from ear_rag.core.models import Document, Query, RetrievalResult
from ear_rag.evidence import DeterministicEvidenceAssessor
from ear_rag.retrieval import (
    DeterministicVectorRetriever,
    DocumentChunker,
    HybridRetriever,
    LocalLexicalRetriever,
    MultiHopRetriever,
)
from ear_rag.routing import BoundedRecoveryPolicy, RetrievalControlPipeline


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DATASET_FILES = {
    "hotpotqa": ("HotpotQA", "hotpotqa_normalized.jsonl", "hotpotqa_evaluation.jsonl"),
    "2wiki": ("2WikiMultihopQA", "2wiki_normalized.jsonl", "2wiki_evaluation.jsonl"),
}
_RETRIEVER_SAFE_METADATA = {
    "title", "dataset", "source_example_id", "context_position", "sentence_offsets",
}


@dataclass(frozen=True, slots=True)
class DemoExample:
    """A query record and its separately retained evaluation-only labels."""

    example_id: str
    question: str
    documents: tuple[Document, ...]
    supporting_document_ids: frozenset[str]


def load_demo_dataset(dataset: str) -> list[DemoExample]:
    """Load a normalized dataset while keeping supervision outside documents."""
    if dataset not in _DATASET_FILES:
        raise ValueError(f"unsupported demo dataset: {dataset}")
    _, normalized_name, evaluation_name = _DATASET_FILES[dataset]
    root = _PROJECT_ROOT / "data" / "processed"
    evaluations = {record["example_id"]: record for record in _read_jsonl(root / "evaluation" / evaluation_name)}
    examples: list[DemoExample] = []
    for record in _read_jsonl(root / normalized_name):
        documents = tuple(_document_from_record(item) for item in record["documents"])
        evaluation = evaluations.get(record["example_id"], {})
        supporting_ids = _supporting_document_ids(dataset, documents, evaluation)
        examples.append(DemoExample(str(record["example_id"]), str(record["question"]), documents, supporting_ids))
    return examples


def _read_jsonl(path: Path) -> Iterable[dict[str, object]]:
    with path.open(encoding="utf-8") as source:
        for line in source:
            if line.strip():
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError(f"expected object records in {path}")
                yield record


def _document_from_record(record: object) -> Document:
    if not isinstance(record, Mapping):
        raise ValueError("normalized document must be an object")
    metadata = {key: value for key, value in record.items() if key in _RETRIEVER_SAFE_METADATA}
    return Document(str(record["doc_id"]), str(record["text"]), metadata)


def _supporting_document_ids(dataset: str, documents: tuple[Document, ...], evaluation: Mapping[str, object]) -> frozenset[str]:
    """Resolve support titles only after retrieval, for Hit@k measurement."""
    raw = evaluation.get("evaluation", {})
    if not isinstance(raw, Mapping):
        return frozenset()
    facts = raw.get("supporting_facts", [])
    titles: set[str] = set()
    if dataset == "hotpotqa" and isinstance(facts, list):
        titles = {str(item[0]) for item in facts if isinstance(item, list) and item}
    elif dataset == "2wiki" and isinstance(facts, Mapping):
        values = facts.get("title", [])
        titles = {str(value) for value in values} if isinstance(values, list) else set()
    return frozenset(document.document_id for document in documents if document.metadata.get("title") in titles)


def _all_documents(examples: Iterable[DemoExample]) -> list[Document]:
    documents = [document for example in examples for document in example.documents]
    if len({document.document_id for document in documents}) != len(documents):
        raise ValueError("normalized corpus document IDs must be unique")
    return documents


def build_backends(documents: list[Document], config: Mapping[str, object] | None = None) -> dict[str, object]:
    """Index the existing deterministic retrievers over retriever-safe documents."""
    config = config or load_config(get_config_path())
    retrieval = config["retrieval"]
    chunking = config["chunking"]
    vector_config, hybrid_config, multihop_config = config["vector"], config["hybrid"], config["multihop"]
    chunker = DocumentChunker(int(chunking["size"]), int(chunking["overlap"]))
    lexical = LocalLexicalRetriever(chunker, name="local_lexical", max_top_k=int(retrieval["max_top_k"]))
    vector = DeterministicVectorRetriever(chunker, name="vector_flat", dimensions=int(vector_config["dimensions"]), max_top_k=int(retrieval["max_top_k"]))
    lexical.index(documents)
    vector.index(documents)
    hybrid = HybridRetriever(lexical, vector, lexical_weight=float(hybrid_config["lexical_weight"]), vector_weight=float(hybrid_config["vector_weight"]))
    multihop = MultiHopRetriever(lexical, max_hops=int(multihop_config["max_hops"]))
    return {"local_lexical": lexical, "vector_flat": vector, "hybrid": hybrid, "multihop": multihop}


class DemoRunner:
    """Thin adapter that presents existing retrieval/control components."""

    def __init__(self, dataset: str = "hotpotqa") -> None:
        self.dataset = dataset
        self.examples = load_demo_dataset(dataset)
        self.config = load_config(get_config_path())
        self.last_results: list[RetrievalResult] = []

    def _fresh_backends(self) -> dict[str, object]:
        return build_backends(_all_documents(self.examples), self.config)

    def get_example(self, index: int) -> DemoExample:
        if not 0 <= index < len(self.examples):
            raise IndexError(f"example index must be between 0 and {len(self.examples) - 1}")
        return self.examples[index]

    def compare(self, index: int) -> list[tuple[str, RetrievalResult, bool]]:
        example, query = self.get_example(index), self._query(index)
        backends = self._fresh_backends()
        results = []
        for name, label in (("local_lexical", "BM25"), ("vector_flat", "Vector Flat"), ("hybrid", "Hybrid"), ("multihop", "Multi-hop")):
            result = backends[name].retrieve(query, self._top_k())
            results.append((label, result, _has_support_hit(result, example.supporting_document_ids)))
        self.last_results = [item[1] for item in results]
        return results

    def run_controller(self, index: int):
        example = self.get_example(index)
        assessment_config, recovery_config = self.config["evidence_assessment"], self.config["recovery"]
        assessor = DeterministicEvidenceAssessor(
            sufficient_threshold=float(assessment_config["sufficient_threshold"]),
            uncertain_threshold=float(assessment_config["uncertain_threshold"]), weights=assessment_config["weights"],
        )
        policy = BoundedRecoveryPolicy(max_recovery_rounds=int(recovery_config["max_recovery_rounds"]), recovery_backends=recovery_config["recovery_backends"], max_retrieved_chunks=int(recovery_config["max_retrieved_chunks"]))
        result = RetrievalControlPipeline(self._fresh_backends(), assessor, policy, top_k=self._top_k()).run(self._query(index), "local_lexical")
        self.last_results = [result.initial_retrieval] + ([result.recovery_retrieval] if result.recovery_retrieval else [])
        return result

    def evaluate(self, count: int) -> dict[str, object]:
        selected = min(max(1, count), len(self.examples))
        method_hits = {name: 0 for name in ("BM25", "Vector Flat", "Hybrid", "Multi-hop")}
        early, recovery, abstain, calls, latency = 0, 0, 0, 0, 0.0
        for index in range(selected):
            for label, result, hit in self.compare(index):
                method_hits[label] += int(hit)
            controlled = self.run_controller(index)
            early += int(controlled.recovery_retrieval is None)
            recovery += int(controlled.recovery_retrieval is not None)
            abstain += int(controlled.final_state == "abstain")
            calls += controlled.total_retrieval_calls
            latency += controlled.total_latency_ms
        return {"count": selected, "hits": method_hits, "early": early, "recovery": recovery, "abstain": abstain, "calls": calls, "latency": latency}

    def _top_k(self) -> int:
        return int(self.config["retrieval"]["default_top_k"])

    def _query(self, index: int) -> Query:
        example = self.get_example(index)
        return Query(example.example_id, example.question, {"dataset": self.dataset})


def _has_support_hit(result: RetrievalResult, support_ids: frozenset[str]) -> bool:
    return bool(support_ids.intersection(chunk.document_id for chunk in result.chunks))


def _print_comparison(runner: DemoRunner, index: int, output: Callable[[str], None] = print) -> None:
    example = runner.get_example(index)
    output(f"\nQuestion:\n{example.question}")
    for label, result, hit in runner.compare(index):
        output(f"\n{'-' * 63}\n{label}\n{'-' * 63}")
        output(f"Retrieved documents : {len(result.chunks)}\nRetrieval calls      : {result.metadata['retrieval_call_count']}\nRequested top_k      : {result.top_k}\nLatency              : {result.metadata['retrieval_latency_ms']:.2f} ms\nHit@{result.top_k}                : {'YES' if hit else 'NO'}")


def _print_controller(runner: DemoRunner, index: int, output: Callable[[str], None] = print) -> None:
    result = runner.run_controller(index)
    output("\n===============================================================\n                  EAR-RAG CONTROLLER\n===============================================================")
    output(f"\nQuestion:\n{result.query.text}\n\nSTEP 1 - INITIAL RETRIEVAL\nStrategy        : BM25\nRetrieval calls : {result.initial_retrieval.metadata['retrieval_call_count']}\nDocuments       : {len(result.initial_retrieval.chunks)}\nLatency         : {result.initial_retrieval.metadata['retrieval_latency_ms']:.2f} ms")
    output(f"\nSTEP 2 - ESA\nEvidence score  : {result.initial_assessment.overall_score:.3f}\nDecision        : {result.initial_assessment.decision.value.upper()}")
    if result.recovery_retrieval and result.recovery_assessment:
        output(f"\nSTEP 3 - RECOVERY\nRecovery        : TRIGGERED\nStrategy        : {result.recovery_retrieval.retriever_name}\nRound           : 1 / 1")
        output(f"\nSTEP 4 - SECOND ESA\nEvidence score  : {result.recovery_assessment.overall_score:.3f}\nDecision        : {result.recovery_assessment.decision.value.upper()}")
    else:
        output("\nSTEP 3 - RECOVERY\nRecovery        : NOT REQUIRED\nRound           : 0 / 1")
    output(f"\nCOST SUMMARY\nInitial retrieval calls : {result.initial_retrieval.metadata['retrieval_call_count']}\nRecovery calls          : {result.recovery_retrieval.metadata['retrieval_call_count'] if result.recovery_retrieval else 0}\nTotal retrieval calls   : {result.total_retrieval_calls}\nRecovery rounds         : {1 if result.recovery_retrieval else 0} / 1\nTotal latency           : {result.total_latency_ms:.2f} ms\n\nFinal decision          : {'ANSWERABLE' if result.final_state == 'generate' else 'ABSTAIN'}")


def _print_evidence(results: list[RetrievalResult], output: Callable[[str], None] = print) -> None:
    if not results:
        output("No retrieval has run yet. Run comparison or EAR-RAG mode first.")
        return
    for result in results:
        output(f"\n{'=' * 63}\nRETRIEVED EVIDENCE: {result.retriever_name}\n{'=' * 63}")
        for rank, chunk in enumerate(result.chunks, 1):
            output(f"\nRank {rank}\nTitle       : {chunk.metadata.get('title', '(untitled)')}\nDocument ID : {chunk.document_id}\nRetriever   : {chunk.retriever_name}\nScore       : {chunk.retrieval_score:.4f}\nRetrieved text:\n{chunk.text}")


def _print_evaluation(runner: DemoRunner, count: int, output: Callable[[str], None] = print) -> None:
    summary = runner.evaluate(count); number = int(summary["count"])
    output("\n===============================================================\n              CONTROLLED DEMO SUMMARY\n===============================================================")
    output(f"Dataset             : {_DATASET_FILES[runner.dataset][0]}\nQuestions evaluated : {number}\n\nRETRIEVAL")
    for name, hits in summary["hits"].items(): output(f"{name} Hit@{runner._top_k():<2} : {100 * hits / number:.1f}%")
    output(f"\nEAR-RAG\nEarly stopping          : {100 * summary['early'] / number:.1f}%\nRecovery triggered      : {100 * summary['recovery'] / number:.1f}%\nAbstention               : {100 * summary['abstain'] / number:.1f}%\nAverage retrieval calls  : {summary['calls'] / number:.2f}\nAverage latency          : {summary['latency'] / number:.2f} ms\n\nPreliminary demonstration metrics only; not final research results.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="EAR-RAG controlled retrieval demonstration")
    parser.add_argument("--dataset", choices=tuple(_DATASET_FILES), default="hotpotqa")
    parser.add_argument("--mode", choices=("compare", "ear-rag", "evidence", "evaluate"))
    parser.add_argument("--index", type=int, default=0, help="deterministic zero-based example index")
    parser.add_argument("--examples", type=int, default=20, help="evaluation example count")
    args = parser.parse_args(argv)
    runner = DemoRunner(args.dataset)
    if args.mode == "compare": _print_comparison(runner, args.index)
    elif args.mode == "ear-rag": _print_controller(runner, args.index)
    elif args.mode == "evidence": _print_evidence(runner.last_results)
    elif args.mode == "evaluate": _print_evaluation(runner, args.examples)
    else:
        _interactive(runner)
    return 0


def _interactive(runner: DemoRunner) -> None:
    while True:
        print("\n===============================================================\n                 EAR-RAG RESEARCH DEMO\n        Cost-Aware Retrieval for Question Answering\n===============================================================")
        print(f"Dataset: {_DATASET_FILES[runner.dataset][0]} ({len(runner.examples)} normalized questions)\n\nMode:\n  [1] Compare Retrieval Methods\n  [2] Run Cost-Aware EAR-RAG\n  [3] View Retrieved Evidence\n  [4] Run Small Evaluation\n  [5] Exit")
        choice = input("Select: ").strip()
        if choice == "5": return
        if choice in {"1", "2"}:
            raw = input(f"Example index [0-{len(runner.examples) - 1}, default 0]: ").strip()
            index = int(raw) if raw else 0
            (_print_comparison if choice == "1" else _print_controller)(runner, index)
        elif choice == "3": _print_evidence(runner.last_results)
        elif choice == "4":
            raw = input("Examples [default 20]: ").strip(); _print_evaluation(runner, int(raw) if raw else 20)
        else: print("Select 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    raise SystemExit(main())
