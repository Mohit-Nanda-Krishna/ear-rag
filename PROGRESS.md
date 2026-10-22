# EAR-RAG Development Progress

## Final completion check — independent evaluation still BLOCKED (2026-10-22)

Re-read Phase6A/6B reports and current status; local MuSiQue inventory and frozen
artifacts are unchanged. No protected support-label cohort, operational authorized
blind evidence scorer or sufficient candidate prior-use record is verified.
Fresh hosted leaderboard checks returned502; public offline gold scorer remains
available but supplies neither missing test gold nor authorized scoring access.
No final evaluation, extra dev benchmark, refit, download or source/config change.
Only README/PROGRESS/handoff clarified; historical reports/outputs remain intact.

Focused command: .\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_learned_router.py tests/test_musique_evidence.py tests/test_condition_evaluation.py tests/test_deterministic_cas.py
Result:78 passed in1.48s. Phase6A30 artifact checksums and49 live frozen
non-document references match; Phase6B8 artifact checksums match. Diff check exit0.
These verify software/artifacts, not final effectiveness or generalization.

No further code work is required for this bounded completion check. The remaining
requirement is verified protected labels or authorized compatible blind scoring,
exact test identity and prior-use/independence evidence; then freeze and evaluate
without tuning. Until supplied, stop; do not relabel used dev/derivative as test.

## Phase 6B audit/validation COMPLETE; protected final evaluation BLOCKED (2026-10-22)

No final benchmark or substitute dev run occurred. No model refit/label generation,
tuning, source/dataset/configuration change, test download or cohort selection.
Audit report: [Phase 6B gate and validation](outputs/phase6b-protected-evaluation-audit-20261022T161807Z-7e19b0ef/REPORT.md).

- Only fitted official train and used official dev/its derivative are local;
  none is an eligible protected final cohort. Test gold, exact cohort identity,
  cross-split overlap and sufficient test-exposure history remain unverified.
- Verified public author offline scorer exists at pinned revision; it needs
  labelled gold and official answer/support predictions, not our retrieval-only
  Hit/Recall@5. Hosted leaderboard access was not verified (browser502/local DNS
  errors); no claim of universal shutdown. No fabricated predictions/submissions.
- Selected model/configuration hashes and runtime integration verified unchanged:
  depth0 single leaf predicts lexical for every supported query with lexical
  available; absence raises, with no fallback. Default remains original heuristic.
  Three synthetic pipeline cases and all2,417 saved dev cases exactly match fixed
  lexical evidence/metrics for trained no-recovery. This establishes software
  equivalence, not a query-dependent learned-routing improvement.
- Fresh focused207 tests passed in3.90s; full519 passed in7.29s; eight-module mypy
  passed. Saved-only replay reproduced16,919 case traces/33,838 metric+ESA stages,
  2,417 paired dev IDs and prior descriptive intervals. No original training
  verifier/refit was run; synthetic tests alone exercise fitting on fixtures.
- Checked30 original Phase6A artifact hashes and50 frozen references (historical
  protocol snapshot retained before this explicit clarification). All runtime,
  model, config, raw data and prior outputs remain unchanged. Current audit
  preservation/checksum results accompany the report. No meaningful resolved bug
  or Obsidian error note.

Minimum next step: verify a custodian-provided protected support-label source or
authorized blind evidence-metric scorer, with exact source/IDs and prior-use/
exposure records; audit overlaps and freeze the unchanged system/protocol before
first outcomes. Dev is selection data and cannot be relabelled final test.
No hallucination, answer correctness, unseen-generalization or superiority claim.

## Phase 6A training/development execution COMPLETE (2026-10-22)

Scope: **development/internal — exposure limitations apply**. No final test or
official scoring procedure is available. Dev has been used for selection and
cannot be relabelled final test. No model/threshold changes after seeing outcomes.

- Acquired only the official author-linked train ZIP member into a new raw
  directory; revision922ac98f19a201998dbdae6d7f2887a5258dbdeb, CC-BY-4.0.
  Train SHA83a75b1e11e4e9bb8f8308e72ac40ca617ae4431b3a0d955b61cab259248490a;
  19,938 valid unique records, zero exclusions. Dev SHA15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b,
  2,417 valid. IDs/normalized questions/decomposition IDs disjoint; 3,696 shared
  normalized paragraph texts disclosed. Existing31 NQ matches remain potential
  exposure indicators, not proof of training. Previous raw data unchanged.
- Added deterministic pure-stdlib CART training and strict query_tree_v1 artifact
  inference using only the existing11 query-text features. Explicit source_split
  supports official train; cached offline example lookup supports full scale.
  Pipeline construction dispatches the chosen router; original heuristic remains
  default. No ESA/CAS/suitability/cost/recovery/backend/config behavior changed.
- Target declared before labels: best fixed-action native paragraph Recall@5,
  then fewest actual calls, then fixed action order. Train targets: lexical17,296,
  vector1,865, hybrid777, multi0. Zero-evidence targets1,706 train/254 dev retained
  and flagged. No missing-action/invalid-case/label exclusions. Gold offline only.
- Frozen depth0/1/2/3, minimum leaf64 search; fit official train only, select dev
  recall/calls/simplicity. **All candidates predict lexical for every dev query**;
  selected depth0 is the training-majority constant. No learned query-dependent
  advantage over fixed lexical was observed; no target/features/search changed.
- [Report/artifact](outputs/phase6a-router-development-20261022T155210Z-95732e1d/REPORT.md):
  model SHA12e44dc3ac8f17300b90082021feffc0dfafc37d6e7737276d89088e6c5bd204.
  Trained router no recovery: Hit.840712/paragraph Recall.479555/2,417 calls,
  exactly fixed lexical. Original heuristic .779065/.437043/2,493 calls.
  Paired trained-minus-original recall+.042511, descriptive95% CI[.035685,.049510],
  n2,417. Agreement with proxy targets86.7489% train/86.0571% dev. Selection-biased
  development intervals do not establish unseen generalization.
- Trained adaptive: .841125/.479692/2,423 calls, six recoveries, six abstentions;
  initial nominal265.87 plus recovery.66 abstract units. All dev methods requested
  and evaluated2,417, zero failed/excluded/unpaired. Sentence coverage and monetary/
  full-controller/processed work remain unavailable. Full distributions/groups/
  baseline costs and uncertainty are saved, separate from source data.
- Before training: focused177 passed in1.71s, full519 passed in7.26s, mypy five
  modules passed, diff check passed. Twelve new synthetic tests cover isolation,
  deterministic labels/model/order/features, artifacts/errors/four actions,
  no fallback and unchanged recovery/reassessment; existing regression suite green.
  Saved replay/preservation results are recorded in the output verification files.

Exact commands and frozen50 source/config/protocol/test/input hashes are in the
new output directory. Phase 6A execution complete; final protected evaluation
remains blocked on independent exposure/test and verified scoring prerequisites.
No answer generation, hallucination reduction or published-method superiority
claim. Prior experiment outputs/dirty work preserved; no commits or error notes.

## MuSiQue integration and official-dev evaluation — COMPLETE within development/internal scope (2026-10-22)

Latest authorized task complete: **development/internal — exposure limitations
apply**. This entry supersedes the earlier Part 2 approval-pending audit; it does
not close independent-exposure/holdout requirements or authorize Phase 6 training.

- Added strict native MuSiQue JSONL ingestion/diagnostics/manifest and native
  paragraph-ID corpus/quality adapter. The existing control/condition evaluator,
  serialization, aggregation and bootstrap are reused. Exact source-window
  validation is shared through a structural type; HotpotQA scoring is unchanged.
- Verified official source SHA256
  15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b:
  2,417 unique answerable records, 48,315 candidates, 6,404 supports, zero
  exclusions/unclassifiable. Author-linked revision/license in acquisition
  manifest retained. Third-party IDs/questions/answers/aliases/flags/candidates
  agree; it is not the evaluation input. 31 NQ decomposition-text matches remain
  potential exposure indicators; six duplicate-question groups are retained.
- Frozen protocol section 20, config/source/input hashes, identical ordered
  pools/top-k and all six v2 conditions. Ran once, no tuning: each requested and
  evaluated 2,417, failed/excluded zero; paired n=2,417. Paragraph metrics use
  first-five chunks deduplicated by native parent idx, never title. Sentence
  coverage remains null with an explicit unavailable reason.
- [Results](outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73/REPORT.md):
  adaptive Hit .829541 / paragraph Recall .473900 / 2,810 calls; router-only
  .779065/.437043/2,493; fixed lexical .840712/.479555/2,417. Adaptive-minus-
  router recall +.036857 [95% paired CI .030651,.043339]; versus lexical
  -.005654 [-.008688,-.002689]. Intervals are descriptive development bootstrap
  estimates (10,000 draws, seed 1729), limited by repeated questions/components.
- 317 recoveries: 199 paragraph-recall improvements, 90 ties, 28 regressions;
  lexical selected 311 times, vector six. Reassessment yields 311 sufficient,
  six uncertain. Final 2,411 generate/evidence-ready and six abstain; 2,058
  sufficient cases still lack complete annotated paragraph recall. No generated
  answer correctness or semantic sufficiency is established.
- Nominal initial work cost 270.43 plus recovery 34.87 = 305.30 abstract units;
  actual calls/chunks/retrieval latency remain separate work proxies. Full
  controller/indexing/processed work and money are unavailable. No learning,
  policy/configuration changes, new downloads, splits or old-output changes.
- Focused 150 passed in 2.71s; full 507 passed in 6.68s; mypy six modules passed;
  git diff check passed before execution. Saved 29,004 paragraph-stage replays,
  paired accounting, hashes and exact analysis/report reproduction passed.
  Additional read-only ESA/CAS replay and preservation checks are recorded in
  the experiment's supplemental record. Tests verify software, not effectiveness.

See [implementation/commands/limitations](docs/musique_dataset_audit.md) and the
experiment artifacts. Remaining: complete historical exposure/independent
evaluation clearance, verified labelled official-test/scoring access, stronger
backend/ESA validation and separately scoped answer generation. Phase 6 router
training remains pending. No claim of hallucination reduction, unseen-data
generalization or superiority over published methods; stop after this task.

## Revised-CAS diagnostic evaluation — COMPLETE; Phase 5 PARTIAL (2026-10-22)

This checkpoint supersedes the earlier "not experimentally evaluated" status below.
User-authorized scope: **development/internal — known exposure**; no cleared
holdout, tuning or runtime change. Frozen protocol was written before execution.

- Output/report: [revised-CAS experiment](outputs/phase5-revised-cas-development-internal-known-exposure-20261022T125412Z-0e6adb98/REPORT.md).
  HEAD a905925db843db98e4dbc848ceb85696b48c693b plus all 37 runtime hashes,
  current config SHA b494caae97e83ff6d095f0f0133b58b0ea6b281f63d62e0f378c8e7a0b6b4835,
  dirty patch, raw/history/derived input hashes and exact settings are frozen there.
- Reapplied raw invalid-record policy: 7,405 inspected; 7,355 structurally valid
  for review; 50 excluded; otherwise invalid/unclassifiable zero. Known 500 exact
  ID/question joins yield 497 strict cases/3 blank-sentence exclusions. Reused
  existing derived input unchanged; no new split or provenance/exposure approval.
- Ran all six current v2 conditions ONCE. Each: 500 requested, 497 evaluated,
  3 excluded, 0 failed; identical ordered IDs/pools/labels/top-k; paired n=497.
  Query/adaptive initial evidence/ESA/routing match; no missing quality values.
- Adaptive recall .789738, coverage .723239, Hit .969819; 537 calls. Query-aware
  no-recovery: .774648/.707981/.959759, 518 calls. Fixed lexical:
  .807847/.741683/.971831, 497 calls. Paired adaptive-minus-query recall +.015091
  [95% CI .005030,.026157], coverage +.015258 [.004192,.027331]. Adaptive-minus-
  lexical recall -.018109 [-.027163,-.009054], coverage -.018444 [-.027834,-.009725].
  Bootstrap: question IDs, 10,000 resamples, seed 1729; secondary comparisons
  exploratory. No unseen-generalization claim.
- 19 recoveries: 17 vector->lexical, two lexical->vector; coverage 13 gains,
  3 ties, 3 regressions. All best CAS >1; zero threshold suppression/no-eligible
  ranked cases. Multi-hop recovery ineligible in all 19 (no dependency signal).
  Final ESA 494 sufficient/3 uncertain; 25 sufficient have zero annotation coverage.
  Nominal CAS cost is separate from actual calls/chunks/latency; uncalibrated.
- Focused tests 114 passed in 2.06s; full suite 470 passed in 6.21s. Ten analytical
  files reproduced byte-for-byte without retrieval; 5,964 saved stage/ESA replays,
  76 candidate entries/38 eligible CAS arithmetic checks and pairing validated.
  Negative controls and failure accounting passed. No meaningful resolved bug;
  zero new error notes. Final validation/checksums accompany the report.
- Changed only README.md, PROGRESS.md, AGENT_HANDOFF.md and protocol; new artifacts
  stay in the unique output directory. All preexisting runtime/config/tests/raw
  data and 52 prior output artifacts preserved. No commit or dependencies.

Phase 5 software and frozen revised-CAS diagnostic execution/analysis complete.
Original upstream provenance, complete project exposure and approved role/split
requirements remain unresolved. Proposed 100/200 roles unapproved; remaining
6,905 questions not certified unseen. Next bounded task: supply genuine acquisition/
revision and exposure evidence, then assess allocation eligibility. Stop here;
no automatic new phase or policy tuning.

## Phase 5 reconciliation — PARTIALLY COMPLETE (verified 2026-10-22)

Current software/CAS verification and status reconciliation are complete. Overall
Phase 5 remains partially complete: revised-CAS research evaluation is outstanding,
and original source-provenance, full exposure-history and approved holdout/split
gates remain unresolved. Older entries below are milestone snapshots. Phase 5.6
remains analysis complete — development/internal, known exposure, for the previous
formula; it is not validation of the revised runtime.

| Original requirement / milestone | Status |
|---|---|
| 5.1 dataset/protocol design | Complete design; proposed 100/200 roles unapproved |
| 5.2 ingestion, policy and split validation | Software/audits complete; cleared real-data preparation still blocked |
| 5.3 corpus/evidence pipeline | Implemented and tested for bounded candidate pools |
| 5.4 evaluation/metrics infrastructure | Implemented; unavailable answer/full-cost fields stay unavailable |
| 5.5C six-condition runner | Implemented; current version ear_rag_conditions_v2_cas |
| 5.5D development experiment | Scoped previous-policy run complete, 497 evaluated/3 excluded/0 failed per condition |
| 5.6 paired error/ESA/uncertainty analysis | Scoped previous-policy analysis complete; no holdout/effectiveness clearance |
| Revised deterministic CAS | Runtime present and freshly software-verified; no revised-policy experiment |

- Inspected actual runtime/types/config, backend instrumentation, current diffs,
  tests, original protocol and saved reports. Existing CAS already implements
  (1-current ESA)*binary suitability/C; C=max(.05*calls+.01*nominal returned
  chunks+.001*nominal latency_ms,.05), strict CAS > tau (1.0). No duplicate code,
  new behavior, source/test/config change, tuning or dependencies were needed.
- Suitability gap: missing query tokens OR normalized-text duplicates OR fewer
  than min(k,2) chunks. Alternative lexical/vector/hybrid require that gap;
  Multi-hop also requires dependent=True, >=2 hops, a nonempty partial lexical
  result and novel first-eight seed tokens. S is exactly 0/1, a proxy rather than
  predicted success or semantic coverage. Callable/allowed/unattempted actions
  are ranked deterministically; no eligible action stops. One round, reassessment,
  abstention and gold separation are verified by existing tests.
- N_chunks means nominal final returned context chunks, not processed/child work.
  Calls/budgets are 1/1/2/max_hops; latency/chunks are configured assumptions.
  Estimated incremental cost excludes initial work, while actual calls/chunks/
  latency are recorded afterward. Coefficients/floor/threshold are uncalibrated
  engineering choices, not monetary or normalized token/compute cost.
- Fresh commands from C:\ear-rag:

```powershell
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_deterministic_cas.py tests/test_phase_17_cost_awareness.py tests/test_phase_15_control.py tests/test_runtime_reliability.py tests/test_initial_pipeline.py tests/test_demo.py tests/test_condition_evaluation.py
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests
.\ai-proj-new\Scripts\python.exe -B -m mypy src/ear_rag/routing/cost_awareness.py src/ear_rag/routing/recovery.py src/ear_rag/routing/pipeline.py src/ear_rag/demo.py src/ear_rag/condition_evaluation.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir .mypy_cache/phase5-validation
git diff --check
```

- Results: focused 114 passed in 1.91s; full 470 passed in 6.75s; mypy passed
  five source modules; diff check passed. These verify software, not effectiveness.
  Hash-only checks verified 25 old experiment manifest entries and 10 analysis
  artifact entries, including old expected-gain configuration; no scoring ran.
- Files changed this task only: README.md (current capability/history wording),
  docs/evaluation_protocol.md (current status and section 18 checklist/evaluation
  gate), this PROGRESS.md and AGENT_HANDOFF.md (verified status/resume point).
  All preexisting source/config/tests/data/results and unrelated work preserved.
- Next required action: freeze revised-policy evaluation definitions and explicitly
  authorize a data scope under protocol sections 2/6/15/17/18. Known-exposed
  development scope would stay diagnostic; a holdout requires the missing genuine
  provenance/exposure/allocation evidence. Do not silently rerun old experiments,
  create splits, tune on the existing 497 questions or relabel them unseen.
- No new qualifying resolved bug or Obsidian error note. No experiment, download,
  split, generation, external provenance audit, commit/reset/stash/clean occurred.
  Stop: this authorized reconciliation is complete; Phase 5 research gates remain.

## Deterministic suitability-aware CAS — implementation COMPLETED

- Runtime CAS is now (1-current ESA)*binary suitability/incremental cost, with
  strict CAS > configured threshold (retained 1.0). No expected ESA gain or
  predicted future score remains in the recovery decision/configuration/output.
- Cost=max(.05*additional calls+.01*nominal returned chunks+.001*nominal latency
  ms,.05). Costs are explicit next-action engineering assumptions, not money or
  measured future work. Missing/invalid cost components exclude candidates;
  current ESA must be finite/in [0,1]. No initial work is charged again.
- Evidence gap is missing query tokens, normalized-text duplicates, or fewer
  than min(k,2) chunks. Lexical/vector/hybrid are alternative applicable rankings;
  Multi-hop additionally requires an observed dependency flag, >=2 hops, a
  nonempty partial lexical result and novel first-eight seed tokens. Rules are
  binary, deterministic proxies, not semantic sufficiency or success predictions.
- Callable, configured, unattempted candidates are ranked with a stable tie-break;
  no eligible candidate safely stops. Existing one-recovery pipeline, ESA
  reassessment, final abstention, initial routing and gold separation are preserved.
  Existing pre-action chunk-budget semantics remain; no new recovery loop.
- Demo and condition factory use revised policy. Condition version is now
  ear_rag_conditions_v2_cas. Existing Phase 5.5D/5.6 artifacts are historical
  previous-policy results and do not validate this replacement. No benchmarks,
  parameter tuning, dataset changes, generation or new dependencies.
- New docs/deterministic_cas.md records exact rules, costs, APIs, limitations and
  commands. README/demo/internal-review notes clarify current versus saved output.
- Focused synthetic suite: 114 passed in 1.90s. Full tests: 470 passed in 5.08s.
  Scoped mypy passed five source modules; git diff --check passed. One legacy
  fixture now includes an observable gap so its recovery/reassessment assertions
  remain meaningful; dispatch guard regression retained for custom policies.
- Baseline hashes cover 150 accessible files, including 52 old output files;
  no old output, raw dataset, retrieval/ESA/initial-router implementation or
  unrelated modification was changed. CAS correction logged in Obsidian:
  Errors/ear-rag-cas-used-predicted-esa-gain.md.
- Stop: scoped software correction complete. No effectiveness, calibrated
  sufficiency, hallucination-reduction or holdout-validity claim. Binary S favors
  the cheapest eligible candidate; nominal latency/chunks and the operating
  threshold remain uncalibrated. Provenance/exposure limitations remain open.

## Phase 5.6 — analysis complete — development/internal, known exposure

- Completed analysis of the saved Phase 5.5D experiment only; no benchmark,
  retrieval, indexing, controller execution, answer generation or tuning.
  New analysis directory:
  outputs/phase56-analysis-development-internal-known-exposure-20261020T191125Z-ab9ca032/
- PHASE56_FINAL_REPORT.md, paired_error_analysis.csv (497 IDs x two comparisons),
  recovery_case_analysis.csv (19 rows), esa_reliability_analysis.json,
  uncertainty_analysis.json and validation.json are complete. Reproduction and
  preservation scripts, four synthetic analysis tests and hashes are retained.
- Same 497 evaluated questions in every condition; zero failures/missing quality
  pairs. All three previous blank-sentence exclusions remain excluded. Candidate
  context/support hashes and ordered IDs reproduce the frozen experiment scope.
- Adaptive-minus-query-aware document recall: +1.3078 percentage points,
  descriptive paired-bootstrap interval [0.5030, 2.2133]; adaptive-minus-lexical:
  -2.0121 points [-3.1187, -1.0060]. Seed 1729, 10,000 resamples of question IDs.
  These describe the exposed cohort, not generalization or research superiority.
- All 19 recoveries reassessed: coverage/recall improved in 12, tied in six,
  worsened in one. Nine final abstentions; six have complete annotated coverage.
  Of 488 terminal sufficient decisions, 47 have annotated coverage below .5,
  including 25 with zero. Proxy agreement 233/497; not true sufficiency accuracy,
  calibration or evidence of hallucination reduction.
- Replayed 5,964 saved stage metrics/ESA signals and checked 2,982 control traces;
  no inconsistencies. Analytical outputs regenerate byte for byte. Focused suite:
  98 passed (1.50s standalone; validator run 1.63s). git diff --check passed.
  Prior 26 experiment files, 37 frozen runtime sources and raw/config hashes
  unchanged. Only this file and AGENT_HANDOFF.md changed outside the new output
  directory; preexisting work preserved. No qualifying Obsidian error note.
- Exact stop: Phase 5.6 scoped analysis complete. Overall research evaluation,
  holdout validation and paper completion remain open. Provenance, complete
  exposure evidence, defensible holdout validity and independent answerability
  labels remain unresolved; indexing/controller/processed-chunk/monetary costs
  are not measured. Recommended next separately authorized task: blinded
  sufficiency annotation of saved diagnostic cases; no automatic phase advance.

## Phase 5.5D development/internal experiment execution — scoped milestone COMPLETED

- Explicitly authorized cohort: historical hotpotqa500 IDs in saved report order,
  joined to current distractor JSON. Label throughout: development/internal —
  known exposure. No holdout, unseen or exposure-clearance claim.
- Existing invalid-record policy reproduced; cohort has exactly three blank-
  sentence exclusions: 5a72c6f65542994cef4bc402, 5a7320565542991f9a20c61d,
  5abbd3ac55429931dba1458b. Derived 497-record copy passes existing strict reader;
  raw records unchanged, original positions/source and derived hashes recorded.
- Existing six-condition runner executed with unchanged configuration/top-k 5
  and isolated state. Each: requested 500, evaluated 497, failed 0, excluded 3.
  Same distractor candidate pools and offline supporting annotations throughout.
- New exclusive output directory:
  outputs/phase55d-development-internal-known-exposure-20261020T185946Z-c62ca682/
  REPORT.md records exact commands, conditions, full metrics/control/work,
  missing measurements, exclusions and all 15 paired comparisons. Existing
  JSONL/aggregate serialization reused; script and frozen inputs retained.
- Terminal support-document recall@5: lexical 80.7847%, Vector Flat 51.2072%,
  Hybrid 68.7123%, Multi-hop 80.8853%, query-aware/no-recovery 77.4648%, adaptive
  78.7726%. Pairing uses the same 497 IDs, no missing quality measurements.
  Adaptive versus query-aware: +1.3078 points recall (12 better/1 worse/484 tied),
  36 extra calls; versus lexical: -2.0121 points, 57 extra calls. Descriptive
  known-exposed development findings only; no general effectiveness claim.
- Adaptive recovers 19/497 and reassesses all 19; terminal abstentions 9/497.
  Processed-chunk work, controller wall latency and monetary costs unavailable;
  actual calls/chunks and reported retrieval latency are work proxies only.
- Relevant six-module synthetic suite: 160 passed in 2.16s. Serialized output
  validator and independent pairing arithmetic passed; original runtime sources,
  configuration and raw source hashes unchanged. No tuning or source-code edits.
- Phase 5.6 is NOT complete: review paired errors/recovery regressions and ESA
  reliability, then decide separately authorized analysis. Provenance/exposure/
  holdout-validity blockers remain unresolved. No router training, answer
  generation, external provenance investigation, download, split planner or commit.
  No qualifying resolved bug or new Obsidian error note.

## Phase 5.5C minimal condition runner — scoped task COMPLETED

- Added `condition_evaluation.py`: six named conditions, reusing `evaluate_cases`,
  its aggregation/serialization, `demo.build_backends`, existing ESA, recovery
  policy and controller. No runtime scoring/controller source changes.
- Fixed lexical/vector-flat/hybrid/multihop conditions disable query selection
  and recovery; query-aware condition enables selection with zero recovery;
  adaptive enables selection and preserves supplied recovery settings. Existing
  controller permits at most one recovery followed by mandatory reassessment.
- Same explicit question list, question-scoped source candidate pools, top-k and
  backend/ESA settings; fresh per-case/per-condition indexes, assessor, policy
  and pipeline. Gold labels stay in offline evaluation. Condition/version/pool/
  effective configuration added to rows and existing aggregates, including failures.
- Baseline: 406 passed in 4.25s. Added 17 synthetic tests; focused runner+driver:
  49 passed in 0.93s. Full: 423 passed in 4.31s, no failures/skips. Scoped mypy
  passed one source module. Exact commands in protocol section 17.
- No benchmark/effectiveness experiment, real-data preparation, splits, router
  labels/training, tuning, generation, download or commit. Phase 5.5 remains
  incomplete. Independent source provenance, complete prior exposure inventory
  and valid approved split allocation remain unresolved; all 500 sample queries
  remain exposed, 100/200 roles provisional. Policy-valid is not evaluation-approved.
- No qualifying resolved bug; no error note created. Final preservation and
  whitespace checks are recorded in the handoff.

## Phase 5.2 invalid-record policy closure - policy/audit task COMPLETED

- Reviewed current inspectors/evidence APIs and phase documentation. Baseline:
  **381 passed in 3.81s**. Starting raw/worktree hashes saved to
  %TEMP%/ear-rag-policy-closure-baseline.json. Strict ingestion unchanged.
- New data/hotpotqa_policy.py defines schema hotpotqa_policy_audit_v1 and policy
  hotpotqa_initial_release_invalid_records_v1. Reuses existing strict record
  validation and JSON hooks, collecting all blank-sentence and uniquely resolved
  integer out-of-range findings rather than parsing first-error messages.
- Deterministic report partitions total=valid+excluded+otherwise_invalid.
  Unclassifiable is a subset of otherwise_invalid, covering missing/duplicate IDs
  or incomplete structure/bounds. All observed policy codes/details remain even
  on those rows. Repeated findings/overlapping codes count a record once; reason
  counts are per-code and explicitly nonadditive. No valid/approved ID list.
- New exclusive-create JSON writer/CLI refuses existing files, including raw
  input. Reports source filename/size/SHA256, version, counts, every excluded or
  otherwise-invalid position/ID, reason codes/details and reliability markers.
  Evaluation approval is always not_granted; unreadable/unparseable inputs are
  errors, never fabricated zero-success datasets.
- Ran CLI on existing hotpot_dev_distractor_v1.json; created only
  docs/hotpotqa_invalid_record_policy_audit_v1.json (28,986 bytes). Observed source
  size 46,320,117 bytes, SHA256
  4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea.
  **7,405 inspected; 7,355 valid; 50 excluded; 0 otherwise invalid; 0 unclassifiable**.
  Exclusion reasons: 49 blank candidate sentences, one index 902 into five
  sentences (ID 5ae61bfd5542992663a4f261, source position 5,059). Repeated audit
  is exactly equal; excluded IDs agree with independent existing strict inspection.
- Added 25 synthetic cases, independent of ignored data: 49-blank pattern,
  index 902, repeated/overlapping defects, missing/duplicate IDs, malformed bounds,
  determinism/hash changes, file errors, source preservation, writer/CLI safety.
  Focused policy+ingestion: **71 passed in 1.03s**. Full suite: **406 passed in
  4.15s**, no failures/skips. Scoped mypy: no issues in new module. Expected
  missing-module red test preceded implementation; no qualifying fixed bug/note.
- README, protocol and handoff updated; exact commands/definitions in section 16.
  Final hash/diff checks in handoff. No raw repairs/filtering, runtime changes,
  splits/manifests, evaluation experiments/tuning/router training/generation,
  downloads/install, commit or Phase 5.5. Earlier user work preserved.
- Policy classification is implemented and audited, not merely proposed now.
  Phase 5.2 real preparation remains partially blocked by independent upstream
  provenance, complete exposure history and provisional allocation/approval.
  No passing record, including the other 6,905 questions, is certified unseen.

## Phase 5.4 evaluation infrastructure/metrics - scoped implementation COMPLETED

- Inspected Phase 5.3 APIs, pipeline traces, metrics, serializers and docs.
  Baseline full suite: **349 passed in 3.23s**. Starting hashes:
  %TEMP%/ear-rag-phase54-baseline.json. Earlier user changes retained.
- Extracted pure `supporting_document_metrics` from the legacy cost-coupled
  helper; legacy utility/call/latency behavior retained and existing tests pass.
- New control_evaluation.py: explicit EvaluationCase, evaluate_cases, evidence
  coverage, aggregate_cases and new-directory-only JSONL/JSON writer. Only fresh
  runtime documents reach the per-question pipeline factory; trace snapshots
  precede offline label joins. Runtime behavior/configuration unchanged.
- Metrics: Hit@5, unique supporting-document Recall@5 and complete supporting-
  sentence coverage within the first five chunks. Initial/terminal separate;
  terminal uses recovery alone if present. Empty-label quality/zero-denominator
  rates are null. Record denominators and requested/evaluated/failed/excluded
  counts reconcile; failed/excluded rows and reasons are never dropped.
- Backend frequencies, recovery/abstention and ESA decision counts accompany
  actual calls/returned chunks/retrieved passages/available latency. Missing or
  cumulative-only calls are not invented; observation/missing counts accompany
  means/totals. Unknown processed chunks, wall time and monetary cost stay null.
- Proposed exclusion of 49 blank-sentence records plus index-902 record is
  documented, not applied. Future exclusions require IDs/reasons/source identity.
  Other records remain eligible only for further validation. Provenance/exposure,
  provisional 100/200 roles and strict-reader rules remain unresolved/unchanged.
- Added 32 synthetic tests. Focused new/legacy/evidence checks: **85 passed in
  1.05s**. Full suite: **381 passed in 3.61s**, no failures/skips. Scoped mypy
  passed both changed modules. Exact commands/schema/denominators in protocol 15.
  Expected missing-API/schema red tests preceded implementation; no bug note.
- Four docs updated; final preservation/diff checks in handoff. No real run,
  benchmark, split/manifest, raw edit, download/install, contact, router labels,
  tuning, generation/EM-F1, commit or Phase 5.5. No meaningful bug resolved;
  no new Obsidian note. Next single step: review the proposed auditable exclusion
  policy before separately authorized real-data preparation; other gates remain.

## Phase 5.3 corpus/evidence layer - scoped implementation COMPLETED

- User explicitly authorized this layer without waiting for complete upstream
  provenance. Phase 5.2 remains **partially blocked** for real preparation; this
  does not approve an invalid subset, certify unseen questions or adopt 100/200.
- Reused strict validation, normalized/core models, sentence offsets and existing
  chunker/lexical/vector/hybrid/multi-hop backends. Inspected prior documentation
  and five error notes. Starting full suite: **318 passed in 2.94s**. Baseline
  source/raw hashes: %TEMP%/ear-rag-phase53-baseline.json.
- Added `HotpotQAInspection` / `inspect_hotpotqa` in data/hotpotqa.py. Structured
  record diagnostics have position, ID (or None), first validation reason and
  existing counts; valid examples remain offline diagnostics. `require_valid`
  blocks release on any error. Strict reader now uses this shared path with the
  same validation rules/counts and all-or-nothing rejection. No sentence/index
  repair or silently approved subset. Eight expected new-API red tests preceded
  implementation; reader/split checks then **65 passed in 0.75s**.
- New data/hotpotqa_evidence.py: per-question corpus exposing fresh core runtime
  objects with allowlisted document metadata; source checksum retained offline.
  Stable local document IDs and original paragraph/sentence ordering reused.
  Chunk resolver checks source IDs/window/text and compensates for chunk trimming;
  reports overlapping versus completely covered sentence indices separately.
- Offline support matcher checks source identity and canonical question/documents,
  unions actual text intervals per candidate, permits whitespace-only gaps and
  returns distinct sentence/support/title sets. Partial sentence overlap or a
  title hit alone is not a support-sentence hit. No semantic entailment or
  numerical effectiveness metric is inferred.
- New tests/test_hotpotqa_evidence.py: 23 synthetic cases, including four existing
  backends, source isolation, wrong sentence, partial/combined coverage, Unicode,
  whitespace trimming, forged metadata, missing offsets and source immutability.
  Added eight inspection cases to tests/test_hotpotqa_ingestion.py. All tests use
  temporary synthetic data; no ignored real source dependency.
- Focused ingestion/evidence/splits/normalization: **95 passed in 1.28s**.
  Full regression suite: **349 passed in 3.17s**, no failures/skips. Scoped mypy:
  **Success: no issues found in 2 source files**. Exact commands in protocol
  section 14. Read-only new inspector check on the real JSON: total 7,405,
  diagnostically accepted 7,355, rejected/malformed 50 (49 blank-sentence records
  plus index 902 at source position 5,059); require_valid correctly blocks release.
  No real corpus or projection was constructed. Review found no need to alter retrieval/chunking/controller behavior,
  dependencies or existing fixtures. Final diff/hash results recorded in handoff.
- Updated README, protocol and handoff. No real corpus/export/split/manifest,
  downloads/install, router labels, experiments, tuning, generator, commit or
  Phase 5.4. No qualifying resolved bug; no new Obsidian note. Existing user work
  retained. Next single step: agree on an explicit policy for the 50 invalid
  records before real evaluation-input preparation; no policy selected here.

## Resumed Phase 5.2 JSON audit - verification complete; preparation BLOCKED

- Exact requested JSON now exists: 46,320,117 bytes, SHA256
  `4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea`,
  matching the user-supplied digest. Fully parsed top-level array: 7,405 records
  and unique IDs; no missing/duplicate IDs, blank questions or normalized-text
  duplicate-question groups. No duplicate keys or non-finite JSON constants.
- Existing public reader rejects all-or-nothing: 7,355 diagnostically accepted,
  50 malformed/rejected. Independent structural checks find exactly 49 blank
  sentence records (one blank each) and one invalid support index: 902 into five
  sentences for Jimmy Butler (basketball), ID 5ae61bfd5542992663a4f261.
- JSON vs Parquet: 7,405 overlapping IDs, none missing or duplicated; all questions,
  answers, ordered supports/contexts, type/level and record order match exactly
  after representation mapping. All 50 prior anomalies remain unchanged.
- Fullwiki vs JSON: all 500 IDs overlap with exact question/answer/support/type/
  level agreement; 362 unordered context contents differ, 138 order only.
  Historical hotpotqa500 report rechecked: all IDs/text match; hotpotqa20 subset
  also matches. All 500 remain exposed, other 6,905 not certified unseen.
- Windows download metadata identifies Hugging Face referrer/CDN host only.
  User-supplied checksum is not independent canonical-source authentication;
  official revision/lineage, anomaly policy and complete exposure remain unresolved.
  Section 12 of the protocol records evidence and supersedes the path-only stop.
- Only four authorized docs changed; no code/raw repairs, downloads, installs,
  splits/manifests/projections, derived datasets, experiments or Phase 5.3.
  No pytest necessary for this read-only audit; final hash/diff verification in
  handoff. No qualifying bug fixed and no new Obsidian note. 100/200 provisional.
- Next single step: trace the index-902 record against an identifiable official
  release, read-only, before proposing an evidence-backed handling policy.

## Phase 5.2 new JSON verification - stopped at missing-path gate

- Requested `data/raw/hotpotqa/hotpot_dev_distractor_v1.json` is absent. The
  request explicitly requires stopping affected comparisons for missing inputs.
- Discovered `hotpot_dev_distractor_v1 (1).json`: 46,320,117 bytes, SHA256
  `4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea`,
  matching the supplied expected digest. This does not independently authenticate
  its source or authorize silent substitution for the missing named file.
- No JSON parse/record count/validation/comparison was performed. Whether the
  previous 50 Parquet anomalies persist in JSON is unverified. Existing fullwiki
  and Parquet hashes are unchanged. Prior exposure findings remain applicable;
  no unseen eligibility or 100/200 split claim is made.
- Updated only README, protocol, progress and handoff; no code/raw data changes,
  renaming, downloads, dependencies, derived datasets, splits, projections,
  experiments or Phase 5.3. No pytest needed for this path-only documentation
  task. Preservation and whitespace checks recorded in the handoff.
- No qualifying fixed bug; no Obsidian error note. Phase 5.2 remains blocked.
  Next single step: identify the existing `(1).json` explicitly as the audit input.

## Phase 5.2 real-data gate - audit completed; preparation BLOCKED (2026-10-20)

- Both expected files exist and fully parse read-only: fullwiki JSONL 3,259,561
  bytes / 500 unique IDs; Parquet 27,452,575 bytes / 7,405 unique IDs. Source
  SHA256 values, schema, mapping and diagnostic counts are in protocol section 10.
- All 500 sample IDs match Parquet, with identical questions, answers, ordered
  supports and type/level. No missing/duplicate IDs or blank questions, and no
  normalized duplicate-question groups. Candidate contents differ for 362;
  the other 138 differ only in order. Parquet has 6,905 additional IDs.
- Audit-only in-memory mapping checks equal-length parallel arrays. Existing
  record validation passes 7,355 Parquet rows and rejects 50: 49 with blank
  candidate sentences; ID 5ae61bfd5542992663a4f261 has support index 902 into
  five Jimmy Butler (basketball) sentences. Fullwiki passes 146/500; 354 have
  unresolved titles, with three blank-sentence cases and one empty-context case
  overlapping that group. No row was repaired, removed or released.
- Parquet metadata gives Arrow 21.0.0 producer and Hugging Face features only;
  no URL/config/revision/license. No raw-directory sidecars. Both local source
  lineages remain unverified; upstream dataset license is CC BY-SA 4.0.
- Historical hotpotqa500 per-query report covers all 500 sample IDs with exact
  question text; hotpotqa20 is a subset. At least those 500 are exposed across
  settings. No complete genuine inventory found in accessible files; old
  pytest_phase_16c_tmp denied access. No clean holdout claim.
- Stopped dependent preparation. Narrow adapter proposed in protocol, not
  implemented. No real manifests/projections, downloads/installs, source/controller
  changes, retrieval experiments/scoring or Phase 5.3. Proposed 100/200 provisional.
- Focused ingestion/split/legacy normalization regression tests: **64 passed in
  0.96s**. Passing synthetic regressions do not clear real input failures. Only
  README, protocol, progress and handoff updated. Final preservation and diff checks
  recorded in handoff. No qualifying fixed bug; no new vault note.
- Next: resolve source-backed anomaly policy/provenance and reconstruct complete
  exposure history before real role selection. Earlier entries below retain the
  historical utilities checkpoint and its then-current source availability.

## Phase 5.2 — completed utilities and synthetic verification; official ingestion pending

- Starting state: main at a905925 with six tracked Phase 2 modifications and two
  untracked Phase 2/5.1 files. Saved their starting SHA256 values before editing.
  Reviewed protocol/source/tests/manifests/configuration and all five prior EAR-RAG
  error notes. Baseline `.\ai-proj-new\Scripts\python.exe -m pytest -q`:
  **261 passed in 2.24s**, no skips/failures.
- Source inventory: `data/raw/hotpotqa/` contains only the legacy
  `hotpot_dev_fullwiki_v1_first_500_samples.jsonl`; no expected official distractor
  JSON array found under data/raw. Prior study reports exist, but no complete
  supplied exposure inventory was found. No real source ingested or split made.
- Added `src/ear_rag/data/hotpotqa.py`: read-only labelled train/dev JSON-array
  validation, duplicate-key/ID diagnostics, exact candidate/title/sentence checks,
  checksummed source provenance and accepted/rejected/malformed/duplicate counts.
  Any record error rejects the entire dataset; no silent partial ingestion.
- Reuses `DatasetNormalizer` and existing dataclasses. The one necessary schema
  adjustment in `data/normalization.py` allows absent type/level annotations rather
  than inventing them; supplied values are still validated. Additional/nested
  annotations are preserved offline. Public blind-test ingestion is unsupported.
- Explicit allowlisted runtime projection retains every valid candidate and exact
  sentences/spans but excludes labels and arbitrary metadata recursively. Separate
  evaluation projection retains answer/supports, support-document IDs and copied
  annotation metadata. Source checksum stays outside runtime objects so label-only
  changes cannot alter them.
- Added `tests/test_hotpotqa_ingestion.py`; initial test-first run failed collection
  for the expected missing new module. After implementation:
  `.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_ingestion.py
  tests/test_dataset_normalization.py -q`: **45 passed in 0.93s**. Tests cover
  source immutability, nested-field separation, label mutation, stable IDs,
  malformed records/files, optional metadata, unresolved supports and diagnostics.
- README/protocol reviewed and updated immediately; handoff checkpoint records
  the verified reader and remaining split/manifest work. No downloads, dependency
  changes, runtime pipeline modifications or indexes. Expected red tests are not
  qualifying error-log entries.

### Split planning and artifacts — focused verification passed

- Added `data/hotpotqa_splits.py`: explicit role counts (no implicit 100/200),
  protocol SHA256(seed:ID) ordering, NFKC/lower/whitespace duplicate groups,
  canonical/alias tracking, development/holdout ID and text-overlap validation,
  and exclusion of prior exposed IDs plus exact normalized text.
- Caller supplies `ExposureInventory(identifier, {id: question_text_or_None})`.
  `None` means unavailable; an explicitly supplied empty map is distinct.
  Source-matched IDs resolve their text; unmatched IDs without text make history
  partial. Unavailable/partial history blocks any nonempty holdout, not a
  development-only plan. Checks are limited to supplied history, not semantic
  near-duplicates or proof that the inventory is globally exhaustive.
- `plan_splits` returns a reproducible manifest with source identity/checksum,
  schema/selection versions, seed, role IDs/counts, ingestion diagnostics counts,
  duplicate aliases, holdout exclusions and separate ID/text check results.
  Insufficient eligible counts raise instead of shrinking the requested roles.
- `write_split_artifacts` validates before touching disk, requires a new output
  directory, writes separate runtime/label JSONL per role and publishes a
  checksummed manifest last. Source files/existing outputs are never overwritten.
  No real artifacts written; output tests use tiny temporary synthetic files.
- New split tests first failed for the expected absent module. Then
  `.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_splits.py
  tests/test_hotpotqa_ingestion.py -q`: **57 passed in 0.69s**. Checks cover
  label-independent/reordered deterministic selection, unknown/duplicate/overlap
  IDs, alias exposures, unavailable/partial inventory, insufficient counts,
  source immutability, repeatable bytes/hashes and label-file access denial.
- README/protocol/handoff updated after this logical change. Final full suite,
  scoped static checks and preservation results are recorded below.

### Full verification

- `.\ai-proj-new\Scripts\python.exe -m pytest -q`: **318 passed in 3.41s**, no
  failures/skips (baseline 261; 57 new ingestion/split cases).
- Scoped mypy initially identified the broad existing `evaluation: dict[str,
  object]` type at a validated fact iterator. Added a local cast matching reader
  validation, with no runtime change. Re-run for both new modules with
  `--follow-imports=silent --ignore-missing-imports --no-incremental` and a
  temporary cache: **Success: no issues found in 2 source files**.
- `.\ai-proj-new\Scripts\python.exe -m pip check`: **No broken requirements
  found**. No packages installed/upgraded, no downloads or benchmark commands.
- Only synthetic temporary artifacts were generated. The expected official
  distractor source and complete exposure inventory remain unavailable, so real
  ingestion, release authenticity, 100/200 feasibility and clean held-out claims
  are **not verified**. Reader source metadata explicitly says authenticity is
  not verified. The API does not infer trust from a source filename.
- Final source/test review and `git diff --check` passed. Preservation SHA256
  comparison confirms every earlier dirty/untracked source/guide/test file and
  every config/dependency manifest is unchanged. Only the shared normalizer's
  optional type/level handling changed in existing data source; the four new
  reader/split/test files and four project documents are this phase's work.
- Updated README, protocol and handoff after logical changes and reviewed them
  against the implementation. Original source text/annotations remain preserved;
  runtime views are explicit allowlists, while combined normalized examples stay
  offline. Versioned source identity/checksum in the manifest scopes local IDs;
  such IDs are not globally unique Wikipedia article identifiers.
- Errors logged: **none**. Read all prior EAR-RAG vault notes. Expected new-module
  red tests and the minor local typing correction are not meaningful new bugs;
  no notes were created or duplicated.
- Remaining decisions: provide an authorized official distractor JSON array and
  a complete exposure inventory; confirm role sizes after validating available
  unique/eligible counts. No actual official data validation, 100/200 split,
  authenticity verification or leakage-free holdout is claimed.
- Phase 5.3 next steps, only after review: (1) resolve those input/exposure gates;
  (2) load/verify manifest hashes, role IDs and runtime-only artifacts; (3) wire
  per-question candidate pools into the existing controller and persist full
  routing/ESA/recovery/cost/abstention traces; (4) join labels offline and reuse
  current metrics with explicit denominators; (5) verify synthetic isolation and
  frozen-role/config behavior before any authorized benchmark. No generation or
  answer EM/F1 is implied by that evaluation work.
- Final Git state on main: seven modified tracked files and six untracked files,
  including retained earlier Phase 2/5.1 work. No commit, reset, stash, cleanup,
  source download, dependency install or research experiment. Stop for review.

Actual verification commands (C:\ear-rag):

```powershell
.\ai-proj-new\Scripts\python.exe -m pytest -q
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_ingestion.py -q
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_ingestion.py tests/test_dataset_normalization.py -q
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_splits.py -q
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_splits.py tests/test_hotpotqa_ingestion.py -q
.\ai-proj-new\Scripts\python.exe -m mypy src/ear_rag/data/hotpotqa.py src/ear_rag/data/hotpotqa_splits.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir "$env:TEMP\ear-rag-phase52-mypy"
.\ai-proj-new\Scripts\python.exe -m pip check
git diff --check
git status --short --branch
```

## Phase 5.1 — completed: dataset selection and evaluation protocol (planning only)

- Planning/inspection only. Starting tree retained the six modified tracked Phase
  2 files and untracked `tests/test_runtime_reliability.py`; HEAD remains a905925.
  Reviewed README, progress, handoff, current source/tests/configuration, manifests,
  `.gitignore`, existing diff and prior reliability error notes.
- `.\ai-proj-new\Scripts\python.exe -m pytest -q`: **261 passed in 2.42s**, no
  failures or skips, using the existing Python 3.12.4 environment. No packages
  installed; no standalone evaluator/benchmark command run.
- Consulted the official HotpotQA website/repository, format/license statements,
  Wikipedia corpus documentation, license summary and official evaluation script.
  Created `docs/evaluation_protocol.md` with source links, candidate-pool versus
  full-corpus distinctions, role-separated records, exact metric denominators,
  selection/exposure safeguards and source-level compatibility/gaps.
- Recommendation: per-question official distractor contexts; proposed deterministic
  100-question development and 200-question internal holdout roles within official
  dev, with prior exposed IDs/duplicate questions excluded from holdout. Official
  test labels are unavailable publicly. No new split or dataset availability/
  validation is claimed; source input and exposure ledger remain review gates.
- Existing JSONL/contexts/documents formats differ; official JSON-array ingestion,
  strict label-isolated runtime projection, per-question corpus scoping and full
  recovery trace aggregation require later work. Current answer generation and
  sentence-level support scoring are absent. Do not claim them from passing tests.
- README updated in the same documentation change with the roadmap/limitations;
  handoff checkpointed before writing. Read back the entire protocol and reviewed
  source links, function/schema references, metric denominators, split/exposure
  safeguards and current-versus-planned claims before marking Phase 5.1 complete.
  No runtime/config/test edits or data/index artifacts.
- Documentation verification: local source references exist; confirmed
  `RetrievalDataPipeline.prepare()` and reference answers in older persistence
  records, so the protocol does not mislabel all existing artifacts runtime-safe.
  Reviewed balanced Markdown fences and README/protocol/handoff consistency.
  `git diff --check` passed; Git's existing LF/CRLF notices are not failures.
- SHA256 preservation check against the start of Phase 5.1: every existing
  source/config/test/manifest/guide file, including the prior uncommitted runtime
  fixes and untracked runtime test, remains byte-for-byte unchanged. Only
  `README.md`, `PROGRESS.md`, `AGENT_HANDOFF.md` and new
  `docs/evaluation_protocol.md` were edited in this phase.
- Existing suite is still the verified baseline: **261 passed in 2.42s**, no
  failures/skips. No code changed afterward, so no redundant suite run or
  benchmark command was needed. No qualifying bug resolved; no new Obsidian note
  created, and existing notes were reviewed rather than duplicated.
- Remaining review decisions: approve/change proposed 100/200 roles; identify an
  authorized official distractor input and reconstruct the prior-exposure ledger.
  Full-corpus resource feasibility and exact clean-holdout availability remain
  unverified. These gate later work, not completion of the planning deliverable.
- Phase 5.2 plan: official JSON-array reader reusing the normalizer; deterministic
  manifests/selection/overlap checks; strict runtime/label projections; synthetic
  schema/role/provenance tests; validate only an explicitly supplied/authorized
  small input afterward. No indexing, research experiment or tuning. Phase 5.3
  separately adds per-question pools and bounded-controller evaluation traces.
- Final working tree retains the original six modified tracked Phase 2 files and
  untracked runtime test, plus new `docs/evaluation_protocol.md`. No commit,
  discard, stash, reset or cleanup performed. Stop for review before Phase 5.2.

Actual verification commands in this phase:

```powershell
git status --short --branch
git log -3 --oneline
git diff --numstat
.\ai-proj-new\Scripts\python.exe -m pytest -q
git diff --check
```

Read-only Python checks additionally compared SHA256 values for all starting
tracked/untracked files, verified cited local file paths and checked Markdown
fences. No dataset/index generation or implementation command was executed.

## Reliability Phase 2 — completed; generation remains outside the implemented pipeline

- User authorized verification and targeted repair of the existing runtime only.
  Initial state: clean `main...origin/main`, HEAD `a905925` contains Phase 1.
  Re-read README, PROGRESS, handoff, error-logger/handoff skills and all three
  existing EAR-RAG error notes before work. No user changes to discard.
- Actual interpreter remains `C:\ear-rag\ai-proj-new\Scripts\python.exe`, Python
  3.12.4; editable package resolves to `src/ear_rag/__init__.py`.
- Baseline full suite: `.\ai-proj-new\Scripts\python.exe -m pytest -q`:
  **244 passed in 1.68s**. Direct import, `-m ear_rag.demo --help`, `-m pip check`
  and `git diff --check` passed.
- `.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --dataset hotpotqa --mode
  ear-rag --index 0`: succeeded using existing local files; initial lexical
  retrieval returned 5 chunks, ESA 0.936 sufficient, 1 leaf call, 0 recovery,
  `ANSWERABLE`. No evaluation or downloads occurred.
- `@('2','0','3','5') | .\ai-proj-new\Scripts\python.exe -m ear_rag.demo`:
  scripted interactive controller, evidence display and exit succeeded. Observed
  reporting defect: evidence titles show `(untitled)` despite source title
  metadata being present at `chunk.metadata.document_metadata.title`.
- Generation gap is explicit: no runtime generator exists. The `Generator`
  protocol and request/response dataclasses do not generate answers;
  `final_state='generate'` is an answerability marker, and config disables
  generation. This phase will verify the controller, not add generation.
- Updated handoff before implementation. Saved tracked-file baseline hashes
  outside the repository for the final preservation check. The baseline plan was
  focused runtime regressions and minimum fixes, without policy changes; final
  results follow below.

### Evidence-title repair — verified

- Added `tests/test_runtime_reliability.py`. Before repairs, all three regression
  cases failed: one title assertion, one missing-backend `KeyError`, and one
  non-callable-backend `AttributeError`. The latter two were addressed by the next fix.
- `src/ear_rag/demo.py`: evidence display now reads the chunker's preserved
  `document_metadata.title`, retaining support for existing flat title metadata.
  No retrieval data, ranking or runtime labels changed.
- `.\ai-proj-new\Scripts\python.exe -m pytest tests/test_runtime_reliability.py
  -k evidence -q`: **1 passed, 2 deselected**. README reviewed and updated with
  the verified local command, scripted menu path, title behavior and generation
  limitation. Other interactive paths are not claimed as verified.

### Unavailable-recovery diagnostic repair — verified

- `src/ear_rag/routing/pipeline.py`: validate a selected recovery backend using
  the same callable-backend registry already used for initial retrieval. Missing
  or non-callable entries now raise a descriptive `ValueError` before dispatch,
  rather than incidental `KeyError`/`AttributeError`. No fallback, retry,
  abstention substitution or policy/estimate change was introduced.
- The two new regressions exercise the real empty initial retriever and real
  insufficient ESA. Initial retrieval executes exactly once; unavailable
  recovery remains an explicit configuration error, not a successful abstention.
- `.\ai-proj-new\Scripts\python.exe -m pytest tests/test_runtime_reliability.py
  tests/test_initial_pipeline.py tests/test_phase_17_cost_awareness.py -q`:
  **25 passed in 0.23s**. README reviewed and
  updated immediately with the explicit failure behavior.

### Runtime regression verification

- Expanded `tests/test_runtime_reliability.py`: real configured ESA and leaf
  retrievers, with observation wrappers that retain their actual implementations.
  Checks all four backend interfaces twice for stable evidence, including empty
  indexes, and compares total calls against observed executed leaf operations.
  Composite returned context size is distinguished from child `retrieved_passages`.
- Added real empty-initial-index recovery cases: alternative vector index contains
  evidence or is empty. Both call the actual ESA after each retrieval, perform
  exactly one recovery and finish answerable or abstaining respectively. Predicted
  ESA and actual post-recovery ESA are checked separately. Main weights/thresholds
  and routing/cost settings remain unchanged.
- Disabled and unconfigured recovery each execute only initial retrieval/ESA and
  abstain. Subprocess tests exercise the actual CLI parser/main with temporary
  normalized input files, recovery/second ESA and scripted compare/controller/
  evidence/exit menu choices. The parser's data root alone is redirected; no
  generator or fake controller is introduced, and injected supervision is absent
  from output. Missing configured recovery remains an explicit error.
- `.\ai-proj-new\Scripts\python.exe -m pytest tests/test_runtime_reliability.py
  -q`: **17 passed in 0.60s**. Subsequently strengthened sufficient-evidence
  cases to leave recovery enabled and assert the sufficient-ESA rejection reason;
  the final full suite verified this refinement successfully.
- README reviewed and updated with verified synthetic test scope, predicted versus
  observed cost distinctions and generation limitation. Updated the linked demo
  guide to use Phase 1 editable installation instead of PYTHONPATH workaround.

### Final results, preserved scope and limitations

- `.\ai-proj-new\Scripts\python.exe -m pytest -q`: **261 passed in 2.14s**, no
  failures or skips. Baseline: **244 passed in 1.68s**. All original Phase 1
  tests remain unchanged; 17 focused runtime cases were added, not substituted.
- Final `-m ear_rag.demo --help`, isolated `-I -c` imports/config loading,
  `-m pip check` and `git diff --check` succeeded. No dependencies were installed
  or upgraded in Phase 2; the existing editable installation was sufficient.
- Re-ran the smallest documented local controller command: query/config,
  routing to lexical, retrieval (5 chunks), real ESA components/overall score,
  sufficient decision (0.936), 1 leaf call, no recovery, `ANSWERABLE`.
- Re-ran the unmatched-query command without changing any thresholds/weights:
  initial ESA 0.642 uncertain, predicted post-recovery ESA 0.892, expected cost
  0.110, CE 2.273 above configured 1.0. Exactly one vector recovery executed;
  actual second ESA was 0.298 insufficient, 2 total leaf calls, `ABSTAIN`.
  This is runtime verification of a single query, not dataset evaluation or
  empirical calibration. The estimate's failure is reported, not tuned away.
- Final scripted local controller/evidence/exit run displayed actual document
  titles (including Sinister (film) and Ed Wood (film)); no `(untitled)` loss.
- Backend checks through the real pipeline with representative synthetic input:

  | Backend | Nonempty leaf calls | Empty-index leaf calls | Verified behavior |
  | --- | ---: | ---: | --- |
  | local_lexical (BM25-inspired) | 1 | 1 | Stable scores/evidence, sufficient or empty-abstain |
  | vector_flat (hashed tokens) | 1 | 1 | Stable scores/evidence, sufficient or empty-abstain |
  | hybrid (score fusion) | 2 | 2 | Counts both children; stable fused context |
  | multihop (bounded expansion) | 2 | 1 | Stops on empty evidence; at most two hops |

- Sufficient-evidence cases leave recovery enabled and prove ESA skips it.
  Empty-index recovery-success and recovery-insufficiency cases each observe the
  exact order: initial leaf retrieval, real ESA, recovery leaf retrieval, real
  ESA; then termination. Disabled or unconfigured recovery has only the first
  retrieval/ESA pair. Missing/non-callable configured backend is an explicit
  `ValueError`, not a fallback or evidence-abstention decision.
- End-to-end scope is **question to evidence/control decision**, not question to
  generated answer. No production generator, deterministic generator or simulated
  generator was added. The unimplemented generation stage requires a separately
  approved future task. No unavailable external resource blocked controller tests.
- Remaining unverified: Python 3.11 execution, standalone wheel deployment,
  manual interactive UX/invalid inputs, optional 2Wiki CLI, evaluation/menu-4
  execution and real-model generation. No dataset/model downloads, preparation,
  research evaluation, baseline reproduction or calibration took place.
- Compared baseline SHA256 hashes: Phase 1 manifests, dependencies, tests,
  fixtures, all four backend implementations, ESA, initial router, recovery
  selection/estimator and `configs/config.yaml` remain byte-for-byte unchanged.
  Only source edits are the title display and two-line dispatch guard. No
  pre-existing changes were discarded; no commits or cleanup were performed.
- Updated README and this progress record after every logical change; updated
  demo guide and handoff. Final Git state: `main...origin/main`, six modified
  tracked files (`AGENT_HANDOFF.md`, `PROGRESS.md`, `README.md`,
  `docs/demo_40_percent.md`, `src/ear_rag/demo.py`,
  `src/ear_rag/routing/pipeline.py`) and one new file
  (`tests/test_runtime_reliability.py`). All changes intentionally uncommitted.
- Created and read back two new Obsidian live notes, without duplicates:
  `C:/Users/anant/MyObsidianVault/Errors/ear-rag-evidence-titles-read-wrong-metadata-level.md`
  and `C:/Users/anant/MyObsidianVault/Errors/ear-rag-unavailable-recovery-backend-dispatch.md`.
  Previous Phase 1 notes were read and retained. No note created for the planned,
  unimplemented generation stage. Stop here; any next phase requires approval.

### Phase 2 command record

All commands below ran from C:\ear-rag using the existing interpreter. The final
scripted-menu command was additionally filtered with `Select-String -Pattern
'Title       :|Final decision|RETRIEVED EVIDENCE'` to inspect the corrected titles.

```powershell
git status --short --branch
git diff --stat
git log -1 --format='%h %s'
.\ai-proj-new\Scripts\python.exe -c "import sys, ear_rag; print(sys.version); print(sys.executable); print(ear_rag.__file__)"
.\ai-proj-new\Scripts\python.exe -m pytest -q
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_runtime_reliability.py -q
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_runtime_reliability.py -k evidence -q
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_runtime_reliability.py tests/test_initial_pipeline.py tests/test_phase_17_cost_awareness.py -q
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --help
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --dataset hotpotqa --mode ear-rag --index 0
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --dataset hotpotqa --mode ear-rag --index 0 --query-text 'unmatched deterministic vocabulary'
@('2','0','3','5') | .\ai-proj-new\Scripts\python.exe -m ear_rag.demo
.\ai-proj-new\Scripts\python.exe -I -c "import sys, ear_rag, ear_rag.data, ear_rag.demo; from ear_rag.config import load_config; print(sys.executable); print(ear_rag.__file__); assert load_config()['project']['name'] == 'EAR-RAG'"
.\ai-proj-new\Scripts\python.exe -m pip check
git diff --check
```

## Reliability Phase 1 (2026-10-20) — completed and verified

This section records Phase 1 completion. Dated entries below are historical snapshots;
their old environment, missing-component and next-phase statements are not current.

- Initial branch/status: `main...origin/main`, clean working tree. At baseline no
  root-level `ear_rag`, `.venv`, `pyproject.toml`, `setup.py`, or `setup.cfg` existed.
  `pytest.ini` correctly uses `[pytest]`, `testpaths = tests`, `pythonpath = src`.
- Actual interpreter: `C:\ear-rag\ai-proj-new\Scripts\python.exe`, Python 3.12.4.
  Relevant installed versions: pytest 9.1.1, PyYAML 6.0.3, pyarrow 25.0.1,
  mypy 2.3.1, pre-commit 4.6.2. No `PYTHONPATH` was set for the baseline.
- Baseline command `.\ai-proj-new\Scripts\python.exe -m pytest -q`:
  **243 passed in 8.53s**. `-m pip check`: **No broken requirements found**.
- Direct `-c "import ear_rag; print(ear_rag.__file__)"` failed:
  `ModuleNotFoundError: No module named 'ear_rag'`. Pytest's source-path setup
  masks the missing package installation; the root `sitecustomize.py` does not
  automatically solve startup imports in this interpreter.
- A `git archive` export of HEAD into a new temporary directory, without ignored
  datasets or environment files, reproduced **7 failed, 236 passed in 1.71s**.
  Six `tests/test_demo.py` tests and the configured-backend test in
  `tests/test_initial_pipeline.py` fail with `FileNotFoundError` for
  `data/processed/evaluation/hotpotqa_evaluation.jsonl`.
- Dependency gap: `src/ear_rag/data/normalization.py` imports `pyarrow.parquet`
  eagerly, but requirements.txt does not declare pyarrow. The previously reported
  missing-pyarrow failure is absent here because pyarrow is already installed.
- Documentation review: README lacks fresh-environment/install/activation steps,
  says pyarrow is undeclared, and lists a duplicate configs directory and absent
  notebooks directory. Old progress sections incorrectly present Python 3.11,
  missing ESA/recovery/routing and an old package shadow as current state.
- Created `AGENT_HANDOFF.md` before implementation. Read the local error-logger
  and agent-handoff skills and existing vault error notes; no EAR-RAG duplicates
  exist. No new error notes yet because repairs have not been verified.
- Repair sequence: dependency/package installation reliability, then
  dataset-independent tests. Research calibration and experiments remain outside
  this phase. Final verification and error-note results are recorded below.

### Setup repair — implemented and verified

- `requirements.txt`: declared pyarrow, already installed in the existing
  environment; no version upgrades requested. `pyproject.toml`: added minimal
  setuptools editable packaging, Python >=3.11 and src-only package discovery.
  Dependency metadata reads requirements.txt rather than duplicating declarations.
  `.gitignore`: ignore editable-install egg-info metadata.
- `tests/test_project_setup.py`: removed its redundant global sys.path mutation,
  assert the exact source-package origin, and added an isolated subprocess import
  check from outside the repository, including data imports and config loading.
- README updated in this same change: explicit installation/test/check commands,
  Python/environment requirements, PowerShell activation template, pyarrow,
  editable-checkout limitation, unverified demo behavior and corrected tree.
  Installation and new commands were initially labelled pending, then updated
  after the verification below.
- Regression reproduced before installation: `-m pytest tests/test_project_setup.py
  -q` returned **1 failed, 2 passed**, with isolated `ModuleNotFoundError`.
- `.\ai-proj-new\Scripts\python.exe -m pip install -e .`: succeeded; existing
  dependency versions were already satisfied. No installed dependencies upgraded.
- `-m pytest tests/test_project_setup.py tests/test_dataset_normalization.py -q`:
  **10 passed in 0.80s**. Direct import resolves to `C:\ear-rag\src\ear_rag\__init__.py`;
  `-m ear_rag.demo --help` succeeded; `-m pip check` reported no broken requirements;
  `git diff --check` passed. README pending labels were updated after verification.
- The next repair addressed dependence on ignored local datasets; complete
  environment verification is recorded in the final verification section.

### Test isolation repair — implemented and verified

- `tests/conftest.py`: added an opt-in fixture that generates 500 synthetic
  normalized HotpotQA examples and separate evaluation labels in pytest's
  temporary directory. Only the demo's data root is redirected; its real loader,
  normalizer, backends and controller still execute. No local data is changed.
- `tests/test_demo.py`: applied the fixture to all six tests; retained the
  500-example and every control/cost assertion. Renamed the loader test to avoid
  implying synthetic data is a real corpus. Added adversarial supervision fields
  to inputs and strengthened label-isolation and support-resolution assertions.
- `tests/test_initial_pipeline.py`: the configured-backend demo test uses the
  same fixture; the routing assertion remains unchanged. No tests skipped.
- README reviewed and updated in this same change to distinguish temporary test
  inputs from the interactive demo's optional user-supplied corpus. Verification
  was updated after focused verification: `.\ai-proj-new\Scripts\python.exe -m
  pytest tests/test_demo.py tests/test_initial_pipeline.py -q`:
  **23 passed in 0.63s**. Fresh-environment results are recorded below.

### Documentation reconciliation and full workspace verification

- Updated this document's old undated architecture, file inventory, dependencies,
  datasets, experiments, limitations and next-phase sections to the inspected
  current state. Explicitly marked the old Phase 1.4 status as historical.
- Reviewed README again: marked its original phase list as an original roadmap;
  recorded verified existing-environment activation and the complete suite result.
- `.\ai-proj-new\Scripts\python.exe -m pytest -q`: **244 passed in 1.92s**;
  `-m pip check`: **No broken requirements found**. Existing environment activation
  `. .\ai-proj-new\Scripts\Activate.ps1` followed by `python -c "import sys,
  ear_rag; print(sys.executable); print(ear_rag.__file__)"` selected the intended
  interpreter and `src/ear_rag/__init__.py`.
- Fresh-install check in a new source snapshot: `python -m venv .venv`,
  `. .\.venv\Scripts\Activate.ps1`, and `python -m pip install -e .` succeeded.
  This separate environment resolved pyarrow 26.0.0, mypy 2.4.0 and pre-commit
  4.7.0 under the unchanged lower-bound specifications. Original installed
  dependency versions remained unchanged. Full snapshot results follow below.

### Final verification and stop point

- Full original environment: **244 passed in 1.92s**, no failures or skips.
  Full fresh source-only snapshot: **244 passed in 1.36s**, no failures or skips.
  Baseline source-only export had **7 failed, 236 passed**; original populated
  workspace had **243 passed**. The additional test guards isolated installation.
- Fresh snapshot path:
  `C:\Users\anant\AppData\Local\Temp\ear-rag-phase1-verified-ew3u0v0v\repo`.
  Exported HEAD using `git archive --format=zip HEAD` and overlaid only changed
  tracked files plus the three new deliverables. No ignored datasets/environment
  were copied. Created/activated `.venv`, installed with `python -m pip install
  -e .`, and ran `python -m pytest -q` and `python -m pip check` successfully.
- `python -I -c "import ear_rag, ear_rag.data; from ear_rag.config import load_config;
  from importlib.metadata import requires, version; print(ear_rag.__file__);
  assert load_config()['project']['name'] == 'EAR-RAG'; print('pyarrow:',
  version('pyarrow')); print('Declared:', requires('ear-rag'))"` succeeded in that
  fresh environment. Metadata declares pyarrow; imports resolve to snapshot src.
  `python -m ear_rag.demo --help` also succeeded without local datasets.
- README and PROGRESS were updated after each logical repair and reviewed again
  after final verification. No tests were skipped or weakened. `src/`,
  `configs/config.yaml`, and `pytest.ini` are unchanged: all four backends, ESA
  dimensions, single recovery bound, mandatory reassessment and abstention remain.
- Obsidian live logging: created and read back three new notes (no duplicates):
  `C:/Users/anant/MyObsidianVault/Errors/ear-rag-src-package-not-installed.md`,
  `C:/Users/anant/MyObsidianVault/Errors/ear-rag-undeclared-pyarrow-dependency.md`,
  `C:/Users/anant/MyObsidianVault/Errors/ear-rag-tests-depend-on-ignored-hotpotqa-files.md`.
  The pyarrow note explicitly distinguishes the verified declaration defect from
  the historical collection error that did not recur in the populated environment.
- No remaining Phase 1 test/dependency/import blocker. Unverified/outside scope:
  Python 3.11 execution, standalone wheel deployment, full interactive demo,
  real-data commands and research evaluation. Ignored inaccessible temporary
  directory remains untouched. Phase 2 requires explicit user approval.
- Final `git diff --check` passed. Compared every changed packaging/dependency/
  test file byte-for-byte with the tested fresh snapshot: all match. Confirmed
  `git diff --name-only -- src configs pytest.ini` is empty.
- Final working tree is intentionally uncommitted: modified `.gitignore`,
  `PROGRESS.md`, `README.md`, `requirements.txt`, `tests/test_demo.py`,
  `tests/test_initial_pipeline.py`, `tests/test_project_setup.py`; new
  `AGENT_HANDOFF.md`, `pyproject.toml`, `tests/conftest.py`.

### Verification command record

Commands below were actually executed in C:\ear-rag unless otherwise stated.
Baseline runs preceded repairs; focused checks preceded final suites.

```powershell
git rev-parse --show-toplevel
git status --short --branch
.\ai-proj-new\Scripts\python.exe -m pytest -q
.\ai-proj-new\Scripts\python.exe -c "import ear_rag; print(ear_rag.__file__)"
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_project_setup.py -q
.\ai-proj-new\Scripts\python.exe -m pip install -e .
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_project_setup.py tests/test_dataset_normalization.py -q
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_demo.py tests/test_initial_pipeline.py -q
.\ai-proj-new\Scripts\python.exe -m pip check
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo --help
. .\ai-proj-new\Scripts\Activate.ps1
python -c "import sys, ear_rag; print(sys.executable); print(ear_rag.__file__)"
git diff --name-only -- src configs pytest.ini
git diff --check
git diff --stat
```

In the fresh source snapshot, the exact setup/suite/check/help commands were:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable); print(sys.version)"
python -m pip install -e .
python -m pytest -q
python -m pip check
python -m ear_rag.demo --help
```

## Query-analysis validation and evaluation (2026-10-09)

- Preserved all 500 existing local HotpotQA routing decisions, features, scores,
  and reason text against a saved baseline. Added fallback/selection codes, score
  margins and tie/signal diagnostics without changing the policy or recovery.
- Extended the existing evaluator with per-query JSONL/CSV, full versus locally
  resolved evidence metrics, seeded sampling/provenance hashes, observed-call
  efficiency utility, regret, ties, missed opportunities and paired bootstrap CIs.
- Reproduced the original 13/20 fallbacks: all lacked recognized routing signals.
  Evaluated all 500 local development queries against 4,957 documents with recovery
  disabled: 418 queries have resolved supports, 146 are fully resolved; 564/1,000
  annotated support documents resolve locally. Fallback was 350/500 (70%).
- Resolved recall@5: lexical 89.71%, hashed vector 12.80%, hybrid 64.23%, bounded
  multi-hop 89.71%, routed 81.22%. Routed utility agreement 87.56%, mean regret
  0.10347; 35 missed-evidence cases and 18 equivalent-quality extra-call cases.
  The router does not improve on lexical in this development check.
- Validation: 243 tests passed, including 99 new cases; scoped mypy passed for
  seven modules, whitespace check passed, real and synthetic reports saved under
  `outputs/query-validation-*`. No dependencies, models or datasets were added.
- Findings, denominators, examples, limitations and reproducible commands:
  [docs/query_analysis_validation.md](docs/query_analysis_validation.md).

## Query-aware initial retrieval (2026-10-09)

- Added separate deterministic query features and configurable scoring policy;
  enabled it in the main runtime configuration. Exactly one initial strategy is
  dispatched before existing ESA and at most one recovery. Recovery-aware initial
  selection remains deferred.
- Added structured decisions, eligibility/fallback checks, query-free INFO logs,
  separate routing latency, and per-invocation composite retrieval-call accounting.
- Added an explicitly offline fixed-versus-routed evaluation with recovery disabled,
  plus a tracked synthetic fixture. Labels remain outside runtime analysis/routing.
- Validation: 144 tests passed (76 new); scoped mypy passed for ten changed/new
  source modules. No new dependencies or model downloads.
- Small HotpotQA development check: 20 queries, 16 with local support labels;
  local recall@5 was lexical 87.5%, hashed vectors 18.75%, hybrid 68.75%, bounded
  multi-hop 87.5%, routed 75%. Router overhead averaged 0.095 ms, fallback 65%.
  Rules remain provisional; no quality-improvement claim. Synthetic smoke passed.
- Details, reproducible commands, label-coverage caveats and backend limitations:
  [docs/initial_routing.md](docs/initial_routing.md). Historical phase entries below
  describe their status at the time and may be superseded by this update.

## Phase 1.7 — Cost-Aware Recovery Selection + Demo Update

**COMPLETE** (2026-09-02)

- Inserted deterministic pre-recovery cost-aware selection into
  `BoundedRecoveryPolicy.decide()`, between initial ESA and the existing
  recovery call. The finite controller still permits at most one recovery and
  only runs the second ESA after an accepted recovery.
- Added the configuration-driven formula
  `CE_expected = (estimated_esa_after - current_esa) / expected_additional_recovery_cost`.
  Estimated ESA is current ESA plus a configured per-candidate gain (clamped to
  1.0). Expected cost is the configured weighted sum of expected additional
  retrieval calls, retrieved chunks, and latency.
- Added `recovery.cost_awareness` configuration for threshold, per-backend ESA
  gains, expected operational work, and explicit cost weights. These are
  deterministic development-style estimates, not calibrated claims.
- Updated `python -m ear_rag.demo --mode ear-rag` to show current ESA, the
  candidate, each estimate, CE threshold decision, actual recovery status,
  recovery round, optional second ESA, and final decision. A controlled real
  FAIL case is available with `--query-text "unmatched deterministic vocabulary" --cost-efficiency-threshold 999`.
- Added focused Phase 1.7 tests for formula components, threshold PASS/FAIL,
  decision ordering, zero calls on rejection, exactly one call on acceptance,
  second ESA behavior, abstention, and label isolation.
- Focused validation: 16 controller/cost-aware/demo tests passed (the new and
  legacy controller checks plus the demo module). The complete suite was run
  once but could not collect two existing data tests because this established
  interpreter lacks `pyarrow`. The direct `python -m ear_rag.demo` command also
  cannot resolve the `src`-layout package in this interpreter, a pre-existing
  environment limitation; pytest resolves it correctly.
- Limitation: estimates are configuration-driven baselines and need later
  development-set calibration; they do not predict outcome from recovered docs.

## Phase 1.6C â€” Controlled Retrieval Evaluation and 40% Demonstration

**COMPLETE** (2026-08-24)

- Implemented `python -m ear_rag.demo`: an interactive and scriptable CLI for
  the normalized HotpotQA default and optional 2Wiki corpus.
- Added separate comparison mode (BM25-style lexical, vector flat, hybrid, and
  bounded multi-hop) and EAR-RAG mode, which runs the existing controller only:
  BM25 initial retrieval, ESA, and at most one configured recovery retrieval.
- Added retrieved-evidence inspection and deterministic small evaluation (20
  examples by default) with post-retrieval Hit@k, ESA/control, latency, calls,
  recovery, and abstention summaries. Retriever documents are constructed only
  from normalized retriever-safe records; separate evaluation labels are read
  only when calculating Hit@k afterwards.
- Cost instrumentation reports actual existing operational proxies: retrieval
  calls, requested/returned chunks, measured latency, strategies, and recovery
  rounds. Second ESA insufficiency terminates as `ABSTAIN`; no second recovery
  is possible.
- Created: `src/ear_rag/demo.py`, `tests/test_demo.py`, and
  `docs/demo_40_percent.md`; added `sitecustomize.py` so the existing
  interpreter can execute the `src`-layout module directly. Modified:
  `PROGRESS.md`.
- Known limitations: no LLM answer generation, no monetary-cost model, and the
  deterministic ESA/vector components are prototype baselines rather than
  calibrated research results. Validation blocker: this environment's existing
  interpreter did not resolve `ear_rag` for direct `-m` execution even after a
  repository startup-path shim; pytest resolves `src` correctly and all tests
  pass with its configured source path. Stopped after the same direct-module
  error recurred, per the phase anti-loop rule.
- Next phase: only proceed to a separately authorized controlled experiment or
  research evaluation phase.

## Phase 1.6B — Dataset Normalization and Corpus Builder

**COMPLETE** (2026-08-24)

- Implemented typed deterministic normalization for the locally supplied
  HotpotQA, 2Wiki, and NQ-Open schemas plus a JSONL corpus/evaluation writer.
- Generated `hotpotqa_normalized.jsonl` (500), `2wiki_normalized.jsonl`
  (12,576), and `nq_open_normalized.jsonl` (3,610) under `data/processed/`.
- Generated retriever-safe HotpotQA and 2Wiki corpus JSONL files and separate
  per-dataset evaluation JSONL files. Corpus records contain no answers,
  supporting facts, evidences, or support sentence labels.
- NQ-Open produces QA-only normalized examples and no corpus because its
  external Wikipedia-corpus requirement remains unresolved by design.
- Created: `src/ear_rag/data/normalization.py`,
  `tests/test_dataset_normalization.py`, and processed output artifacts.
- Modified: `src/ear_rag/data/__init__.py`,
  `docs/dataset_schema_report.md`, and `PROGRESS.md`.
- Known limitation: the per-example HotpotQA/2Wiki contexts are a local,
  closed-world corpus representation; no global external corpus was built.
- Tests: `.\\ai-proj-new\\Scripts\\python.exe -m pytest` — **57 passed in
  1.21s**.
- Next phase: validate/load these artifacts through a controlled retrieval
  experiment harness; do not address the NQ corpus gap without an explicit
  corpus input.

## Phase 1.6A — Dataset Schema Inspection

**COMPLETE** (2026-08-24)

- Inspected only the locally supplied NQ-Open (3,610 JSONL QA records),
  HotpotQA fullwiki subset (500 JSONL records), and 2Wiki validation Parquet
  (12,576 records); no raw data was modified or downloaded.
- Finding: NQ-Open has only `question` and answer-list fields, no IDs or
  contexts, so it requires a separately supplied Wikipedia corpus for final
  retrieval experiments.
- Finding: HotpotQA contexts are title plus ordered sentence lists with
  `_id`, `type`, `level`, and `supporting_facts`; 2Wiki uses parallel
  `context.title`/`context.sentences` and support title/sentence-ID arrays.
- Planned corpus boundary: title/text and safe provenance are retriever input;
  answers, supporting facts, evidences, and support sentence IDs are strictly
  evaluation-only to prevent leakage.
- Created: `docs/dataset_schema_report.md`.
- Modified: `PROGRESS.md`.
- Tests: `.\\ai-proj-new\\Scripts\\python.exe -m pytest` — **50 passed in
  0.30s**.
- Phase 1.6B should implement only a deterministic schema-specific
  normalization/corpus builder with separate evaluation labels and tests.

## Phase 1.5 Completion — Retrieval Backend Architecture + Bounded ESA/Recovery

**COMPLETE** (2026-08-24)

- Preserved and adapted the BM25-inspired lexical backend; metadata includes backend, initial/recovery action, and hop count.
- Added deterministic hashed-vector flat cosine retrieval, deterministic hybrid score fusion, and bounded multi-hop evidence aggregation (`max_hops: 2`).
- Added explainable deterministic ESA using score quality, query/evidence coverage, evidence amount, and duplicate-evidence rate.
- Added an explicit finite retrieval-control pipeline and configurable recovery policy using operational proxies (calls, chunks, latency, hops).

### Retrieval Backends

- **BM25 / lexical:** existing lightweight BM25-inspired backend retained.
- **Vector Flat:** deterministic hashed-vector flat search implemented.
- **Hybrid:** deterministic lexical/vector normalized fusion implemented.
- **Multi-hop:** bounded deterministic architecture implemented, not an autonomous agent.

### ESA / Cost-Aware Control / Bounded Recovery

ESA returns relevance, coverage, support, consistency, overall score, decision, rationale, and structured signals. The policy only selects a configured alternative backend when ESA is not sufficient and configured operational limits allow it. Default `max_recovery_rounds` is **1** (`max_attempts: 1` remains a compatibility alias); a second ESA always runs after recovery; remaining insufficiency terminates as `abstain`. No uncontrolled loop exists.

### Test Result

`.\\ai-proj-new\\Scripts\\python.exe -m pytest` — **50 passed in 0.31s**. The requested `.\\.venv\\Scripts\\python.exe` path does not exist; this is the available project interpreter.

### Files Created

- `src/ear_rag/retrieval/{vector,hybrid,multihop}.py`
- `src/ear_rag/evidence/{__init__,esa}.py`
- `src/ear_rag/routing/{__init__,recovery,pipeline}.py`
- `tests/test_phase_15_control.py`

### Files Modified

- `src/ear_rag/retrieval/local.py`
- `src/ear_rag/retrieval/__init__.py`
- `configs/config.yaml`
- `PROGRESS.md`

### Known Issues

The vector encoder is deliberately a deterministic, no-download architecture stand-in, not a production semantic-search quality claim.

### Research Components Still Missing

Learned/calibrated ESA and policy, generation, calibrated abstention, baseline experiments, and dataset-scale evaluation.

### Next Phase

Phase 1.6 — controlled baseline/evaluation harness for the bounded controller.

### What We Did / Why It Matters

EAR-RAG can now make one inspectable, bounded recovery decision based on current evidence. This creates the reproducible control surface needed to study when additional retrieval is worth its operational cost.

## Project

Evidence-Aware Adaptive Retrieval with Selective Query Recovery (EAR-RAG)

## Research Objective

Evaluate whether an evidence-aware adaptive retrieval policy can improve answer
quality and reduce unsupported or hallucinated answers relative to fixed
retrieval and adaptive-RAG baselines.

## Historical Phase 1.4 status (2026-08-23; superseded)

**Phase 1.4 dataset and persistent retrieval pipeline: COMPLETED (2026-08-23).**

The repository contains a typed, persistent local retrieval pipeline: project
directories, lightweight dependencies, a YAML configuration file, validated core
contracts, implementation-independent protocol interfaces, deterministic lexical
retrieval, local dataset adapters, and tests. Evidence-sufficiency assessment,
adaptive recovery, generation, and evaluation are not implemented.

The source package and configuration loader are working. The complete test suite
passes, and pytest imports the intended `src/ear_rag` package even though the
empty protected root-level `ear_rag` reparse-point directory remains in place.

### Configuration Path Portability Fix

- Root cause: `configs/config.yaml` was documented and expected by the loader
  and tests, but was not tracked in Git. Fresh clones therefore lacked the
  default configuration; stale paths seen in a copied virtual environment were
  not repository configuration.
- Fix: restored the tracked default configuration and made the loader derive
  the repository root explicitly from its `src/ear_rag/config/loader.py`
  location using `pathlib.Path`.
- Test result: `python -m pytest` — **45 passed in 0.29s**.
- Configuration paths are now repository-relative and portable across clone
  locations; no machine-specific repository path is used.

## Phase History

### Phase 1.1 — Project Foundation

**PARTIALLY COMPLETED** (pre-existing; inspected 2026-08-23)

- Date completed: not recorded by the prior implementation.
- Implemented: directory scaffold; `README.md`; `requirements.txt`; `pytest.ini`;
  `.gitignore`; `configs/config.yaml`; virtual environment; basic tests.
- Files created: pre-existing source and test files described below.
- Tests run: `\.venv\Scripts\python.exe -m pytest`.
- Initial result: 2 tests collected and 3 collection errors, all caused by
  `ear_rag` resolving to the empty top-level directory rather than `src/ear_rag`.
- Important decisions: no models or datasets were downloaded; no large ML
  framework was installed.
- Known issues: package shadowing prevents the default test command from
  collecting the core/configuration tests.

### Bootstrap / Repository Inspection

**PARTIALLY COMPLETED** (2026-08-23)

- Inspected repository structure, source files, configuration, tests,
  dependencies, virtual environment, and Git state. Git is not initialized.
- Existing components: all nine requested core data models (`Query`, `Document`,
  `RetrievedChunk`, `RetrievalResult`, `EvidenceAssessment`, `RecoveryAction`,
  `GenerationRequest`, `GenerationResponse`, and `EvaluationResult`) and six
  protocol interfaces (`Retriever`, `QueryAnalyzer`, `EvidenceAssessor`,
  `RecoveryPolicy`, `Generator`, and `Evaluator`).
- Missing research components: query analysis implementation, retrieval,
  embeddings, vector store, BM25, hybrid retrieval, evidence-sufficiency
  assessment, adaptive policy, recovery, reformulation, decomposition,
  generation, confidence/abstention, evaluation, and baselines.
- Repairs made:
  - added the missing `ear_rag.config.loader` module expected by package code and
    tests;
  - made `ear_rag.config` re-export that module’s public API, removing duplicated
    loader logic;
  - imported `Any` and `Dict` used by interface annotations;
  - corrected `pytest.ini` so `pythonpath` is `src`, not the literal string
    `"src"`;
  - exempted the tracked default configuration from the broad YAML ignore rule.
- Files created: `src/ear_rag/config/loader.py`, `PROGRESS.md`.
- Files modified: `src/ear_rag/config/__init__.py`,
  `src/ear_rag/core/interfaces.py`, `pytest.ini`, `.gitignore`.
- Tests run after repairs: `\.venv\Scripts\python.exe -m pytest`.
- Final result: 2 tests collected and 3 collection errors (`test_config.py`,
  `test_core_models.py`, and `test_interfaces.py`), all due to the protected
  top-level package shadow. No test failures were reached.
- Direct validation: with `PYTHONPATH` set to the repository’s `src` directory,
  `import ear_rag` resolved to `src/ear_rag/__init__.py` and `load_config()`
  returned project name `EAR-RAG`.

### Phase 1.1.5 — Foundation Repair

**COMPLETED** (2026-08-23)

- Problem discovered: ordinary pytest collection resolved `ear_rag` to the empty
  protected root-level OneDrive reparse-point directory, causing three import
  collection errors.
- Root cause: `pytest.ini` used the `[tool.pytest]` header, which is valid for a
  `pyproject.toml` table but not for an INI configuration file. Pytest therefore
  ignored `pythonpath` and did not place `src` ahead of the root directory.
- Repair performed: changed the header to `[pytest]`, supplied valid INI values
  for `testpaths` and `pythonpath`, and preserved the intended `src/ear_rag`
  package layout.
- Accidental artifacts removed: `update_init.py`; `src/ear_gr/__init__.py`;
  `src/ear_rag/config/_/_init__.py`; and
  `src/ear_rag/core/_/_init__.py`. They were duplicate/one-off files with no
  references elsewhere in the repository.
- The empty artifact directories could not be removed because the execution
  environment rejected the deletion command. `src/ear_gr` still contains only
  its generated `__pycache__`; `config/_` and `core/_` are empty. No source code
  remains in these paths.
- Files modified: `pytest.ini`, `PROGRESS.md`.
- Tests run: `\.venv\Scripts\python.exe -m pytest`.
- Test result: **26 passed in 0.15s**.
- Package import result: with the same relative source-path arrangement used by
  pytest, `ear_rag.__file__` resolves to `src/ear_rag/__init__.py`.
- No models, datasets, or large ML dependencies were downloaded or installed.

### Phase 1.2 — Configuration and Core Interface Hardening

**COMPLETED** (2026-08-23)

- Hardened models: all nine core dataclasses retain independent mutable defaults;
  `EvidenceAssessment` now normalizes and validates `EvidenceDecision` values;
  `RecoveryAction` now normalizes and validates `RecoveryActionType` values.
- Hardened interfaces: retained the six framework-independent, runtime-checkable
  protocols; removed unused interface imports and replaced broad interface
  `Any` annotations with `object` or `Mapping[str, object]` where applicable.
- Configuration changes: added `query_analysis`, `evidence_assessment`,
  `recovery`, and `generation` sections; added initial ESA thresholds and
  dimension weights, recovery attempt limits, and generation placeholders. The
  values are documented initial research configuration, not experimental claims.
- Configuration loader: added an exported `get_config_path()` helper, accepts a
  portable `str` or `Path` override, validates that a configuration is a file,
  and rejects a non-mapping YAML root.
- Tests added: `tests/test_contract_hardening.py` verifies mutable-default
  independence, enum validation, all six protocols with minimal mocks, required
  configuration sections/values, and repository-derived configuration paths.
- Files created: `tests/test_contract_hardening.py`.
- Files modified: `configs/config.yaml`; `src/ear_rag/__init__.py`;
  `src/ear_rag/config/__init__.py`; `src/ear_rag/config/loader.py`;
  `src/ear_rag/core/__init__.py`; `src/ear_rag/core/interfaces.py`;
  `src/ear_rag/core/models.py`; `PROGRESS.md`.
- Tests run: `\.venv\Scripts\python.exe -m pytest`.
- Test result: **32 passed in 0.25s**.
- Package/config validation: `ear_rag` resolves to `src/ear_rag/__init__.py` and
  the `evidence_assessment` configuration exposes relevance, coverage, support,
  and consistency weights.
- Research functionality still not implemented: retrieval, embeddings, vector
  store, BM25, hybrid retrieval, ESA scoring, adaptive policy, recovery logic,
  query reformulation/decomposition, generation, confidence/abstention,
  evaluation, and baselines.
- No models, datasets, or large ML dependencies were downloaded or installed.

### Phase 1.3 — Local Retrieval Backend

**COMPLETED** (2026-08-23)

- Implemented `DocumentChunker`, a reusable deterministic character-window
  chunker with configurable size and overlap. It preserves document identity and
  stores stable chunk IDs, source offsets, chunk indices, and document metadata.
- Implemented `LocalLexicalRetriever`, a dependency-free in-memory,
  BM25-inspired lexical retriever. Indexing replaces the corpus to avoid hidden
  state; retrieval returns ranked `RetrievedChunk` objects in a
  `RetrievalResult` and satisfies the existing `Retriever` protocol.
- Retrieval configuration now declares the `local_lexical` backend, chunk size,
  chunk overlap, default top-k, and maximum top-k. These are initial experimental
  defaults, not claims of optimality.
- Cost instrumentation added to every retrieval result: retriever name,
  requested top-k, returned chunk count, cumulative retrieval call count,
  measured retrieval latency, indexed document count, and indexed chunk count.
- Tests added: `tests/test_local_retrieval.py` covers chunking, deterministic
  IDs and scores, metadata preservation, empty/short documents, ranking, top-k,
  cost metadata, protocol compatibility, configuration, and a document-to-result
  smoke flow.
- Files created: `src/ear_rag/retrieval/__init__.py`;
  `src/ear_rag/retrieval/chunking.py`; `src/ear_rag/retrieval/local.py`; and
  `tests/test_local_retrieval.py`.
- Files modified: `configs/config.yaml`; `src/ear_rag/__init__.py`; and
  `PROGRESS.md`.
- Tests run: `\.venv\Scripts\python.exe -m pytest`.
- Test result: **39 passed in 0.32s**.
- Limitations: lexical matching is intentionally simple; no persistent index,
  semantic chunking, dense retrieval, BM25 library implementation, hybrid
  retrieval, or retrieval experiments exist yet.
- **ESA and cost-aware adaptive decision-making are NOT implemented yet.**
- No models, datasets, or large ML dependencies were downloaded or installed.

### Phase 1.4 — Dataset and Persistent Retrieval Pipeline

**COMPLETED** (2026-08-23)

- Added a configuration-driven, normalized local JSONL dataset adapter and the
  `DatasetAdapter` contract. It recognizes the fixture, Natural Questions,
  HotpotQA, and 2WikiMultihopQA identifiers; the latter three require a locally
  normalized JSONL file and are not downloaded by the project.
- Added a deterministic whitespace preprocessor that preserves document IDs and
  source metadata, skips empty documents, and detects conflicting duplicate IDs.
- Added `RetrievalDataPipeline`, which loads a configurable subset, preprocesses
  documents, invokes the existing chunker, writes artifacts, reloads them, and
  restores a `LocalLexicalRetriever` from persisted chunks without re-chunking.
- Persistence writes deterministic JSONL for processed examples/documents and
  chunks, plus versioned JSON manifests in separate `data/processed` and
  `data/indexes` roots. Each manifest records dataset/split/subset, counts, and
  chunking settings.
- Configuration now declares dataset, subset, split, maximum example count,
  repository-relative data paths, standalone chunking settings, and persistence
  paths. The development fixture is the only configured/available dataset.
- Added the tracked deterministic fixture `data/fixtures/tiny_retrieval.jsonl`
  and prepared `outputs/demos/` for the Phase 1.5 demonstrator. No external
  datasets were downloaded.
- Added `LocalLexicalRetriever.index_chunks()` so chunk-index artifacts can be
  reloaded across Python runs while recreating only lightweight lexical stats.
- Tests added: `tests/test_data_pipeline.py` covers fixture loading, adapter
  configuration/contract, subset limits, deterministic preprocessing, chunking,
  deterministic persistence, reload/metadata preservation, and retrieval from
  persisted chunks.
- Files created: `src/ear_rag/data/__init__.py`;
  `src/ear_rag/data/datasets.py`; `src/ear_rag/data/preprocessing.py`;
  `src/ear_rag/data/persistence.py`; `src/ear_rag/data/pipeline.py`;
  `data/fixtures/tiny_retrieval.jsonl`; `outputs/demos/.gitkeep`; and
  `tests/test_data_pipeline.py`.
- Files modified: `configs/config.yaml`; `.gitignore`;
  `src/ear_rag/retrieval/local.py`; and `PROGRESS.md`.
- Tests run: `\.venv\Scripts\python.exe -m pytest`.
- Test result: **45 passed in 0.68s**.
- Limitations: no native parser or downloader for NQ, HotpotQA, or 2Wiki; no
  persistent precomputed lexical term statistics; no dataset-level experiments.
- **ESA, cost-aware decision-making, recovery, generation, and evaluation are
  NOT implemented yet.**
- No models, datasets, or large ML dependencies were downloaded or installed.

## Current Architecture

- `src/ear_rag/core/models.py`: typed dataclass contracts only.
- `src/ear_rag/core/interfaces.py`: typed `Protocol` contracts only.
- `src/ear_rag/config/loader.py`: lightweight YAML configuration loading and
  access helpers.
- `src/ear_rag/retrieval/`: chunking, lexical/BM25-style, hashed Vector Flat,
  score-fusion Hybrid and bounded Multi-hop retrieval, with cost metadata.
- `src/ear_rag/data/`: local adapters, schema normalization (including Parquet),
  preprocessing, separate corpus/evaluation artifacts and persisted-index reload.
- `src/ear_rag/evidence/`: deterministic relevance, coverage, support and
  consistency assessment. `routing/`: heuristic initial routing, provisional
  cost-aware recovery selection and bounded retrieval control.
- `demo.py`: existing retrieval/controller CLI; no generated answers.
  `evaluate_initial.py` and `evaluation_*.py`: existing offline evaluation tools;
  no research evaluation run during this reliability phase.
- `configs/config.yaml`: tracked runtime defaults. Recovery is capped at one
  round, must reassess ESA after recovery and abstains on remaining insufficiency.
- `tests/`: contracts, local data/retrieval/control/routing/evaluation checks and
  isolated package imports; demo tests use temporary synthetic normalized inputs.

## Current File Structure

```text
src/ear_rag/
  __init__.py
  config/{__init__.py, loader.py}
  core/{__init__.py, models.py, interfaces.py}
  data/{__init__.py, datasets.py, preprocessing.py, persistence.py, pipeline.py, normalization.py}
  retrieval/{__init__.py, chunking.py, local.py, vector.py, hybrid.py, multihop.py}
  evidence/{__init__.py, esa.py}
  routing/{__init__.py, query_analysis.py, initial.py, cost_awareness.py, recovery.py, pipeline.py}
  demo.py, evaluate_initial.py, evaluation_metrics.py, evaluation_report.py, evaluation_artifacts.py
configs/config.yaml
tests/{conftest.py, test_*.py}
pyproject.toml, requirements.txt, pytest.ini, README.md, PROGRESS.md, AGENT_HANDOFF.md
data/{raw,processed,indexes,fixtures}/
outputs/  # ignored generated artifacts
```

## Dependencies

- Python >=3.11 is required by StrEnum/Self; actual verification uses 3.12.4.
- Existing environment `ai-proj-new`: pytest 9.1.1, PyYAML 6.0.3, pyarrow 25.0.1,
  mypy 2.3.1 and pre-commit 4.6.2, all declared. Installed editable ear-rag 0.1.0.
- `requirements.txt` remains the single dependency source, read by pyproject.toml.
  No existing dependency versions were upgraded; no model frameworks were added.

## Models

No models selected, configured beyond placeholder strings, or downloaded.

## Datasets

Tracked deterministic fixtures support tests without external datasets. This
workspace already contains ignored raw/processed datasets from earlier phases;
the interactive demo needs these local normalized artifacts, which fresh clones
do not contain. No dataset/model downloads or preparation occurred in this phase.
NQ-Open still requires a separately supplied external retrieval corpus.

## Experiments

Historical local development evaluations are documented in the 2026-10-09 entries
and linked reports. They do not establish independent research improvement.
No evaluation or calibration experiments were started during reliability Phase 1.

## Known Issues

- Python 3.11 and standalone wheel deployment are not tested in this phase.
  Editable installation retains repository-relative config/fixture paths.
- Full interactive demo behavior and real-dataset commands are outside scope.
- The ignored `pytest_phase_16c_tmp/` directory denies enumeration; it is outside
  configured testpaths and was left untouched. No root package shadow exists now.
- Heuristic routing, ESA and cost estimates remain uncalibrated prototypes;
  generation, independent baselines and research claims are not completed.

## Next Phase

Reliability Phase 2 requires the user's explicit review and approval. Proposed
scope: separately review remaining demo/data prerequisites and define the next
controlled validation task. Do not automatically prepare datasets, calibrate
estimators, change routing policy or start research evaluation.
