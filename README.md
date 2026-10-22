# EAR-RAG: Evidence-Aware Adaptive Retrieval with Selective Query Recovery

## Local supervisor dashboard

From `C:\ear-rag` in PowerShell, run:

```powershell
.\ai-proj-new\Scripts\python.exe -B -m streamlit run src/ear_rag/dashboard.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8501`. The Live Query Demo runs native MuSiQue questions
through the unchanged default controller with fresh state. Benchmark Results reads
existing HotpotQA/MuSiQue artifacts, including Phase 6A router comparisons; it does
not rerun experiments. All results are development/internal, with independent final
evaluation pending. See [the demo guide](docs/internal_review_demo_guide.md).
The optional UI dependency is pinned in `requirements-dashboard.txt` and installed
in the existing `ai-proj-new` environment. Stop the server with Ctrl+C.

## Research Objective
This project investigates whether an evidence-aware adaptive retrieval policy can improve answer quality and reduce unsupported/hallucinated answers compared with fixed retrieval and existing adaptive-RAG baselines.

## Architecture Components (Planned)
1. Query analysis
2. Adaptive initial retrieval
3. Evidence Sufficiency Assessment (ESA)
   - Relevance
   - Coverage
   - Support
   - Consistency
4. Confidence classification
   - High / sufficient
   - Uncertain
   - Low / insufficient
5. Selective recovery
   - Increase k
   - Alternative retriever
   - Query reformulation
   - Query decomposition
   - Hybrid retrieval
6. Re-retrieval
7. ESA reassessment
8. Local/open-source LLM generation
9. Confidence estimation
10. Optional abstention
11. Evaluation against fixed and adaptive baselines

## Current Implementation Status

**Final completion check (2026-10-22): the current retrieval/controller software
and Phase 6A development workflow are complete; independent final evaluation
remains blocked.**
No verified protected MuSiQue paragraph-support labels, authorized compatible
blind scorer, or sufficient candidate prior-use evidence is available. No final
benchmark ran. The required next step is access/independence verification, not
more development runs or model changes. See the [Phase 6B audit](outputs/phase6b-protected-evaluation-audit-20261022T161807Z-7e19b0ef/REPORT.md).

Phase 6A router training and development selection are implemented using the
official MuSiQue train/dev splits. The selected artifact is a **depth-0 decision
tree that always chooses lexical**; it matches fixed lexical on dev and provides
no observed query-dependent routing benefit. The project default remains the
original heuristic; learned inference requires explicit configuration and a
validated artifact. ESA, CAS, recovery and backends are unchanged.

[Phase 6A report, commands and limitations](outputs/phase6a-router-development-20261022T155210Z-95732e1d/REPORT.md)
and [selected model](outputs/phase6a-router-development-20261022T155210Z-95732e1d/model.json).
All development results are **development/internal — exposure limitations apply**.
The official offline gold scorer exists; protected-test gold and compatible
authorized scoring access remain unverified. Dev is model-selection data, not
a final test. No answer correctness or hallucination claim is supported.

The training command uses the existing environment and writes exclusively to a
new prepared output directory (see the frozen protocol/report before running):

```powershell
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.router_training --output outputs/<new-prepared-directory>
```

For inference only, load the saved explicit settings; no training or labels are
required. The same query_analysis settings work with RetrievalControlPipeline:

```python
from ear_rag.config.loader import load_config
from ear_rag.routing.learned import make_router

config = load_config("outputs/phase6a-router-development-20261022T155210Z-95732e1d/selected_config.json")
router = make_router(config["query_analysis"])
decision = router.select("Where was the author born?", ("local_lexical", "vector_flat", "hybrid", "multihop"))
print(decision.selected_strategy)
```

Missing or incompatible artifacts fail explicitly; there is no learned-router
fallback. Relocating the artifact requires updating its path while retaining its
SHA-256. No new ML dependency was installed. Final evaluation remains pending.

MuSiQue official-dev ingestion and a six-condition development comparison are
now available, labelled **development/internal — exposure limitations apply**.
See [the saved results](outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73/REPORT.md)
and [native data/metric protocol](docs/evaluation_protocol.md). Adaptive paragraph
Recall@5 was .473900 versus .437043 for router-only and .479555 for fixed lexical;
this does not establish answer correctness, unseen generalization or hallucination
reduction. Native paragraph IDs handle repeated titles; HotpotQA sentence coverage
is unavailable on MuSiQue. Existing runtime policy/configuration is unchanged.

Historical Phase 5 verification checks the frozen Phase 5 source hashes; it needs
that implementation, rather than the subsequently extended Phase 6A runtime.
Its original read-only command (PowerShell) is:

```powershell
Set-Location C:\ear-rag
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.musique_experiment verify --output outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73
```

The module also provides `run --output outputs/<new-unique-name>` over the existing
condition runner. Use only after ingestion/isolation/regression gates pass and
an explicitly frozen development protocol; it rejects existing output directories.
No data download or new dependency is needed for that historical workflow. Phase
6A training is recorded separately above; Phase 5 outputs remain unchanged.

The Python package in `src/ear_rag/` implements local dataset processing,
retrieval, deterministic evidence assessment, and bounded cost-aware recovery.
Query-aware initial routing is enabled in `configs/config.yaml`:

`Question -> lightweight query analysis -> one initial strategy -> evidence -> ESA -> at most one recovery -> ANSWERABLE or ABSTAIN`.

The provisional scoring policy favors lexical retrieval for exact anchors,
vector-flat for conceptual phrasing, hybrid for mixed requirements, and bounded
multi-hop for explicit dependent requirements. It returns features, heuristic
suitability scores, a reason, fallback information, and router latency. Ambiguous
or unavailable choices use the configured fallback. Disabling query analysis
restores `retrieval.backend`. Initial selection never consults gold labels, ESA
outcomes, or predicted recovery success; recovery-aware initial selection is deferred.

Backends are research prototypes: BM25-inspired lexical scoring, hashed-token
vectors rather than learned dense embeddings, score-fusion hybrid, and bounded
lexical expansion rather than learned multi-hop decomposition. No LLM answer
generation is implemented. The planned architecture above includes future work.

See [routing policy, configuration, tests and measured evaluation](docs/initial_routing.md)
and [demo usage](docs/demo_40_percent.md).

Recovery now uses deterministic evidence-sufficiency CAS:
`CAS=(1-current_ESA)*binary_suitability/max(.05*calls+.01*chunks+.001*latency_ms,.05)`.
It ranks executable, allowed, unattempted actions and recovers only when CAS is
strictly greater than the configured threshold (currently 1.0). Suitability uses
observable evidence gaps; no predicted ESA/gain or learned recovery model remains.
Costs are nominal incremental work assumptions, separate from realized telemetry.
See [exact rules, costs, interfaces and limitations](docs/deterministic_cas.md).
Phase 5.5D/5.6 outputs describe the previous policy and do not validate this change;
the current condition version is `ear_rag_conditions_v2_cas`. A separate
[frozen revised-CAS evaluation](outputs/phase5-revised-cas-development-internal-known-exposure-20261022T125412Z-0e6adb98/REPORT.md)
is now complete, labelled **development/internal — known exposure**.

The [500-query validation study](docs/query_analysis_validation.md) adds per-query
fallback causes, evidence-label coverage, decision regret, paired comparisons and
JSON/CSV reports. It preserves the existing routing policy and documents where
its features and prototype backends fail.

## Dataset and evaluation roadmap

**Current Phase 5 status (verified 2026-10-22): partially complete.** Data/evidence
and evaluation tooling, the condition runner, and revised deterministic CAS are
implemented and pass software verification. The six-condition Phase 5.5D run and
Phase 5.6 analysis are complete **development/internal — known exposure** work
under the previous expected-gain policy. The revised CAS was separately evaluated
on the same 497 usable exposed questions: all six conditions completed without
failures, retaining three exclusions from 500 requests. Adaptive document recall
rose 1.509 percentage points over query-aware/no-recovery (paired bootstrap 95%
interval .503–2.616), with 19 extra calls, but remained below fixed lexical recall
by 1.811 points while using 40 more calls. Of 19 recoveries, evidence coverage
improved 13, tied 3 and worsened 3. These are diagnostic cohort results.
Original source-provenance, exposure-history and approved holdout/split
gates remain unresolved; the proposed 100/200 roles are still provisional.
See the [current diagnostic evaluation and remaining gates](docs/evaluation_protocol.md#19-frozen-revised-cas-diagnostic-evaluation-2026-10-22).

Phase 5.5C adds the small Python API
`ear_rag.condition_evaluation.evaluate_conditions(dataset, cases, config)`.
It returns existing evaluator reports for four fixed backends without recovery,
query-aware selection without recovery, and the adaptive controller. Each case
gets fresh indexes and controller state; comparable conditions share candidate
pools, top-k and backend settings. Fixed conditions bypass initial selection.
Reports include condition/configuration metadata and reuse existing serialization.
See [condition definitions and usage](docs/evaluation_protocol.md#17-phase-55c-minimal-baseline-condition-runner).
The Phase 5.5C checkpoint used synthetic fixtures only (17 new tests; 423 total).
Subsequent authorized Phase 5.5D evaluation requested the same 500 exposed IDs in
all six conditions: 497 evaluated, zero failures and three explicit exclusions.
The [saved experiment report](outputs/phase55d-development-internal-known-exposure-20261020T185946Z-c62ca682/REPORT.md)
and [Phase 5.6 analysis](outputs/phase56-analysis-development-internal-known-exposure-20261020T191125Z-ab9ca032/PHASE56_FINAL_REPORT.md)
remain previous-policy evidence. Current focused CAS/regression checks pass 114
tests; the full suite passes 470 tests. Passing invalid-record checks or software
tests grants neither exposure clearance nor effectiveness evidence.

[Phase 5.1 protocol](docs/evaluation_protocol.md) documents the proposed first
dataset: a small HotpotQA distractor development subset with **per-question
candidate pools**, not full-Wikipedia retrieval. It separates runtime questions/
documents, development labels and held-out labels; defines metrics and leakage
checks; and gives the Phase 5.2/5.3 plan. Proposed 100 development / 200 internal
held-out roles within official dev require review and a prior-exposure inventory.
Earlier development examples cannot be treated as unseen test questions.

Phase 5.2 now provides a labelled train/dev JSON-array reader and separate runtime
and evaluation projections in `ear_rag.data.hotpotqa`, verified with synthetic
fixtures. It rejects malformed/duplicate records and unresolved supporting facts;
it does not support unlabelled blind-test inputs. Type/level are optional offline
annotations. The [bounded real-data gate](docs/evaluation_protocol.md#10-bounded-real-data-completion-gate-2026-10-20)
parsed the 500-record fullwiki JSONL and 7,405-record distractor Parquet. All 500
IDs/questions/answers/supports match; candidate contents differ for 362 questions
(138 differ only in order). At that gate real preparation was blocked: 49 Parquet records
have blank candidate sentences and one has an out-of-range support index. Source
lineage and complete exposure history are unresolved; existing reports establish
exposure to all 500 sample IDs. No production adapter or real split was created
at that checkpoint. Later policy-aware development preparation explicitly
excluded three of those IDs and retained a strict 497-record copy for Phase 5.5D;
this did not approve an exposure-cleared split. The 100/200 roles remain provisional.

The [resumed JSON audit](docs/evaluation_protocol.md#12-exact-path-distractor-json-audit---verification-complete-preparation-blocked)
verified the now-present `hotpot_dev_distractor_v1.json`: 46,320,117 bytes,
7,405 unique IDs and the exact user-supplied SHA256. All records and their order
match Parquet after field mapping, including the same 50 validation anomalies.
JSON format availability is resolved; input quality, independent provenance and
complete exposure history still block preparation. Local download metadata points
to Hugging Face's CDN, without authenticating an official upstream revision.

`ear_rag.data.hotpotqa_splits` now provides explicit-size split planning,
ID/normalized-text/exposure checks and a new-directory artifact writer. Missing
or partial exposure history blocks holdout; an explicit empty inventory is never
inferred from missing files. Checks cover supplied history only, not semantic
near-duplicates. Manifests record source/checksum, selection/seed, role IDs,
validation counts, aliases/exclusions and output hashes.

Verified synthetic ingestion/split checks:

```powershell
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_splits.py tests/test_hotpotqa_ingestion.py -q
```

The API flow is `read_hotpotqa(..., source_split="dev")`, then
`runtime_projection` / `evaluation_projection`, and optionally `plan_splits` or
`write_split_artifacts` with explicitly chosen counts and an `ExposureInventory`.
The writer requires a new destination and separates each role's runtime and label
JSONL. No reader CLI or approved real-data preparation command is claimed. Treat
the combined `HotpotQADataset.examples` as offline records; use the runtime
projection rather than legacy normalized-example serialization for retrieval.
Phase 5.2 synthetic verification passed **318 tests** in the complete suite
(57 new cases); scoped mypy passed for both new modules. Split utilities are
implemented, but no exposure-cleared dataset release or holdout split is approved.
Initial-only and bounded-controller evaluation wiring were subsequently implemented
and used in the explicitly authorized development/internal experiment.

The scoped [Phase 5.3 corpus/evidence layer](docs/evaluation_protocol.md#14-phase-53-corpusevidence-layer)
is implemented. `inspect_hotpotqa` exposes record positions, IDs and validation
reasons while `read_hotpotqa` still rejects an entire malformed input. Inspection
examples are diagnostics, not an approved filtered dataset.
`ear_rag.data.hotpotqa_evidence.build_question_corpus` adapts a fully valid dataset
into one question's candidate pool using existing `Query`/`Document` contracts.
`locate_evidence` maps existing backend chunks to source context and sentence
positions; `match_supporting_evidence` joins labels offline and distinguishes
title hits from complete sentence coverage, including coverage across chunks.
All four existing backend contracts pass synthetic compatibility tests. The Phase
5.3 checkpoint passed **349 tests**. Phase 5.2 remains **partially blocked** for
exposure-cleared preparation: the anomaly policy is implemented, while independent
provenance and complete exposure history are unresolved. No real inputs, splits
or results were produced at the Phase 5.3 checkpoint; later development/internal
inputs and results are described above.

[Phase 5.4 evaluation infrastructure](docs/evaluation_protocol.md#15-phase-54-evaluation-infrastructure-and-metrics)
is implemented in `ear_rag.control_evaluation`. `evaluate_cases` takes explicit
case requests and a fresh, documents-only pipeline factory, records initial and
terminal retrieval/ESA/recovery/abstention, then joins supporting labels offline.
It reports Hit@5, supporting-document Recall@5 and complete supporting-sentence
coverage@5; terminal metrics use recovery evidence alone when present.
Failed and explicitly excluded cases remain in versioned per-case JSONL and
aggregate JSON. Missing calls/latency/work stay `null`, with observation counts.
`write_evaluation_report` writes only to a new output directory. No real run or
benchmark CLI was added. Synthetic regression status: **381 tests passed**.

The [versioned invalid-record policy](docs/evaluation_protocol.md#16-phase-52-auditable-invalid-record-policy)
is now implemented in `ear_rag.data.hotpotqa_policy`. Its
[machine-readable audit](docs/hotpotqa_invalid_record_policy_audit_v1.json)
reproduces 49 blank-sentence exclusions and one out-of-range-support exclusion
on the current 7,405-record JSON. It preserves all applicable policy reason codes,
source positions and details without changing raw data or producing a filtered
dataset. The 7,355 records counted as valid passed strict record/identity checks;
**none is automatically approved for evaluation**. Ambiguous identity/structure
is otherwise invalid and explicitly flagged as unclassifiable. Reproduce an audit
with `python -m ear_rag.data.hotpotqa_policy SOURCE --output NEW_AUDIT.json`;
existing outputs cannot be overwritten. This closes the policy/audit task, while
provenance, exposure and 100/200 allocation remain unresolved. ESA
sufficiency does not establish answer correctness; retrieval metrics are not
answer EM/F1. Phase 5.5C/5.5D and the previous-policy Phase 5.6 analysis have since
been completed within their documented scopes.

No new dataset, split or experiment was produced during the CAS correction or
this status reconciliation. Existing previous-policy results remain intact.
The legacy pooled-context, recovery-disabled evaluator remains separate from the
per-question controller driver.
Answer EM/F1 remains unavailable because there
is no answer generator. Full-corpus retrieval and 2Wiki are later extensions.

## Setup and validate

Python 3.11+ is required (`StrEnum` and `typing.Self`); this phase was verified
on Python 3.12.4. The existing environment is `ai-proj-new`, not `.venv`.
From `C:\ear-rag` in Windows PowerShell:

```powershell
.\ai-proj-new\Scripts\python.exe -m pip install -e .
.\ai-proj-new\Scripts\python.exe -m pytest -q
.\ai-proj-new\Scripts\python.exe -m pip check
```

The editable installation uses `requirements.txt` as its single dependency source,
including existing development tools and the required `pyarrow` Parquet reader.
It makes `ear_rag` importable without setting `PYTHONPATH`. This is a development
checkout installation: keep `src/`, `configs/`, and tracked fixtures together;
standalone wheel deployment is not verified. Editable installation, isolated
imports/config loading, and Parquet normalization tests passed on Python 3.12.4;
see [PROGRESS.md](PROGRESS.md) for results and remaining work.

For a fresh checkout, create a virtual environment first, then install the package.
This creation/activation/install sequence was verified in a temporary source-only
snapshot with no local datasets and a fresh Python 3.12.4 environment:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pytest -q
python -m pip check
```

Verified activation of the existing environment uses
`. .\ai-proj-new\Scripts\Activate.ps1`. Explicit interpreter commands above also
work without activation or changes to PowerShell execution policy.

Verified package/CLI smoke checks:

```powershell
.\ai-proj-new\Scripts\python.exe -c "import ear_rag; print(ear_rag.__file__)"
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --help
```

Running the interactive demo (`python -m ear_rag.demo`) additionally requires
local normalized HotpotQA files in `data/processed/`; those files are ignored by
Git and absent from a fresh clone. Automated demo tests instead generate temporary
synthetic inputs and exercise the real loader, retrievers and controller. No
external datasets are needed by the test suite. Both the existing environment and
the fresh installation passed **244 tests** during Phase 1, with no skips. The
Phase 2 baseline passed 244 tests; the final suite passed **261 tests**, with no
failures or skips, including 17 new runtime regression cases.
Python 3.11 execution and standalone wheel deployment remain unverified.
No datasets or models were downloaded.

## Verified retrieval/controller demo

Historically, before the deterministic CAS replacement, these commands were run
with the existing local normalized HotpotQA files:

```powershell
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --dataset hotpotqa --mode ear-rag --index 0
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --dataset hotpotqa --mode ear-rag --index 0 --query-text "unmatched deterministic vocabulary"
@('2','0','3','5') | .\ai-proj-new\Scripts\python.exe -m ear_rag.demo
```

The first command selected lexical retrieval, returned five evidence chunks,
scored ESA 0.936 sufficient and reported `ANSWERABLE` without recovery. The
unmatched-query command performed one vector recovery and a mandatory second ESA
(0.298), then reported `ABSTAIN` after two leaf retrieval calls. Its predicted
post-recovery ESA was 0.892; this estimate did not match the actual result.
The last command exercised the interactive controller, evidence view and exit
with scripted input. Evidence titles now use the source document metadata
preserved by chunking. Evaluation mode, invalid interactive input and other
unexercised menu paths remain unverified in Phase 2.

Automated subprocess checks also exercise comparison, controller, evidence view
and exit on temporary synthetic inputs. Real-backend tests verify empty results,
sufficient initial evidence, recovery success, mandatory reassessment, abstention
and disabled/unconfigured recovery. These test cases do not constitute research
evaluation, and synthetic recovery-success cases deliberately give the initial
index no documents while the alternative index has evidence.

`ANSWERABLE` (internally `final_state='generate'`) means evidence passed the
deterministic ESA. **No answer is generated**: generation is disabled and there
is no runtime generator, deterministic or language-model-based. Operational
retrieval costs and nominal incremental CAS costs are not calibrated monetary costs.
Per-run retrieval-call counts include actual child operations for Hybrid and
Multi-hop. Returned context chunks and child retrieved passages are separate
quantities; retrieval latency excludes separately reported routing time, loading
and indexing. The current demo prints deficiency, binary suitability, incremental
cost and CAS instead of predicted ESA/gain, and still prints actual second ESA.

Recovery disabled by its round limit or without configured candidates performs no
recovery. Unavailable candidates are explicitly excluded before CAS ranking; if
none remain, recovery stops. The dispatch guard still rejects an unavailable action
returned by a custom policy. No hidden retrieval retry is added.

The existing offline evaluator compares fixed strategies with query-aware routing
with recovery disabled. Its tracked synthetic fixture and historical reports are
documented in [the routing guide](docs/initial_routing.md). Evaluation commands
and new research experiments are outside this reliability phase.

The initial 20-question HotpotQA development check did not establish improvement:
routed local-support recall@5 was 75%, versus fixed lexical 87.5%, among 16 queries
with locally resolved support labels. Rules are provisional and need development-set
calibration; freeze settings before independent test evaluation. Details and label
coverage caveats are in the [evaluation report](docs/initial_routing.md#measured-development-check-2026-10-09).

## Repository Structure
```
ear-rag/
├── src/ear_rag/          # Python package
├── configs/              # Configuration files
├── data/                 # Raw and processed data
├── tests/                # Test suite
├── outputs/              # Logs and results
└── docs/                 # Documentation
```

## Original Implementation Roadmap

These were the original phase labels; current implemented and verified status is
summarized above and recorded in [PROGRESS.md](PROGRESS.md).
- **Phase 1.1**: Project foundation ✓
- **Phase 1.2**: Configuration and Core Interfaces
- **Phase 2.x**: RAG pipeline implementation
- **Phase 3.x**: Evaluation and baselines

## Note

Consult [PROGRESS.md](PROGRESS.md) for phase history. Current routing and ESA are
deterministic baselines, not learned or calibrated policies; generation and
independent dataset-scale research validation remain future work. The existing
local development evaluations do not establish a research improvement.
