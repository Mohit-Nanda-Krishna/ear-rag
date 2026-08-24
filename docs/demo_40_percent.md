# EAR-RAG Controlled Retrieval Demonstration

Start the interactive demo with:

```powershell
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo
```

For a reproducible non-interactive run, use:

```powershell
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --dataset hotpotqa --mode ear-rag --index 0
```

The default dataset is the local normalized HotpotQA corpus. The optional
`--dataset 2wiki` uses the already-normalized 2WikiMultihopQA corpus. NQ-Open
is deliberately excluded because it has no local retrieval corpus.

The menu offers comparison mode, EAR-RAG controller mode, retrieved-evidence
viewing, and a small preliminary evaluation (20 deterministic first examples by
default). Comparison runs BM25-style lexical, vector-flat, hybrid, and
multi-hop retrieval independently. EAR-RAG mode instead runs only its initial
BM25 retrieval and, if ESA is insufficient, one configured recovery backend.

Every result reports operational cost proxies: retrieval calls, requested and
returned chunks, measured retrieval latency, recovery rounds, and selected
strategies. These are not monetary costs. Evidence view displays only title,
document ID, retriever, score, and retrieved text; answers and support labels
remain evaluation-only.

The controller is finite: initial retrieval, ESA, at most one recovery, second
ESA, then either `ANSWERABLE` or `ABSTAIN`. If the second ESA is insufficient,
the run abstains rather than performing another recovery. The deterministic ESA
and hashed-vector retriever are research-prototype components, so the printed
metrics are controlled preliminary demonstration metrics, not final results or
published-baseline comparisons.
