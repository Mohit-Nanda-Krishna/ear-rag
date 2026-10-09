# Query-aware initial retrieval

The subsequent [query-analysis validation study](query_analysis_validation.md)
adds structured fallback diagnostics, per-query fixed-strategy comparisons,
evidence-label coverage, regret, paired uncertainty intervals and JSON/CSV outputs.
The 20-query check below remains a historical initial result.

## Runtime flow

`Query -> lightweight analysis -> one initial strategy -> evidence -> existing ESA -> existing bounded recovery/answerable-or-abstain decision`.

`DemoRunner.run_controller` passes the main configuration to
`RetrievalControlPipeline`. Analysis and scoring happen before any retrieval.
The pipeline dispatches one initial strategy; hybrid's two children and multi-hop's
bounded internal calls belong to that one strategy. Existing ESA and cost-aware
recovery decisions are unchanged, and the controller performs at most one recovery.
The existing recovery map can select hybrid again after an initial hybrid run;
this change does not optimize or redesign that recovery mapping.
There is still no answer generator; `ANSWERABLE` is a control decision.
**Recovery-aware initial selection remains deferred.** No initial-routing feature
or score uses predicted recovery success, future evidence/ESA, answers, or support labels.

The runtime router accepts query text and static available backend identifiers.
It constructs a metadata-free query with an empty ID for the existing
`QueryAnalyzer` contract. Only scalar feature values leave the analyzer.
The original query object, ID, text, metadata and configured `top_k` reach retrieval
and ESA unchanged. Runtime routing does not read the corpus or evaluation labels.

## Provisional policy

`LightweightQueryAnalyzer` extracts NFKC-normalized Unicode token and character
counts, quote/identifier/number/date counts, conceptual phrasing, comparisons, and
conservative English dependent-relation templates. Empty strings, whitespace, and
punctuation are accepted, matching existing retrievers; weak signals fall back.
Non-string text raises `TypeError`. Normalization does not change retrieval input.

Examples of identifiers are `XJ-42`, `ERR_INVALID_TOKEN`, and `XJ42`. Plain dates,
numbers, capitalization, length, and entity count do not independently select a
strategy. Dependency templates recognize questions such as “Where was the author
of Golden River born?” and “First identify ... then find ...”. A comparison between
two names alone does not imply dependent retrieval. These English templates can
miss relationships and can produce false positives; Unicode text is accepted,
but there is no multilingual intent model. Unsupported intents generally fall back.

Each suitability score is a bias plus the weighted sum of features. Defaults:

| Backend identifier | Nonzero default contributions |
| --- | --- |
| `local_lexical` | 4 × exact anchor |
| `vector_flat` | 3 × conceptual phrasing |
| `hybrid` | 1 × exact anchor + 1 × conceptual + 4 × mixed |
| `multihop` | 8 × explicit dependent requirement |

`exact_anchor` is true for a quoted phrase or identifier; `mixed` requires both an
exact anchor and conceptual phrasing. All biases are zero. Length, numeric/date
counts, and comparison are diagnostic features with zero default weight.
An explanation containing an exact anchor can favor hybrid, and a dependent
requirement can outweigh conceptual phrasing. These are policy hypotheses, not
empirically optimal routes. There are no reliable development-set quality/cost
estimates for initial routing in the repository; recovery estimates are deliberately
excluded. No LLM call, remote service, new dependency, or model download was added.

Scores are **heuristic suitability scores, not calibrated probabilities, accuracy,
or expected evidence gain**. The policy identifier is `query_features_v1`.
Rules and weights are provisional and need development-set calibration. Tests of
expected routes establish the policy contract, not retrieval quality or novelty.

## Configuration, eligibility, fallback, and observability

`configs/config.yaml` enables query analysis in the main demo runtime. Set
`query_analysis.enabled: false` to use `retrieval.backend` directly. Existing direct
pipeline callers that omit `query_analysis` retain their explicit initial backend.

The `query_analysis` section supports:

| Setting | Behavior |
| --- | --- |
| `enabled` | Boolean runtime switch |
| `policy` | Must be `query_features_v1` |
| `weights` | Per-strategy feature weights; each supplied row replaces that strategy's default row |
| `biases` | Optional per-strategy additive biases |
| `minimum_score` | Default 1; lower top scores trigger fallback |
| `minimum_margin` | Default 0.25; smaller top-versus-runner-up margins trigger fallback |
| `tie_break_order` | All four identifiers exactly once; deterministic rank order for equal scores |
| `fallback_backend` | Default `local_lexical` |
| `eligible_backends` | Explicit allowed subset of supported identifiers |

The router ranks all four hypotheses using arithmetic. A weak/ambiguous query or
unavailable/ineligible preferred strategy uses the configured fallback. If that
fallback is also unavailable/ineligible, the first available eligible strategy in
tie-break order is used, with an explicit substitute-fallback reason. No eligible
strategy produces a clear error. With `minimum_margin: 0`, ties use tie-break order;
with a positive margin, ties are ambiguous and use fallback.

Availability uses registry identifiers with callable retrieval methods, without
running retrieval or instantiating another backend. The current demo still builds
its existing lightweight indexes before execution, shared by composites/recovery;
there are no heavyweight factories or learned models in this implementation.
Global `default_top_k`/`max_top_k` are validated by the pipeline, existing backend
limits remain enforced, and `multihop.max_hops` still bounds internal calls.
`eligible_backends` governs initial selection only; recovery uses its existing
independent configuration. Retrieval errors propagate; routing adds no retry loop.

An `InitialRoutingDecision` records selected strategy, features, per-strategy
scores (including unavailable hypotheses), eligible identifiers, reason, fallback
reason, policy ID, and routing latency. Standard-library INFO logs record the
decision and router latency without query text or ID. The demo configures logging
from `logging.level`. `routing_latency_ms` includes feature extraction/scoring and
is separate from retrieval latency. `initial_strategy_selections` is one per run.

Existing cumulative `retrieval_call_count` fields are preserved. New
`retrieval_calls` fields count underlying operations per invocation: lexical/vector
one, hybrid two, and multi-hop actual bounded child calls. The controller and
evaluation prefer these counts, avoiding inflation from shared/reused indexes.
`retrieved_passages` includes child/hop outputs before fusion/deduplication; final
context size counts returned chunks and their characters/Unicode lexical tokens.

## Backend limitations

- `local_lexical` is a deterministic BM25-inspired scorer, not a validated external BM25 baseline.
- `vector_flat` uses 64-dimensional hashed token vectors by default. It is an architecture stand-in, **not learned dense semantic retrieval**; conceptual routing to it is an unvalidated hypothesis.
- `hybrid` fuses lexical/vector scores, requesting `top_k` candidates from each child and returning at most `top_k` chunks.
- `multihop` performs bounded lexical expansion/aggregation, appending the first eight tokens of the top passage. It does not implement learned decomposition or reliably resolve a relation chain. Its current insertion-order truncation can retain only first-hop evidence when that hop already fills `top_k`. This task preserves that backend behavior rather than claiming it solves multi-hop questions.
- ESA is deterministic and uncalibrated. No answer EM/F1 is available because generation is not implemented.

## Tests and reproducible evaluation

From the repository root in PowerShell, use the existing environment and explicitly
set the source path (the repository's startup shim does not reliably resolve it):

```powershell
$env:PYTHONPATH = "$PWD\src"
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.demo --mode ear-rag --index 0
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.evaluate_initial --smoke --examples 5
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.evaluate_initial --dataset hotpotqa --examples 20
```

Use `--dataset 2wiki` for the existing normalized 2Wiki development corpus and
`--config path/to/frozen-config.yaml` for a frozen policy. Real evaluation requires
the normalized and separate evaluation JSONL files in `data/processed` (see
`demo_40_percent.md` and `dataset_schema_report.md`). Synthetic smoke requires
only the tracked `data/fixtures/initial_routing.json`. The demo/evaluation requires
PyYAML; dataset preprocessing tests additionally require the already-installed
`pyarrow`, which is not currently declared in `requirements.txt`.

The explicitly offline command runs each registered fixed strategy and query-aware
initial routing against the same complete loaded corpus and cutoff. It disables
recovery with `max_recovery_rounds=0` for **every** condition. It selects the first
N questions in file order. Index construction is shared and excluded from reported
retrieval latency. Running all strategies here never becomes the runtime policy.
Reported metrics include locally resolved supporting-document recall@k, label
coverage, strategy distribution, fallback rate, router overhead, retrieval latency,
underlying calls, passages retrieved, and final context size. Recall uses unique
document IDs from the first `top_k` chunks, macro-averaged over queries with nonempty
local support IDs. The existing loader resolves gold titles only against each
example's local documents: missing support titles are not in its denominator, and
queries with no locally resolvable support are excluded. This is **not full-dataset
gold recall**. Label evaluation occurs only after runtime retrieval finishes.

Tune settings on development data only, then freeze the configuration and policy
code before independent test evaluation. This change did not tune to these results.
JSON reports include the router, chunking, vector, hybrid, and hop settings. Timing
is a single-run observation, not a statistically controlled performance claim.

## Measured development check (2026-10-09)

With the committed defaults, `top_k=5`, 400-character chunks with overlap 50,
64-dimensional hashed vectors, hybrid weights 0.5/0.5 and at most two hops:

| Condition | Local support recall@5 | Mean underlying calls | Mean retrieval ms |
| --- | ---: | ---: | ---: |
| Fixed lexical | 87.5% | 1.0 | 43.05 |
| Fixed hashed vector | 18.75% | 1.0 | 49.56 |
| Fixed hybrid | 68.75% | 2.0 | 90.78 |
| Fixed bounded multi-hop | 87.5% | 2.0 | 85.64 |
| Query-aware | 75.0% | 1.0 | 40.01 |

These are the first 20 HotpotQA development questions against all 500 normalized
examples' 4,957 documents. Only 16/20 had nonempty locally resolved supports; four were
excluded from recall. Query-aware routing selected lexical 17 times and hashed
vectors three times; fallback rate was 65%, and mean router overhead was 0.095 ms.
Its mean final context was 5 chunks, 1,624 characters and 271.4 lexical tokens;
mean passages retrieved was 5. All conditions made zero recovery calls.
The provisional router underperformed fixed lexical retrieval on this small check.
There is no demonstrated retrieval-quality improvement.

The five-query synthetic smoke exercised all four routes and fallback: lexical 2,
vector 1, hybrid 1, multi-hop 1; fallback 20%, seven underlying calls, zero recovery.
Every condition scored 100% recall on this deliberately tiny fixture. That result
only verifies wiring and has no research-quality interpretation.

Raw reports from this run are `outputs/initial-routing-smoke.json` and
`outputs/initial-routing-hotpotqa-dev20.json` (ignored generated outputs).
Validation: all 144 tests passed, including 76 new routing/integration/evaluation
cases; mypy checked the ten changed/new Python modules successfully with
`--follow-imports=silent --ignore-missing-imports --no-incremental` and a cache under
the temporary directory. No lint configuration or linter is installed in this
repository; `git diff --check` is used for whitespace validation.

Scoped type-check command (PowerShell, after setting `PYTHONPATH` as above):

```powershell
.\ai-proj-new\Scripts\python.exe -B -m mypy --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir "$env:TEMP\ear-rag-mypy" src/ear_rag/routing/query_analysis.py src/ear_rag/routing/initial.py src/ear_rag/routing/pipeline.py src/ear_rag/evaluate_initial.py src/ear_rag/demo.py src/ear_rag/core/interfaces.py src/ear_rag/retrieval/local.py src/ear_rag/retrieval/vector.py src/ear_rag/retrieval/hybrid.py src/ear_rag/retrieval/multihop.py
```

## Files changed

- `src/ear_rag/routing/query_analysis.py`, `initial.py`: new feature extraction, validated scoring configuration, and structured routing decisions.
- `src/ear_rag/routing/pipeline.py`, `__init__.py`: one-strategy dispatch, public exports, separate routing metrics/logs, and compatible call accounting.
- `src/ear_rag/demo.py`, `configs/config.yaml`: main runtime wiring, enabled routing, configuration-driven disabled behavior, and displayed decisions/costs.
- `src/ear_rag/core/interfaces.py`: indexable retriever protocol for existing composite backends.
- `src/ear_rag/retrieval/local.py`, `vector.py`, `hybrid.py`, `multihop.py`: per-invocation calls/passages alongside existing cumulative metadata; typed composite dependencies.
- `src/ear_rag/evaluate_initial.py`, `data/fixtures/initial_routing.json`: offline evaluation and tracked synthetic fixture.
- `tests/test_query_routing.py`, `test_initial_pipeline.py`, `test_initial_evaluation.py`: 76 new policy, integration, privacy, failure, recovery, and evaluation cases.
- `README.md`, `PROGRESS.md`, `docs/demo_40_percent.md`, `docs/initial_routing.md`: current status, launch commands, policy/configuration, reproducible evaluation and measured limitations.
