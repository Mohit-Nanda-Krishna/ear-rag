# Deterministic evidence-sufficiency CAS

The runtime recovery policy is `evidence_sufficiency_cas_v1`. It replaces the
previous configured expected-ESA-gain policy. Initial query routing and ESA's
calculation/thresholds are unchanged. No new experiment validates this policy's
effectiveness; Phase 5.5D/5.6 results describe the previous implementation.

## Formula and stopping

For each executable, configured, suitable action:

```text
D = 1 - current_ESA
CAS(a) = D * S(a | current_state) / C(a)
C_raw(a) = .05 * additional_calls + .01 * additional_chunks + .001 * additional_latency_ms
C(a) = max(C_raw(a), .05)
```

Current ESA must be finite and in [0,1]; invalid scores raise an explicit error.
Suitability S is exactly 0 or 1, not a future-success probability. No predicted
future ESA, expected gain, learned suitability, answer or supporting-fact label
enters CAS. The old expected-gain/expected-work/cost-weight configuration keys are
rejected, rather than retained as another policy option.

The greatest CAS wins. Exact ties follow
`local_lexical, vector_flat, hybrid, multihop`, independently of dictionary/list
order. Recovery runs only when `best_CAS > cost_efficiency_threshold`.
The repository retains threshold **1.0** as an engineering operating value;
it has not been calibrated on development data. Equality stops recovery.
The cost floor **0.05** is an engineering safeguard in abstract work units.

For example, with illustrative current ESA=.2, S=1 and Vector Flat nominal work
1 call, 5 chunks, 10 ms: C=.11 and CAS=.8/.11=7.272727. This exceeds 1.0.
At a threshold of exactly .8/.11 the same action would be rejected. These
arithmetic examples are not experimental effectiveness or timing results.

## Observable suitability and exclusions

Tokenization reuses `LocalLexicalRetriever._tokenize`. A supported evidence gap
exists when at least one of these is observed in the current returned chunks:

- A distinct question token is missing from all evidence text.
- Two chunks have identical normalized token sequences.
- Fewer than `min(requested_top_k, 2)` chunks were returned. Two is the existing
  ESA support-saturation count, not a newly fitted threshold.

These are literal coverage/redundancy/quantity proxies. They do not establish
missing semantic facts, contradiction, entity coverage or unanswerability.
No gap means S=0 even if ESA is uncertain for another reason.

| Action | S=1 rule, in addition to a supported gap |
|---|---|
| Local lexical | Alternative, unattempted backend is callable and allowed. Uses literal token ranking. |
| Vector Flat | Alternative, unattempted backend is callable and allowed. Uses hashed-token cosine ranking; no semantic-coverage claim. |
| Hybrid | Alternative, unattempted backend is callable and allowed. Uses existing lexical/vector fusion. |
| Multi-hop | All common rules, `dependent` is exactly true in the router's feature snapshot, max_hops>=2, current backend is lexical, 0<returned chunks<top-k, and its first chunk's first eight tokens include a token absent from the question. |

Multi-hop eligibility is deliberately conservative. The backend starts a fresh
lexical search; CAS does not inject the current chunks as its seed. In the
standard factory it wraps the same lexical index. Its insertion-order final
top-k can otherwise contain only first-hop chunks, so a full initial lexical
top-k is excluded. The seed rule does not prove a missing reasoning chain.
If initial routing is disabled, no router feature snapshot is supplied and
Multi-hop recovery is ineligible. Other actions can still qualify from evidence.

Unknown actions, missing/invalid top-k, tokenless questions, already-attempted
top-level backends, unavailable backends and actions with S=0 are excluded with
recorded reasons. Shared child operations are not treated as free cached work:
Hybrid/Multi-hop can execute a previously used lexical child and those calls count.

The `recovery_backends` mapping is now an allow-list, not a single selected action.
Each source-backend entry can contain a list; a single string remains a supported
one-candidate allow-list. A `default` list applies without a source-specific entry.
The shipped default permits all four actions; no configured candidates means stop.

## Cost before selection versus work after execution

`recovery.cost_awareness.incremental_work` contains explicit **nominal next-action
work assumptions**. These are deterministic configuration, not a learned model
or an estimate derived from already-incurred initial latency.

| Action | Calls/budget | Nominal returned chunks | Nominal latency ms | Cost |
|---|---:|---:|---:|---:|
| Local lexical | 1 | 5 | 10 | .11 |
| Vector Flat | 1 | 5 | 10 | .11 |
| Hybrid | 2 | 5 | 20 | .17 |
| Multi-hop | max_hops=2 | 5 | 20 | .17 |

Lexical/vector execute one leaf call. Hybrid executes two, including when fusion
weights make one child's score contribution zero. Multi-hop may terminate early;
its configured max_hops is a reserved call budget, not predicted realized work.
Factories pass max_hops to CAS; a mismatching configured call budget is invalid.

Chunks mean the final **returned context chunks**, consistent with
`returned_chunk_count`; they do not mean processed chunks or Hybrid's child
passages. The nominal five is an explicit configuration assumption, not a
guarantee that five will be returned; review nominal work if operating top-k
changes. Latency 10/20 ms is an uncalibrated engineering assumption, not a measured
next-run latency. Do not infer speed or equal compute from these constants.

Every component is required for a configured action. Missing entries, negative,
non-numeric, non-finite or fractional count inputs exclude that candidate.
Zero raw cost in the cost helper receives the .05 floor; an executable backend
still needs its positive structural call count. Unknown work is never zero-filled.
Without an explicit incremental_work mapping, documented built-in defaults are
used; an explicitly empty mapping leaves every candidate without cost information.

Actual calls, returned chunks, child passages and latency continue to be recorded
after execution by existing backend/controller/evaluator instrumentation. They
are separate from `estimated_work` and `incremental_cost` used for selection.
Initial retrieval and earlier shared-child calls are not charged again in C(a).
No cache-reuse credit is assumed. Indexing, processed work, full-controller latency
and monetary/token/normalized-compute cost remain outside this proxy.

## Control flow and interfaces

`RetrievalControlPipeline.run` passes callable backend names, the attempted initial
backend and existing router features into `BoundedRecoveryPolicy.decide`.
Direct callers must supply `available_backends`; omitted availability means no
executable candidate is established. `attempted_backends` can record additional
attempts; current result backend is always excluded as well.

Sufficient ESA, the configured round limit, and the existing already-returned
chunk budget stop recovery before ranking. The chunk budget retains its existing
pre-action check; it is not a new guaranteed post-action bound. No candidate or
no CAS strictly above threshold also stops. The pipeline still performs at most
one recovery, reassesses its returned evidence, and abstains if final ESA is not
sufficient. No recovery loop, answer generator or retriever scoring change is added.

Decision metadata records the CAS policy version, every candidate's reason,
deficiency, suitability and nominal cost/CAS where computable. The demo displays
these values and measured work separately. The condition runner now records
`ear_rag_conditions_v2_cas`; scoring/aggregation definitions and gold-label
separation are unchanged. Existing v1 experiment reports remain untouched.

## Limits and verification

Binary S means the cheapest eligible backend wins; expensive composites cannot
outscore an eligible cheaper action merely because they have more capabilities.
Under default routing, dependent queries often start with Multi-hop, making it
unavailable as a repeated recovery action. All four actions have rules and can be
executed when eligible, but the policy does not promise to select all four in a run.
Graded suitability would require another explicit design and empirical evaluation.

Synthetic tests cover exact arithmetic, bounds, deterministic decisions/ranking,
cost floor and malformed/missing components, action exclusion, real composite
child calls, strict threshold equality, limits, reassessment, abstention, initial
routing and gold isolation. Old gain-formula assertions were replaced; valid
runtime safety tests remain. In particular, a custom policy returning an invalid
action is still caught by the pipeline's dispatch guard.

Run from the repository root:

```powershell
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_deterministic_cas.py tests/test_phase_17_cost_awareness.py tests/test_phase_15_control.py tests/test_runtime_reliability.py tests/test_initial_pipeline.py tests/test_demo.py tests/test_condition_evaluation.py
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests
.\ai-proj-new\Scripts\python.exe -B -m mypy src/ear_rag/routing/cost_awareness.py src/ear_rag/routing/recovery.py src/ear_rag/routing/pipeline.py src/ear_rag/demo.py src/ear_rag/condition_evaluation.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir "$env:TEMP\ear-rag-cas-mypy"
git diff --check
```

No Phase 5.5D/5.6 experiment was rerun. Its saved results do not validate this
replacement CAS. Independent sufficiency, provenance/exposure and holdout-validity
limitations remain unresolved; no hallucination-reduction claim is established.
