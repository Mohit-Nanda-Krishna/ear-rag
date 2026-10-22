# Agent Handoff

## COMPLETED local supervisor dashboard (2026-10-22)

Two Streamlit tabs implemented in src/ear_rag/dashboard.py; dashboard_data.py
adapts the existing fresh pipeline factory and reads saved reports. No research
runtime, config, data, model or prior-output changes. Optional Streamlit1.66.1
installed in ai-proj-new with new dependencies only; requirements-dashboard.txt
pins it. README and internal_review_demo_guide.md contain the launch command.
Live example2hop__152700_141308 reproduced ESA.5763514423 ->.9365596937,
lexical recovery CAS3.8513505247>1, ANSWERABLE, two calls/ten chunks. Benchmark
reader loaded6/6/8 rows from HotpotQA/Phase5 MuSiQue/Phase6A without errors.
Focused tests:5 passed; full suite524 passed in8.37s. Mypy:2 modules clean;
pip check clean; git diff --check exit0 (existing CRLF warnings only). Streamlit
AppTest exercised real example, synthetic UI, both tabs and all saved groups;
HTTP health returned ok. Browser screenshot unavailable: no browser surface.
241 preexisting source/test/config/raw/output hashes match the prior baseline.
No qualifying bugs fixed; no error notes created. No benchmark or training run.
Resume: no dashboard work pending. Preserve all earlier dirty work. Independent
evaluation and lack of a real default-policy rejection example remain limitations.

## COMPLETED real-data supervisor demo verification (2026-10-22)

Inspecting saved real-data traces then replaying selected native records with
unchanged default router/ESA/CAS/config. No synthetic queries or data edits.
Current saved MuSiQue317/Hotpot19 non-sufficient adaptive cases all recovered;
no rejection found there. Selected MuSiQue dev2hop__152700_141308 exact native
question/pool: ESA.5763514423 uncertain -> lexical recovery CAS3.8513505247>1,
S1/C.11 -> ESA.9365596937 sufficient, generate/evidence-ready, two calls total.
Both gold parent paragraphs retrieved; annotations used offline only.
Guide now contains exact question/source/hash/evidence and verbatim PowerShell
replay, executed successfully. Rejected non-sufficient case unavailable under
defaults: non-sufficiency implies gap/S1, an unattempted lexical/vector action
costs.11 and hasCAS>2.727>1; limits/budget do not block the first recovery.
Scanned all local native JSON/JSONL and Hotpot Parquet question tokens: zero
tokenless exceptions. No second question/outcome fabricated. 92 focused tests
passed in1.71s. Only guide/handoff changed; no runtime/config/data/output edits,
no qualifying fixed bug/error note. Exact resume: STOP, demo request complete
with explicit second-scenario limitation; do not tune to manufacture it.

## Final completion check COMPLETE; independent evaluation BLOCKED (2026-10-22)

Read Phase6A/6B reports and current README/PROGRESS/handoff before acting.
Protected final evaluation still BLOCKED: unchanged local train/used dev/derivative,
no verified protected support labels, authorized compatible blind scorer or
complete candidate-use history. Fresh hosted leaderboard checks returned502;
public offline gold scorer exists but does not supply missing labels/access.
Only README/PROGRESS/this handoff received final status clarification. Focused
tests78 passed in1.48s (learned router, native evidence, condition orchestration,
deterministic CAS); diff check exit0. Phase6A30 artifact hashes/49 live frozen
non-document references and Phase6B8 artifact hashes matched. Starting269 files
hashed for scope verification. No new benchmark, refit, acquisition, source/config
changes or output files; no qualifying bug/error note.
Exact resume: STOP. No further code change required for this completion check.
To resume final research evaluation, supply verified protected support labels or
authorized compatible blind scoring, exact cohort identity and prior-use evidence;
then independently audit/freeze before first outcomes. Existing Phase6B report
remains the detailed gate record. Do not rerun dev, tune, or claim research completion.

## COMPLETED Phase 6B audit/validation; protected final evaluation BLOCKED (2026-10-22)

User attachment97ad5c30-5f7a-4110-a178-b393edc0507f. Task allows final benchmark
ONLY with defensible protected data/scoring/exposure/protocol. Gate FAILED:
locally only fitted official train, used dev and dev-equivalent derivative;
no verified protected support-label cohort, exact test identity/overlap/use
history or operational blind scoring for the intended evidence metrics.
No final benchmark, substitute dev run, refit/label generation/tuning, new test/
dataset acquisition, submission/contact or cohort selection. No fake final scores.

Output: outputs/phase6b-protected-evaluation-audit-20261022T161807Z-7e19b0ef/.
Read REPORT.md and eligibility.json. Official source checks are hashed in
official_source_checks.json. Fresh author HEAD remains
922ac98f19a201998dbdae6d7f2887a5258dbdeb. Pinned public evaluate_v1.0.py EXISTS and
requires labelled gold + answer/support predictions; metrics are F1/sufficiency,
not our Hit/Recall@5. Hosted Ans/Full URLs: browser502/local urllibDNS failure,
not proof of universal shutdown. Raw-data metadata has train/dev variants only.
Old test probes are first-record schemas without labels, not complete test audits.
No complete candidate-test exposure ledger found within searched repository/
known artifacts; external historical use is not assumed absent. Existing31 dev
NQ step-text matches are potential indicators, not proof of training. Train/dev
ID/question/component disjointness and3696 shared paragraph texts remain verified.

Frozen model SHA12e44dc3ac8f17300b90082021feffc0dfafc37d6e7737276d89088e6c5bd204;
selected config SHA f98a14b1db3a9c157e134ddf55d903b062c358d82e1b49ac31f9fadcbe279483;
default config SHAb494caae97e83ff6d095f0f0133b58b0ea6b281f63d62e0f378c8e7a0b6b4835.
Depth0 single leaf [17296,1865,777,0] proves all valid supported strings choose
lexical when available; otherwise error/no fallback. Eight inference samples
and3 synthetic pipeline comparisons verify actual trained artifact load and
fixed-lexical equality. No query-dependent learned advantage is established.

Fresh focused207 tests in3.90s, full519 in7.29s, mypy8 modules, diff check exit0.
validate_frozen.py passed30 Phase6A artifact hashes and50 frozen references:
historical protocol snapshot saved before the explicit Phase6B doc clarification;
all runtime/model/config/input hashes still match live files. Saved-only replay
16,919 dev case traces/33,838 metric+ESA stages and deterministic policy decisions,
all2417 paired IDs and old intervals reproduced without refit or real-data
retrieval. Synthetic tests alone exercise fitting on fixtures; helper runs three
synthetic retrieval cases. Do NOT run Phase6A verify_training.py main during6B:
it refits actual training labels. Current saved-only command:
.\ai-proj-new\Scripts\python.exe -B outputs/phase6b-protected-evaluation-audit-20261022T161807Z-7e19b0ef/validate_frozen.py

Only status/verified clarification changes: this handoff, PROGRESS.md,
docs/evaluation_protocol.md section22, docs/musique_dataset_audit.md source check.
No production source/tests/config/README/raw/prior-output changes; preservation.json
and artifact_checksums.json record final scope. Starting260 files hashed; old
dirty tree retained. No qualifying resolved bugs/error notes.

Exact resume point: STOP; audit/validation complete, final evaluation remains
BLOCKED. Minimum next task: verify protected paragraph-support labels or an
authorized blind evidence-metric scoring endpoint, exact source/identity/hash/
license and prior project exposure/use evidence. Then audit train/dev overlap/
paragraph reuse and freeze unchanged six conditions/model/settings/metric/
pairing/failure/uncertainty protocol BEFORE first test outcomes. No dev relabel,
new random split, model/CAS/ESA tuning, fake answers or generalization/hallucination/
published-superiority claims. Historical completed checkpoints below preserved.

## COMPLETED Phase 6A training pipeline and development selection (2026-10-22)

User attachment e4e2d19d-273d-47c6-acb0-9b77ca8c779a authorized official-train
acquisition, train-only fitting, development model selection; no final test.
Label: development/internal — exposure limitations apply. Stop after this task.
Original heuristic remains default. Do not tune further on these results.

Implemented routing/learned.py (pure-stdlib deterministic CART/Gini, exact11
text-only features, strict query_tree_v1 artifact/explicit config/checksum and no
fallback), router_training.py (existing evaluator for four fixed targets,
depth0/1/2/3 min_leaf64 train-only fitting/dev recall-calls-depth selection and
paired comparison), tests/test_learned_router.py (12 new synthetic tests).
data/musique.py explicit source_split train/dev (dev identity unchanged), cached
offline example lookup; musique_evidence.py uses the lookup. pipeline.py only
changes router construction to explicit policy factory. ESA/CAS/suitability/cost/
thresholds/recovery/reassessment/backends and project default config unchanged.

New raw directory data/raw/musique/official_v1_0_train/: official train and new
acquisition manifest. Exact member-only HTTPS range acquisition from existing
pinned author-linked ZIP, raw DEFLATE/CRC/size validation, no test/full ZIP/gdown.
Revision922ac98f19a201998dbdae6d7f2887a5258dbdeb, CC-BY-4.0. Train19,938 valid unique,
SHA83a75b1e11e4e9bb8f8308e72ac40ca617ae4431b3a0d955b61cab259248490a.
Dev2,417 valid, SHA15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b.
No invalid/label exclusions/failures. Exact IDs/normalized questions/decomposition
IDs disjoint; 3,696 normalized paragraph texts shared. No exposure clearance:
31 dev NQ decomposition-text matches remain potential indicators, not training
proof. No protected test or verified official evaluation/scoring access.

Target: max native paragraph Recall@5, then minimum actual calls, then action
order lexical/vector/hybrid/multi. Train labels17296/1865/777/0; zero-evidence
targets1706 train/254 dev flagged/retained. No gold in runtime features.
All four candidate depths choose lexical for every dev case; selected depth0 is
the majority constant, not a query-dependent routing improvement. Proxy-label
agreement86.7489% train/86.0571% dev is not correctness.
Trained no-recovery .840712Hit/.479555Recall/2417calls == fixed lexical.
Original heuristic .779065/.437043/2493calls. Paired recall difference+.042511,
descriptive selection-biased95%CI[.035685,.049510], n2417. Trained adaptive
.841125/.479692/2423calls, six recoveries/six abstentions, no CAS changes.
All dev methods evaluated all2417 with zero failed/excluded/unpaired IDs.

Output: outputs/phase6a-router-development-20261022T155210Z-95732e1d/.
REPORT.md includes source/commands/objective/limitations. PROTOCOL.md and global
protocol section21 were written before labels. frozen.json pins50 sources/
config/protocol/test/input hashes. model.json SHA
12e44dc3ac8f17300b90082021feffc0dfafc37d6e7737276d89088e6c5bd204.
selected_config.json explicitly opts into this artifact. model_selection.json,
training/development labels+four fixed trace streams, three runtime condition
reports and results.json retain all targets/outcomes/selections/groups/pairs.
No source/config/protocol changed after results. Acquisition/training commands
are exclusive: NEVER restart into existing directories or overwrite artifacts.

Checks: focused177 passed in1.71s; full519 in7.26s; five-module mypy clean;
diff check clean before training. Saved verify_training.py passed 89,420 fixed
traces/193,342 metric+ESA stages, every target/feature, exact model/search including
reversed train order, artifact/runtime predictions, paired quality/intervals.
It runs no retrieval/test evaluation (only reproduces same fit from saved labels).
README/PROGRESS/protocol/audit updated. Error logger: zero qualifying fixed bugs;
no notes created. Final preservation.json and artifact_checksums.json record
exact scoped changes and protected old raw/output/source hashes.

Exact resume point: STOP; Phase6A complete, final evaluation BLOCKED on a
defensible protected test and verified official scoring procedure. Dev is used
for selection and cannot become final test. No unseen-data/hallucination/answer-
correctness/published-superiority claim, no further training/tuning.
Historical completed task checkpoints below are preserved.

## COMPLETED: MuSiQue native integration and development/internal evaluation (2026-10-22)

Task: implement native official MuSiQue-Ans dev adapter, synthetic tests, then
conditionally run the existing six conditions. Mandatory label:
**development/internal — exposure limitations apply**. No training/tuning/downloads,
raw changes, independent holdout claims, resets/stashes/clean/commits.

Implementation: data/musique.py strict all-or-nothing JSONL/diagnostics/manifest;
data/musique_evidence.py native paragraph-ID source views and offline metrics;
control_evaluation.py/condition_evaluation.py narrow supported-dataset dispatch;
hotpotqa_evidence.py shared source-window structural type only (no scoring change).
musique_experiment.py is a small CLI over existing runner/serializer/aggregator/
bootstrap. Three synthetic test modules added. Router/ESA/CAS/recovery/backends
and config bytes unchanged. Passing validation is not exposure clearance.

Verified input: official_v1_0/musique_ans_v1.0_dev.jsonl, SHA256
15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b.
2,417 unique/valid/answerable records; 48,315 candidates/6,404 supports; zero
exclusions/unclassifiable. Derivative identity fields agree. 31 NQ decomposition
text matches remain potential exposure indicators, not proof of training.
Six normalized duplicate-question groups retained. Author-linked pinned source
and acquisition hashes/licenses are in the dataset manifest/audit.

Gate passed before benchmark: focused 150 tests in 2.71s; full 507 in 6.68s;
six-module mypy clean; diff check clean; all protected starting hashes intact.
Frozen protocol section 20 and 47 source/input/config hashes precede retrieval.
Config SHA b494caae97e83ff6d095f0f0133b58b0ea6b281f63d62e0f378c8e7a0b6b4835.
All six ran ONCE, 2,417 requested/evaluated each, zero failures/exclusions, paired
n=2,417. No implementation/config/protocol changes after seeing results.

Output: outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73/.
Read EXPERIMENT_RECORD.md (commands/provenance/tests/limits), REPORT.md (table/CIs),
analysis.json and frozen/dataset/cohort manifests. Paragraph metrics deduplicate
first-five CHUNKS by native parent idx; sentence coverage stays null/unavailable.
Adaptive paragraph recall .473900, router-only .437043, fixed lexical .479555.
Adaptive-minus-router +.036857 [.030651,.043339] with 317 extra calls; versus
lexical -.005654 [-.008688,-.002689] with 393 extra calls. Recovery 199 improved/
90 tied/28 worsened; 311 reassessed sufficient/six uncertain, final 2,411 evidence-
ready/six abstain. ESA sufficiency does not mean correct generated answers.

Saved verification passed: 29,004 paragraph-stage metric replays, exact analysis/
report reproduction, all frozen and original artifact hashes. Additional
validate_saved_runtime.py replays 29,004 ESA stages/14,502 exact policy decisions/
1,268 candidates; seven corruptions rejected and injected failure retained.
Read-only verification commands:
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.musique_experiment verify --output outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73
.\ai-proj-new\Scripts\python.exe -B outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73/validate_saved_runtime.py
Never rerun run into this directory or overwrite the frozen results.

README/protocol/PROGRESS/audit updated. Prior dirty work, nine raw files and all
88 prior output files remain protected; final preservation/checksum record in
the experiment directory captures this task's exact changed/added files.
No qualifying verified project bug was fixed; zero Obsidian error notes.

Exact resume point: STOP; authorized implementation/evaluation task complete.
Independent exposure clearance, verified labelled official-test/scoring access,
semantic sufficiency and answer quality remain unresolved. Phase 6 router
training explicitly pending and requires a separate authorized leakage-safe plan.
No tuning on this cohort or claims of hallucination reduction/generalization/
published-method superiority. Historical checkpoints below remain intact.

## Revised-CAS evaluation COMPLETE — stop here (2026-10-22)

This supersedes the earlier no-experiment checkpoint below. Frozen protocol,
execution and paired analysis completed: development/internal — known exposure.
Output: outputs/phase5-revised-cas-development-internal-known-exposure-20261022T125412Z-0e6adb98/.
Read REPORT.md, PROTOCOL.md, scope.json and validation.json there to resume.
HEAD a905925db843db98e4dbc848ceb85696b48c693b plus 37 runtime source hashes and
config b494caae97e83ff6d095f0f0133b58b0ea6b281f63d62e0f378c8e7a0b6b4835 identify
the dirty frozen revision. Runtime/config/tests/data were not edited.

All six conditions ran ONCE with identical 500 requests: 497 evaluated, three
blank-sentence exclusions, zero failures; paired n=497, zero quality missing.
Revalidated raw policy 7,405/7,355 review-valid/50 excluded/0 otherwise invalid or
unclassifiable. Reused prior 497-record input byte-identically after raw joins.
CAS/S/cost/tau=1/recovery limit/router/ESA settings unchanged throughout.

Adaptive recall .789738/coverage .723239, 537 calls; query-aware .774648/.707981,
518 calls; lexical .807847/.741683, 497 calls. Paired adaptive-query recall
+.015091 CI[.005030,.026157]; coverage +.015258 CI[.004192,.027331]. Adaptive
remains below lexical. Bootstrap 10,000, seed1729, paired IDs,95% percentile;
exposed diagnostic inference only. 19 recoveries:17 lexical,2 vector;13 coverage
gains,3 ties,3 losses;16 sufficient afterward,3 abstentions. No ranked no-eligible
or threshold-suppressed case. Multi-hop absent dependency rejects all19.
Final sufficient494 includes25 with zero complete annotated supporting facts.

Verification: focused114 passed in2.06s, full470 passed in6.21s. --verify reproduced
10 analytical files without retrieval; 5,964 stage/ESA replays, all candidate
arithmetic/eligibility, pairing and negative controls passed. Baseline152 files
checked including52 prior outputs; source/config/raw/old results unchanged.
Only README/PROGRESS/HANDOFF/protocol changed plus new unique output directory.
No new qualifying resolved project bug, no error note, dependency or git mutation.

Commands and hashes in REPORT.md. Safe saved-output verification (no retrieval):
.\ai-proj-new\Scripts\python.exe -B outputs/phase5-revised-cas-development-internal-known-exposure-20261022T125412Z-0e6adb98/run_revised_cas.py --verify
.\ai-proj-new\Scripts\python.exe -B outputs/phase5-revised-cas-development-internal-known-exposure-20261022T125412Z-0e6adb98/validate_artifacts.py
Do not repeat --prepare/--execute/--analyze: exclusive writers intentionally reject
existing artifacts; another experiment needs new authorization and a new directory.

Resume point: STOP, current evaluation request complete. Overall Phase5 PARTIAL:
software and scoped revised-CAS diagnostic evaluation complete, original independent
provenance/revision, complete project exposure and approved split/holdout gates
unresolved. Remaining6,905 not certified unseen;100/200 roles provisional. Next
bounded work requires genuine source/acquisition/exposure evidence, not tuning or
relabeling this cohort. Historical previous-policy reports remain intact.

## Phase 5 reconciliation — COMPLETED; overall Phase 5 PARTIALLY COMPLETE (2026-10-22)

Current request satisfied: inspected actual CAS/config/types, working-tree diffs,
tests, backend behavior, original protocol and previous reports; implementation
already exists, so no duplicate source or test changes were made. Current CAS
is (1-current ESA)*binary suitability/C, C=max(.05*calls+.01*nominal returned
chunks+.001*nominal latency_ms,.05), strict CAS > configured tau=1.0.
Suitability and limitations are in docs/deterministic_cas.md; lexical/vector/
hybrid use observable gaps, Multi-hop adds dependency/partial-seed guards.
Initial routing, one-recovery/reassessment/abstention and gold isolation intact.

Phase checklist: 5.1 design complete; 5.2 ingestion/policy/split tooling complete
but cleared preparation blocked; 5.3 corpus/evidence and 5.4 evaluator implemented;
5.5C runner complete; 5.5D development run and 5.6 analysis complete for PREVIOUS
expected-gain CAS, known-exposed 497-question cohort. Revised CAS effectiveness
has not been evaluated. Original independent provenance, complete exposure
history and approved split/holdout allocation are unresolved. Do not mark overall
Phase 5 complete from passing tests. Original 100/200 proposal remains provisional.

Fresh verification commands from C:/ear-rag:
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_deterministic_cas.py tests/test_phase_17_cost_awareness.py tests/test_phase_15_control.py tests/test_runtime_reliability.py tests/test_initial_pipeline.py tests/test_demo.py tests/test_condition_evaluation.py
114 passed in 1.91s.
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests
470 passed in 6.75s.
.\ai-proj-new\Scripts\python.exe -B -m mypy src/ear_rag/routing/cost_awareness.py src/ear_rag/routing/recovery.py src/ear_rag/routing/pipeline.py src/ear_rag/demo.py src/ear_rag/condition_evaluation.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir .mypy_cache/phase5-validation
Five source modules passed. First attempted --cache-dir NUL caused mypy internal
error (exit 1); normal in-repository cache succeeded without source/dependency
changes. This tooling-path issue is not a new resolved project bug.
git diff --check passed. Direct Markdown/link/whitespace and preservation checks
cover untracked documents as well. No benchmark/analysis execution; read/hash-only
checks verified 25 old experiment manifest entries and 10 analysis artifact
entries, including the old expected-gain configuration and 497/3 accounting.

Files changed THIS task: README.md, docs/evaluation_protocol.md, PROGRESS.md,
AGENT_HANDOFF.md. Current README/status checklist supersede stale milestone
claims, with history retained. Protocol section 18 records remaining gates,
exact CAS/cost/suitability rules, validation and next evaluation requirements.
All source/config/tests/data/old outputs and unrelated changes remain unchanged.
No new test was needed; no meaningful bug was resolved or Obsidian note created.

Exact resume: STOP; authorized verification/status task complete. Next work
requires a frozen, explicitly authorized revised-CAS evaluation scope under
protocol sections 2/6/15/17/18. A known-exposed development comparison stays
diagnostic; an exposure-cleared cohort needs genuine provenance/exposure and
allocation evidence. Do not rerun old experiments as smoke tests or modify their
frozen hashes to match current code. No tuning, downloads, split planning, answer
generation, dependency changes or git mutations were performed.

## Deterministic suitability-aware CAS — COMPLETED

Runtime now uses CAS=(1-current ESA)*binary suitability/incremental cost and
strict CAS > configured threshold, retained at 1.0. Cost is
max(.05*calls+.01*nominal returned chunks+.001*nominal latency_ms,.05), next
action only. No predicted future ESA/gain, learned recovery model or runtime
gold labels. Missing/invalid candidate work excludes it, not zero-fills it.
Current ESA is validated finite/in [0,1].

Suitability is binary: missing query tokens OR duplicate normalized evidence OR
fewer than min(k,2) chunks. Alternative lexical/vector/hybrid apply to that gap.
Multi-hop additionally needs dependent=True in the router snapshot, >=2 hops,
a nonempty partial lexical result and novel first-eight seed tokens. No router
snapshot means Multi-hop ineligible; other actions still use observed evidence.
Candidates are allowed/callable/unattempted; fixed tie order lexical/vector/
hybrid/multihop. No eligible action safely stops. A custom policy dispatch guard
remains. One recovery plus reassessment/final abstention are preserved.

Changed runtime modules: routing/cost_awareness.py, recovery.py, pipeline.py,
demo.py and condition_evaluation.py. Config now has candidate lists and nominal
incremental_work; removed gain/old weight fields (old configurations rejected).
Condition version ear_rag_conditions_v2_cas distinguishes revised semantics.
New docs/deterministic_cas.md and tests/test_deterministic_cas.py; updated relevant
README/demo/review guide and three old test modules. Core model, ESA, retrieval,
query analyzer/router and evaluator metric/schema implementations unchanged.

Verification:
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_deterministic_cas.py tests/test_phase_17_cost_awareness.py tests/test_phase_15_control.py tests/test_runtime_reliability.py tests/test_initial_pipeline.py tests/test_demo.py tests/test_condition_evaluation.py
114 passed in 1.90s.
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests
470 passed in 5.08s.
Scoped mypy: five changed source modules passed (command in CAS guide).
git diff --check passed; direct whitespace checks include new/untracked files.
One obsolete fixture now includes a literal gap to keep recovery assertions
meaningful. Unavailable candidates safely exclude; custom-policy dispatch still
raises for unavailable actions. Real Hybrid/Multi-hop recovery tests verify
actual child calls and mandatory reassessment.

Preservation baseline:
C:/Users/anant/AppData/Local/Temp/ear-rag-cas-baseline.json (150 accessible files,
including 52 prior output files). All old outputs/raw data/unrelated work
unchanged. No benchmark, download, dependency, tuning, generation, split or commit.
Logged verified CAS correction to:
C:/Users/anant/MyObsidianVault/Errors/ear-rag-cas-used-predicted-esa-gain.md.

Exact resume: STOP; authorized software task complete. Old Phase 5.5D/5.6 results
were produced by the previous policy and do not validate new CAS. Their frozen
source/config hash checks refer to the previous runtime; do not modify historical
artifacts to make those hashes match new code. Binary S favors cheaper eligible
actions, Multi-hop is conservative, and costs/threshold are uncalibrated.
No effectiveness, hallucination-reduction, sufficiency-calibration or holdout
claim is established. Preserve all preexisting dirty/untracked work.

## Phase 5.6 — analysis complete — development/internal, known exposure

Latest task COMPLETED: final paired-error/recovery/ESA/uncertainty analysis of
the existing Phase 5.5D experiment, with no new retrieval or controller run.
This checkpoint supersedes historical statements below that Phase 5.6 is open;
overall research evaluation, holdout validation and paper completion remain open.

New outputs:
outputs/phase56-analysis-development-internal-known-exposure-20261020T191125Z-ab9ca032/
Read PHASE56_FINAL_REPORT.md and validation.json first. Required report, paired
CSV (497 IDs x two comparisons), recovery CSV (19 rows), ESA proxy JSON and
uncertainty JSON are complete. analyze_saved_results.py --verify reproduces
five analytical files byte for byte; validate_analysis.py verifies artifacts,
saved hashes and preservation. --record refreshes only its validation manifest.
Run from repository root with .\ai-proj-new\Scripts\python.exe -B.

Verified same 497 paired questions, zero failures/missing quality values and
three retained exclusions. All candidate/support hashes and requested order
match the frozen scope. Offline reconstruction matches all 5,964 stage metric/
ESA calculations; all 2,982 control traces are consistent. Prior 26 experiment
files and 37 frozen runtime sources remain unchanged, as do raw/config hashes.
Only PROGRESS and this handoff are changed outside the new analysis directory.

Adaptive-minus-query-aware recall: +1.3078 points, descriptive interval
[0.5030, 2.2133]; adaptive-minus-lexical: -2.0121 [-3.1187, -1.0060].
Paired bootstrap: 497 question IDs, seed 1729, 10,000 resamples. No generalization
or significance claim. Recovery: 12 coverage gains, six ties, one loss; all 19
reassessed. Of nine abstentions, six have complete annotated coverage. Of 488
terminal sufficient decisions, 47 have coverage <.5, including 25 zero.
Complete-support proxy agreement 233/497 is not true sufficiency accuracy.
Semantic answerability, calibration and hallucination reduction are unverified.

Verification: 98 focused tests passed (1.50s standalone, 1.63s validator);
four new synthetic analysis tests stay beside outputs. git diff --check passed.
No runtime/source/config/policy changes, downloads, splits, tuning, generation,
commits or qualifying resolved bug; no new Obsidian error note.

Exact resume point: STOP; this authorized analysis is complete. Recommended
next separately authorized diagnostic task is blinded independent sufficiency
annotation of saved recovery/low-coverage sufficient cases. Do not start it
automatically. Upstream provenance, complete exposure history and defensible
holdout validity remain unresolved. Known exposure is not cleared. Measured
calls/latency are work proxies, with indexing/controller/processed-chunk/monetary
costs unavailable. Preserve all preexisting dirty and untracked work.

## Phase 5.5D experiment execution — COMPLETED (development/internal only)

User now explicitly authorizes development/internal known-exposure experiments
using the historical 500 IDs joined to current distractor contexts/annotations.
This supersedes earlier instructions to stop before real experiments, for this
cohort only. No holdout clearance, tuning or runtime/source/policy changes.
New exclusive output directory:
outputs/phase55d-development-internal-known-exposure-20261020T185946Z-c62ca682
Execution finished: all six conditions requested the same 500 ordered IDs;
each has 497 evaluated, 0 failed, 3 explicit blank-sentence exclusions. Strict
reader accepted the 497 derived records. Saved source/config/scope hashes,
six existing-format JSONL/aggregate reports, summary CSV/JSONL, all 15 paired
comparisons on the same 497 IDs, per-question values and execution marker.
Runner's saved-result validation passed twice, including --validate-only.
Independent arithmetic reproduced all 15 pairs x 6 quality metrics and counts;
all 497 initial query-aware/adaptive retrievals and ESA assessments agree.
Focused six-module suite: 160 passed in 2.16s. No source, policy, configuration
or raw-data edits. REPORT.md contains exact commands and full descriptive results;
summary.csv/summary.jsonl, paired_summary.json and paired_per_question.jsonl are
the machine-readable results. Scope and original/derived source hashes retained.
PROGRESS updated only after completion. Existing artifact checksum validation,
git diff --check and direct whitespace/fence checks passed. Preservation check
over 112 pre-existing accessible files: only PROGRESS and this handoff changed;
all raw sources, configurations, runtime code and old outputs unchanged, none
removed. All new files confined to the new exclusive experiment directory.

Terminal document recall: lexical 80.7847%, Vector Flat 51.2072%, Hybrid 68.7123%,
Multi-hop 80.8853%, query-aware 77.4648%, adaptive 78.7726%. Adaptive versus
query-aware: +1.3078 points on 497 pairs, 36 additional calls. Adaptive versus
lexical: -2.0121 points, 57 additional calls. Adaptive recovery 19/497, final
abstention 9/497. No general effectiveness, novelty or monetary-cost conclusion.
Missing work fields: processed chunks, controller wall latency, monetary cost.

Exact resume point: execution milestone finished; stop. Phase 5.6 stays open for
separately authorized paired-error/recovery/ESA analysis. Do not tune or advance
automatically. Provenance/exposure/holdout validity remain unresolved for future
unseen evaluation. No source changes, downloads, split planning, router training,
generation, commit or qualifying resolved bug; no new Obsidian error note.

## Phase 5.5C checkpoint — COMPLETED (scoped task only)

Task: add only a synthetic-tested six-condition runner, reusing control_evaluation
and demo.build_backends. Verified switches: query_analysis.enabled=False bypasses
selection; recovery.max_recovery_rounds=0 prevents recovery; existing pipeline
caps recovery at one with mandatory reassessment. Preserve all prior work.
Added src/ear_rag/condition_evaluation.py and tests/test_condition_evaluation.py;
updated README, PROGRESS, protocol section 17 and this handoff. All six conditions
are supported. Fixed conditions bypass routing; all no-recovery conditions use
zero rounds. Adaptive explicitly enables configured selection and retains supplied
recovery settings; a supplied zero limit still disables recovery. Full effective
configurations are recorded. Same case list/pools/top-k/settings, fresh indexes/
pipeline/assessor/policy per case/condition; gold annotations stay offline.
Existing reports/aggregates/writer reused, including failures and exclusions.

Final focused command: .\ai-proj-new\Scripts\python.exe -m pytest -q
tests/test_condition_evaluation.py tests/test_control_evaluation.py
Result: 49 passed in 0.93s (17 new tests). Full pytest -q: 423 passed in 4.31s,
no failures/skips; baseline 406 in 4.25s. Scoped mypy passed one new source module
(exact command in protocol section 17). git diff --check passed, existing CRLF
warnings only. Direct whitespace/fence checks include new/untracked files.

Preservation hashes in %TEMP%/ear-rag-phase55c-baseline.json confirm all three raw
sources and every prior project file outside the four requested docs unchanged;
only the new runner/test files added, none removed. No qualifying bug resolved,
no new error note. No real benchmark/effectiveness experiment, splits, tuning,
router labels/training, generation, download, contact or commit performed.

Exact resume point: scoped task finished; stop. Phase 5.5 remains incomplete.
Future real experiments still require independent source provenance, complete
genuine exposure inventory and valid approved allocation; all 500 sample queries
stay exposed, 100/200 provisional, other 6,905 not certified unseen. Policy-valid
is not approved, and strict full-source ingestion still rejects 50 anomalies.
Do not auto-prepare real data or start another phase. Reconcile prior checkpoints
below as historical records rather than current instructions to resume work.

Status: **COMPLETED - Phase 5.2 policy/audit closure; provenance/exposure still blocked**.

## Original Task
Implement minimum JSON-array ingestion, runtime/label projections, split/exposure
checks, reproducible manifests, tests and docs. No downloads, indexing, pipeline/
ESA/routing/recovery changes, benchmarks, training, generation or commits.
Preserve every earlier modification and untracked file. Stop before Phase 5.3.

## Project Context
C:/ear-rag, main at a905925. Earlier Phase 2/5.1 dirty work retained. Existing
Python 3.12.4: C:/ear-rag/ai-proj-new/Scripts/python.exe; editable installation.
Baseline 261 passed in 2.24s. Five prior reliability error notes were read.

## Implementation Plan
- [x] Inspect protocol/docs/readers/tests/config/manifests and available sources.
- [x] Tests first, strict labelled JSON-array reader using current normalizer.
- [x] Explicit runtime and separate evaluation-label projections.
- [x] Explicit-size deterministic split/overlap/exposure checks and manifests.
- [x] Synthetic artifact round-trip, full suite, scoped mypy, docs and hash audit.

## Completed Work / Files
- src/ear_rag/data/hotpotqa.py: read_hotpotqa, HotpotQADataset,
  HotpotQAValidationError, runtime_projection, evaluation_projection. Strict
  all-or-nothing records, duplicate keys/IDs, context/title/sentence/support checks,
  read-only source hash/provenance; exact sentences/spans, offline annotations.
- src/ear_rag/data/normalization.py: only allow missing optional type/level;
  supplied annotation values still validated. Existing dataclasses unchanged.
- src/ear_rag/data/hotpotqa_splits.py: ExposureInventory, plan_splits,
  validate_split_integrity and write_split_artifacts. Explicit role counts,
  SHA256(seed:ID), canonical normalized-text groups, alias/exposure checks,
  counts/role IDs and new-directory runtime/label JSONL plus manifest hashes.
- tests/test_hotpotqa_ingestion.py and tests/test_hotpotqa_splits.py: 57 new cases.
- README.md, PROGRESS.md and docs/evaluation_protocol.md synchronized after each
  logical change; source/manifest scoping and future role-aware loading explicit.

## Historical Utilities Checkpoint / Source Availability
No official distractor JSON array found under data/raw. Only legacy fullwiki
first-500 JSONL and historical study outputs are present. No complete exposure
inventory was supplied. All new outputs are synthetic pytest temporary files;
no real dataset or split artifact was produced, and no authenticity claim made.
The proposed 100 development / 200 internal-holdout roles remain provisional.

## Decisions / Integrity
Reader supports labelled train/dev only; blind test is explicitly unsupported.
Unknown/nested annotations stay offline. Combined NormalizedExample records and
legacy serializers are not the new runtime API; use runtime_projection.
Source checksum stays offline; label-only edits do not alter runtime views.
Missing history is unavailable; unmatched exposure IDs without text are partial.
Both block nonempty holdout. An explicit empty inventory is caller-supplied, not
inferred. Exact IDs and NFKC/lower/whitespace duplicates only; no semantic check
or guarantee that supplied history is exhaustive. Insufficient counts raise.
Writer validates before creating a new directory, refuses overwrite and publishes
manifest last. A failed write without a manifest is not a completed preparation.

## Tests and Errors
Baseline: 261 passed in 2.24s. Reader+legacy normalization: 45 passed in 0.93s.
New reader/split focused tests: 57 passed in 0.69s. Full suite: 318 passed in
3.41s, no failures/skips. Scoped mypy: no issues in both new modules. pip check
and git diff --check passed. Initial missing-module red tests were expected;
minor fact-iterator type annotation corrected, no behavioral repair loop.
No qualifying meaningful bug resolved; no new Obsidian notes, no duplicates.

## Preservation / Git State
Starting hashes: %TEMP%/ear-rag-phase52-baseline-hashes.json. All earlier dirty
source/guide/test changes, all configuration and dependency manifests preserved
byte-for-byte. Existing source changes in this phase are limited to optional
metadata in the normalizer; no retrieval/controller behavior changed.
Final combined tree: seven modified tracked and six untracked files; uncommitted.

## Historical Utilities Next Steps (superseded by gate below)
Stop for review. Before real preparation, obtain the authorized official input,
complete prior-exposure history and approved counts. Do not fabricate clean
holdout claims or substitute legacy fullwiki JSONL for distractor data.
Phase 5.3 after approval: verify manifest/hash/role consistency when loading
runtime-only artifacts; wire exact per-question pools into current controller;
record full selection, initial/post-recovery ESA, actual work and abstention;
join labels offline and reuse metrics. Verify synthetic role/freeze/isolation
before any separately authorized benchmark. No answer generator/EM-F1 yet.

## Instructions for Next Agent
Inspect actual Git state and reconcile newer edits before continuing. Retain all
prior work, read protocol section 9 and PROGRESS, and use handoff/live error
logging on the next authorized task. No reset, stash, clean, commit or automatic
Phase 5.3 continuation is authorized.

## Real-data gate checkpoint (2026-10-20)

**COMPLETED: read-only audit. Real preparation gate BLOCKED.**

Both expected sources fully parsed: 500 unique fullwiki IDs and 7,405 Parquet IDs.
All 500 match with identical questions/answers/supports/type/level; 362 differ in
unordered context content, 138 in order only. No missing/duplicate IDs/questions
or normalized duplicate-question groups. Protocol section 10 gives exact paths,
bytes, hashes, schema, mapping and provenance limitations. Temporary evidence:
%TEMP%/ear-rag-real-gate-baseline.json and %TEMP%/ear-rag-real-gate-audit.json
(diagnostics only, no split/projection).

BLOCKERS: current validator rejects 50 Parquet rows: 49 blank-sentence records;
support index 902 into five sentences on ID 5ae61bfd5542992663a4f261. Fullwiki
passes 146/500; 354 have unresolved support titles. Both source lineages remain
unverified; Parquet metadata gives features/Arrow 21.0.0 producer only. No sidecars.
No complete exposure inventory found. Historical hotpotqa500 report verifies
exposure of all 500 sample IDs with exact questions; hotpotqa20 is a subset.
Other 6,905 IDs are not certified unseen. Old pytest_phase_16c_tmp denied access.

Only four documents changed. Adapter proposed with required tests in protocol;
none implemented. No real role selection/manifests/runtime-label projections,
source repair/filtering, behavior changes, downloads/installs, scoring or Phase 5.3.
Proposed 100/200 provisional. Focused ingestion/split/normalization tests:
**64 passed in 0.96s**. `git diff --check` passed. SHA256 comparison confirms
both raw files and every baseline file outside the four authorized documents
are unchanged; no missing or new nonignored paths. Existing dirty/untracked work
is retained, with no reset/stash/clean/commit.
No meaningful bug resolved; no new Obsidian note. Prior error notes reviewed.

Historical resume point: resolve source-backed sentence/support anomaly policy and
export provenance; reconstruct complete exposure history before real preparation.
Do not interpret audit-only mapped records as an accepted dataset, weaken checks
silently, start Phase 5.3 or run research scoring from this checkpoint.

## Latest JSON Verification / Exact Resume Point

User resolved the missing named input. All three expected files now exist. Exact
data/raw/hotpotqa/hotpot_dev_distractor_v1.json is 46,320,117 bytes, SHA256
4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea
(matches user-supplied digest, not independently authenticated upstream).
Top-level array: 7,405 records / unique IDs; no missing/duplicate IDs, blank
questions, normalized duplicate-question groups, duplicate keys/nonfinite values.

Audit completed: all 7,405 whole records match Parquet after lossless field mapping,
including record, candidate and support order. Both have the same 50 anomalies:
49 blank sentence records; support index 902 into five sentences on ID
5ae61bfd5542992663a4f261. Existing public reader rejects input with diagnostic
7,355 accepted / 50 malformed / 50 rejected / 0 duplicate IDs; no subset released.
Fullwiki overlap 500: question/answer/support/type/level match; 362 unordered
contexts differ, 138 order only. Both historical 500/20 reports rechecked directly
against JSON with matching IDs/questions. All 500 remain exposed, other 6,905
not certified unseen. Complete inventory and 100/200 eligibility unresolved.

Local Zone.Identifier points to Hugging Face referrer/CDN, without repository,
configuration/revision or official upstream identity. No signed URL queries
copied to docs. JSON source envelope absent; authenticity remains unverified.
Format/path gates resolved, data quality/provenance/exposure gates remain blocked.

Only four existing project documents updated. Baseline preservation hashes:
%TEMP%/ear-rag-json-resumed-baseline.json. Audit counts/diagnostic IDs:
%TEMP%/ear-rag-json-verification-audit.json. No derived dataset/projection/split.
No code changes, so no pytest run; real parse/structural/reader/comparison checks
executed successfully as diagnostics (reader rejection is an observed blocker).
No qualifying resolved bug, no new error note. Final `git diff --check` passed;
all three raw SHA256 values unchanged. Every starting file outside the four docs
is byte-for-byte unchanged, with no missing/new nonignored paths. All four docs
have no trailing whitespace and balanced Markdown fences. Prior user work retained.

Next single action: trace the index-902 record against an identifiable official
release, read-only, to establish evidence for a later explicit handling policy.
Stop here. Do not change data/validation, start Phase 5.3, prepare splits or
projections, run research experiments or automatically continue the investigation.

## Latest Index-902 Trace / Exact Resume Point

Completed targeted read-only investigation; protocol section 13 records details.
Raw JSON/Parquet target contexts/supports match. Index 902 appears only as the
fourth support's index; five sentences under its unique title, 64 across record.
Target ID is absent from first-500 fullwiki. In-memory legacy normalization keeps
902 unchanged and five sentence spans; strict validator rejects support[3].
Three raw empty-string examples retain zero-length spans under legacy joining
and are rejected by strict validation. No demonstrated common origin with 902.

Official repo issue #47 (2023-12-20, Ghost---Shadow) quotes same record/anomaly;
this is external corroboration, NOT reproduction from a pinned dataset release
or maintainer confirmation. Official code master identified via git ls-remote:
3635853403a8735609ee997664e1528f4480762a. Pinned README/download.sh/prepro.py
inspected; external dev-v1 file links are not content-pinned dataset revisions.
GitHub API rate limited (403); public pages/raw code and Git remote readable.
No full dataset downloaded, upstream code executed or message sent.

Only protocol and handoff updated for verified facts. No source repair, policy,
tests weakened, split/projection/artifact, research scoring or Phase 5.3.
No pytest needed for unchanged code; targeted checks recorded in protocol.
No qualifying fixed bug, so no new error note. Preservation baseline:
%TEMP%/ear-rag-index902-baseline.json. Final hash checks confirm all three raw
files and every other starting file unchanged except the two documented edits;
no missing/new nonignored paths. `git diff --check` and direct whitespace/fence
checks passed. Existing dirty/untracked user changes preserved.

Next single action: obtain a maintainer-confirmed, revision-identified excerpt
for this record, with release identity/checksum. Do not automatically contact
anyone or continue to policy/Phase 5.3. Stop after reporting this investigation.

## Active Phase 5.3 Task / Exact Resume Point

New user request explicitly authorizes corpus/evidence implementation without
waiting for upstream provenance. Earlier stop instructions are historical.
Preserve strict validation and raw data; no splits/manifests, benchmark, router
labels, tuning, generator, downloads/install, commit or Phase 5.4.

Inspected readers, normalized/core models, character chunker and four backends.
Reuse them. Baseline full suite: 318 passed in 2.94s. All five prior error notes
read. Starting worktree/raw hashes: %TEMP%/ear-rag-phase53-baseline.json.

Plan: (1) tests first for explicit inspection diagnostics with IDs while keeping
strict reader all-or-nothing; (2) per-question corpus adapter using core Query/
Document, source-scoped mapping, chunk-to-sentence locations and separate offline
support matching; (3) synthetic four-backend compatibility and adversarial tests;
(4) focused/full suite, scoped type checks, diff/preservation audit, four docs.
No real-data artifacts or automatic filtering of the 50 invalid records.

Initial resume point (completed): add focused inspection tests before implementation.

Checkpoint: inspection API implemented in hotpotqa.py after 8 expected new-API
red tests; reader/split suite 65 passed in 0.75s. Strict validator untouched;
inspection report includes positions/IDs/reasons; require_valid blocks any errors.
New hotpotqa_evidence.py and synthetic tests: initial 21 passed in 0.39s.
Corpus reuses normalized docs and exposes fresh allowlisted core Query/Documents.
Chunk mapping accounts for character-window stripping; offline matching unions
complete non-whitespace sentence coverage, separately reports title-only hits.
No backend/chunker/controller modifications. Added Unicode/overlap and forged
metadata cases next. Resume: run focused/full tests and scoped mypy, review diff,
update docs and finish source/worktree preservation checks. No real-data artifacts.

## Phase 5.3 Completion / Exact Resume Point

Scoped implementation complete. New APIs in data/hotpotqa.py:
inspect_hotpotqa / HotpotQAInspection with copied structured report and
require_valid (all-or-nothing); read_hotpotqa retains original strict rules.
New data/hotpotqa_evidence.py: build_question_corpus, HotpotQACorpus with fresh
runtime Query/Documents, locate_evidence / EvidenceLocation, offline
match_supporting_evidence / SupportingEvidenceMatch. Labels remain offline;
per-question pools and original IDs/spans reused. Chunk text/source bounds are
verified; title-only/partial-sentence hits do not count as full sentence support.
Whitespace-only gaps may join actual chunk intervals for complete text coverage.

Tests: 8 new inspection cases plus 23 new corpus/evidence cases; synthetic only.
Focused ingestion/evidence/splits/normalization: 95 passed in 1.28s. Full suite:
349 passed in 3.17s (baseline 318), no failures/skips. Scoped mypy: no issues in
both changed source modules. Exact commands/contracts/limitations: protocol 14.
README/PROGRESS updated. Read-only real JSON inspection confirms 7,405 total,
7,355 diagnostic examples, 50 rejected/malformed, zero duplicate IDs; all 49 blank
cases plus index 902 at position 5,059 reported, require_valid blocks release.
No real corpus/projection constructed. Final hashes: all three raw sources and
all previous project work outside the six intended baseline edits unchanged.
Only evidence source/test added; no baseline removals. Diff/direct whitespace/
fence checks passed. Existing user modifications/untracked files retained.

Remaining limitations: real-file 50 validation failures unchanged; upstream
release provenance and complete exposure history unresolved. Phase 5.2 remains
partially blocked, 100/200 provisional; all 500 known questions remain exposed.
No real artifacts/selection/filtering, dependency change, benchmark, tuning,
generator, router labels, controller integration, commit or Phase 5.4 work.
No meaningful bug resolved; expected feature red tests are not new error notes.

Next single step: agree on explicit handling of the 50 invalid source records
before any real evaluation-input preparation. Do not implement that policy or
start Phase 5.4 automatically. Stop after the Phase 5.3 report.

## Active Phase 5.4 / Exact Resume Point

New request authorizes evaluation infrastructure and proposed anomaly-policy
documentation. No real benchmark/splits/manifests, raw changes, downloads,
maintainer contact, tuning/training/generation, commits or Phase 5.5.
Read docs, Phase 5.3 APIs, control traces, existing metrics/report serializers.
Starting hashes: %TEMP%/ear-rag-phase54-baseline.json. Prior error notes retained.

Design: reuse document overlap metric algebra through a small pure extraction
from evaluation_metrics.py, keeping its legacy outputs unchanged. New offline
driver creates fresh runtime-only per-question pipelines via documents-only
factory. Runtime traces precede offline label joins. Final metrics use recovery
alone when present, matching controller semantics. Missing per-invocation calls/
latency remain null; known cost summaries include observation/missing counts.
Evaluated/failed/explicitly excluded rows all retained. Fixed schema JSONL/JSON
writer only targets a new directory. Proposed 50 exclusions are NOT applied.

Next: add synthetic metric/driver tests first, then implement in small slices;
verify isolation, accounting, recovery/abstention, serialization and full suite.

Checkpoint: baseline 349 passed in 3.23s. Pure supporting_document_metrics
extracted from legacy cost-coupled metric helper with old outputs retained;
33 focused new/legacy tests passed in 0.52s. New control_evaluation.py driver,
explicit EvaluationCase, coverage, case aggregation and new-directory JSONL/JSON
writer: first 13 tests passed in 0.35s. Runtime pipeline/backends/ESA unchanged.
Added cutoff, real four-backend/routing, partial/legacy measurements, offline
failure work-retention and schema tests. Next: run expanded tests/mypy, review
availability/accounting edge cases, docs and final regression/preservation.

## Phase 5.4 Completion / Exact Resume Point

Scoped infrastructure complete. New control_evaluation.py provides explicit
EvaluationCase, evaluate_cases, supporting_evidence_coverage, aggregate_cases and
new-directory JSONL/JSON writer. Pure supporting_document_metrics extracted from
existing evaluation_metrics.py without changing legacy cost/utility behavior.
Only runtime documents reach the fresh per-question factory; gold joins happen
offline. No backend, pipeline, ESA or recovery code/config changed.

Schema ear_rag_control_evaluation_v1: per_case rows retain source/IDs, initial/
terminal retrieval locations/metrics, control decisions, actual available work,
errors/exclusion reasons. Counts reconcile; quality/rates use evaluated cases,
failure/exclusion rates requested cases; known work includes failed observations.
Final metrics use recovery-only evidence, never initial+recovery union. First
five chunks define quality cutoff; denominator unique annotated docs/sentences.
Unknown labels/rates/measurements null. Cumulative-only calls not treated as
per-invocation. Real timing naturally variable; fixed-observation reports stable.

Final tests: 32 new synthetic cases. Focused new/legacy/evidence 85 passed in
1.05s; full 381 passed in 3.61s (baseline 349), no failures/skips. Scoped mypy
passed both changed modules. Exact commands, schema and all denominator/availability
rules in protocol section 15. README/PROGRESS synchronized. Final preservation
check: all three raw SHA256 values unchanged; every baseline project file outside
four authorized docs and evaluation_metrics.py unchanged. Only new driver/test
paths added, no baseline removals. `git diff --check`, direct whitespace/fence
checks and final metric-helper diff review passed. Earlier user work retained.

Proposed policy: exclude 49 blank-sentence records and index-902 record in an
initial release, preserving raw bytes and auditing original IDs/source/reasons.
NOT applied. Others eligible only for subsequent validation. Provenance, exposure
and provisional 100/200 remain unresolved. No real driver/effectiveness run,
split/manifest/filtered source, download/install/contact, router labels/training,
tuning, generation/EM-F1, commit or Phase 5.5. No qualifying fixed bug, no note.

Next single action: review the proposed auditable exclusion policy before any
separately authorized real-data preparation. Do not apply it, generate splits,
run a benchmark or start Phase 5.5 automatically. Stop after Phase 5.4 report.

## Active Invalid-record Policy Closure / Exact Resume Point

User now authorizes a reproducible versioned exclusion policy/audit, not a
filtered dataset, approval, split, benchmark or Phase 5.5. Inspectors, evidence
interfaces and docs reviewed. Keep strict reader/normalizer untouched. The
inspector's first-error semantics cannot enumerate overlapping policy defects.
New audit will reuse its record validator/JSON hooks plus an exhaustive scan of
the two exclusion predicates, with separate reliability/identity diagnostics.
Partition total=valid+excluded+otherwise_invalid; unclassifiable is a subset of
otherwise_invalid, not a fourth additive count. No passing record auto-approved.

Starting hashes: %TEMP%/ear-rag-policy-closure-baseline.json. Next: synthetic
tests first, implement audit/JSON writer/CLI, run real source read-only into a
new machine-readable audit report, focused/full/type/diff/hash checks, four docs.
No raw file changes, repairs, splits/manifests, retrieval/controller changes,
experiments, downloads/install, commit or Phase 5.5.

Policy checkpoint: new data/hotpotqa_policy.py + 25 synthetic tests implemented
after expected missing-module red check. Existing strict source untouched.
Focused policy+ingestion: 71 passed in 1.03s; scoped mypy passed new module.
Policy v1 enumerates all blanks/known integer-bound violations; identity/shape
uncertainty remains otherwise-invalid, with observed findings preserved.
No approved-ID list, filtered data or approval returned. CLI writer uses exclusive
new-file creation and deterministic finite UTF-8 JSON. Next: create real audit
docs/hotpotqa_invalid_record_policy_audit_v1.json read-only, independently check
counts/determinism/source hashes, full tests and docs/preservation review.

## Invalid-record Policy Closure Completed / Exact Resume Point

Policy hotpotqa_initial_release_invalid_records_v1, schema hotpotqa_policy_audit_v1
implemented in data/hotpotqa_policy.py. Existing strict parser hooks and record
validator reused unchanged; all policy findings scanned independently. Total
partitions into valid/excluded/otherwise_invalid; unclassifiable is a subset of
otherwise_invalid. Missing/duplicate IDs/ambiguous structure take precedence over
exclusion but retain all observed codes/details. Never an approved-ID list or
filtered dataset. Writer creates new files exclusively, including from CLI.

Real CLI created docs/hotpotqa_invalid_record_policy_audit_v1.json (28,986 bytes).
Current source hotpot_dev_distractor_v1.json: 46,320,117 bytes, SHA256
4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea.
Observed 7,405 total; 7,355 valid; 50 excluded; otherwise_invalid/unclassifiable 0.
49 blank-sentence records plus index-902 case at source position 5,059. Repeated
audit equals saved report, IDs agree with separate strict inspection. This is
audit classification only: evaluation_approval=not_granted, raw input unchanged.

New synthetic policy tests: 25 cases. Policy+ingestion 71 passed in 1.03s;
full 406 passed in 4.15s (baseline 381), no failures/skips; scoped mypy passed.
Exact commands/contracts/results in protocol section 16. Four docs updated.
Final preservation/diff review passed: all three raw SHA256 values unchanged;
every existing project file outside the four authorized docs unchanged, including
all prior code/tests/config/untracked work. Only policy source/test/audit report
added, no baseline removals. `git diff --check` and direct whitespace/fence checks
passed. No qualifying bug fixed, no new Obsidian note.

Closure task complete; Phase 5.2 real preparation still partially blocked by
independent provenance, complete exposure inventory and allocation/approval.
All 500 known questions stay exposed. No dataset materialization, splits/
manifests, runtime change, experiments/tuning/training/generation, download/
install/contact, commit or Phase 5.5. Stop after reporting; do not auto-prepare
the 7,355 passing records or certify the other 6,905 as unseen.
