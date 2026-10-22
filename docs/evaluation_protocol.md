# EAR-RAG dataset and evaluation protocol — Phase 5.1

## 22. Phase 6B eligibility audit — final evaluation BLOCKED (2026-10-22)

No protected final cohort or operational evidence-only test-scoring procedure was
verified. No final benchmark, new development benchmark, refit, label generation,
test download or cohort selection occurred. Audit/validation report:
outputs/phase6b-protected-evaluation-audit-20261022T161807Z-7e19b0ef/REPORT.md.
This is a gate decision, not a new research result or a replacement test split.

Clarification: the pinned author repository DOES provide evaluate_v1.0.py, an
offline scorer requiring labelled gold answers/aliases, support flags and answerable
fields. It reports answer/support F1 and optional sufficiency metrics, not EAR-RAG
Hit@5/paragraph Recall@5. Public scorer existence does not establish access to
protected test gold or hosted scoring compatible with this evidence-only task.
Both official leaderboard URLs could not be reached through the checked tools;
this is an access limitation, not proof the service is universally unavailable.
No official prediction file or answer was fabricated or submitted.

Local official train is fitted and official dev is already used for development
and selection; third-party test.json is the same dev cohort. Historical test
schema probes cover one record per test variant and lack gold fields; do not
generalize those probes into verified labels/identity for an entire test cohort.
Test IDs/normalized-question disjointness, paragraph overlap and prior-use history
cannot be certified without the exact eligible test records. Existing train/dev
disjointness and 3,696 shared paragraph texts remain separate verified facts;
the 31 NQ step-text matches are potential indicators, not proven training use.

The unchanged Phase 6A candidate is query_tree_v1 depth0, one leaf with counts
[17296,1865,777,0], artifact SHA256
12e44dc3ac8f17300b90082021feffc0dfafc37d6e7737276d89088e6c5bd204.
It chooses lexical for every valid query when lexical is available; otherwise it
raises rather than falling back. No query-dependent learned benefit is established.
Original query_features_v1 remains the normal default. Existing six-condition
runner can use the explicit selected_config.json: fixed conditions bypass routing,
condition5 uses this frozen trained artifact without recovery, condition6 the same
artifact with unchanged deterministic CAS/one recovery/reassessment. The original
heuristic may be separately labelled supplementary; do not silently substitute it
for the trained candidate. No final system/test-ID manifest is invented here.

Before any later final run: obtain verifiable protected paragraph-support labels
or an authorized blind scorer for the intended evidence metrics, exact source/
revision/license/hash/IDs and a defensible project-exposure/use record. Check
cross-split identity/text and quantify paragraph reuse; overlap alone is not
automatic invalidation, while missing history is not clearance. Freeze candidate,
preprocessing, label objective, settings, six conditions, metrics and pairing/
failure/uncertainty procedure BEFORE first test outcomes. No further model or
CAS/ESA/backend tuning. Dev cannot become final test via random repartitioning.

## 21. Phase 6A initial-router training/development protocol (2026-10-22)

Official MuSiQue-Ans v1.0 train is now explicitly authorized for fitting, with
official dev used for model selection only. Both are development/internal —
exposure limitations apply. No protected final test or official scoring access
has been established. Prior Phase 5 outputs remain historical, not tuning targets.
The bounded search/target was declared before labels in
outputs/phase6a-router-development-20261022T155210Z-95732e1d/PROTOCOL.md.

Offline target: greatest native paragraph Recall@5 among four fixed no-recovery
actions; ties minimize actual underlying calls, then lexical/vector/hybrid/multihop
order. Zero-hit targets retain their minimum-call tie choice and flag. Any missing/
failed action excludes that question from fitting with explicit accounting;
invalid native input stops the workflow. Targets reflect these prototype backends
and candidate pools/cutoff, not an optimality guarantee. No test results involved.

The only learned component is a small pure-stdlib CART/Gini initial router over
the existing 11 text-only features. Depths 0/1/2/3 and minimum leaf 64; deterministic
ties, no RNG (recorded seed 0). Fit on official train only. Select by dev macro
paragraph recall, then calls, then smallest depth. No refitting on dev, further
feature/search changes or recovery/ESA/CAS tuning. Official split IDs and normalized
questions must be disjoint; shared components/paragraph text are separately
disclosed and do not establish independent exposure clearance.

Model artifact query_tree_v1 records exact feature/class schema, counts/splits,
fit settings and data hashes. Runtime query_analysis must explicitly specify
enabled/policy/artifact_path/artifact_sha256. Missing/incompatible artifacts or
unavailable selected backends fail; no silent fallback. Original heuristic config
remains reproducible and is still the project default. Pipeline factory dispatch
is the only controller integration change; trained features and CAS dependency
features use the same original analyzer. No answers, gold, IDs/order, decomposition,
retrieved evidence or outcome measures enter inference.

Evaluate fixed baselines, original router, training-majority constant and selected
trained router without recovery on dev; also report selected bounded adaptive
controller separately. Paired requested/evaluated/failed IDs and missing measures
remain explicit. Report label agreement (proxy only), native Hit/Recall, observed
calls/chunks/latency and separate nominal cost. Primary descriptive paired recall/
Hit intervals: existing mean_interval B=10000/seed=1729, question unit, development
and shared-component caveats; other comparisons exploratory. Predeclared groups
are dependent signal, conceptual without dependent, remaining; n>=30 for metrics.
Sentence coverage, answer quality, calibrated monetary costs and hallucination
reduction remain unavailable. No final test evaluation is authorized by Phase 6A.

## 20. Frozen MuSiQue official-dev protocol (2026-10-22)

Authorized cohort label: **development/internal — exposure limitations apply**.
Use every strictly validated native MuSiQue-Ans v1.0 dev record, in source order,
from data/raw/musique/official_v1_0/musique_ans_v1.0_dev.jsonl, SHA256
15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b.
The acquisition manifest pins author repository revision
922ac98f19a201998dbdae6d7f2887a5258dbdeb and CC-BY-4.0; local byte integrity is
verified, without an author-signed canonical archive hash. The derivative
test.json is checked for identity only and is not the benchmark input.

Native validation policy musique_official_jsonl_v1 rejects the entire input if
any record is defective: malformed/duplicate-key/nonfinite JSON, missing fields,
blank required text, duplicate question/paragraph/decomposition IDs, invalid
indices, or support-reference/flag disagreement. Diagnostics retain all defective
IDs/positions/reasons; valid/excluded/unclassifiable are disjoint counts.
Missing IDs are unclassifiable. No partial inspection becomes an evaluation
dataset. Passing validation does not confer exposure clearance or split approval.
Repeated titles and duplicate question text are allowed, preserved and reported.
Current checks: 2,417 unique answerable records, 48,315 candidates, 6,404 supports,
zero exclusions/unclassifiable; six duplicate normalized-question groups retained.
31 decomposition-text matches with local NQ are potential exposure indicators,
not proof of training. No independent test or holdout is asserted.

Reuse the existing six v2 conditions unchanged: fixed_local_lexical_no_recovery,
fixed_vector_flat_no_recovery, fixed_hybrid_no_recovery,
fixed_multihop_no_recovery, query_aware_no_recovery, adaptive_controller.
All receive identical ordered IDs, candidate text/title/order, top-k 5, chunking
400/50, vector dimensions 64, hybrid .5/.5 and max_hops 2. Fixed conditions bypass
initial selection; first five set recovery rounds to zero. Adaptive retains one
round, mandatory ESA reassessment and final abstention when still insufficient.
Router/ESA/CAS/configuration remain exactly frozen: ESA .7/.4, equal .25 weights;
CAS=(1-current ESA)*binary observable suitability/incremental configured work
cost, strict CAS>tau=1, with existing .05 minimum and nominal work table.
No labels, aliases, answerable, decomposition, enrichment, or ID-derived hop
features enter runtime decisions. Runtime receives only question text/ID and
fresh safe paragraph documents; source checksums and gold stay offline.

Primary comparison: adaptive minus router-only/no-recovery terminal paragraph
Recall@5. Secondary: paragraph Hit@5 and comparisons with four fixed baselines.
Metric cutoff means first FIVE CHUNKS, then deduplicate by native parent paragraph
ID; it does not mean five distinct paragraphs. Native idx-scoped IDs, never title
joins, identify supports. Any chunk credits its parent, without claiming full
paragraph text coverage or semantic support. Terminal evidence is replacement
recovery evidence, not a union. Quality includes abstentions.
supporting_document_recall_at_5 is explicitly labelled native_paragraph;
supporting_evidence_coverage_at_5 retains its HotpotQA sentence meaning and is
null/unavailable with reason/count for MuSiQue. No sentence labels are invented.

Retain every requested row, failure and exclusion. Require identical requested
IDs/order/configuration definitions before comparing; pair only IDs evaluated
in all six, report unpaired/failure IDs and metricwise missing denominators.
Uncertainty: existing mean_interval, 10,000 paired question bootstrap draws,
seed 1729, 95% percentile intervals. These describe this development cohort;
duplicate texts/shared components limit independence, secondary intervals are
exploratory without multiplicity correction. No unseen-generalization inference.
Report initial/final ESA, recovery reassessment, paragraph recall improvements/
ties/regressions and generate/abstain counts. Generate means evidence judged
sufficient; no answer is generated or verified.

Measured calls, returned chunks, child passages and retrieval/router latency are
work proxies. Report nominal configured initial and incremental recovery costs
separately, never as money or realized future latency. One fixed-order pass;
loading/index construction, complete controller time, processed chunks and money
are unmeasured. No parameter tuning, rerun in response to outcomes, or training.

Execution command (only after focused/full tests and isolation gates pass):
`python -B -m ear_rag.musique_experiment run --output outputs/<new-unique-name>`.
There was no existing condition CLI: this is a narrow wrapper over the existing
evaluate_conditions/serialization/aggregation/mean_interval APIs, not a second
evaluator. It writes frozen source/config/protocol/input hashes before retrieval,
dataset/cohort manifests, six condition outputs, paired analysis, report and hashes.
`python -B -m ear_rag.musique_experiment verify --output <same-directory>` replays
saved source-window/paragraph metrics and analysis without retrieving again.
Benchmark completion/results belong to the dated audit/progress/output report;
this frozen protocol is not rewritten after seeing outcomes. Phase 6 pending.

## Historical HotpotQA status and protocol

**Current status, verified 2026-10-22: Phase 5 is PARTIALLY COMPLETE.** The
ingestion/policy, corpus/evidence, metric/controller evaluation and condition-runner
software is implemented. Phase 5.5D development execution and Phase 5.6 analysis
are complete for the previous expected-gain policy, labelled
**development/internal — known exposure**. The revised deterministic CAS is
implemented, software-verified and separately evaluated on the same 497 known-
exposed development questions under the frozen protocol in section 19. All six
current conditions completed, with 500 requested/497 evaluated/3 excluded/0 failed
each. No exposure-cleared evaluation has been performed.
Source provenance, complete exposure evidence and approved holdout/split validity
remain unresolved. Proposed 100/200 roles have not been approved or created.

[Section 19](#19-frozen-revised-cas-diagnostic-evaluation-2026-10-22) records the current
diagnostic results and remaining gates; section 18 preserves the prior software
reconciliation checkpoint. Sections
1–8 preserve the original Phase 5.1 design; sections 9–17 preserve milestone
history. Statements such as "no experiment" or "planned" in those snapshots
describe their original checkpoints, not the later Phase 5.5D/5.6 work. No
historical report, metric definition or original exposure requirement is changed.

## 1. Dataset decision and official sources

Recommend a small **HotpotQA distractor development subset**, with retrieval
restricted to each question's supplied candidate paragraphs. This validates the
evaluation machinery under bounded conditions, not open-domain retrieval quality.
Keep 2WikiMultiHopQA as a later extension.

Official facts checked for this decision:

- [HotpotQA website](https://hotpotqa.github.io/): distractor supplies ten
  paragraphs; full-wiki targets search over Wikipedia. Dataset licensing is
  CC BY-SA 4.0.
- [Official repository](https://github.com/hotpotqa/hotpot#json-format): releases
  use a JSON array; records include `_id`, question and title/sentence contexts.
  Labels identify answers and supporting `(title, zero-based sentence index)`
  pairs. Public test records omit answer/support labels and type/level metadata.
  The repository distinguishes Apache-2.0 code licensing from dataset licensing.
- [Official setting description](https://github.com/hotpotqa/hotpot#data-download-and-preprocessing):
  supplied full-wiki contexts are pre-retrieved candidates and can miss gold
  evidence. A file named fullwiki does not contain an independently searchable
  Wikipedia corpus.

Keep dataset attribution, paper citation, source URL, license link and a record of
normalization changes in future manifests. If redistributing adapted dataset
material, retain the applicable ShareAlike terms; see the
[license summary](https://creativecommons.org/licenses/by-sa/4.0/). Do not infer
that the upstream code license licenses the data. Do not run the upstream
download script: it also obtains assets outside this task's scope.

The initial **candidate-pool** condition uses every supplied paragraph for that
question, never a gold-filtered subset, and gives initial/recovery retrieval the
same pool. A union of contexts from many examples is a different
`pooled-provided-context` condition; neither condition is full-corpus retrieval.
Existing historical local reports used pooled contexts and remain separate.

For a later full-corpus experiment, the
[official Wikipedia documentation](https://hotpotqa.github.io/wiki-readme.html)
offers an introductory-paragraph archive of about 1.55 GB compressed and a larger
processed-article archive of about 7.41 GB compressed. Prefer assessing the
introductory-paragraph corpus first. Compression sizes do not establish RAM,
index size or acceptable latency. Current retrievers keep Python structures in
memory and use flat scans; feasibility is **unmeasured**. Require a separately
approved corpus version, title/paragraph alignment, disk/RAM/indexing budget and
retrieval design before acquiring/indexing it. No full-corpus availability claim
is made here.

## 2. Development, held-out roles and exposure safeguards

Recommended project-level partition, to be confirmed before Phase 5.2:

1. Source: the official `hotpot_dev_distractor_v1.json`; retain
   `official_split=dev` for every record. Define a 100-question engineering/
   development subset and a prospective 200-question internal held-out subset.
   These are **roles within official dev**, not new official train/test splits
   and not an official test benchmark score.
2. Check duplicate `_id` values before selection; conflicting/repeated source IDs
   fail validation rather than being overwritten. Group duplicate question text
   by NFKC normalization, lowercase and collapsed whitespace, without labels.
   Pick the lexicographically smallest source ID as each group's representative;
   retain all aliases for overlap/exposure checks. Report removed duplicates.
3. Rank representatives by the hexadecimal SHA256 of UTF-8
   `"1729:" + source_id`, ascending, breaking ties by source ID. First 100 are
   development. This is a specified hash order, not the evaluator's existing
   seeded shuffle or the historical first-500 prefix.
4. Construct a prior-exposure ledger from the existing local development studies,
   demonstrations, reports and any earlier tuning. Exclude from held-out selection
   all development IDs, previously exposed IDs and all their duplicate-text aliases.
   Treat distractor/full-wiki versions of an ID as the same question. Select the
   next 200 eligible representatives in the same hash order; leave others unused.
5. Store the ordered selected IDs, aliases, exclusions/reasons, seed string,
   selection version, source SHA256 and role in a manifest. If insufficient
   eligible questions or exposure history cannot be reconstructed, **do not claim
   a clean held-out set**. Report the blocker; do not silently shrink or replace it.

Why repartition official dev: official test labels are not public, while earlier
EAR-RAG work already examined development labels. The old 500-question full-wiki
subset is development material, not a pristine test set. This partition supports
a transparent internal check only; report its filtering/selection bias. No
exposure ledger, selected ID list or split artifact has been created in Phase 5.1.

Development labels may tune thresholds, routing rules or cost estimates only in
a separately authorized tuning phase. Held-out labels are evaluator-only and
used for final scoring only after code/configuration are frozen. Offline data
preparation may validate their schema/joins and package them without displaying
values or reporting performance; it must not use them to alter system decisions.
A revealed held-out
result cannot be reused to tune a system and still be called held-out. Official
training data could support future tuning, with source provenance and overlap
checks; it is not selected here. Official blind test scoring is a separate future
submission path, not a source of local test labels.

## 3. Normalized records and access boundaries

The following is a proposed artifact contract; reuse existing dataclasses where
possible rather than passing one object containing questions and labels around.

| Artifact / role | Required content | Access |
| --- | --- | --- |
| Runtime questions (A) | `example_id`, original question text, dataset, official split, role, source version, candidate-pool ID and ordered document IDs | Runtime input loader; only ID/text become `Query` |
| Runtime documents (A) | `doc_id`, title, exact ordered source sentences, joined text, sentence character spans, dataset/source version and pool provenance | Indexer/retrievers; no supervision fields |
| Development labels (B) | `example_id`, reference answer(s), raw supporting facts, resolved supporting-document IDs, source/split, type/level and annotation status | Development evaluator/tuning only |
| Held-out labels (C) | Same label schema as B, `role=heldout`, separate artifact/location | Final evaluator after freeze; never a tuning input |
| Manifest | Schema version, source/license attribution, file/content hashes, ID namespace, roles/selection/exposure exclusions, normalization policy and corpus scope | Audit/orchestration; no labels copied into runtime objects |

Keep `_id` as stable `example_id`, qualified by dataset/source version in joins.
Preserve official split separately from the project's usage role. Type and level
are annotation metadata for offline grouping; exclude them from runtime analysis
because blind test does not supply them.

Runtime receives only `Query(example_id, question)` and allowlisted `Document`
fields. Source question IDs in document provenance must not be used as a ranking
shortcut. No answer, support membership, support sentence ID, type/level, or
answer-derived feature may enter query metadata, document/chunk metadata, text,
index selection, query expansion, routing, ESA or recovery. Naturally occurring
answer text in an unmodified source paragraph is legitimate evidence; appending
the gold answer is leakage. Never identify candidates by support labels.

The future runtime projection must not open either label artifact. An offline
evaluator can join labels **after** execution; development and held-out evaluation
must use distinct entry points/permissions or an explicit guarded role check.
Filesystem separation alone is not an enforcement mechanism. Add tests that
changing labels cannot change documents, routing, evidence, ESA or cost traces,
and that runtime operation succeeds without label-file access. These stronger
boundaries are planned, not all enforced by today's demo loader.

## 4. Document, chunk and support mapping

For per-question pools, retain the existing document convention
`hotpotqa:<example_id>:<original_context_position>` within a versioned `corpus_id`.
Identity is `(corpus_id, doc_id)`: positions can change between release/settings,
so IDs alone are not cross-version Wikipedia article IDs. Reordering or selecting
questions must not renumber their original contexts. Do not merge repeated titles
across questions into a global corpus under this protocol.

Join original sentences with one ASCII space, retain sentence order and exact
character spans. The existing chunker emits `<doc_id>:chunk:<index>`, parent
`document_id`, character window bounds and nested `document_metadata`. Preserve
the title/provenance chain; a retrieved chunk maps to its parent ID regardless of
its backend. Deduplicate parent IDs for document-level retrieval metrics.

Only evaluation resolves each gold `(title, sent_id)` within the correct original
question pool. Require a unique exact title and an integer in-range sentence ID;
record missing/ambiguous mappings. Do not guess a match using an answer, another
question's repeated title, a fuzzy title or corpus insertion order. Candidate
distractor input should resolve its annotations; an unexpected mapping failure
blocks release of the primary benchmark artifact, with counts/reasons retained.

Document retrieval does **not** imply sentence evidence retrieval. Proposed
supporting-fact coverage requires the union of actually returned character spans
to cover the complete annotated sentence span. Partial sentence overlap does not
count. Whitespace trimming, overlapping chunks and source sentence segmentation
must pass alignment tests first; current title-only metrics do not implement this.
For a later independent corpus, establish canonical article/paragraph IDs and
versioned aliases, and validate sentence alignment rather than reusing local IDs.

## 5. Metrics, denominators and failures

Primary cutoff: **k=5 returned chunks per retrieval invocation**, matching current
configuration. Freeze chunk size 400/overlap 50 for the initial protocol; changing
chunking is a separately versioned condition. k is not five unique documents or
a budget of five child/hop passages. No settings are changed in Phase 5.1.

For question q, let Gq be its unique, correctly resolved gold supporting-document
IDs and Rq(k) the unique parent IDs in its first k returned chunks. Report initial
and terminal evidence separately. Terminal means the recovery result if recovery
occurred, otherwise initial result: current ESA reassesses recovery evidence
alone. Do not silently union initial/recovery chunks into the assessed context.
An optional ever-retrieved union is a separately labelled diagnostic.

| Metric | Definition and aggregation | Current capability |
| --- | --- | --- |
| Hit@5 | Indicator that Rq(5) intersects Gq; mean over eligible labelled questions | `retrieval_metrics` key `hit_at_k`; missing/unresolved labels produce null |
| Supporting-document Recall@5 | `len(Rq(5) & Gq) / len(Gq)`; primary headline uses fully resolved annotated support sets | `full_support_recall_at_k`; resolved-only recall for partial cases is a separate conditional diagnostic |
| All-support coverage | Indicator that all gold documents are retrieved; never equate one hit with multi-hop coverage | Existing full/resolved coverage fields |
| Label-resolution coverage | Unique resolved support titles / unique annotated support titles; report complete/partial/unresolved/unknown counts | `LabelResolution.record()` and `resolve_labels()` |
| Supporting-fact coverage | Unique fully covered gold sentence pairs / annotated sentence pairs; macro mean; optional all-facts indicator | Planned sentence alignment/scorer; unavailable today |
| ESA | Relevance, coverage, support, consistency, overall and categorical outcome; initial and post-recovery per query, then means/counts | Runtime result has fields; dedicated trace/report aggregation missing |
| Initial selection | Selected backend counts / all successfully executed questions; report policy fallback and causes | Current initial-only evaluator reports routing distribution |
| Recovery | Performed rounds >0 / successfully executed questions; action/backend, policy reason, second ESA and actual-minus-initial ESA | Controller supports it; existing `evaluate_initial` explicitly disables recovery |
| Operational cost | Sum actual per-invocation leaf calls; initial/recovery returned chunks, total and unique context chunks, child passages and latency separately | Runtime/metadata available; bounded-recovery report extension needed |
| Abstention | Terminal `abstain` count / successful questions, with original policy reason and final ESA; distinguish initial rejection from post-recovery insufficiency | State/reason fields available; complete reason taxonomy/aggregation planned |
| Answer EM/F1 | **Unavailable** for EAR-RAG answers until an actual generation stage exists | `ANSWERABLE` is not a prediction; generator contracts do not generate |

For partial annotation resolution, never present resolved-only recall as full
gold recall. Report `N_requested`, `N_successful`, `N_fully_resolved` and all
quality denominators; primary distractor release requires complete mapping.
Unknown/no usable labels yield null quality metrics, not zero. With valid nonempty
Gq, an empty retrieval result yields zero hit/recall/coverage. All-zero sample
counts yield null rates. Labelled sentences/documents and returned chunks are
deduplicated in their respective units, not counted repeatedly across hops.

Runtime exceptions, unavailable backends and invalid records are explicit failures
with `failure_rate = failures / requested`; they are not successful abstentions.
Do not silently omit them from a comparative result. Report completed-case metrics
as partial if any requested execution fails; stop the primary comparison until
the cause is resolved. Missing generation is a capability gap, not a resource
failure or an invented zero answer score.

Means are macro averages over questions with the stated eligibility; rates are
counts with numerator/denominator. Compare systems on identical eligible IDs.
Report call/chunk means and totals; latency mean/median/p95 with sample count and
timing scope. Retrieval metadata times exclude routing, ESA, loading and indexing;
log router time separately. Future controller wall time should time `run()` and
include its assessment/dispatch overhead; report load/index costs separately.
Five warmed timing repeats per question/condition are proposed, with first-run
timing retained separately; no timing repeat or new metric was run in this phase.
Use question-paired differences and seeded 1,000-resample bootstrap intervals for
comparisons; intervals on a small development subset do not establish generality.

## 6. Fair comparison and reproducibility

Every condition gets the same ordered questions, exact per-question candidate
pool, source text, chunking, k and evidence access. Freeze configuration, code
hashes including uncommitted changes, dataset/pool/label hashes and backend
parameters. Models, learned embeddings and cost calibration are absent; label
prototype backends accordingly. Record measured work rather than assuming equal
cost for lexical and two-child/two-hop strategies.

Keep two separately labelled evaluation regimes: initial-only comparison
(recovery disabled for every condition), and bounded-controller verification
(same frozen recovery settings, maximum one round, mandatory reassessment).
Do not combine results across regimes. All four strategies remain implementation
options, not newly reproduced research baselines. Fixed-strategy replay and
best-observed diagnostics remain offline, never runtime label-based selection.

Record condition order, seeds, manifest/role, source/config hashes, Python/package
versions, hardware, warm-up/repeat policy and exceptions in per-question JSONL
and aggregate JSON/CSV. Persist traces before offline label joins. Use seed 1729
for the proposed selection/order/bootstrap procedures, recording the algorithm
for each; a seed alone is insufficient. No result artifact has been generated
for this protocol. Existing synthetic tests are software checks, not benchmarks.

## 7. Verified compatibility and gaps

| Inspected implementation | Verified finding / minimum gap |
| --- | --- |
| `core/models.py`: `Query`, `Document`, `RetrievedChunk`, `RetrievalResult`; `core/interfaces.py`: `Retriever`, `IndexableRetriever`, `EvidenceAssessor` | Already accept ID/text/metadata and normalized documents; no core redesign needed |
| `data/normalization.py`: `normalize_hotpotqa_record`, `NormalizedExample.example_record/evaluation_record`, `NormalizedDocument.corpus_record` | Existing per-record normalization separates supervision and preserves title, local IDs and spans; lacks split/role/source-manifest enforcement |
| `data/normalization.py`: `NormalizedCorpusBuilder._read_jsonl/build` | Reads JSONL and requests NQ/2Wiki inputs too; not an official HotpotQA JSON-array-only input path |
| `data/datasets.py`: `LocalJsonlDatasetAdapter._parse_record` | Older `contexts/document_id` interchange differs from newer `documents/doc_id`; unrestricted metadata is copied, so a strict runtime projection is needed |
| `data/persistence.py`: `RetrievalArtifactStore`; `data/pipeline.py`: `prepare` | Existing persistence/index preparation is reusable, but examples may include reference answers; do not treat all persisted records as runtime-safe |
| `demo.py`: `load_demo_dataset`, `build_backends`, `DemoRunner._fresh_backends` | Loads separate labels for reporting, but in the same loader; builds a pooled corpus across loaded questions, not this per-question distractor condition |
| `retrieval/chunking.py`: `DocumentChunker.chunk_document` | Stable parent/chunk IDs and metadata chain exist; fact-level span alignment needs validation |
| `evaluation_artifacts.py`: `resolve_labels`, `provenance`, `save_reports` | Existing title-based label resolution, hashes and JSON/CSV reports; no prior-exposure ledger/role lock or sentence-ID validation |
| `evaluation_metrics.py`: `retrieval_metrics`, `LabelResolution`, `mean_interval`; `evaluate_initial.py`: `evaluate_initial/main` | Existing hit/recall/coverage, operational metadata and seeded comparisons; fixed pooled backends, recovery disabled, no full controller traces or sentence metrics |
| `routing/pipeline.py`: `RetrievalControlPipeline.run`, `RetrievalControlResult` | Already records initial/second ESA, one recovery, decision/reason and actual work; no answer generator |
| `tests/test_dataset_normalization.py`, `test_initial_evaluation.py`, `test_evaluation_validation.py`, `test_runtime_reliability.py` | Existing synthetic separation/reproducibility/control checks pass; new official-array, role/exposure, per-question scope and sentence-alignment tests are missing |
| `configs/config.yaml`, `.gitignore`, `requirements.txt`, `pyproject.toml` | Current fixture configuration stays unchanged; data/index/output roots are ignored, pyarrow is declared, no new dependency is needed for a JSON reader/manifest |

These are source/test findings, not a validation of a newly acquired official
dataset. Prior progress records describe legacy local data; this phase neither
recertifies its provenance nor treats it as the proposed distractor input.

## 8. Precise next-phase plan and review gates

**Phase 5.2 — data contract and preparation tooling, only after approval:**

1. Confirm source file availability and the 100/200 role recommendation; inventory
   historical exposure IDs, including aliases across settings. If the official
   input or exposure history is unavailable, record the blocker. Do not fetch
   assets or silently substitute the existing full-wiki prefix.
2. Add a narrow official HotpotQA JSON-array reader/validator in the existing data
   package, reusing `normalize_hotpotqa_record`; retain existing JSONL support.
   Avoid a duplicate normalizer or requiring unrelated NQ/2Wiki files. Test blind
   label absence explicitly before claiming blind-test ingestion is supported.
3. Add split/source/role manifests, deterministic hash selection, duplicate and
   overlap checks, and strict runtime versus evaluation projections. Preserve
   existing local IDs within versioned pools; keep type/level offline. Require
   round-trip title/sentence/span and evaluation-join checks.
4. Write synthetic tests for array/schema failures, stable IDs under reordering,
   duplicate aliases, held-out exposure rejection, annotation bounds and runtime
   label-file denial/mutation invariance. Verify reproducible artifact hashes and
   no overwrite of legacy files. Prefer a versioned new output directory.
5. Once an input is explicitly supplied/authorized, validate and emit only the
   approved small artifacts/manifests, with attribution and validation counts.
   Run the full software suite, synchronize docs/handoff and stop. No indexing,
   retrieval experiment, tuning, evaluation results or generator integration is
   part of that data-tooling deliverable.

**Phase 5.3 — evaluation wiring, separately approved:** adapt the evaluation
driver to exact per-question pools; reuse current metric/report functions; add
bounded-controller traces/aggregation, explicit terminal-context semantics,
failure/abstention reporting and locked role/configuration checks. Implement
sentence coverage only after alignment tests pass. Verify wiring with synthetic
fixtures before authorizing any development experiment. Answer EM/F1 remains
unavailable unless generation is separately implemented and verified.

Open review decisions: approve/change the proposed role counts/partition; supply
the official distractor input and complete exposure inventory; decide whether a
later full-corpus resource assessment is worthwhile. Unknown resources and exact
eligible holdout counts remain unverified. These do not block the Phase 5.1
design deliverable, but they gate subsequent preparation and held-out claims.

## 9. Phase 5.2 implementation status

`data/hotpotqa.py` now implements `read_hotpotqa(path, source_split=...)` for
labelled train/dev JSON arrays. It uses the existing normalizer/dataclasses and
validates nonempty questions/answers/contexts, unique IDs/titles, support-title
resolution and integer sentence bounds. Source bytes remain read-only; JSON
duplicate keys are rejected. Any record failure raises `HotpotQAValidationError`
with counts/diagnostics instead of returning a partially accepted dataset.

`runtime_projection` allowlists safe question/document fields, preserving exact
candidate sentence text and offsets. `evaluation_projection` separately retains
answers, raw supports, supporting-document IDs, annotations and provenance.
Additional source fields are retained offline, including nested annotations;
they never enter the runtime view. Type/level may be absent without fabricated
values; the normalizer's existing requirement changed only for those optional
annotations. Blind test input remains explicitly unsupported. The source checksum
identifies the offline input, not a runtime feature influenced by gold labels.

Synthetic reader/projection plus legacy normalization tests: **45 passed**.
At the initial utilities checkpoint, no official distractor JSON array or complete
exposure inventory was found. Section 10 records the subsequently supplied
Parquet audit. No real split or authenticity certification is claimed.
Role counts remain provisional.
No retrieval/ESA/routing/recovery change is made.

`data/hotpotqa_splits.py` now implements `plan_splits`,
`validate_split_integrity` and `write_split_artifacts`. Counts must be explicit;
there is no automatic adoption of the proposed 100/200 roles. Selection follows
section 2's hash order and canonical duplicate groups. The manifest records raw
source hash/identity and a format version, requested role IDs/counts, accepted/
rejected/malformed/duplicate-ID counts, normalized-text duplicates/aliases,
holdout exclusions and integrity-check scope. Reader failures carry diagnostic
counts but cannot generate split artifacts; malformed file-level input has no
countable records and is rejected separately.

`ExposureInventory(identifier, questions)` maps exposed IDs to known question text
or `None`. Matched source IDs recover text without labels; unmatched IDs need text.
Unavailable (`None`) or partial inventories block nonempty holdout. An explicitly
supplied empty mapping is allowed for synthetic tests or an explicitly asserted
empty history, not inferred from missing information. Supplied history is checked
exactly; it is not certified exhaustive. Near-duplicate semantics are not checked.

The writer preflights before creating a new destination, never overwrites one,
and writes `{development,holdout}.{runtime,labels}.jsonl` plus `manifest.json`.
File hashes/row counts are recorded; the manifest is written last. A disk/write
failure can leave an incomplete directory without a manifest; callers must not
treat that as a successful preparation. Combined normalized examples and their
legacy serializers are offline data, not the new runtime projection API. The
writer does not alter the existing demo/evaluator or implement role-aware runtime
loading; that integration remains Phase 5.3.

Synthetic ingestion/split tests: **57 passed**. This includes source preservation,
repeatable output bytes/checksums, explicit ID/text overlap failures, duplicate
alias exposure, unknown inventory status, counts/selection integrity and reading
runtime JSONL with label-file access denied. Only pytest temporary artifacts were
written. Official distractor ingestion and real held-out claims remain pending.

Final Phase 5.2 software suite: **318 passed**, no failures/skips; scoped mypy
passed for both new modules. No real split/manifest was generated. The proposed
100/200 counts and input/exposure validation gates remain provisional. This
phase adds data utilities only; section 8's Phase 5.3 evaluation wiring, stricter
role-aware runtime integration and sentence metrics are still future work.
Exports are scoped by their manifest's source checksum plus setting and local
document ID. Source checksums are not injected into runtime question features;
label-only edits therefore leave runtime projections unchanged. A later loader
must verify the manifest before using unqualified local IDs across artifacts.

## 10. Bounded real-data completion gate (2026-10-20)

**Audit completed; real preparation gate BLOCKED.** Both files under
`C:/ear-rag/data/raw/hotpotqa/` were fully parsed read-only. No Phase 5.3 work
or research scoring was performed.

| Source file | Bytes | Records | Unique IDs |
| --- | ---: | ---: | ---: |
| `hotpot_dev_fullwiki_v1_first_500_samples.jsonl` | 3,259,561 | 500 | 500 |
| `validation-00000-of-00001.parquet` | 27,452,575 | 7,405 | 7,405 |

Raw SHA256 values, recorded before inspection:

- Fullwiki: `8741b7ec050ee21bcec31a03822d53f99bf1c712d5ddc77b5cf085c184087e1c`
- Parquet: `c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6`

### Schema and proposed adapter

JSONL has one object per line with `_id`, `question`, `answer`, `type`, `level`,
`context` pairs and `supporting_facts` pairs. It is not the top-level JSON array
accepted by `read_hotpotqa`. Parquet has eight row groups and this mapping:

| Parquet field | Existing offline field | Lossless mapping |
| --- | --- | --- |
| `id: string` | `_id` | Copy verbatim |
| `question`, `answer`, `type`, `level`: strings | Same names | Copy verbatim |
| `context.title: list<string>`, `context.sentences: list<list<string>>` | `context` | Equal-length parallel arrays to ordered `[title, sentences]` pairs |
| `supporting_facts.title: list<string>`, `supporting_facts.sent_id: list<int32>` | `supporting_facts` | Equal-length parallel arrays to ordered `[title, sentence_id]` pairs |

All parallel-array lengths matched. Mapping occurred only in audit memory for
comparison and calls to the existing private `_normalize_record` validator.
No dataset release, runtime/label projection or split was produced. The current
public reader supports neither Parquet nor JSONL directly.

Proposed later adapter: a separate read-only Parquet reader reusing validation,
with explicit format identity, original filename/hash, caller-supplied source
URL/config/revision/split and authenticity status. Preserve IDs, candidate order,
sentence text/positions and annotations. Reject null/misaligned arrays; never
truncate pairs, clean blank sentences, renumber supports or silently discard rows.
Tests must cover exact mapping, source immutability, null/misaligned arrays,
annotation retention, diagnostics and provenance. **No production adapter was
implemented** because unresolved input/history gates stop dependent preparation;
format conversion alone cannot resolve those prerequisites.

### Agreement and context differences

- All 500 fullwiki IDs match Parquet; zero sample IDs are missing. There are
  6,905 additional Parquet IDs outside the sample.
- Neither source has blank/missing IDs or questions, duplicate IDs, or duplicate
  question groups under NFKC/lower/whitespace normalization. Semantic near
  duplicates were not assessed.
- All 500 matched questions, answers, ordered supporting-fact lists, type and
  level agree exactly. No cross-source ID/question inconsistency was found.
- All 500 ordered context lists differ. Candidate title sets differ for 354;
  unordered `(title, sentences)` contents differ for 362. The remaining 138
  have identical candidates/text in different order. Same IDs across settings
  are the same questions, not independent unseen examples.
- Fullwiki candidate counts: 493 have 10; two have 9, one has 4, two have 2,
  one has 1 and one has 0. Parquet: 7,345 have 10; the other 60 have 2-9
  (2:21, 3:7, 4:9, 5:6, 6:8, 7:2, 8:4, 9:3). No padding was performed.

### Input validation blockers

Existing record validation passes 146/500 fullwiki and 7,355/7,405 mapped Parquet
rows. These are diagnostic counts, **not an accepted subset or ingestion release**.
Independent support/context checks found:

- Fullwiki: 354 records have unresolved supporting titles; three have blank
  candidate sentences and one has an empty context, all overlapping that group.
  Pre-retrieved fullwiki candidates do not guarantee gold support coverage and
  cannot replace the distractor input.
- Parquet: 49 records have blank/whitespace-only candidate sentences. One other
  record has an out-of-range supporting index. No unresolved/ambiguous support
  titles or duplicate candidate titles were found.
- Out-of-range case: ID `5ae61bfd5542992663a4f261`, title
  `Jimmy Butler (basketball)`, index **902**, context length **5 sentences**
  (valid indices 0-4). No labels were rewritten.
- Blank-sentence examples shared across settings: `5a7320565542991f9a20c61d`,
  `5abbd3ac55429931dba1458b`, `5a72c6f65542994cef4bc402`.
  Fullwiki empty-context ID: `5a8cfee555429941ae14df5c`.

Do not weaken validation, delete/reindex sentences, fix labels speculatively or
silently exclude rows. A source-backed, explicit sentence/support policy and its
tests must precede any real release.

### Provenance and prior exposure

Parquet footer `created_by`: `parquet-cpp-arrow version 21.0.0`. Embedded
`huggingface` metadata describes features only: no source repository/configuration,
revision, download URL, release version, license or upstream checksum. No sidecars
exist in this raw source directory. JSONL has record fields only, with no embedded
release/derivation metadata. Filename `v1`/`first_500` and matched content do not
authenticate lineage. Download/derivation history and upstream identity/revision
remain unresolved for both artifacts.

The [official HotpotQA website](https://hotpotqa.github.io/) states CC BY-SA 4.0
for the dataset and supplies separate dev distractor/fullwiki links. The
[official repository](https://github.com/hotpotqa/hotpot) documents the format.
That upstream license statement does not authenticate this local Parquet export
or certify its redistribution history.

No complete genuine exposure inventory was located in accessible project files.
`outputs/query-validation-hotpotqa500/per_query.jsonl` contains 500 unique IDs:
exactly all 500 sample IDs with matching question text. The hotpotqa20 report has
20 unique IDs within that set, also with matching text. These reports establish
**at least 500 exposed questions**, including their corresponding Parquet IDs.
They do not exhaust demos/manual inspection/other runs or certify the other
6,905 as unseen. File enumeration excluded environment/Git/cache directories;
old `pytest_phase_16c_tmp` denied access, limiting exhaustive discovery further.
No inventory or empty-history assertion was fabricated.

### Outcome and verification

Resolve source provenance, strict-reader incompatibilities and complete exposure
history before real role selection or projections. Proposed 100/200 roles remain
provisional; no eligibility or clean-holdout claim is made.

Relevant existing tests: ingestion, splits and legacy normalization together:
**64 passed in 0.96s** using the existing virtual environment. These regression
tests do not override real-file validation failures. No dependencies installed,
data downloaded, source/controller behavior changed or retrieval scoring run.
No meaningful bug was fixed, so no error-log note was created.

Final SHA256 comparison confirms both raw sources unchanged and every baseline
project file outside the four authorized documents unchanged. No baseline file
was removed; no new nonignored path was created. `git diff --check` passed.

## 11. New distractor JSON verification - stopped at path gate

Historical checkpoint: the missing-path blocker below was resolved by the user.
Section 12 records the resumed audit of the exact requested filename.

The subsequent verification request names
`C:/ear-rag/data/raw/hotpotqa/hotpot_dev_distractor_v1.json` and explicitly requires
stopping affected comparisons if an input is missing. That exact file is absent.
The directory instead contains `hotpot_dev_distractor_v1 (1).json`, **46,320,117
bytes**, with SHA256
`4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea`.
Its bytes match the checksum supplied in the request. This is an inventory and
integrity observation about a differently named file, not substitution of that
file for the requested input or independent source-authenticity verification.

No JSON parsing, record validation or JSON-vs-Parquet/fullwiki comparison was
performed after detecting the missing named input. Therefore the JSON record
count, anomaly breakdown and whether it resolves the previous 50 Parquet
validation anomalies remain **unverified**. Section 10 findings remain historical
facts about the two previously audited sources; their SHA256 values were checked
again and are unchanged. In particular, the 500 exposed questions remain exposed;
the other 6,905 are not certified unseen, and 100/200 remains provisional.

The matching user-supplied checksum is not an independently authenticated upstream
digest. Existing upstream license/attribution references remain in sections 1/10;
local source URL/release lineage and complete exposure history remain unresolved.
No raw file was renamed, changed or regenerated. No code, adapter, split,
manifest, projection, experiment, dependency or Phase 5.3 work was performed.
No code changes required tests; no pytest suite was run for this path-only gate.
No qualifying bug was resolved and no error note was created.

Phase 5.2 remains **blocked**, not complete. Next single step: identify the existing
`hotpot_dev_distractor_v1 (1).json` explicitly as the intended audit input, so its
contents can be verified without renaming or substituting files silently.

## 12. Exact-path distractor JSON audit - verification complete, preparation blocked

After the user added the requested path, all three expected files were present.
The resumed audit fully parsed the exact JSON and compared it read-only with
the Parquet and fullwiki sources. Earlier section 11 describes the initial stop,
not the current source availability.

### JSON integrity and validation

- Path: `C:/ear-rag/data/raw/hotpotqa/hotpot_dev_distractor_v1.json`.
- Observed size: **46,320,117 bytes**. SHA256:
  `4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea`.
  This exactly matches the expected checksum supplied by the user.
- UTF-8 JSON top-level array: **7,405 objects, 7,405 unique IDs**. No duplicate
  object keys, non-finite JSON constants, duplicate IDs, missing/blank IDs or
  blank questions. No duplicate question groups under NFKC/lower/whitespace
  normalization; semantic near duplicates were not assessed.
- Every object has `_id`, `question`, `answer`, `type`, `level`, `context` and
  `supporting_facts`. Required strings, candidate/support pair structures,
  sentence types, title uniqueness/resolution and integer bounds were checked.
  JSON syntax is valid; **50 records fail the current strict record contract**:
  49 records each contain one blank/whitespace-only candidate sentence, and one
  other record has an out-of-range support reference. No other anomaly category
  was found by these structural checks.
- Exact out-of-range case is unchanged: ID `5ae61bfd5542992663a4f261`, support
  `Jimmy Butler (basketball)`, index **902** for a five-sentence context.
  The existing public `read_hotpotqa(..., source_split="dev")` rejects the entire
  input with total 7,405 / accepted 7,355 / rejected 50 / malformed 50 /
  duplicate IDs 0. Accepted counts are diagnostics, not a released subset.
- 7,345 records have ten candidates; 60 have 2-9, with the same distribution
  recorded for Parquet in section 10. No candidate padding or filtering occurred.

### Cross-source comparison

JSON and Parquet each have 7,405 records and unique IDs. All IDs match, with
**zero missing IDs in either direction** and zero duplicate IDs. All 7,405
questions, answers, ordered supporting facts, ordered contexts, type and level
match exactly. Whole records match after the lossless section 10 field mapping,
and record ID order also matches. Differences are representation only: JSON
`_id` versus Parquet `id`, list pairs versus structs of parallel arrays, and
JSON text versus typed columnar encoding. No semantic or candidate/sentence-order
difference was found. Therefore **all 50 previous Parquet anomalies are present
unchanged in the JSON**, rather than resolved or transformed. A Parquet export
alone cannot be blamed for these anomalies; their upstream origin is unverified.

Fullwiki overlap is **500 IDs**, with no sample IDs missing. All questions,
answers, ordered supports and type/level match exactly. All 500 ordered context
lists differ; 362 have different unordered candidate contents and 138 differ
only in order. Candidate title sets differ for 354. The JSON has 6,905 further
IDs outside the sample. Existing hotpotqa500 history was rechecked against this
JSON: 500 unique IDs matched, zero question mismatches; hotpotqa20 similarly
matches 20 IDs with zero mismatches. All 500 remain exposed and cannot be called
unseen holdout questions. No unseen status is established for the other 6,905.

### Provenance, blockers and outcome

The filename, fields, count and agreement with existing sources are consistent
with HotpotQA distractor development data. A matching **user-supplied** digest
establishes the expected local bytes, not independent source authenticity. The
JSON contains no source/version/license envelope beyond its record fields.
Windows `Zone.Identifier` records a `huggingface.co` referrer and an
`us.aws.cdn.hf.co` download host. This is local download metadata, not an
authenticated release record; it does not identify a dataset repository/config,
revision, official upstream digest or full derivation history. Signed URL query
parameters were not copied into project documentation.

Upstream HotpotQA's [dataset attribution and CC BY-SA 4.0 statement](https://hotpotqa.github.io/)
remain applicable references; see section 1 for citation/license requirements.
Neither the filename nor the checksum proves that this local download is an
independently authenticated canonical upstream release.

Resolved: exact input path availability, supplied-checksum integrity, JSON format
compatibility with the existing reader, and uncertainty about JSON/Parquet content
equivalence. A Parquet adapter is unnecessary to inspect this JSON with the
existing reader. **Unresolved:** strict sentence/support validation failures,
independent upstream provenance/revision and a complete exposure inventory.
Proposed 100-development/200-internal-holdout roles remain unverified. No role
eligibility, prepared dataset release or Phase 5.2 completion is claimed.

Only the four authorized documents changed. No source repair, code change,
download, dependency install, split, manifest, projection, derived dataset,
retrieval experiment, research result or Phase 5.3 work. Audit diagnostics are
temporary outside the repository, not dataset artifacts. No pytest run was
needed because there were no code changes; the real-file parse, structural
checks, reader rejection and cross-source comparisons are the audit evidence.
No meaningful bug was fixed, so no new Obsidian error note was created.

Final preservation checks: all three raw SHA256 values unchanged; all starting
project files outside the four authorized documents unchanged, with no missing
or new nonignored paths. `git diff --check` passed; the four documents also passed
direct trailing-whitespace and balanced-fence checks, including the untracked
protocol file.

**Phase 5.2 remains blocked.** Recommended next single action: investigate the
source history of record `5ae61bfd5542992663a4f261` and its index 902 against a
traceable official release, without modifying local data, to establish evidence
for a later explicit sentence/support handling policy.

## 13. Read-only index-902 provenance trace

The targeted investigation reproduced ID `5ae61bfd5542992663a4f261` directly in
raw JSON and Parquet, before EAR-RAG normalization. Question: "Which teams did
Jimmy Butler play and what role did he play on these teams?" Answer: `swingman`;
type `bridge`, level `hard`. Supports, in order:
`["Shooting guard", 4]`, `["Shooting guard", 5]`,
`["Jimmy Butler (basketball)", 0]`, `["Jimmy Butler (basketball)", 902]`.
The Jimmy Butler context is candidate position 7 (zero-based), containing five
sentence strings. Index 902 occurs only at `/supporting_facts/3/1` in this record,
not in another field or context text. There are 64 sentences across all ten
candidates, so 902 is not a valid flattened sentence position either. The
anomalous ID is absent from the 500-question fullwiki sample; that sample cannot
independently validate this particular annotation.

### Local code and bounded reproduction

`data/hotpotqa.py:read_hotpotqa` decodes JSON without index conversion;
`_normalize_record` rejects index 902 using the exact title's sentence count,
before invoking the normalizer. Direct raw JSON/Parquet context and support
equality was rechecked. There is no production HotpotQA Parquet reader here;
previous comparison used read-only equal-length parallel-array mapping.

`DatasetNormalizer.normalize_hotpotqa_record` copies the support list through
`_json_value` (serializability check, not conversion). `_join_sentences` retains
every sentence, including empty ones, and creates character offsets rather than
rewriting support indices. In-memory reproduction preserved the source object,
the support list containing 902 and five Jimmy Butler sentence spans. Strict
validation rejected `supporting_facts[3]`. The normalizer can carry an invalid
source annotation forward; it was not observed creating it. Git history locates
this copy/join behavior at local commit `b346353`; raw sources are not tracked,
and no download/conversion chain linking them to an official release was found.

The generic document preprocessor collapses whitespace/drops empty documents
later, while demo support resolution operates at title level and ignores
sentence IDs. Those paths can lose sentence-level fidelity or fail to detect an
invalid ID; they do not explain a literal 902 already present in these raw files.
Python 3.12.4 / installed PyArrow 25.0.1 were used; the existing Parquet producer
metadata says Arrow 21.0.0. Those versions alone do not establish creation history.

### Identifiable external evidence and its limits

[Official-repository issue #47](https://github.com/hotpotqa/hotpot/issues/47),
opened by `Ghost---Shadow` on 2023-12-20, independently reports this exact ID,
question, answer, four support references and five Jimmy Butler sentences.
It is a third-party issue in the official project, not a maintainer-certified
release or provenance record; no exact source/config/revision is specified.
Thus the anomaly is **corroborated by an upstream report**, not independently
reproduced from a pinned official dataset release in this investigation.

Read-only `git ls-remote` identified official `hotpotqa/hotpot` master as
`3635853403a8735609ee997664e1528f4480762a`. The pinned
[README](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/README.md),
[download script](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/download.sh)
and [preprocessor](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/prepro.py)
were inspected, not executed. They define paragraph-local zero-based support
indices and link the external `curtis.ml.cmu.edu/datasets/hotpot/` dev v1 JSON.
The code commit pins those instructions, not the external data bytes: no dataset
checksum is supplied by that download script. The upstream preprocessor consumes
support tuples and enumerates paragraph sentences; its downstream token/span
conversion does not establish how the raw 902 annotation was created.
GitHub API access returned HTTP 403 rate limiting; public pages/raw code remained
readable and Git remote inspection supplied the code commit. No full dataset or
unversioned mirror record was downloaded as a substitute for a pinned release.

### Blank-sentence comparison and conclusion

Only three prior blank examples were inspected for shared mechanisms, not all 49:

| ID | Candidate title | Empty-string sentence index / sentence count |
| --- | --- | --- |
| `5a7320565542991f9a20c61d` | 1989 Houston Oilers season | 10 / 11 |
| `5abbd3ac55429931dba1458b` | Gulfstream Natural Gas Pipeline | 3 / 4 |
| `5a72c6f65542994cef4bc402` | Pandanus conoideus | 5 / 6 |

Each empty string already exists in raw JSON and is not referenced by that
record's supporting facts. The old normalizer retains a zero-length sentence
span at that position; the strict reader rejects it. There is no observed title
misalignment, index renumbering or sentence filtering causing either raw symptom.
No shared origin for the blanks and index 902 is established. Earlier source
annotation, paragraph extraction or shared upstream transformation remain
unresolved hypotheses, not verified causes.

Verified: invalid annotation in local inputs, local preservation/rejection
behavior and a historical report in the official repository. Unverified:
membership in an authenticated immutable official release, first introduction,
correct intended index and the producing process. No handling policy or repair
was selected. Next single step: obtain a maintainer-confirmed, revision-identified
excerpt for this record (with release identity/checksum) to close the release
provenance gap. No contact was sent during this investigation.

Only this protocol and the handoff were updated to record these factual findings;
no code/raw/derived data changes, experiment, split or Phase 5.3 work. Targeted
in-memory checks replace a pytest run because nothing executable changed. No
qualifying bug was fixed, so no new error-log note was created.

Final preservation check for the index-902 trace: all three raw file hashes and
every starting project file outside its two documents were unchanged, with no
missing/new nonignored paths. Diff and direct document checks passed.

## 14. Phase 5.3 corpus/evidence layer

**Scoped implementation complete; Phase 5.2 real preparation partially blocked.**
The new request authorizes corpus/evidence tooling while provenance remains
unresolved. It does not authorize data repair, split preparation, controller
evaluation-driver integration, research experiments or Phase 5.4. Earlier phase
plans/status entries describe their historical scope; this section records what
is now implemented.

### Inspection and strict release contract

`ear_rag.data.hotpotqa.inspect_hotpotqa(path, source_split=..., setting=...,
source_id=...)` shares the existing strict record validation and returns
`HotpotQAInspection`. Its `examples` are individually normalized offline
diagnostics; `report` returns a copy of counts, source checksum, duplicate IDs,
errors and `record_errors`. Each record error has zero-based `position`, original
string `question_id` (or None) and the first strict `reason`. This is not an
exhaustive list of every defect within a malformed record. File-level JSON/key/
encoding/empty-input failures still raise; they cannot provide partial records.

`inspection.require_valid()` returns `HotpotQADataset` only when the entire input
passes. `read_hotpotqa` now calls this shared path, retaining all original strict
rules and count semantics. An earlier occurrence of a duplicate ID can appear in
diagnostic examples, but the duplicate blocks release of the entire file. No
filtered dataset constructor or automatic anomaly policy was added. Editing a
returned diagnostic report does not clear the inspection's internal failure.

The known 49 blank-sentence records and index-902 record are still invalid. No
validation rule was weakened and no real source was released or prepared here.

### Corpus and source mapping contracts

`ear_rag.data.hotpotqa_evidence` adds:

| Interface | Contract |
| --- | --- |
| `build_question_corpus(dataset, question_id)` | Requires `HotpotQADataset`, rejects diagnostic inspections and missing/ambiguous question IDs; returns one question's candidates without pooling other questions |
| `HotpotQACorpus.query` / `.documents` | Fresh core `Query` / tuple of `Document` objects, directly consumable by existing backends, with allowlisted runtime metadata |
| `HotpotQACorpus.source_documents` / `.source` | Existing normalized candidate records retain exact text and sentence spans; offline source identity/checksum/split/setting/authenticity remain available |
| `locate_evidence(corpus, chunks)` | Resolves chunk document IDs and character windows against canonical source text, returning `EvidenceLocation` records |
| `match_supporting_evidence(dataset, corpus, chunks)` | Offline label join with exact source/question/document checks, returning `SupportingEvidenceMatch` sets |

The normalizer's local IDs `hotpotqa:<question_id>:<context_position>` are reused,
not replaced with globally unique Wikipedia identifiers. Source checksum plus
setting scopes comparisons across input artifacts. Candidate and sentence order,
exact sentence text and source question IDs remain intact. Existing offline
dataset records retain answers and support annotations; neither those annotations
nor arbitrary metadata are copied to runtime queries/documents. Checksums stay
offline so changing labels alone cannot change runtime views. Runtime objects
are fresh copies; modifying their metadata does not corrupt the canonical map.

Corpora are in-memory adapters, not persistent indexed datasets. Callers must
index only the selected question's documents before using an existing backend.
Multi-hop wraps an already indexed leaf, as before. No ranking, fusion, hashing,
multi-hop policy, chunking, router, ESA or controller code changed. The vector
backend remains the existing deterministic hashed-token Flat stand-in.

### Evidence and support semantics

`EvidenceLocation` contains chunk/document/question IDs, original context position
and title, actual returned-text character bounds, overlapping sentence indices
and single-chunk complete sentence indices. Positions are zero-based Python
character offsets, not byte/token offsets. The resolver accounts for the current
chunker's boundary `.strip()` without modifying that chunker. Unknown documents,
missing/bool/out-of-range offsets and mismatched text raise explicit errors;
there is no fuzzy lookup or reliance on claimed titles/sentence IDs in chunk
metadata. Later document preprocessing that changes text requires a separate
alignment map and is not silently accepted by this resolver.

Support matching unions the verified text intervals per source candidate.
Overlapping/adjacent intervals and whitespace-only gaps can cover a sentence
collectively. Every non-whitespace source character of a sentence must be
covered; partial sentence overlap alone never counts as complete support.
The result reports `retrieved_sentences`, `matched_supports`, `missing_supports`
as sets of `(exact title, sentence_index)`, and `matched_support_titles`
separately. Duplicate annotations/chunks count once. This is exact evidence
coverage, not semantic entailment, answer generation or a computed research
precision/recall result. A title match cannot be substituted for sentence support.

### Verification and remaining limits

Synthetic tests cover valid normalization/provenance, stable IDs and deterministic
corpus construction, unknown questions, diagnostics/missing/duplicate IDs, blank
sentences/index 902 rejection, immutable source bytes, isolated runtime metadata,
source/question mismatches, wrong/partial sentences, combined/overlapping coverage,
Unicode offsets, chunk trimming and forged chunk metadata. Compatibility checks
exercise the existing lexical, vector Flat, hybrid and multi-hop implementations
using only synthetic temporary inputs; they are not effectiveness experiments.

Commands using the existing environment:

```powershell
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_ingestion.py tests/test_hotpotqa_evidence.py tests/test_hotpotqa_splits.py tests/test_dataset_normalization.py -q
.\ai-proj-new\Scripts\python.exe -m pytest -q
.\ai-proj-new\Scripts\python.exe -m mypy src/ear_rag/data/hotpotqa.py src/ear_rag/data/hotpotqa_evidence.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir "$env:TEMP\ear-rag-phase53-mypy"
```

Results: **95 passed in 1.28s** focused; **349 passed in 3.17s** full suite, no
failures/skips; mypy passed both source modules. Baseline was 318 tests; 31 new
synthetic cases were added. Expected initial missing-API/module red tests are
part of feature development, not resolved reliability bugs or error-log entries.

A read-only `inspect_hotpotqa` call on the existing real JSON also confirmed
7,405 total / 7,355 diagnostically accepted / 50 rejected and malformed / zero
duplicate IDs. Diagnostics identify 49 blank-sentence records and the index-902
record at zero-based position 5,059. `require_valid()` raises as required. This
check did not construct a real corpus, projection or filtered evaluation dataset.

Remaining real-data gates: explicit sentence/support anomaly policy, independent
upstream release provenance and complete exposure history. All known 500 exposed
questions remain exposed; no unseen status is asserted for the other 6,905.
The 100/200 proposal remains provisional. Role locks/manifest verification,
controller/evaluation-driver integration and metric aggregation remain future
work. No splits, manifests, real runtime/label projections or prepared corpora
were created; no research scores, thresholds or costs were tuned. No dependency
was added, no raw file modified and no Phase 5.4 work started.

Final hash comparison against the Phase 5.3 starting baseline confirms all three
raw files and all earlier project work outside the intended edits unchanged.
Only hotpotqa.py, its ingestion tests and four project documents changed among
baseline files; the evidence module and its tests are the only new paths. No
baseline files were removed. `git diff --check` and direct whitespace/fence checks
passed, including untracked files. No qualifying resolved bug; no new vault note.

## 15. Phase 5.4 evaluation infrastructure and metrics

**Scoped infrastructure complete; no effectiveness run or final benchmark.**
`ear_rag.control_evaluation` reuses Phase 5.3 corpus/evidence interfaces and the
existing controller. Pure `supporting_document_metrics` was extracted from the
legacy `evaluation_metrics.retrieval_metrics`; legacy cost/utility outputs remain
unchanged. The new driver avoids its mandatory-call/default-zero-latency
assumptions. No selection, scoring, ESA or recovery semantics changed.

### Interfaces and label boundary

| Interface | Contract |
| --- | --- |
| `EvaluationCase(question_id, exclusion_reason=None)` | Explicit request or exclusion with a nonblank reason; no automatic anomaly policy or split selection |
| `evaluate_cases(dataset, cases, pipeline_factory, initial_backend=...)` | Takes a fully validated `HotpotQADataset` and explicit ordered cases; returns per-case records and aggregate |
| `supporting_evidence_coverage(match)` | Fraction of unique annotated sentences completely covered under the Phase 5.3 contract |
| `aggregate_cases(records)` | Reconciled status counts, conditional quality/control rates, backend selection and observed work |
| `write_evaluation_report(report, directory)` | Version-checks/pre-serializes and writes per-case JSONL plus aggregate JSON into a new directory only |

Ingestion remains separate: use `inspect_hotpotqa` for diagnostics, not automatic
partial release. `build_question_corpus` supplies one candidate pool at a time.
The caller factory receives only fresh runtime documents and must build a fresh
pipeline per case; `run` receives only the runtime query. No answer, gold facts,
dataset or offline corpus is passed to runtime components. Caller factories must
respect this dependency-injection contract. After runtime returns, the driver
snapshots retrieval/control traces, resolves source locations with
`locate_evidence`, then joins labels with `match_supporting_evidence`. No raw
answers or full gold-label lists are copied into the new report.

### Metrics and denominators

For each evaluated question, G is the set of annotated supporting document IDs
and S the set of annotated `(exact title, sentence index)` pairs. Quality uses
the **first five returned chunks**, in backend order, not five distinct documents.

| Per-stage field | Definition |
| --- | --- |
| `hit_at_5` | Whether any of those chunks belongs to G |
| `supporting_document_recall_at_5` | Unique documents from G hit / size of G; repeated chunks count once |
| `supporting_evidence_coverage_at_5` | Completely covered unique facts from S / size of S, combining verified chunk ranges within this stage |

Initial metrics use initial retrieval. Terminal metrics use **recovery alone**
when present, otherwise initial retrieval, matching terminal ESA context. Never
union initial/recovery evidence for terminal quality. Title hits and partial
sentence overlap do not imply full sentence support. Per-stage records retain
support-document/fact denominator and matched counts. With nonempty labels,
empty evidence gives zero quality. Empty/no usable labels give null quality;
pure helpers support that edge case, but the strict reader still rejects empty/
missing support annotations and blind-test inputs.

Aggregate quality is a macro mean over evaluated cases with defined values,
separately for initial/terminal. Each summary has `observed`, `missing`, `total`,
`mean`; empty samples have null total/mean. Binary hit totals are hit counts;
recall/coverage totals sum case fractions rather than pooling gold denominators.
Initial backend frequencies use actual routed selections (or requested backend
when routing is disabled), divided by evaluated cases. Recovery-trigger and
abstention rates expose numerator/denominator/rate, with evaluated denominators.
Recovery count sums executed stages, at most one per case in this controller.
Initial/terminal ESA decision counts are separate; sufficiency is not correctness.
Final state `generate` means sufficient evidence, not an answer was generated.

Failure/exclusion rates divide by all requested cases. Every request has a row:
`requested = evaluated + failed + excluded`. Duplicate requested IDs fail without
dispatch. Errors retain stage/type/message; exclusions retain ID/reason. Any
failure/exclusion sets `partial=true`. Quality, control rates and backend
frequencies are conditional on evaluated cases, not silently complete results.
Failed offline joins retain captured work; if `run` raises without returning a
trace, partial work is unknown rather than invented or counted as abstention.

### Work availability and timing

| Field | Meaning |
| --- | --- |
| `retrieval_calls` | Explicit per-invocation child/hop calls; absent is null, and cumulative `retrieval_call_count` alone is insufficient |
| `returned_chunks` | Observed result lengths, initial plus executed recovery, without metric cutoff |
| `retrieved_passages` | Reported child/hop retrieved passages, including those not kept in final context; missing is null |
| `processed_chunks` | Only an explicitly reported counter; existing backends do not report scanned/processed chunk counts |
| `retrieval_latency_ms` | Reported backend latency, summed only when every executed stage supplies it |
| `routing_latency_ms` | Existing routing decision latency; zero when routing is disabled |
| `controller_latency_ms`, `monetary_cost` | Null: controller wall time and actual monetary cost are unmeasured |

Counts must be finite nonnegative integers; timing must be finite/nonnegative.
Invalid measurements fail explicitly; known zero stays zero. Missing any stage
makes its case total null, with known stage values retained. Controller default
zeros and expected-cost estimates are not substitutes for measurements.
Work summaries include all nonexcluded cases, including failed cases with known
work, and expose observed/missing case counts plus observed-only totals/means.
Totals are incomplete whenever observations are missing. Retrieval latency
excludes loading/indexing, routing and ESA; ESA timing is unavailable. No new
wall timer, repeat, percentile, comparison or confidence interval was implemented.
Real timing varies; order/accounting/serialization are deterministic for identical
observations, as verified by fixed-timing synthetic repeated runs.

### Versioned schema and serialization

Version is `ear_rag_control_evaluation_v1`. Driver result keys are
`schema_version`, `per_case`, `aggregate`. Every row has the same top-level keys:

```text
schema_version, case_index, question_id, source, status,
requested_initial_backend, initial_backend, initial, terminal,
control, work, error, exclusion_reason
```

Source retains dataset identity/hash/split/setting/authenticity offline. Stages
are null until available, otherwise contain retriever name, requested k,
retrieval metadata, work, chunks and metrics. Chunk entries retain IDs, score,
backend and source location (question/context/title, actual character bounds,
overlapping/complete sentence indices). Control retains assessments, recovery
and routing decisions, trigger/count, final state and abstention. Error is null
or `{stage, type, message}`. Exclusion reason is nonnull only for excluded rows.
Aggregate retains version, counts/partial/scope, both quality summaries, backend
frequencies, recovery rate/count, abstention/failure/exclusion rates, initial/
terminal ESA counts and work summaries. Unknowns are JSON null, not omitted.

`per_case.jsonl` and `aggregate.json` use UTF-8/LF, sorted keys and finite JSON.
Writer refuses unsupported versions/existing destinations and serializes before
touching disk. A later disk failure can leave an incomplete directory; no
manifest is published. Legacy JSON/CSV reporting is untouched. These reports
do not certify benchmark configuration freezes, role locks or full provenance.

### Proposed initial-release anomaly policy - not applied

Historical Phase 5.4 proposal: section 16 now implements and audits policy v1.
No filtered dataset or evaluation approval is created by that policy audit.

Propose excluding the 49 blank-sentence records and the single out-of-range
support-index record. Preserve raw files and original indices; never remove
sentences, clamp/remap supports or weaken validation. Future application must log
every excluded original ID, source identity/checksum and reason. Explicit
`EvaluationCase` exclusions support an audit trail but do not discover/apply this
proposal. No real exclusions, filtered dataset or split/manifest were produced.
All remaining records are eligible for **subsequent validation only**, not
automatically cleared for evaluation. Provenance, complete exposure history and
100-development/200-holdout allocation remain unresolved; the known 500 exposed
questions remain exposed. Any approved filtered-source preparation is separate.

### Verification and status

```powershell
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_control_evaluation.py tests/test_initial_evaluation.py tests/test_evaluation_validation.py tests/test_hotpotqa_evidence.py -q
.\ai-proj-new\Scripts\python.exe -m pytest -q
.\ai-proj-new\Scripts\python.exe -m mypy src/ear_rag/control_evaluation.py src/ear_rag/evaluation_metrics.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir "$env:TEMP\ear-rag-phase54-mypy"
```

Focused: **85 passed in 1.05s**; full: **381 passed in 3.61s**, no failures/skips
(baseline 349); scoped mypy passed both changed modules. The 32 new synthetic
tests cover multi-document/sentence metrics, cutoff/deduplication, empty labels,
zero denominators, multi-case macro/rate accounting, label isolation, recovery-
only final evidence, failures/exclusions, missing/partial/legacy work counters,
known zero/invalid measurements, real four-backend/routed compatibility, stable
schema/serialization and overwrite refusal. No ignored data or network required.
These are code regression results, not effectiveness or answer EM/F1. No real
evaluation run, download/install/contact, training/router labels, tuning,
generation, commit or Phase 5.5 work. Phase 5.4 is complete; Phase 5.2 real
preparation remains partially blocked. No qualifying bug fixed; no error note.

Final preservation review confirms all three raw SHA256 values unchanged and
every baseline file outside the four authorized documents and the pure metric
extraction unchanged. Only the driver and its synthetic test file were added;
no baseline files removed. Final diff review, `git diff --check` and direct
whitespace/fence checks passed, including untracked files. Existing user work
was retained without reset, stash, clean or commit.

## 16. Phase 5.2 auditable invalid-record policy

**Policy/audit implementation complete; real preparation still partially blocked.**
`ear_rag.data.hotpotqa_policy` defines policy
`hotpotqa_initial_release_invalid_records_v1` and report schema
`hotpotqa_policy_audit_v1`. It classifies the initial-release exclusions without
changing strict ingestion, modifying records or releasing a filtered dataset.

### Rules, reuse and disjoint classification

- `blank_candidate_sentence`: a candidate sentence string is empty or whitespace
  only, using the same `.strip()` criterion as strict validation.
- `support_sentence_index_out_of_range`: a non-bool integer support index is
  negative or >= the sentence count of its uniquely resolved, valid context title.
  Never convert, clamp or guess an index, resolve ambiguous titles or drop text.
- Reuse the existing `_normalize_record` strict validator and duplicate-key/
  nonfinite JSON hooks. An additional complete scan collects every instance of
  both policy predicates; it does not infer membership from first-error text.
  The existing strict error is also retained, but is still only its first error,
  not an exhaustive diagnosis of unrelated annotation/schema defects.

Each parsed record belongs to exactly one group:

| Count | Definition |
| --- | --- |
| `valid` | Existing strict per-record validation passes, with a usable unique ID; **not evaluation approval** |
| `excluded` | Identity is reliable and policy structures/bounds are classifiable, with at least one exclusion finding |
| `otherwise_invalid` | Any remaining invalid or unclassifiable record; disjoint from the first two groups |
| `unclassifiable` | Subset of otherwise_invalid with missing/nonstring/blank/duplicate IDs or incomplete policy structure/bounds; not a fourth additive group |

Thus total=valid+excluded+otherwise_invalid. Ambiguous identity or structure takes
precedence over exclusion, preserving any decidable policy findings on the
otherwise-invalid row instead of inventing a reliable ID/bound. All occurrences
of duplicate IDs are flagged, not just later ones. Other strict failures, such as
blank answers, remain otherwise invalid and are not new policy exclusions.
Multiple defects/facts in a record retain all applicable policy reason codes and
all instance details, while counting the record once. Per-code exclusion counts
count records once per code and may overlap; never sum them as a record total.

### API, reproducibility and machine-readable report

`audit_hotpotqa_policy(path)` reads one byte snapshot and returns JSON-compatible
diagnostics, not a dataset or approved-ID list. Source contains filename, SHA256,
size and expected format. Root fields include schema/policy versions, status,
definitions, disjoint counts, per-code exclusion counts, excluded and otherwise-
invalid record lists, unclassifiable positions and `evaluation_approval` set to
`not_granted`. Each nonvalid row contains original string ID (or null), zero-based
source position, classification/reliability, sorted reason codes, all policy
instance details and the first existing strict-validation error.

Blank details identify context/title/sentence position and original blank value;
index details identify support position/title, raw integer, sentence count and
valid bounds. Missing IDs, duplicate IDs and incomplete checks receive explicit
reason codes/details. Valid records are counted, not exported as eligible IDs.
Unreadable files raise. Unsupported/unparseable files return `file_error` with
unknown counts; an empty array has known zero counts but is still a file error.
No unknown record counts or classifications are fabricated.

`write_policy_audit(report, output)` emits sorted, finite UTF-8/LF JSON using
exclusive new-file creation. It cannot overwrite any existing report or raw file.
No timestamps, absolute paths or nondeterministic ordering enter the report.
Identical bytes/filename under the same versioned implementation produce equal
reports; changed source bytes change its checksum even for whitespace-only edits.
Changes to classification semantics require a new policy version. This binds the
audit to local bytes, not to an authenticated upstream release or exposure status.

Actual real-source command (output must not already exist):

```powershell
.\ai-proj-new\Scripts\python.exe -m ear_rag.data.hotpotqa_policy data/raw/hotpotqa/hotpot_dev_distractor_v1.json --output docs/hotpotqa_invalid_record_policy_audit_v1.json
```

For repetitions use a new destination or compare `audit_hotpotqa_policy` in
memory. CLI exits 2 on file-level errors or output/I/O errors; record-level
exclusions/otherwise-invalid rows remain explicit audit results, not repairs.

### Verified current-source result and remaining gates

The [complete audit report](hotpotqa_invalid_record_policy_audit_v1.json) lists
every excluded ID/position/reason/detail. Current source is
`hotpot_dev_distractor_v1.json`, **46,320,117 bytes**, SHA256
`4e9ecb5c8d3b719f624d66b60f8d56bf227f03914f5f0753d6fa1b359d7104ea`.
Observed: **7,405 inspected; 7,355 valid; 50 excluded; zero otherwise invalid or
unclassifiable**. There are 49 blank-sentence records and one out-of-range-index
record, with no overlap in this source. Index-902 ID is
`5ae61bfd5542992663a4f261`, zero-based source position 5,059, title
`Jimmy Butler (basketball)`, five sentences, valid indices 0-4.
Repeated in-memory audit equals the saved report exactly. Excluded IDs also agree
with a separate call to the existing strict inspector; counts were not assumed.

The policy is implemented and applied to **audit classification only**. No raw
record was changed, excluded from a generated dataset or automatically approved.
All passing records remain eligible only for subsequent preparation checks.
Independent source provenance, complete exposure inventory, allocation/approval
and the 100/200 proposal remain unresolved. The known 500 exposed questions stay
exposed; no unseen status is granted to the other 6,905. Strict ingestion still
rejects the unchanged full input. No splits/manifests, projections or evaluation
experiments, ESA/recovery/retrieval changes or Phase 5.5 work were performed.

Verification commands:

```powershell
.\ai-proj-new\Scripts\python.exe -m pytest tests/test_hotpotqa_policy.py tests/test_hotpotqa_ingestion.py -q
.\ai-proj-new\Scripts\python.exe -m pytest -q
.\ai-proj-new\Scripts\python.exe -m mypy src/ear_rag/data/hotpotqa_policy.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir "$env:TEMP\ear-rag-policy-closure-mypy"
```

Focused: **71 passed in 1.03s**. Full: **406 passed in 4.15s**, no failures/skips,
from baseline 381; scoped mypy passed. The 25 new synthetic tests cover the
49-blank pattern, index 902, overlapping/repeated defects, missing/duplicate IDs,
uncertain bounds/structures, other strict failures, file errors, determinism,
checksum changes, serialization/CLI and raw immutability/overwrite refusal.
They require no ignored dataset. No qualifying bug was fixed; no new error note.

Final SHA256 preservation check confirms all three raw sources and every baseline
project file outside the four authorized documents unchanged. Only policy source,
synthetic tests and the real audit report were added; no baseline files removed.
`git diff --check` and direct whitespace/fence checks passed, including untracked
files. Earlier user changes were preserved without reset, stash, clean or commit.


## 17. Phase 5.5C minimal baseline condition runner

`ear_rag.condition_evaluation.evaluate_conditions(dataset, cases, config, *,
conditions=CONDITIONS)` is a small orchestration API, not a benchmark CLI or an
input-approval gate. It requires an explicit strictly validated HotpotQADataset,
EvaluationCase sequence and complete JSON-compatible configuration (the shape of
configs/config.yaml). Unknown or duplicate condition names raise before dispatch.
The default order and definitions have version `ear_rag_conditions_v1`.

| Condition | Initial selection | Recovery |
| --- | --- | --- |
| `fixed_local_lexical_no_recovery` | Forced local_lexical, selector bypassed | Disabled |
| `fixed_vector_flat_no_recovery` | Forced vector_flat, selector bypassed | Disabled |
| `fixed_hybrid_no_recovery` | Forced hybrid, selector bypassed | Disabled |
| `fixed_multihop_no_recovery` | Forced multihop, selector bypassed | Disabled |
| `query_aware_no_recovery` | Existing configured query selector, enabled | Disabled |
| `adaptive_controller` | Existing configured query selector, enabled | Supplied recovery configuration |

These use the current prototype backends: BM25-inspired local lexical, hashed
vector-flat, weighted hybrid and bounded lexical multi-hop. They do not add
learned dense retrieval or query decomposition. Fixed conditions set
query_analysis.enabled=False and retrieval.backend to the stated backend.
Other conditions explicitly enable the configured selector, even if the caller
had disabled it. All no-recovery conditions set max_recovery_rounds=0, using the
existing policy guard. Adaptive preserves all recovery settings, including a zero
limit if supplied. Existing pipeline semantics permit at most one recovery even
when that configured limit exceeds one; every recovery is reassessed, and the
last assessment determines generate/abstain (no answer generation occurs).

The caller's configuration is detached, never mutated. Top-k, max-top-k,
chunking, vector dimensions, hybrid weights, hop limits and ESA settings are
shared unchanged. Factories build fresh indexes, assessor, policy and controller
for every requested question and condition; there is no cache across cases.
Candidate pool definition `question_scoped_source_context_v1` means the exact
same source question's supplied paragraphs, through build_question_corpus.
This API does not support a global/full-Wikipedia pool. Each condition receives
the same ordered case list, including missing, duplicate and explicitly excluded
IDs. Underlying evaluation failures are retained with stage/type/message and
included in existing accounting, not removed from comparisons.

Only corpus.documents and corpus.query reach construction/dispatch. Gold answers,
support annotations and type/level remain within offline scoring. Source identity
and checksum are retained in the existing per-case source record. Condition,
condition_version, candidate_pool and full effective configuration are additive
fields on each row and aggregate. The returned mapping holds one existing-format
report per condition; no new metric, aggregation or file writer was introduced.
Existing metrics and missing-cost semantics remain those in section 15. Repeated
runs have deterministic condition definitions and output structure; measured
latencies naturally vary and are not promised byte-identical.

Usage after independent input approval, with already supplied in-memory inputs:

```python
from pathlib import Path
from ear_rag.condition_evaluation import evaluate_conditions
from ear_rag.control_evaluation import write_evaluation_report

reports = evaluate_conditions(dataset, cases, config)
for condition, report in reports.items():
    write_evaluation_report(report, Path(output_directory) / condition)
```

The existing writer refuses existing result directories. This example does not
load, approve or prepare real inputs; no such experiment was executed here.

Verification used synthetic temporary JSON fixtures exclusively. Seventeen new
tests prove fixed backend dispatch, selector bypass, no-recovery guards, adaptive
limits/reassessment (limits 0/1/3), identical pools/settings/top-k, fresh backend
and pipeline objects, immutable caller configuration/raw synthetic input, runtime
independence from changed gold annotations, retained failures/exclusions and
duplicate IDs, stable definitions/structure, and existing serialization round-trip
and overwrite refusal. The whole suite remains software verification, not
research evidence. No novel or effective retrieval behavior is claimed.

Exact final verification commands:

```powershell
.\ai-proj-new\Scripts\python.exe -m pytest -q tests/test_condition_evaluation.py tests/test_control_evaluation.py
.\ai-proj-new\Scripts\python.exe -m pytest -q
.\ai-proj-new\Scripts\python.exe -m mypy src/ear_rag/condition_evaluation.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir "$env:TEMP\ear-rag-phase55c-mypy"
git diff --check
```

Focused: **49 passed in 0.93s**. Full: **423 passed in 4.31s**, no failures/skips
(baseline 406 in 4.25s). Scoped mypy passed one module. Initial new-test import
failure was expected before implementation; a test assertion used the wrong
source checksum key and was corrected to the existing source.sha256 contract.
No qualifying resolved bug or new Obsidian error note.

Phase 5.5C orchestration is implemented; Phase 5.5 is not complete. No real-data
benchmark, effectiveness experiment, split, manifest, router labels/training,
threshold/policy/objective tuning, answer generation, download or maintainer
contact occurred. All existing retrieval/controller behavior and prior work were
preserved. The real-data blockers remain independent pinned source provenance,
a complete genuine exposure inventory and approved split validity/allocation.
All 500 known sample questions remain exposed; the other 6,905 are not certified
unseen. The 100/200 proposal remains provisional. Policy audit v1 does not approve
the 7,355 passing records, and strict full-source ingestion still rejects the
50 anomalous records; policy-aware preparation remains separate future work.

## 18. Phase 5 status reconciliation (2026-10-22)

### Completion decision against the original requirements

**Phase 5 remains PARTIALLY COMPLETE.** No additional runtime implementation was
needed in this reconciliation: inspection verified the existing CAS path and
fresh synthetic checks passed. The original data-role/exposure safeguards in
section 2 and experimental comparison requirements in section 6 still apply.
Their completion cannot be inferred from passing software tests.

| Requirement / milestone | Verified current state | Remaining gate |
|---|---|---|
| Phase 5.1 dataset/protocol design | Complete as a design deliverable; per-question distractor pools and runtime/label separation specified | 100/200 proposal remains unapproved; no unseen-cohort claim |
| Phase 5.2 ingestion, split-validation and invalid-record policy | Software and recorded audits complete; policy-valid does not mean evaluation-approved | Independent provenance, complete exposure ledger and approved allocation still unresolved; no cleared holdout prepared |
| Phase 5.3 corpus/evidence | Implemented; source-window and supporting-sentence alignment tested | Full-Wikipedia retrieval remains a separately scoped extension |
| Phase 5.4 evaluation infrastructure | Implemented; stages, quality, work, failures/exclusions and abstentions recorded offline | Answer EM/F1 and full cost measurements remain unavailable, not invented zeros |
| Phase 5.5C six-condition orchestration | Implemented with isolated per-case state; current condition version ear_rag_conditions_v2_cas | Previous v1 result artifacts retain their original definition |
| Phase 5.5D development experiment | Scoped run complete for previous CAS: 500 requested, 497 evaluated, 3 excluded, 0 failures per condition | Known-exposed internal data only; not revised-CAS validation or a holdout |
| Phase 5.6 final analysis | Analysis complete — development/internal, known exposure; paired errors, ESA proxy limits and uncertainty retained | Analyzes the previous policy only; does not establish current-policy effectiveness |
| Revised deterministic suitability-aware CAS | Runtime implementation and software verification complete | A separately authorized, frozen revised-policy experiment is still outstanding |

The invalid-record audit's 7,355 structurally valid records are not automatically
approved. All 500 historical sample questions remain exposed; absence from that
sample does not establish that the other 6,905 questions are unseen. The specific
497-question development exception did not satisfy or waive the holdout gates.

### Current CAS and work definitions

The path is `RetrievalControlPipeline.run` -> ESA ->
`BoundedRecoveryPolicy.decide` -> `DeterministicRecoveryEstimator.estimate`:

```text
CAS(a) = (1-current_ESA) * S(a | current_state) / C(a)
C_raw(a) = .05*N_calls + .01*N_chunks + .001*L_ms
C(a) = max(C_raw(a), .05)
recover only if best eligible CAS > configured tau (currently 1.0)
```

Current ESA must be finite/in [0,1]. S is binary: missing literal query tokens,
duplicate normalized evidence, or fewer than min(k,2) chunks establishes the
supported gap for alternative lexical/vector/hybrid rankings. Multi-hop also
requires dependent=True in the existing router snapshot, >=2 hops, a nonempty
partial lexical result, and novel tokens among the first chunk's first eight
tokens. Otherwise the action is ineligible. These are observable proxies, not
semantic coverage or predicted success. See [full rules](deterministic_cas.md).

Allowed, callable, unattempted candidates are ranked by CAS with a fixed
lexical/vector/hybrid/multihop tie-break. Invalid/missing candidate work excludes
that action; no eligible candidate means stop. Recovery is at most one round,
followed by mandatory ESA reassessment and abstention if not sufficient.
Initial routing, metric definitions and runtime/gold-label boundaries are intact.

N_chunks is nominal final returned context chunks, not processed chunks or child
passages. Shipped nominal work is lexical/vector: 1 call, 5 chunks, 10 ms;
Hybrid: 2 calls, 5 chunks, 20 ms; Multi-hop: max_hops=2 call budget, 5 chunks,
20 ms, with possible early termination. Backend code was checked against these
call counts. Latency/chunks, coefficients, floor and threshold are uncalibrated
engineering assumptions in abstract work-cost units. Initial work is excluded.
Realized calls, chunks, child passages and latency are measured afterward and
remain separate. Indexing/controller/processed work and money are not measured.
No future ESA, expected gain, learned suitability or predictive cost model is used.

### Validation performed in this reconciliation

Commands from `C:\ear-rag`:

```powershell
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/test_deterministic_cas.py tests/test_phase_17_cost_awareness.py tests/test_phase_15_control.py tests/test_runtime_reliability.py tests/test_initial_pipeline.py tests/test_demo.py tests/test_condition_evaluation.py
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests
.\ai-proj-new\Scripts\python.exe -B -m mypy src/ear_rag/routing/cost_awareness.py src/ear_rag/routing/recovery.py src/ear_rag/routing/pipeline.py src/ear_rag/demo.py src/ear_rag/condition_evaluation.py --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir .mypy_cache/phase5-validation
git diff --check
```

Focused: **114 passed in 1.91s**. Full: **470 passed in 6.75s**. Scoped mypy:
**five source modules passed**. Existing coverage includes exact arithmetic,
strict equality rejection, all four suitability rules, deterministic ranking,
incremental accounting/cost errors, prior-attempt and availability exclusions,
limits, real composite calls, reassessment/abstention, routing and gold isolation.
No missing behavior justified another implementation or duplicate tests.

Read/hash-only checks verified all 25 entries in the previous experiment's
`final_artifact_checksums.json` and all 10 artifact entries recorded in the
analysis `validation.json`. The frozen old configuration still contains expected
gain, confirming the policy distinction. No benchmark or analysis script ran.
Historical frozen source hashes intentionally refer to the old runtime; they
must not be rewritten to match the new implementation.

### Next required evaluation gate

Before judging revised-CAS effectiveness, freeze its policy/configuration, source
hashes and v2 condition definitions against sections 6, 15 and 17. Explicitly
choose and authorize the data scope: a known-exposed development/internal run
would remain diagnostic, while an exposure-cleared evaluation requires the
unresolved provenance/exposure/allocation evidence in section 2. Do not relabel
the existing 497 questions as unseen or treat missing exposure history as empty.

A future comparison must use identical ordered IDs/pools/labels/top-k across all
six conditions, retain failures/exclusions/paired denominators, and write to a new
output directory. No suitability, cost coefficient or threshold may be tuned on
the existing cohort by this task. Repeated timing requires its own declared
measurement design; nominal latency is not actual future latency.

This reconciliation creates no cohorts, manifests, splits or results. It closes
software verification and documentation reconciliation only. Revised-policy
research validation and the original clearance gates remain open; no novelty,
ESA calibration or hallucination-reduction claim is established. Answer generation
is still absent and remains a separately scoped capability under section 5.

## 19. Frozen revised-CAS diagnostic evaluation (2026-10-22)

The current request explicitly authorizes a development/internal comparison;
no exposure-cleared holdout is available. Scope and analysis were documented
before execution in [the frozen protocol](../outputs/phase5-revised-cas-development-internal-known-exposure-20261022T125412Z-0e6adb98/PROTOCOL.md)
and its adjacent scope.json/frozen_hashes.json. Label every result
**development/internal — known exposure**. Revalidated raw JSON: 7,405 records,
7,355 structurally valid for further review, 50 policy exclusions, zero otherwise
invalid/unclassifiable. The known 500 requests yield 497 strictly readable cases
and three explicit blank-sentence exclusions; no new split or clearance.

Run all six v2 conditions once with identical ordered requests, question-scoped
distractor contexts, annotations, top-k 5 and unchanged backend/ESA settings.
Fresh pipelines/indexes per case; gold labels remain offline. Fixed conditions
bypass routing; the first five disable recovery; adaptive retains one recovery
and mandatory reassessment. CAS, suitability, nominal costs and tau=1.0 are frozen.

Primary comparison: adaptive minus query-aware/no-recovery terminal supporting-
document Recall@5. Secondary: Hit@5, supporting-evidence coverage@5, the four fixed
baselines and measured calls. Macro quality includes abstentions; terminal evidence
is replacement evidence, not initial/recovery union. Retain all failures/exclusions.
Pair on common evaluated question IDs; report metricwise missing counts. Bootstrap
paired differences over question IDs with existing mean_interval: 10,000 resamples,
seed 1729, 95% percentile intervals. Secondary intervals are exploratory without
multiplicity correction; no unseen-generalization inference. Report all 15 pairs
descriptively, candidate eligibility/threshold decisions, recovery gains/ties/losses,
ESA/annotated-coverage disagreement and measured work separately from nominal CAS.

One fixed-order timing run excludes loading/index construction; controller overhead,
processed chunks and monetary cost are unavailable. No tuning, answer generation,
hallucination-reduction or novelty claim. Prior-policy outputs remain intact.
Execution and paired analysis are now **complete for this frozen diagnostic scope**.
The [new report](../outputs/phase5-revised-cas-development-internal-known-exposure-20261022T125412Z-0e6adb98/REPORT.md)
records exact commands, hashes, exclusions, six-condition results and limitations.
Every condition requested 500, evaluated 497, excluded the same three, and failed
zero. All 497 IDs pair across all conditions, with no missing quality values.
Adaptive versus query-aware/no-recovery: document recall +.015091 (95% paired
bootstrap [.005030,.026157]), evidence coverage +.015258 [.004192,.027331],
19 extra calls (537 versus 518). Versus fixed lexical, adaptive recall -.018109
[-.027163,-.009054], coverage -.018444 [-.027834,-.009725], and 40 more calls.

Recovery: 19/497 cases; 13 coverage improvements, three ties, three regressions;
16 become ESA-sufficient, three abstain. All 19 ranked cases exceed tau; none
are threshold-suppressed or have no eligible action. Lexical selected 17 times,
vector twice; Multi-hop ineligible in all 19 because dependency signal is absent.
Of 494 final sufficient cases, 257 have incomplete annotated coverage, including
25 with zero. These findings do not validate semantic sufficiency or calibration.

Verification: focused 114 passed (2.06s), full suite 470 passed (6.21s); 5,964 saved
stage metric/ESA replays, candidate arithmetic/eligibility checks, all paired
accounting and byte-reproduced analysis passed. Negative controls reject duplicate
or missing rows, mismatched top-k, forbidden recovery and missing reassessment;
a synthetic in-memory failure reduces pairing without being dropped. Runtime,
configuration, raw inputs and all 52 prior output files remain unchanged.
No thresholds, costs, retrieval/controller behavior, old results or splits changed.

Software and revised-CAS diagnostic evaluation are complete; overall Phase 5 is
still PARTIALLY COMPLETE under the original provenance/exposure/approved allocation
requirements. Known 500 remain exposed; remaining 6,905 are not certified unseen.
Next task requires actual acquisition/revision and project exposure evidence before
assessing a defensible cohort. Do not tune on this run and relabel it independent.
