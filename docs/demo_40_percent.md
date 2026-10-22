# EAR-RAG Controlled Retrieval Demonstration

Use the editable installation described in [README](../README.md#setup-and-validate)
and run from the repository root. Start the interactive demo with:

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
The processed files are optional local assets, ignored by Git. No dataset is
downloaded by the demo, and the CLI has no built-in synthetic dataset mode.
Automated tests generate temporary normalized records instead of relying on
these local assets.

Reliability Phase 2 verified the non-interactive command above and this scripted
interactive path (controller, example zero, evidence view, exit):

```powershell
@('2','0','3','5') | .\ai-proj-new\Scripts\python.exe -m ear_rag.demo
```

Temporary-input subprocess tests additionally cover comparison/controller/
evidence/exit. Evaluation mode, invalid interactive input and all other menu
paths are not claimed as verified by this phase.

The menu offers comparison mode, EAR-RAG controller mode, retrieved-evidence
viewing, and a small preliminary evaluation (20 deterministic first examples by
default). Comparison runs BM25-style lexical, vector-flat, hybrid, and
multi-hop retrieval independently. EAR-RAG mode analyzes the query and selects
one initial strategy, then runs existing ESA and, if warranted, one CAS-selected
recovery backend. [Deterministic CAS](deterministic_cas.md) defines binary evidence
suitability, incremental cost with a .05 floor, candidate ranking and strict
CAS > threshold. No expected future ESA or evidence gain is used. Set
`query_analysis.enabled: false` to preserve the configured
`retrieval.backend`. The displayed routing scores are provisional suitability
scores, not probabilities. See [initial routing](initial_routing.md) for policy,
fallback, backend limitations, and isolated offline evaluation commands.

Every result reports operational cost proxies: retrieval calls, requested and
returned chunks, measured retrieval latency, recovery rounds, and selected
strategies. These are not monetary costs. Evidence view displays only title,
document ID, retriever, score, and retrieved text; answers and support labels
remain evaluation-only.
Titles are read from source document metadata preserved inside chunk metadata.
Total retrieval calls count executed leaf operations; returned contexts and
child retrieved passages are distinct. Retrieval latency excludes router time,
loading and index construction. CAS uses explicit nominal next-action work
assumptions; these remain separate from measured post-recovery ESA and actual
calls. Phase 5.5D/5.6 reports were produced by the previous expected-gain policy.

The controller is finite: initial retrieval, ESA, at most one recovery, second
ESA, then either `ANSWERABLE` or `ABSTAIN`. If the second ESA is insufficient,
the run abstains rather than performing another recovery. The deterministic ESA
and hashed-vector retriever are research-prototype components, so the printed
metrics are controlled preliminary demonstration metrics, not final results or
published-baseline comparisons.

`ANSWERABLE` is a controller decision only. There is no runtime answer generator,
deterministic or language-model-based, and no answer text is produced. The
internal `generate` state does not mean generation was performed. Unavailable
candidates are excluded before ranking and recorded with reasons. No eligible
candidate means stop. The pipeline's dispatch guard still rejects invalid actions
returned by custom policies; no hidden retry is added.
