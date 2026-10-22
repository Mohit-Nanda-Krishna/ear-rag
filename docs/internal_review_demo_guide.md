# EAR-RAG internal review demo guide

## Local two-tab dashboard (2026-10-22)

From `C:\ear-rag` in PowerShell:

```powershell
.\ai-proj-new\Scripts\python.exe -B -m streamlit run src/ear_rag/dashboard.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8501`; exit with Ctrl+C in the terminal. No activation is
required because this command uses the existing environment directly. Streamlit
1.66.1 is installed; optional reproducible UI setup is
`.\ai-proj-new\Scripts\python.exe -m pip install -r requirements-dashboard.txt`.

1. **Live Query Demo:** the verified MuSiQue ID below is selected first. Read its
   exact question, then click **Run actual controller**. Walk through the numbered
   trace: query analysis/selection, initial retrieval/ESA, deterministic CAS,
   recovery/reassessment and final evidence status. Expand evidence to show native
   paragraph indices, chunk IDs and actual text. Changing IDs hides the previous
   result until another run. No supporting annotations or answers enter runtime.
2. Explain CAS as current evidence deficiency multiplied by observable action
   suitability, divided by configured incremental nominal work cost. The candidate
   table and decision come from the controller. Actual retrieval calls/chunks and
   retrieval-only latency are separate from this nominal cost; neither is money.
3. **Benchmark Results:** select one saved experiment at a time. HotpotQA uses
   document recall; native MuSiQue uses paragraph recall. Keep the experiments
   separate. Tables include requested/evaluated/failed/excluded counts and source
   paths. Phase 6A records eight comparisons, including the selected depth-0
   trained router (always lexical), original query-aware router and adaptive runs.

Verified with Streamlit AppTest: actual example initial ESA 0.5763514423,
local lexical recovery CAS 3.8513505247 > tau 1, final ESA 0.9365596937,
ANSWERABLE, two retrieval calls and ten returned chunks. The app computes these
on each run and warns if the saved example is not reproduced. No benchmark ran.
All 6 HotpotQA, 6 MuSiQue Phase 5 and 8 Phase 6A saved rows loaded successfully.

Say: “EAR-RAG selects a retrieval backend, checks evidence sufficiency, and uses
a deterministic cost-aware rule to decide whether an additional retrieval is
justified. It reassesses recovered evidence and can abstain. This demonstration
shows evidence control, not generated-answer quality. The results are development
results; independent final evaluation and hallucination-reduction validation are
still pending.” No real recovery-rejection example is promised under defaults;
the limitation explained below remains unchanged. Missing dataset/artifact errors
are shown explicitly. A browser screenshot could not be checked in this session
because no browser control surface was available; AppTest exercised both tabs.

## Verified native real-data replay (2026-10-22)

Use this section for the current CAS policy; older menu excerpts below remain
historical. One requested scenario is reproducible; the requested recovery-rejected
scenario is unavailable under the unchanged default configuration. Do not stage
it by disabling recovery, changing thresholds, hiding backends or inventing output.

### Accepted recovery: actual dataset question

- Dataset/split: official MuSiQue-Ans v1.0 **dev**, native candidate paragraphs.
- File: data/raw/musique/official_v1_0/musique_ans_v1.0_dev.jsonl.
- SHA256: 15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b.
- ID: `2hop__152700_141308`.
- Exact question: **What company is the record label for Oh Woman, Oh Why a part of?**
- Router: unchanged default `query_features_v1`, not the optional trained
  depth-0 router. The latter always starts lexical and will not reproduce this
  vector-to-lexical sequence. No setting is overridden here.

Actual replay through condition_evaluation._pipeline (the existing factory) and
RetrievalControlPipeline.run:

| Observable | Initial | After recovery |
|---|---:|---:|
| Backend | vector_flat | local_lexical |
| ESA relevance | .3823288460 | .9000849286 |
| ESA coverage / support | .4615384615 / .4615384615 | .9230769231 / .9230769231 |
| ESA consistency | 1 | 1 |
| ESA overall | **.5763514423** | **.9365596937** |
| ESA decision | uncertain (not sufficient) | sufficient |
| Actual underlying retrieval calls | 1 | 1 additional (2 total) |
| Returned chunks | 5 | 5 additional (10 total) |

The initial enum is `uncertain`, not `insufficient`; both are below sufficient
threshold .7 and enter recovery consideration. Suitability S=1 because query
tokens are missing from current evidence. Lexical incremental nominal cost
C=.05*1+.01*5+.001*10=.11 abstract work units. CAS=(1-.5763514423)*1/.11
=**3.8513505247**, strictly greater than tau=1, so recovery actually executes.
Hybrid also qualifies (S=1, C=.17, CAS=2.4920503395); lexical wins. Vector is
ineligible because already attempted; Multi-hop has S=0 because no dependency
indicator is present. Mandatory reassessment follows the recovery retrieval.
Final internal state `generate` is displayed/explained as **ANSWERABLE/evidence
ready**, not a generated or verified answer.

Nominal initial+recovery cost .11+.11=.22 is separate from measured work. One
observed replay reported .207700 ms total retrieval latency; timing varies and
excludes indexing/controller overhead. No monetary cost is measured.

Relevant actual retrieved evidence (native paragraph/chunk indices; quotes are
exact excerpts, ellipses indicate omitted text):

- Initial rank1: paragraph2/chunk0, **Beech Bottom, West Virginia**:
  “Beech Bottom is a village in Brooke County, West Virginia, along the Ohio River.”
  Other initial chunks concern West Farmington, Yankee Lake, Ohio State Route523
  and Malvern, rather than the record-label chain.
- Recovery rank1: paragraph12/chunk0, **Oh Woman, Oh Why**:
  `"Oh Woman, Oh Why" is a song written by English musician Paul McCartney, first released on the Apple Records label in February 1971 as the B-side to McCartney's debut single as a solo artist, "Another Day".`
- Recovery rank2: paragraph13/chunk0, **Apple Records**:
  “Apple Records is a record label founded by the Beatles in 1968 as a division
  of Apple Corps Ltd.” This is an excerpt from the returned 400-character chunk.

Offline support checking after runtime confirms both annotated parent paragraphs
are retrieved (paragraph Recall@5=1). These annotations never select the backend,
score ESA or choose recovery. This is a selected internal demonstration, not an
independent effectiveness test or answer-generation evaluation.

### Exact PowerShell replay command

This reads the exact native question/pool from the dataset, creates fresh real
backends/controller, and prints actual trace/evidence. It does not use hard-coded
trace output or the menu's different processed HotpotQA pool. No files are written.

```powershell
Set-Location -LiteralPath 'C:\ear-rag'
@'
import json
from dataclasses import asdict
from ear_rag.config.loader import load_config, get_config_path
from ear_rag.condition_evaluation import _pipeline
from ear_rag.data.musique import read_musique
from ear_rag.data.musique_evidence import build_question_corpus

dataset = read_musique('data/raw/musique/official_v1_0/musique_ans_v1.0_dev.jsonl')
corpus = build_question_corpus(dataset, '2hop__152700_141308')
config = load_config(get_config_path())
trace = _pipeline(corpus.documents, config).run(corpus.query, config['retrieval']['backend'])
print(json.dumps({
    'id': corpus.question_id, 'question': corpus.question,
    'initial_backend': trace.initial_retrieval.retriever_name,
    'initial_ESA': asdict(trace.initial_assessment),
    'recovery_decision': asdict(trace.recovery_decision),
    'post_ESA': asdict(trace.recovery_assessment) if trace.recovery_assessment else None,
    'final_state': trace.final_state, 'retrieval_calls': trace.total_retrieval_calls,
    'returned_chunks': trace.total_retrieved_chunks, 'retrieval_latency_ms': trace.total_latency_ms,
    'initial_evidence': [asdict(c) for c in trace.initial_retrieval.chunks],
    'recovery_evidence': [asdict(c) for c in trace.recovery_retrieval.chunks] if trace.recovery_retrieval else []
}, ensure_ascii=True, indent=2))
'@ | .\ai-proj-new\Scripts\python.exe -B -
```

### Why the requested rejected-recovery/ABSTAIN example cannot be supplied

No qualifying second question was found. This follows from the actual default
rules, not a hard-coded demo limitation:

1. All four backends are callable, recovery limit is1, initial top-k5 is below
   budget20, and every backend permits all four recovery candidates.
2. On a token-bearing question, absence of every supported gap means full literal
   query coverage, at least two chunks and no normalized duplicates. Default ESA
   then has coverage=support=consistency=1 and nonnegative relevance, so ESA>=.75.
   Therefore ESA<.7 necessarily supplies a gap and S=1 for unattempted lexical/vector.
3. At least one of lexical/vector is unattempted after the single initial strategy.
   Its C=.11, so any non-sufficient ESA<.7 yields CAS>.3/.11=2.72727>tau1.
   That candidate cannot be rejected by the CAS threshold. Recovery can still
   finish in ABSTAIN, but it has already spent the extra call; that is a different
   scenario and must not be presented as recovery rejection.

Checked all questions in local HotpotQA distractor JSON(7,405), fullwiki sample
JSONL(500), distractor Parquet(7,405), MuSiQue official dev(2,417) and train(19,938):
none has an empty token set (the potential no-query-tokens suitability exception).
These counts overlap and are not a unique-cohort claim. Saved revised-CAS traces
also contain no non-sufficient/no-recovery case: all19 HotpotQA and317 MuSiQue
such cases recover. No exhaustive new retrieval benchmark was needed for the
rule-based impossibility argument. No second ID/question/CAS rejection is invented.

Runtime references: routing/pipeline.py::run/_finish; evidence/esa.py::assess;
routing/recovery.py::decide; routing/cost_awareness.py::action_suitability,
incremental_cost and DeterministicRecoveryEstimator. For the reviewer, say:
“The current defaults always permit an alternative on these non-sufficient real
questions. We can demonstrate recovery and reassessment, but cannot honestly
demonstrate CAS rejecting one without changing the configuration or policy.”

Verification for the native replay: the exact PowerShell block above was executed
successfully, with its actual JSON trace checked for recovery, improvement, two
calls and final generate. Focused command:
`.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_deterministic_cas.py tests/test_phase_17_cost_awareness.py tests/test_runtime_reliability.py tests/test_condition_evaluation.py tests/test_musique_evidence.py`
Result: **92 passed in 1.71s**. No runtime, data, threshold or CAS change.

CAS update: the current runtime uses [deterministic evidence-sufficiency CAS](deterministic_cas.md)
with binary suitability and nominal incremental cost; it no longer predicts ESA
gain. The saved recovery/results examples below are historical outputs from the
previous policy, not validation or promised outputs of the revised controller.
The original readiness smoke excerpts below were recorded before this CAS change.

This is a 3–5 minute demonstration of retrieval and evidence control. The current
demo starts successfully with the existing local environment and processed data.
It does not generate an answer. Use the saved research results for the results
discussion; do not run the menu's evaluation option during the review.

## 1. Start in Windows PowerShell

Open PowerShell (or the VS Code terminal) and enter:

```powershell
Set-Location -LiteralPath 'C:\ear-rag'
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.demo --dataset hotpotqa
```

The menu should say `Dataset: HotpotQA (500 normalized questions)`. The interpreter
is `C:\ear-rag\ai-proj-new\Scripts\python.exe`; the saved experiment records
Python 3.12.4. Explicit interpreter invocation works without environment activation.

Optional activation, if you prefer it:

```powershell
Set-Location -LiteralPath 'C:\ear-rag'
. .\ai-proj-new\Scripts\Activate.ps1
```

Continue using the explicit interpreter command above so another installed Python
does not get selected accidentally. No installation or download is needed in this
checkout. The demo reads these existing local assets:

- `C:\ear-rag\data\processed\hotpotqa_normalized.jsonl`
- `C:\ear-rag\data\processed\evaluation\hotpotqa_evaluation.jsonl`
- `C:\ear-rag\configs\config.yaml`

These processed dataset files are ignored by Git and may be absent from a fresh
clone. The CLI uses them; it does not automatically use the raw distractor JSON
or the frozen Phase 5.5D cohort.

## 2. Live sequence: about four minutes

### 0:00–0:30 — Explain the purpose

Say:

> “EAR-RAG is a prototype for deciding how to retrieve evidence and when to try
> another retrieval method. It analyzes the question, chooses a backend, checks
> the retrieved evidence with a deterministic heuristic, and can make one bounded
> recovery attempt. Today I am showing this control flow and the evidence it
> returns. Answer generation and independently validated answerability assessment
> are still incomplete.”

### 0:30–1:30 — Submit the prepared example

At `Select:`, type **2** and press Enter. At `Example index`, type **0** and press
Enter. This submits the existing sample question:

> Were Scott Derrickson and Ed Wood of the same nationality?

The menu accepts an example index, not free-form question text. Point to
`INITIAL ROUTING`, then `STEP 1 - INITIAL RETRIEVAL`.

Say:

> “The selected strategy is local lexical retrieval. For this example the query
> rules did not find a strong routing signal, so the configured lexical fallback
> was used. The zero suitability scores are heuristic scores, not probabilities.
> The next stage retrieves up to five chunks of text.”

The interface prints `Documents: 5`, but this is the number of returned **chunks**;
it does not guarantee five different documents.

### 1:30–2:15 — Explain ESA and inspect evidence

Point to `Current ESA: 0.936`, `SUFFICIENT`, no recovery and `ANSWERABLE`.
Then type **3** at the next menu to show titles, scores and actual retrieved text.

Say:

> “ESA combines query-word overlap, retrieval relevance, an overlap-based support
> signal and a text-uniqueness signal. These are simple deterministic heuristics.
> The current sufficient threshold is 0.7; this example passed, so recovery was
> skipped. ANSWERABLE means the evidence passed that heuristic. It is not a
> verified answer and does not mean an LLM answered the question.”

The verified evidence view begins with **Woodson, Arkansas**, followed by
**Sinister (film)** and **Ed Wood (film)**. This is a useful limitation to explain:
matching names and query words does not establish the nationality comparison.
Do not present this example as proof that correct supporting evidence was found.

### 2:15–3:15 — Show a genuine saved recovery case

Type **5** to exit the menu. Show the saved recovery table in the
[Phase 5.6 report](../outputs/phase56-analysis-development-internal-known-exposure-20261020T191125Z-ab9ca032/PHASE56_FINAL_REPORT.md#all-19-adaptive-recoveries),
using question ID `5ae7ed17554299540e5a56a3`.

These are **actual saved Phase 5.5D results**, not output from today's live run:

| Stage | Recorded result |
|---|---|
| Initial backend | `vector_flat` |
| Initial ESA | 0.633774, `uncertain` |
| Recovery action | One alternative-retriever attempt using `hybrid` |
| Mandatory reassessment | 0.773583, `sufficient` |
| Final state | `generate` (the control flag; no answer generated) |
| Supporting-document recall@5 | 0.5 → 1.0 |
| Annotated supporting-sentence coverage@5 | 0.5 → 1.0 |
| Underlying retrieval calls | 3 total: one vector call plus two hybrid child calls |

Recovery adds annotated support `Ernest Foot:1`; terminal evidence also covers
`Albert Ball:1`. This is measured evidence retrieval improvement in this case.
It does not independently prove semantic sufficiency.

Say:

> “Here the first evidence was uncertain, so the controller tried Hybrid once.
> It reassessed the new evidence instead of trusting its predicted improvement.
> The annotated evidence coverage improved in this saved case. If reassessment
> remains uncertain or insufficient, the controller abstains. Terminal evaluation
> uses the recovery result alone, rather than combining both retrieval results.”

For an abstention example in the same saved table, point to
`5a7cbf8c554299452d57b9f4`: lexical → vector recovery, ESA .6984 → .5692,
coverage .5 → 0, final `abstain`. Recovery can make retrieval worse.

The interactive demo pools documents from its 500 normalized examples. The saved
experiment used **per-question distractor candidate pools**. Therefore a saved
case's score or recovery cannot be promised by entering its index in this menu.
Show it as a saved trace; no parameter changes or new experiment are needed.

### 3:15–4:30 — Present the measured trade-off

Use the results notes below. End with the limitations and the spoken summary.

## 3. Expected output and verified smoke command

The following existing command was run once for this readiness check, from
`C:\ear-rag`; it completed with **exit code 0** in approximately 1.25 seconds:

```powershell
@('2','0','3','5') | .\ai-proj-new\Scripts\python.exe -B -m ear_rag.demo --dataset hotpotqa
```

It selects controller mode, submits example 0, displays evidence and exits.
This is the reproducible scripted version of the live sequence's first part.

**Actual output excerpts from that smoke run** (intervening lines omitted):

```text
Dataset: HotpotQA (500 normalized questions)
Selected strategy : local_lexical
Fallback : Insufficient query signals for an initial strategy.

Question:
Were Scott Derrickson and Ed Wood of the same nationality?

STEP 1 - INITIAL RETRIEVAL
Strategy        : local_lexical
Retrieval calls : 1
Documents       : 5

STEP 2 - ESA
Current ESA                  : 0.936
Decision                     : SUFFICIENT

STEP 4 - RECOVERY
Recovery performed           : NO
Recovery round               : 0 / 1

Total retrieval calls   : 1
Final decision          : ANSWERABLE

RETRIEVED EVIDENCE: local_lexical

Rank 1
Title       : Woodson, Arkansas
```

Latency varies by machine/run and is deliberately omitted from these excerpts.
Routing logs may appear between prompts because logging and console output use
different streams. A successful startup check is software verification, not
research effectiveness evidence.

If a reviewer asks to enter arbitrary text, the existing CLI supports it:

```powershell
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.demo --dataset hotpotqa --mode ear-rag --index 0 --query-text "Were Scott Derrickson and Ed Wood of the same nationality?"
```

This syntax is verified from `demo.py`; this separate command was not run during
this check. It runs one query and returns to PowerShell. It searches the same
local pooled corpus; it cannot answer questions whose evidence is absent.
For tomorrow, the tested menu sequence is the recommended path.

## 4. Architecture in plain language

```text
Question → query analysis → select one backend → initial retrieval → ESA
                                                        ├─ sufficient → final evidence status
                                                        └─ recovery allowed/worthwhile?
                                                            ├─ no → final evidence status
                                                            └─ yes → one alternative retrieval
                                                                      → mandatory ESA reassessment
                                                                      → final evidence status
```

Final status is `ANSWERABLE` only if the final ESA decision is sufficient;
otherwise it is `ABSTAIN`. There is at most one recovery in the current pipeline.
The recovery decision uses configured limits and heuristic gain/work estimates.
These estimates are not actual money or guarantees of improvement. Gold answers
and supporting facts are reserved for offline evaluation and do not drive runtime
routing, ESA or recovery.

The four retrieval backends are prototypes: lexical is BM25-inspired, Vector Flat
uses deterministic hashed tokens rather than learned dense embeddings, Hybrid
combines lexical/vector scores, and Multi-hop uses bounded lexical expansion.
ESA's “consistency” measures normalized text uniqueness, not contradiction detection.

## 5. Results slide notes: use existing reports, do not rerun

Label the discussion **development/internal — known exposure**. Each condition
requested the same 500 questions; three explicit invalid-record exclusions left
497 usable questions, zero failures and no missing quality pairs. Top-k was five.
The first four conditions force their named backend and disable query-aware
initial selection and recovery; query-aware enables selection without recovery;
adaptive adds the existing bounded recovery controller.

| Condition | Document Recall@5 | Evidence coverage@5 | Total retrieval calls |
|---|---:|---:|---:|
| `fixed_local_lexical_no_recovery` | 80.78% | 74.17% | 497 |
| `fixed_vector_flat_no_recovery` | 51.21% | 45.79% | 497 |
| `fixed_hybrid_no_recovery` | 68.71% | 61.68% | 994 |
| `fixed_multihop_no_recovery` | 80.89% | 74.30% | 994 |
| `query_aware_no_recovery` | 77.46% | 70.80% | 518 |
| `adaptive_controller` | 78.77% | 72.09% | 554 |

Recall measures the fraction of annotated supporting documents retrieved.
Evidence coverage measures the fraction of annotated supporting sentences fully
covered. Neither is answer accuracy. All usable questions, including abstentions,
remain in these means.

Main talking point:

> “Adaptive recovery improved document recall by 1.31 percentage points over
> query-aware routing without recovery, using 36 additional retrieval calls.
> However, it remained 2.01 points below fixed lexical retrieval and used 57 more
> calls. We observed a trade-off, not evidence that adaptive retrieval wins overall.”

Phase 5.6 descriptive paired-bootstrap intervals for these recall differences:
+0.50 to +2.21 points versus query-aware, and −3.12 to −1.01 versus lexical;
497 paired question IDs, 10,000 resamples, seed 1729. These describe this exposed
cohort and do not establish unseen performance or general research superiority.

Adaptive recovered on 19 questions: coverage improved in 12, tied in six and
worsened in one. Nine final abstentions remained. Six of those nine had complete
annotated coverage; 47 sufficient decisions had coverage below 50%, including
25 with zero. These show disagreement with an evidence-coverage proxy, not
validated ESA accuracy. Calls and latency are work proxies; monetary cost,
processed-chunk counts, indexing and complete controller costs are unavailable.
Timing was a single sequential run, not a robust speed comparison.

Sources:

- [Phase 5.5D experiment report](../outputs/phase55d-development-internal-known-exposure-20261020T185946Z-c62ca682/REPORT.md)
- [Phase 5.6 final analysis](../outputs/phase56-analysis-development-internal-known-exposure-20261020T191125Z-ab9ca032/PHASE56_FINAL_REPORT.md)

Some README and older demo notes describe earlier phases. Use the latest
`PROGRESS.md`, `AGENT_HANDOFF.md` and the two reports above for current status.
The reports must already exist locally because `outputs/` is ignored by Git.

## 6. Limitations and a short closing explanation

Say:

> “The implemented contribution is an inspectable evidence-control prototype:
> selecting an initial retriever, assessing its output, limiting recovery and
> reassessing before permitting a final evidence status. We have implemented
> and tested the orchestration and measured its trade-offs on internal development
> questions. These questions are known-exposed, and we have no exposure-cleared
> holdout. We have not evaluated actual answer generation or validated hallucination
> reduction. Our next research needs are independent sufficiency labels, defensible
> dataset provenance and exposure/split checks, and a frozen evaluation design.”

Do not claim novelty, calibrated confidence, correct answers, full-Wikipedia
retrieval, reduced hallucinations or overall research completion from this demo.
Phase 5.6 is **analysis complete — development/internal, known exposure**.

## 7. Troubleshooting and exit

| Symptom | Action |
|---|---|
| PowerShell cannot find `ai-proj-new\Scripts\python.exe` | Run `Set-Location -LiteralPath 'C:\ear-rag'`. Confirm the existing executable path; `.venv` is not this checkout's environment. |
| `Activate.ps1` is blocked by execution policy | Skip activation and use the explicit interpreter command. No execution-policy change is needed. |
| `ModuleNotFoundError: No module named 'ear_rag'` | Use the explicit environment interpreter and `-m ear_rag.demo` from the repository root. Avoid the IDE's direct Run button on `src/ear_rag/demo.py`. If it persists with this exact command, stop and report the import error; do not install packages during the review. |
| Missing normalized/evaluation file | Check the two processed paths listed above. The demo has no built-in synthetic dataset mode. Use the saved report as fallback; restoring existing processed assets is a separate preparation task. |
| Unicode output/encoding trouble | In the current PowerShell session set `$env:PYTHONIOENCODING = 'utf-8'`, then use the startup command. |
| Evidence view says no retrieval has run | In the same menu session choose **2**, then **0**, before **3**. A new `--mode evidence` process has no previous evidence in memory. |
| Unexpected example/index error | Use numeric index **0**; this local menu currently accepts 0–499. Custom text belongs in `--query-text`, not the index prompt. |
| Output pauses before retrieval | The demo constructs fresh local indexes for a controller run. This startup work is separate from the printed retrieval latency. |
| Want to exit | Type **5** at the menu. Use **Ctrl+C** to interrupt a running operation; a `KeyboardInterrupt` traceback can appear. After optional activation, `deactivate` leaves the environment. |

Leave menu **4** (small evaluation), full benchmark scripts and threshold overrides
unused for this review. If startup fails tomorrow, show this guide's verified
excerpts and the existing saved recovery/results reports, clearly labelled as
saved artifacts. No startup blocker was found in this readiness check.

Validation for this task: one scripted controller/evidence/exit smoke run passed;
the displayed recovery values were read from the saved per-case artifact; results
were checked against Phase 5.5D/5.6 reports. Only this guide was added. No research
code, configuration, data or previous output was changed. No qualifying bug was
resolved, so no Obsidian error note was created.
