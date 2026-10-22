# MuSiQue dataset audit and integration readiness — Part 1

## Phase 6B protected-test source check (2026-10-22)

Protected eligibility remains unverified. Fresh git ls-remote confirms official
HEAD922ac98f19a201998dbdae6d7f2887a5258dbdeb. Pinned README/download script/license,
evaluate_v1.0.py, metrics/support.py and .all_data_information.json were checked
via HTTPS source/metadata reads only; URLs, exact byte counts, SHA-256 hashes and
methods are in outputs/phase6b-protected-evaluation-audit-20261022T161807Z-7e19b0ef/official_source_checks.json.
No dataset/archive member was acquired in Phase 6B.

Newly verified distinction: the public OFFLINE evaluator exists, requires gold
answers/aliases/support flags/answerable, and computes answer/support F1 rather
than this project's Hit/Recall@5. The README describes hosted test submissions;
the linked Ans/Full leaderboard URLs returned browser fetch502 and local urllib
DNS failures. Operational hosted scoring/access was not verified; these failures
do not establish universal service shutdown. No submission/contact was made.
The pinned raw-data metadata lists train/dev and their variants, no test entry.
This bounded source check found no accessible verified labelled protected cohort;
it is not a claim that no test labels exist anywhere.

Only native train/dev and the known dev-equivalent derivative are local. The old
test probes are FIRST-RECORD schema observations, not a complete test audit.
No complete project test-exposure ledger was found in the repository/artifacts
searched; external historical use cannot be inferred absent. No final test IDs,
disjointness, paragraph overlap or exposure clearance were invented. All existing
raw bytes/previous experiment outputs remain protected. See the new report for
artifact/runtime verification, tests and the minimum access/evidence needed.

## Phase 6A official training acquisition addendum (2026-10-22)

The subsequent Phase 6A request authorizes fitting on official training data and
selection on development only. A new source member was acquired without changing
any previous source file: data/raw/musique/official_v1_0_train/musique_ans_v1.0_train.jsonl.
Size 241,046,755 bytes; SHA256
83a75b1e11e4e9bb8f8308e72ac40ca617ae4431b3a0d955b61cab259248490a;
ZIP CRC32 ffc3ec5d. Strict validation: 19,938 unique answerable/valid records,
zero excluded/unclassifiable. The new adjacent acquisition_manifest.json records
exact member/header/range/CRC/size checks, URL, timestamp and SHA-256.

Source is the same author-linked v1.0 Drive archive, pinned author repository
922ac98f19a201998dbdae6d7f2887a5258dbdeb, CC-BY-4.0. The pinned download_data.sh
and LICENSE were checked against their primary-source URLs. Used established
stdlib HTTPS ranges/raw-DEFLATE/CRC convention; only the 56,046,094 compressed
training-member bytes and its header/name were acquired. No upstream script,
gdown installation, full archive or test download. No author-signed canonical
archive hash was found; local byte integrity is not independent authenticity.

Official train/dev exact question IDs and NFKC/lowercase/whitespace-normalized
question overlap: zero. Decomposition ID overlap: zero. **3,696 normalized
paragraph texts are shared**, so query/component disjointness does not imply
corpus independence or exposure clearance. Existing 31 dev NQ decomposition-text
matches remain potential exposure indicators, not proof of training use. Complete
project exposure history, protected final test and verified official scoring
access remain unresolved. The 2,417 dev records are for selection, not final test.

Predeclared training protocol/output:
outputs/phase6a-router-development-20261022T155210Z-95732e1d/PROTOCOL.md.
Its acquisition script is acquire_train.py. Training/development completion and
results are recorded in that directory's report and current PROGRESS/handoff;
this addendum records verified acquisition/isolation facts only. Historical audit
and Phase 5 outputs below remain unchanged.

Date: 2026-10-22. Repository: C:\ear-rag.
**Recommendation: proceed with conditions for adapter development; do not approve
this file as an official or independent research test set.** Its bytes can be
identified at a pinned third-party revision, and its native paragraph annotations
are internally consistent. Official split lineage, transformation/licensing
details and project exposure clearance remain incomplete. No experiment ran.

## 1. File integrity and variant

Path: C:\ear-rag\data\raw\musique\test.json.
Only test.json exists in that directory; no local dataset card, conversion script,
official split manifest or license sidecar is present.

| Check | Observed result |
|---|---|
| Size | 64,122,182 bytes |
| SHA-256 | b8a2f97c09f666cccf9663550eab73bbecc72af4f44f75af15c84b646f49cc38 |
| Encoding/container | Strict UTF-8, no BOM; JSON array, not JSONL |
| Records / unique IDs | 2,417 / 2,417 |
| Duplicate IDs / JSON object keys | 0 / 0 |
| Non-finite JSON values | 0 |
| Missing required fields, inconsistent checked types, blank IDs/questions/answers | 0 |
| Answerable | 2,417 true, zero false |
| Hop counts from decomposition | 2-hop 1,252; 3-hop 760; 4-hop 405 |

All records have the same ten fields and types listed below. Zero malformed
records means zero failures under the native schema/relationship checks performed
here; it is not canonical-release authentication or evaluation approval.

**Variant:** positively identified third-party configuration small-musique_ans
(version label 1.1.0), with answerable-only, MuSiQue-Ans-like records and added
instruction/reasoning material. It is not a mixed answerable/unanswerable
MuSiQue-Full cohort. This does not prove exact membership in an official Ans split.

## 2. Source identity, lineage and licensing

Local Zone.Identifier records Internet-zone delivery from us.aws.cdn.hf.co.
Its Xet object hash is
5f77202db8a3d5e4295e145407bfe3f9986e0889c8f2e0b8346ce349d6b37e8a.
No repository referrer was retained.

A metadata-only source search identified **pensieves/musique-ans**, path
small-musique_ans/test.json, commit
**f4de5c0125186fe0f9a81b044afed3f5afb64265** (2024-09-26).
Its published LFS SHA-256 and size exactly match the local file; its published Xet
hash also matches the browser stream. This establishes byte identity to that
third-party revision, not authenticity as an unchanged official release.
[Provider commit and file pointers](https://huggingface.co/datasets/pensieves/musique-ans/commit/f4de5c0125186fe0f9a81b044afed3f5afb64265),
[revision-specific metadata](https://huggingface.co/api/datasets/pensieves/musique-ans/tree/f4de5c0125186fe0f9a81b044afed3f5afb64265/small-musique_ans?expand=true).

The provider's commit says its train/validation/test files were prepared from
MuSiQue-Ans **train and dev**. Its card maps this file to its own test split;
the official split assignment and transformation process are not documented by
a reproducible conversion script in the inspected source listing. Therefore
test.json must not be described as the official MuSiQue test release.
[Provider card at the pinned revision](https://huggingface.co/datasets/pensieves/musique-ans/blob/f4de5c0125186fe0f9a81b044afed3f5afb64265/README.md).

Official upstream: StonyBrookNLP/musique, observed HEAD
**922ac98f19a201998dbdae6d7f2887a5258dbdeb**.
Its download script identifies musique_v1.0.zip at Google Drive object
1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h, but supplies no checksum. This identifies an
official acquisition path; the archive was not downloaded and no canonical
dataset checksum was available in the inspected script. Hash equality between an
official JSONL and this augmented JSON array would not be expected: compare
per-ID core fields after an explicitly documented projection instead.
[Pinned official acquisition script](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/download_data.sh).

Licensing evidence differs: the provider card declares **CC BY-SA4.0**; upstream
explicitly declares **CC BY4.0**, supported by its license file. Record both
declarations; do not assert that upstream confirms the derivative's exact license
or that different declarations alone prove a violation. Attribution and provenance
of the added reasoning/statements/instructions are unexplained in the inspected
metadata. Clarify that chain before redistribution/research-release documentation.
[Official license](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/LICENSE).

## 3. Actual schema and runtime boundary

| Native field | Observed type / meaning | Intended access |
|---|---|---|
| id | String; question ID, including hop-shape prefix | Pairing/source identity; analyzer must ignore prefix |
| question | Nonblank composed question string | Runtime query text |
| paragraphs | Ordered list of objects | Runtime candidates after allowlist projection |
| paragraphs[].idx | Integer, unique within record; equals array position in every case | Stable paragraph identity |
| paragraphs[].title / paragraph_text | Nonblank strings | Runtime text and safe title metadata |
| paragraphs[].is_supporting | Boolean gold paragraph flag | Offline evaluator only |
| answer / answer_aliases | String / list of strings | Offline labels |
| answerable | Boolean, always true here | Offline label |
| question_decomposition | List of 2–4 steps: id, question, answer, paragraph_support_idx, raw_question, statement | Entirely offline |
| combined_paragraphs / reasoning / instruction | Nonblank strings, one shared instruction template | Exclude from runtime; preserve offline if needed |

There are **6,404 decomposition steps**. In **3,636**, question differs from
raw_question; precisely those raw questions contain numbered placeholders, while
the rewritten question strings contain none. Added statements and reasoning are
not evidence passages. Their production method was not verified.

For future canonical comparison, inspect official decomposition question versus
raw_question explicitly; do not assume the rewritten question preserves it.
The [official converter](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/raw_data_to_official_format.py)
defines the core paragraph/label schema and can remove labels for blind exports.

Sanitized representative records (zero-based positions; no answers or passages):

| Position | ID | Candidates | Supporting idx | Distractors |
|---:|---|---:|---|---:|
| 0 | 2hop__460946_294723 | 20 | 5,10 | 18 |
| 1179 | 3hop1__454441_55349_651302 | 20 | 0,7,9 | 17 |
| 1826 | 4hop1__93963_170667_443779_52195 | 20 | 3,11,13,14 | 16 |

First question preview: “Who is the spouse of the Green performer?”
This audit also inspected question previews at positions 1 and 2; preserve those
three inspected IDs as known schema-review exposure:
2hop__460946_294723, 2hop__252311_366220, 2hop__701895_752697.
Machine inspection covered the whole file; no independence clearance follows.

## 4. Candidate pools, joins and anomalies

**No additional distractor corpus is needed for bounded per-question evaluation.**
Every record supplies both gold-support and non-supporting candidate paragraphs.
A full-Wikipedia search experiment would be a different, separately scoped design.

| Count/check | Result |
|---|---|
| Candidate paragraphs | 48,315 total: 6,404 supporting; 41,911 distractor |
| Candidate-count distribution | 17: 2 records; 18: 5; 19: 9; 20: 2,401 |
| Supporting-count distribution | 2: 1,252 records; 3: 760; 4: 405 |
| Distractors per record | 14–18 |
| Missing/duplicate/invalid paragraph idx | 0; unique per record, contiguous 0..N-1 |
| Missing/invalid flags, blank titles/text | 0 |
| Unresolved decomposition support pointers | 0 across 6,404 steps |
| Pointer to a non-supporting paragraph | 0 |
| Gold flag set versus decomposition pointer set | Exact agreement in all 2,417 records |
| Duplicate exact passage text within a pool | 0 records |
| Duplicate NFKC/lower/whitespace-normalized passage text within a pool | 1 record |
| Repeated exact titles within a pool | 1,293 records |
| Repeated titles among supporting paragraphs | 116 records |
| A support title also attached to a distractor | 626 records |
| Duplicate normalized composed questions | 6 groups, 12 records; 2,411 distinct normalized texts |
| Duplicate normalized answer aliases | 42 records |
| Canonical answer repeated as normalized alias | 20 records |

These anomaly categories overlap and must not be summed into an invalid-record
count. Repeated titles are legitimate paragraph-level identities, not grounds to
exclude 1,293 records. Native support joins are unambiguous by idx; joining by title
would merge different evidence and can falsely count a distractor as support.

The one normalized passage duplicate is record3hop2__25177_19506_23299,
idx 15 and 17, both non-supporting; strings differ before normalization.
Do not silently deduplicate, rename or repair source candidates.

All six duplicate-question groups agree on normalized answer. Five also share
support-text sets; one pair does not. Preserve source IDs and flag/group these
aliases for split review rather than automatically dropping records:

- 2hop__48033_90973 / 2hop__64175_90973
- 2hop__808562_72813 / 2hop__683203_72813 (different support-text sets)
- 2hop__144150_82341 / 2hop__444265_82341
- 3hop2__851134_326964_7713 / 3hop2__326964_851134_7713
- 3hop2__127483_125104_10557 / 3hop2__125104_127483_10557
- 3hop1__46571_87694_64412 / 3hop1__64957_87694_64412

Cross-record reuse: 21,098 unique normalized passage texts among 48,315 occurrences;
915 of 2,768 distinct decomposition-step IDs recur across records. This is another
reason to preserve official roles and examine component overlap before claiming
independence, rather than randomly splitting this file.

## 5. Existing EAR-RAG interfaces and compatibility

Inspected README.md, PROGRESS.md, AGENT_HANDOFF.md and docs/evaluation_protocol.md;
the modules below and their relevant tests. No MuSiQue reader, preparation
manifest or evaluator registration currently exists.

| Actual module / symbol | Finding and minimum implication |
|---|---|
| src/ear_rag/data/normalization.py: NormalizedDocument, NormalizedExample | Reusable query/document containers. Document identity can represent one paragraph; preserve exact text. Do not copy arbitrary offline metadata into runtime serialization. |
| src/ear_rag/data/hotpotqa.py: read_hotpotqa, _normalize_record, HotpotQADataset | HotpotQA JSON array, _id, answer, context[title,sentences], supporting_facts[title,sentence_idx]; unique titles required; labelled train/dev only. Does not accept this file directly. |
| src/ear_rag/data/hotpotqa_evidence.py: _get_example, build_question_corpus, locate_evidence, match_supporting_evidence | Enforces HotpotQADataset and matches sentence facts using titles. Cannot serve as a MuSiQue paragraph scorer unchanged. |
| src/ear_rag/control_evaluation.py: EvaluationCase, evaluate_cases, _runtime_stage, _quality, aggregate_cases, write_evaluation_report | Explicit IDs, fresh factory, retained exclusions/failures, offline scoring, existing JSON output/aggregation are reusable. evaluate_cases has a concrete HotpotQADataset guard; corpus/scoring imports are Hotpot-specific. |
| src/ear_rag/condition_evaluation.py: evaluate_conditions, _pipeline | Existing six definitions/factory isolation/config switches should remain the single runner; needs a narrow dataset/evidence adapter seam. |
| src/ear_rag/demo.py: build_backends | Accepts Sequence[Document]; lexical/vector index ordinary text, composites wrap them. All four support native candidate paragraphs without changing scoring. |
| src/ear_rag/data/hotpotqa_splits.py: normalized_question, ExposureInventory, validate_split_integrity | Reuse normalization/overlap principles; current source identity/manifest/export implementations are Hotpot-specific. A supplied inventory is not proof of complete history. |

Do not masquerade MuSiQue as HotpotQA, fabricate unique titles, turn each paragraph
into a fictitious gold sentence, or stuff decomposition into runtime metadata.

Recommended new adapter projection, not an existing API:
one runtime Document per original paragraph, stable IDs scoped by dataset/source
version + question ID + original idx, exact paragraph_text, original title and safe
position metadata. Keep file checksum offline. Query contains ID/text only.
All gold flags, answers, aliases, answerable, hop/decomposition annotations,
instruction, reasoning, statement and combined_paragraphs stay offline.

Keep every original candidate in original order, identical requested IDs/pools and
top-k 5 across conditions; fresh pipeline/index per question/condition. Preserve
chunking 400/50, vector dimension 64, hybrid weights .5/.5, max_hops 2 and all other current settings.
Top-k counts chunks, not distinct paragraphs; 26,144 paragraphs exceed 400 characters
(range 100–2,010), so repeated chunks from a paragraph must deduplicate by paragraph
ID for support recall. No real retrieval was run to test effectiveness.

## 6. Router, ESA and deterministic CAS

src/ear_rag/routing/query_analysis.py: LightweightQueryAnalyzer.analyze reads query.text only;
regex/numeric features ignore query ID and metadata.
src/ear_rag/routing/initial.py: InitialRetrievalRouter applies fixed query_features_v1 weighted
rules, availability, minimum score 1.0, margin .25 and lexical fallback from
configs/config.yaml. There is no fitted router/model-loading/training path.
**MuSiQue training data is not required to use this configured router.**
Routing remains a component of EAR-RAG, not a separate proposed contribution.

src/ear_rag/evidence/esa.py: DeterministicEvidenceAssessor combines lexical coverage, transformed
retrieval score, support-quantity/overlap and text uniqueness; weights .25 each,
thresholds .7/.4. These are proxies, not calibrated answerability.

src/ear_rag/routing/pipeline.py: RetrievalControlPipeline.run performs initial retrieval/ESA,
at most one recovery, mandatory reassessment, then evidence-ready or abstain.
src/ear_rag/routing/recovery.py: BoundedRecoveryPolicy.decide and
src/ear_rag/routing/cost_awareness.py preserve deterministic
CAS=(1-current ESA)*binary suitability/C, strict CAS>1.0,
C=max(.05*calls+.01*nominal chunks+.001*nominal latency_ms,.05).
Nominal cost and observed work remain separate. No expected ESA gain, future-score
prediction or learned recovery model is needed or permitted for integration.

Reuse the exact existing conditions:

1. fixed_local_lexical_no_recovery
2. fixed_vector_flat_no_recovery
3. fixed_hybrid_no_recovery
4. fixed_multihop_no_recovery
5. query_aware_no_recovery — router-integrated ablation
6. adaptive_controller — full router-integrated EAR-RAG

The four fixed conditions bypass initial routing; the first five disable recovery.
Existing condition tests verify dispatch, limits, reassessment, fresh state, pool
equality, gold isolation and accounting on synthetic HotpotQA fixtures; they do
not yet verify a MuSiQue adapter. No routing/retrieval/ESA/CAS change is proposed.

## 7. Faithful metrics and explicit gaps

| Measurement | MuSiQue status / definition |
|---|---|
| Hit@5 | Reuse supporting_document_metrics: any top-five chunk belongs to a gold supporting paragraph ID. |
| Supporting-document Recall@5 | Reuse helper with paragraphs as documents: distinct gold paragraph IDs hit / total gold paragraph IDs; never title-deduplicate. |
| Current supporting_evidence_coverage_at_5 | **Unavailable as defined:** HotpotQA annotated-sentence complete-span coverage. MuSiQue has paragraph labels, not sentence labels. Keep null with an explicit reason; do not substitute paragraph recall under the old name. |
| Optional complete-supporting-paragraph coverage@5 | Requires a separately named/versioned definition and approval: fraction of gold paragraphs fully covered by union of verified chunk spans. It is stricter than paragraph Hit/Recall and is not an official MuSiQue metric. Defer unless requested. |
| Official support precision/recall/F1 | Can be defined offline from predicted distinct paragraph indices, but needs explicit export/aggregation implementation; not currently emitted by the runner. |
| Calls/chunks/latency/routing/recovery/ESA/abstention | Existing telemetry/control summaries reusable; preserve unknowns. Latency excludes index construction/loading; not money/equal compute. |
| Processed chunks/controller overhead/monetary cost | Currently unavailable where existing telemetry returns null. |
| Answer EM/F1 | Answers/aliases exist, but no answer generation/predictions exist in EAR-RAG; cannot measure end-to-end answer quality now. |
| Answerability/hallucination reduction | Cannot establish from this all-answerable file, heuristic ESA and absent answer generator. |

The official evaluator consumes answer predictions and supporting paragraph
indices; its MuSiQue-Full sufficiency metrics require paired answerable/
unanswerable examples. Current retrieval outputs are not equivalent to those
official answer/sufficiency scores.
[Official evaluator](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/evaluate_v1.0.py).

Preserve evaluated/failed/excluded accounting, metric-missing counts and paired
question denominators. Do not compare new paragraph metrics numerically with old
HotpotQA sentence coverage as though their evidence units were identical.

## 8. Split and exposure strategy

Bounded checks against documented HotpotQA artifacts found:

- Zero composed-question ID or NFKC/lower/whitespace text matches against the known
  500 per_query.jsonl questions.
- Zero such matches against the 547-ID union of those 500 and the 50 detailed
  policy-audit records (three overlap).
- Zero decomposition-question normalized-text matches against the known500.
- As an extra check, zero composed-question normalized-text matches against all
  7,405 current HotpotQA questions.

These checks used outputs/query-validation-hotpotqa500/per_query.jsonl,
docs/hotpotqa_invalid_record_policy_audit_v1.json and the unchanged raw HotpotQA
JSON. ID namespaces differ; zero matches are a limited exact-overlap finding,
not proof of semantic novelty, complete project history or independence.
There was no prior MuSiQue mention in the searched project docs/source/tests;
absence from those files is not an exposure ledger.

Preferred future source: the official MuSiQue-Ans release. Acquire later, only
with authorization, official labelled dev plus authenticated train/test ID
inventories and the official dev_test_singlehop_questions_v1.0.json safeguard.
Full training data is needed only if training or train-content auditing is
actually authorized; the fixed router needs none. An official test claim requires
the actual official test role and available annotations/scoring access, not a
third-party rename. If test labels are unavailable, the current offline retrieval
scorer cannot compute gold metrics there; use an explicitly approved labelled-dev
research role without calling it official test.

Upstream warns about overlap with seed single-hop datasets and publishes the
dev/test single-hop inventory. Because EAR-RAG has local NQ material, that broader
source-level history also needs review; the HotpotQA-only check does not cover it.
[Official split and seed-overlap guidance](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/README.md).

For this derivative, first join official IDs and compare original question,
paragraph idx/title/text/support flags and answers; examine raw_question versus
rewritten decomposition separately. Obtain provider conversion/split records.
Do not assume that 2,417 records proves they are exactly official dev.

Do not randomly split test.json or select cases by favorable outcomes. Preserve
official allocations; check normalized question aliases, reused component IDs and
project exposure before approving any role. Six duplicate-question groups and 915
reused step IDs require explicit overlap handling, not automatic removal.
Keep the inspected sample IDs in exposure history. No split, cohort approval,
exclusion policy, filtered dataset or exposure inventory was created here.

## 9. Minimal prioritized Part 2 plan — proposed, not implemented

1. **Resolve source/role decision first.** Prefer official Ans data/core-field
   verification. If this pinned derivative is retained for engineering, explicitly
   label it derivative/split-unverified; obtain transformation and attribution
   records before research approval. Confirm paragraph-level metrics with sentence
   coverage unavailable; decide separately whether an additional span metric is
   wanted. No threshold or router training decision is necessary.

2. **Add one strict native reader/projection** (proposed
   src/ear_rag/data/musique.py). Preserve bytes/source SHA/revision/provider role
   separately from official role; retain all records or emit auditable diagnostics.
   Validate UTF-8/JSON keys/types/IDs, idx uniqueness, text, support flags,
   decomposition references and set agreement. Do not reject repeated titles or
   silently collapse duplicate questions/aliases/candidate text. Use existing
   normalized Document/Example containers and an allowlisted runtime projection;
   no artificial sentence annotations.

3. **Add paragraph-ID evidence adapter** (proposed
   src/ear_rag/data/musique_evidence.py). Build per-question pools and offline gold
   paragraph-ID sets; verify chunk source/window identity and join by idx-scoped
   document ID. Reuse evaluation_metrics.supporting_document_metrics.
   Keep original paragraph titles for display without using them as join keys.

4. **Introduce one narrow evaluator adapter seam** in control_evaluation.py and
   pass it through condition_evaluation.py. Keep HotpotQA's existing default path,
   validation and serialized metric meanings unchanged. The seam supplies validated
   case/corpus access, chunk locations and offline scoring; remove neither safety
   checks nor the gold/runtime boundary. Reuse the same condition loop, factory,
   aggregation, failure accounting and new-directory writer. Do not duplicate the
   evaluator or wrap MuSiQue in a forged HotpotQADataset.

5. **Synthetic tests first**, proposed tests/test_musique_ingestion.py and
   tests/test_musique_evidence.py plus small additions to existing evaluator/
   condition tests: malformed inputs, duplicate IDs/indices, repeated titles with
   support/distractor collisions, unresolved/inconsistent pointers, alias handling,
   source immutability/determinism, exact text/Unicode chunk windows, label-only
   mutations of every enrichment field, ID-prefix/hop-feature isolation,
   all-four backend compatibility, all-six condition isolation/accounting,
   null sentence coverage and unchanged HotpotQA outputs. Use small fixtures;
   no local benchmark dependency.

6. After those tests pass, run focused/full regressions and configured type checks.
   Any later real evaluation needs a separately frozen/authorized role, exposure
   evidence, metric definitions and unique output directory. Never tune on the
   evaluated cohort. Part2 integration does not itself approve independent data.

## 10. Inspection commands, tests and preservation

All local commands ran from C:\ear-rag with the existing environment.
Only bounded inline inspection scripts were used; none was saved as another file.

~~~powershell
git --no-optional-locks status --short --untracked-files=all
git ls-remote https://github.com/StonyBrookNLP/musique.git HEAD
~~~

Repository rg searches located dataset/evaluator/factory/router/ESA/CAS symbols and
relevant tests. Inline Python was executed as
@' ... '@ | .\ai-proj-new\Scripts\python.exe -B - and performed:
SHA-256; strict UTF-8/JSON duplicate-key/non-finite checks; full-file field/type/
empty-value/ID and paragraph/decomposition joins; normalized duplicate/alias/
passage counts; exact HotpotQA overlap checks; before/after file/ADS inventories.
No script executed retrieval, routing decisions, scoring experiments or bootstrap.

Metadata-only HTTPS GETs used urllib.request with 30-second timeout and 1,000,001-byte
read cap (reject responses over 1 MB), without saving responses:

- https://huggingface.co/datasets/pensieves/musique-ans/raw/f4de5c0125186fe0f9a81b044afed3f5afb64265/README.md
- https://huggingface.co/api/datasets/pensieves/musique-ans/revision/f4de5c0125186fe0f9a81b044afed3f5afb64265
- https://huggingface.co/api/datasets/pensieves/musique-ans/tree/f4de5c0125186fe0f9a81b044afed3f5afb64265/small-musique_ans?expand=true

Primary-source browser inspection covered the pinned provider commit/card/file
pointer and official README/license/download/conversion/evaluation code.
The browser tool could not render some pinned card/pointer pages; the bounded
metadata/card GETs above succeeded. No dataset file/archive was downloaded.
No source code from those repositories was executed.

Tests run: **none**. This stage changes no executable code; inspected existing
tests rather than invoking fixtures that write files. Relevant existing suites:
tests/test_hotpotqa_ingestion.py, test_hotpotqa_evidence.py,
test_hotpotqa_splits.py, test_control_evaluation.py,
test_condition_evaluation.py, test_query_routing.py and
test_deterministic_cas.py. Their prior pass counts are not asserted as new results.
No qualifying bug was fixed; no error note was created.

Initial preservation baseline: 189 accessible project files and 6 existing raw-file
Zone.Identifier streams, including MuSiQue. Excluded .git internals, environment/
caches and legacy pytest_phase_16c_tmp from file hashing; no claim about external
session histories. README.md, PROGRESS.md and AGENT_HANDOFF.md remain untouched as
explicitly required. Final preservation/check results follow below.

## 11. Handoff and unresolved decisions

Proceed with a native paragraph-ID adapter; no separate distractor corpus is
required. Existing runtime methods and router configuration can remain frozen.
This file is a verified pinned third-party artifact, not a verified official test
or exposure-cleared cohort. Official lineage/split comparison, added-field
provenance/licensing explanation, project exposure and paragraph metric approval
remain research gates.

User decision for Part2: authorize integration against this identified derivative
for engineering only, or first supply/authorize official-source comparison.
Recommendation: prefer official-source verification; synthetic adapter work can
proceed without a research-cohort claim. Full training data/router training is not
a prerequisite. Official dev/split/component inventories are needed for the
recommended provenance path; official test/scoring is needed only for an official
test claim. Do not acquire anything or begin implementation automatically.

Stop after Part1. Only docs/musique_dataset_audit.md may be new; no existing
HotpotQA artifact, source/configuration, threshold, result or project-status
document is authorized to change.

## 12. Final preservation results

- All 189 starting accessible project files remain byte-identical; none missing.
- All six starting raw-file Zone.Identifier streams remain byte-identical.
- MuSiQue test.json retains SHA-256
  b8a2f97c09f666cccf9663550eab73bbecc72af4f44f75af15c84b646f49cc38.
- Only added file: docs/musique_dataset_audit.md. Git status row-set comparison
  shows exactly that new untracked path, with no changed prior status rows.
- Git HEAD remains a905925db843db98e4dbc848ceb85696b48c693b.
- git --no-optional-locks diff --check passed (exit 0); the untracked report also
  passed direct trailing-whitespace and balanced-fence checks.
- No dataset download/replacement, benchmark, tests, tuning, commit, source/config
  edit or existing report/output modification occurred. No new error note.


## 13. Official-source verification and Phase 5 preparation — 2026-10-22

**Outcome: official-source acquisition and derivative/dev identity are verified.
Independent-test clearance is not granted.** This dated addendum supersedes the
earlier uncertainty about which official split the derivative represents.
Sections 1–12 remain the historical Part 1 audit. This stage prepares the next
implementation task; no adapter, benchmark, tuning or router training occurred.

### Authoritative source, variants and release

The author paper is Trivedi, Balasubramanian, Khot and Sabharwal, TACL 2022,
DOI 10.1162/tacl_a_00475. MuSiQue-Ans contains answerable 2–4-hop questions;
MuSiQue-Full adds corresponding unanswerable contrasts. The paper's split design
limits overlap in component questions, answers and supporting paragraphs; it is
not equivalent to a random split of this derivative.
[Paper, sections 5 and Table 2](https://aclanthology.org/2022.tacl-1.31.pdf).

Author-maintained source: StonyBrookNLP/musique, HEAD rechecked as
922ac98f19a201998dbdae6d7f2887a5258dbdeb. Its pinned download_data.sh identifies
Google Drive object 1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h. The script's output name is
musique_v1.0.zip; Google's Content-Disposition calls the same object
musique_data_v1.0.zip. Both names are recorded; no identity is inferred from names.
[Official download script](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/download_data.sh).

Release history: commit 42cb6551c9de9e987bb7574f74ed900afff9ba8a added v1 data/
predictions on 2022-05-06; commit 454c66b338f29e5b37012a4724d49305bbde5f3c
subsequently adjusted the script that day. The GitHub releases API returned zero
Release objects; this audit identifies v1.0 through the author source/script,
not a claimed GitHub release asset.
[Script history API](https://api.github.com/repos/StonyBrookNLP/musique/commits?path=download_data.sh&per_page=5).

Official licensing is **CC BY 4.0**, explicitly stated by upstream and its pinned
LICENSE. Preserve dataset/paper attribution and source links. The derivative's
CC BY-SA 4.0 card and added explanations remain separate provenance; they are not
needed when using the acquired official records.
[Official license](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/LICENSE).

### Verified split availability and label limits

The official ZIP directory contains all six documented files below.
Counts marked paper are publication counts, not new local full-file counts.

| Archive member under data/ | Records | Public-label finding |
|---|---:|---|
| musique_ans_v1.0_train.jsonl | 19,938 (paper) | First-record schema probe has answer, aliases, answerable, decomposition and paragraph support flags |
| musique_ans_v1.0_dev.jsonl | **2,417 measured** | Every locally acquired record has answers and supporting-paragraph annotations |
| musique_ans_v1.0_test.jsonl | 2,459 (paper) | First-record probe has only id/question/paragraphs; no answer, answerable, decomposition or support flags |
| musique_full_v1.0_train.jsonl | 39,876 (paper) | Archive entry exists; full contents/labels not inspected |
| musique_full_v1.0_dev.jsonl | 4,834 (paper) | Author documentation uses it for labelled evaluation; not acquired |
| musique_full_v1.0_test.jsonl | 4,918 (paper) | First-record probe has no answer/answerable/decomposition/support flags |

No public **labelled official test** artifact was identified. The author converter
has a blind-export branch removing exactly these labels. Schema probes examined
first records only, not every test row; they are not a claim to have downloaded
or exhaustively validated either test file.
[Official converter, hide_labels branch](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/raw_data_to_official_format.py).

The author's documented test route is formatted predictions submitted to the Ans/
Full leaderboards. Both leaderboard URLs returned 502 in this audit's browser tool;
current submission availability and permission/access are **unverified**, not
proven permanently unavailable. The current EAR-RAG system also has no answer
generator and cannot satisfy the complete official prediction contract.
[Author scoring/submission instructions](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/README.md#leaderboard).

### Minimum official acquisition completed

New directory: **C:\ear-rag\data\raw\musique\official_v1_0\**.
Raw member names and bytes are preserved. They were retrieved at
2026-10-22T15:01:16.424382+00:00 from the author-linked Drive object over HTTPS.

| File | Bytes | SHA-256 |
|---|---:|---|
| musique_ans_v1.0_dev.jsonl | 30,439,728 | 15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b |
| dev_test_singlehop_questions_v1.0.json | 915,921 | 013be00ab914799891e5ae40de6cdc1baf03aaffd1f3ce4bf0de796020069613 |
| acquisition_manifest.json (project metadata) | 22,394 | 5605cda92ce84168084909af6bbe964e658ad9420b12712f3d12329c509d8622 |

The metadata records source URL, pinned repository revision, date, license,
member path, exact size/hash, ZIP CRC, archive directory, request ranges,
other-split field probes and relationship/exposure checks. It is an acquisition
record, not an approved cohort/split manifest.

Acquisition used standard-library HTTPS Range requests and zipfile: read the ZIP
directory, decompress **only** the two retained members, validate their CRCs and
JSON, then write exclusively into a new directory. No author script was executed,
no dependency installed and no entire ZIP/full training/full test set was retained.
Three bounded first-record probes (Ans train and Ans/Full test) fetched 20,668
compressed/header bytes solely to verify split-schema/label availability.

The complete archive is 272,049,578 bytes. The successful selective acquisition
received 7,752,601 range bytes; two preliminary directory/range probes received
another 131,114. The server reported Last-Modified 2022-05-06. Neither that timestamp
nor a repository commit cryptographically pins mutable Drive content. No
author-published canonical archive hash was found; archive SHA is therefore null,
while the local member hashes and CRCs are recorded. This is verified acquisition
from an author-endorsed source, not a signed/immutable release certification.

The component inventory has **6,371 entries**: squad2 1,122; natural_questions
1,202; zerore 975; mlqaen 128; trex 2,944. Every entry has id/question; source IDs have
mixed string/integer types. They are not directly interchangeable with the
MuSiQue-internal integer decomposition IDs. No such crosswalk was acquired.
That namespace distinction is not a failed paragraph-support join.

The author's usage caution asks users of the seed datasets to avoid the published
dev/test single-hop IDs in training/pretraining. This is why the inventory and
the local NQ overlap matter even when complete composed questions do not match.
[Upstream seed-data caution](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/README.md#data).

### Exact relationship between official dev and derivative

Compared unchanged C:\ear-rag\data\raw\musique\test.json with the official JSONL:

| Comparison | Matches / mismatches |
|---|---|
| Records / unique IDs | 2,417 / 2,417 in each file; zero duplicate IDs |
| ID intersection / unmapped | 2,417 common; zero official-only or derivative-only |
| Ordered IDs | Identical |
| Questions, answers, ordered alias lists, answerable | Each field identical in all 2,417 records |
| Candidate paragraph idx/title/text/support flags and order | Entire paragraph arrays identical in all 2,417 records; 48,315 paragraph occurrences |
| Decomposition step ID/answer/support index | All 6,404 steps identical for each field |
| Official decomposition question versus derivative question | 2,768 equal; 3,636 rewritten |
| Official decomposition question versus derivative raw_question | All 6,404 equal |
| Official record versus derivative core projection using raw_question | All2,417 equal |

**Established:** this derivative's test file is an enriched copy of **official
MuSiQue-Ans development records**, in the same order. It is not the official test
split. Added instruction/reasoning/statement fields and rewritten decomposition
questions explain why whole-file hashes differ; the observed equality does not
establish the provider's uninspected train/validation split membership.

### Official candidate pools and structural validation

All2,417 official dev rows pass the checked native schema, type, nonblank text,
unique-record/paragraph-ID and support-reference checks. Each contains both
support and distractors. Native JSONL is UTF-8; labels remain offline.

- Candidate counts: 17 paragraphs in 2 records, 18 in 5, 19 in 9, 20 in 2,401.
- Supporting paragraphs: 2 in 1,252 records, 3 in 760, 4 in 405; 6,404 total.
- Distractors:14–18 per question;41,911 total. **No additional corpus is required**
  for the planned bounded per-question candidate-pool experiment.
- All 6,404 paragraph_support_idx references resolve to candidates marked
  is_supporting; the two gold support sets agree in every record.
- Paragraph idx values are unique and equal array position here. Match by the
  source idx-scoped paragraph identity, not by title.
- Repeated titles occur in 1,293 records; 116 repeat titles among gold paragraphs,
  and 626 have a support title also attached to a distractor.
- Six normalized duplicate-question groups remain, plus one normalized duplicate-
  passage case. No raw records were repaired, excluded or deduplicated.

These confirm the Part 1 compatibility findings on official bytes rather than
only a mirror. A shared pool means the same ordered candidates for **all six
conditions for a question**, not a gold-filtered pool or a global pool assembled
from different questions.

### Exposure checks and recommended Phase 5 role

Exact ID and NFKC/lower/whitespace question checks found zero matches against the
known 500 HotpotQA questions and zero against the 547-ID union with the detailed
invalid-record audit. Composed-question text also has zero matches against all
7,405 local HotpotQA questions. These are exact checks, not semantic detection.

The official seed inventory exposes an additional limitation:

- **35** inventory question texts, all natural_questions, exactly match normalized
  questions in data/raw/nq/NQ-open.dev.jsonl (3,610 local records).
- **31 official dev records** contain a matching decomposition question:31 step
  occurrences representing 13 distinct internal step IDs.
- Zero complete MuSiQue composed questions match the local NQ questions.
- Local NQ-open rows lack original source IDs, so no source-ID join was possible.
  Overlap details and normalized-text hashes are retained in acquisition metadata.

Presence in processed/raw project data is not proof of training or per-question
experimentation. Conversely, absence from saved outcome reports is not proof of
no exposure. The seed inventory covers dev/test together; this audit does not
assign all 35 matches to one split or infer a missing source-ID crosswalk.
No automatic exclusions were made from these findings.

The Part 1 previews and whole-file schema review remain documented exposure.
Repository-local docs, code and saved HotpotQA reports cannot establish all
earlier manual sessions or outside-repository use. No semantic duplicate search,
complete exposure attestation or approved independent allocation exists.

**Recommended prospective Phase 5 source:** the acquired official Ans dev file,
preserving official role=dev and original IDs. An authorized later study should
be labelled **development/internal — official-source MuSiQue-Ans dev; contains
inspected questions, project exposure history incomplete**. It provides a source-
verified external-dataset check of the frozen policy, but is not an
exposure-cleared independent test. Prefer it over the enriched derivative for
provenance and leakage simplicity. No actual evaluation cohort or new split was
selected by this task.

Before any stronger independence claim: reconcile the 31 component-overlap cases,
the inspected samples, duplicate-question groups, other historical uses and the
source-component ID mapping. Do not call the remaining records unseen after
simply subtracting those cases. Do not invent a labelled test, random partition
or outcome-based selection. Official train is not needed for the current
configured router or to establish the derivative/dev identity.

### Binding implementation specification for Part 2

The relevant APIs were rechecked using repository search. Existing HotpotQA
validation and outputs remain the default unchanged path.

| Proposed file/change | Smallest required work |
|---|---|
| New src/ear_rag/data/musique.py | Strict official JSONL reader/diagnostic types; explicit musique_official_jsonl_v1 identification, source hash/revision and official split. Validate duplicate JSON keys/IDs, required labelled fields, text, paragraph idx, flags and decomposition support agreement. Native duplicate titles are allowed. No guessed format/split from test.json. |
| New src/ear_rag/data/musique_evidence.py | Native per-question corpus, fresh safe Query/Documents, original paragraph text/title/order and stable idx-scoped IDs. Offline gold paragraph-ID sets and verified chunk character windows. Reuse NormalizedDocument/NormalizedExample where appropriate; never manufacture sentence labels. |
| src/ear_rag/control_evaluation.py | Small explicit dataset/evidence adapter seam at evaluate_cases, _runtime_stage and _quality; preserve HotpotQA guards/default behavior and existing failure/serialization/aggregation paths. Runtime factory still receives only fresh safe documents. |
| src/ear_rag/condition_evaluation.py | Pass the adapter through evaluate_conditions; reuse its six conditions and _pipeline. No duplicate runner or forged HotpotQADataset. |
| src/ear_rag/evaluation_metrics.py | Reuse LabelResolution/supporting_document_metrics without changing existing definitions. Only add a separately specified pure metric helper if actually required. |
| tests/test_musique_ingestion.py and tests/test_musique_evidence.py (new) | Synthetic JSONL/schema/type/duplicate-ID/index/reference validation, source immutability and native repeated titles; Unicode/span identity and gold isolation. |
| tests/test_control_evaluation.py and tests/test_condition_evaluation.py | Synthetic adapter compatibility, equal pools/top-k, failures/exclusions, repeated-title support/distractor distinction, duplicate-question accounting, fresh state, all four backends and all six conditions; missing-metric counts and unchanged HotpotQA behavior. |

Metric contract before implementation:

- Hit@5: any first-five retrieved chunk belongs to a gold paragraph ID.
- Supporting-document Recall@5: unique gold paragraph IDs hit / total gold
  paragraph IDs, using evaluation_metrics.supporting_document_metrics.
  With one paragraph per document, this is paragraph-level annotated-support
  coverage; version/label its unit explicitly.
- Existing supporting_evidence_coverage_at_5 remains unavailable/null for MuSiQue:
  it means complete annotated **sentence** coverage in HotpotQA. Do not replace it
  silently with paragraph recall. Report the missing reason/count.
- Optional support precision/F1 can use unique predicted/gold paragraph indices,
  but needs an explicit implementation/aggregation contract. Whole-paragraph
  span coverage would be another separately named metric; do not invent it as a
  substitute during integration.
- Dataset answerable (all true here), runtime ESA sufficiency and annotated-support
  coverage are different quantities. No generator exists, so answer EM/F1,
  hallucination reduction and official end-to-end scores remain unavailable.
- Work: existing measured underlying calls, returned chunks, child passages,
  requested top-k and retrieval/router latency; missing full-controller/processed/
  monetary fields stay null. CAS nominal incremental cost is separate.

Keep all original candidates and identical top-k 5, chunking 400/50, vector dimension 64,
hybrid weights .5/.5, max_hops 2, ESA and CAS settings across comparable conditions.
MuSiQue's 2–4-hop annotation is not permission to change runtime hop limits or
route using ID prefixes/decomposition. Query analysis must still read text only.
Answers, aliases, support flags/indices, answerable and every decomposition/
enrichment field stay offline; test that label-only mutations leave runtime
selection/retrieval/control traces unchanged.

**Phase 5 uses the existing configured router. Router training belongs to Phase 6**
and requires its own authorized training source, frozen evaluation separation and
leakage checks. No learned recovery/ESA/cost model is part of either integration
step. After synthetic implementation checks, run focused/full regression tests,
configured type checks and diff checks; do not use a benchmark as an integration
smoke test.

### Commands, validation and remaining approval

Commands used: git --no-optional-locks status; git ls-remote for official HEAD;
rg symbol/test searches; primary-source browser/PDF inspection; bounded Python
stdlib urllib/http.cookiejar/zipfile range acquisition; inline Python JSON,
SHA-256, CRC, schema, per-ID field and normalized-text checks. No scripts were
saved as new runtime modules. No gdown/upstream shell script was run.

The acquisition manifest records all successful member range requests. To repeat
later, use the pinned download script's Drive object; request the ZIP directory
and only the two named members, check206/Content-Range/length/CRC, and write into
a **new** directory. Do not execute the script unchanged: it installs gdown and
downloads/extracts the entire archive, beyond this bounded acquisition scope.

Checks completed: both retained member hashes/CRCs; 2,417-record strict native
validation; complete derivative/dev field comparison; component inventory checks
and limited HotpotQA/NQ overlap checks. **No tests, router decisions, retrieval
experiment, six-condition run, training or statistical analysis ran.**
No meaningful bug was fixed; no new error note.

Remaining decision: approve a separately frozen **development/internal official-dev**
study after the minimal adapter, or require genuine exposure-clearance evidence/
verified official scoring access first. Neither approval is inferred here.
No additional distractor download or Phase 6 router training is needed now.

The final preservation check below applies to this addendum stage; earlier
preservation statements describe their earlier checkpoints.

Final stage preservation: checked all 190 starting accessible project files.
Only this audit document changed, by an addendum; its original 28,052-byte prefix
is unchanged. All other 189 files, including README.md, PROGRESS.md,
AGENT_HANDOFF.md, runtime/configuration, HotpotQA data and existing outputs,
remain byte-identical. The six existing download-metadata streams are unchanged.
The derivative retains SHA-256
b8a2f97c09f666cccf9663550eab73bbecc72af4f44f75af15c84b646f49cc38.

Only three files were added, all under data/raw/musique/official_v1_0/: the two
verified source members and acquisition_manifest.json. Git HEAD and prior status
rows remain unchanged; the already-untracked audit stays untracked and raw data
is ignored, so file hashes/inventories, not Git status alone, establish scope.
git --no-optional-locks diff --check passed (exit 0); direct audit whitespace and
fence checks also passed. No unrelated change was found or reverted. Stop here.

## Part 2 implementation and development/internal evaluation addendum — 2026-10-22

The subsequent user request explicitly authorized integration and one official-dev
evaluation after integrity/isolation/regression gates passed. This supersedes
the approval-pending statement above for this bounded development/internal task.
Label: **development/internal — exposure limitations apply**. No exposure-cleared
holdout, labelled official-test/scoring access, or Phase 6 training is implied.

Implemented native reader/diagnostics/manifest in data/musique.py; source-only
paragraph corpus and offline idx-based scoring in data/musique_evidence.py;
narrow supported-dataset dispatch in existing control/condition evaluators.
Shared exact window validation now accepts a structural corpus type; HotpotQA
matching/scoring behavior is unchanged. The small musique_experiment command
reuses the existing six-condition runner, serializer, aggregator and bootstrap.
No backend, router, ESA, CAS, recovery or configuration behavior was changed.

Revalidated original official dev SHA256
15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b:
2,417 unique answerable/valid records, 48,315 candidates, 6,404 supports, zero
exclusions/unclassifiable. Acquisition revision/license/hash and single-hop
inventory match. Full ordered derivative ID/question/answer/alias/answerable/
candidate comparison still agrees. Recomputed 31 NQ matching-decomposition
records and six normalized duplicate-question groups; all retained explicitly.
Matching text is not proof of training use. Raw datasets were never rewritten.

Synthetic tests prove repeated-title gold/distractor discrimination by native
paragraph idx; mapping through chunking; first-five-chunk parent deduplication;
strict schema/JSON/reference failures; raw immutability; runtime gold mutation
isolation; same pools/top-k/fresh state; fixed bypass, recovery disabling/limit/
reassessment; failed/excluded/duplicate accounting and deterministic serialization.
Focused: 150 passed in 2.71s. Full: 507 passed in 6.68s. Six changed source modules
pass mypy. Software tests are not evidence of research effectiveness.

Before execution, protocol section 20 and 47 source/config/input hashes were
frozen; config SHA b494caae97e83ff6d095f0f0133b58b0ea6b281f63d62e0f378c8e7a0b6b4835.
All six existing v2 conditions ran once on the same ordered 2,417 IDs/candidate
pools/top-k 5, no tuning. Each requested/evaluated 2,417; failed/excluded zero;
common paired n=2,417. Native paragraph Hit/Recall use parent IDs among the first
five chunks. HotpotQA sentence evidence coverage remains null with explicit
unavailable reason; no sentence labels were invented.

| Condition | Paragraph Recall@5 | Hit@5 | Measured calls | Recoveries | Abstain |
|---|---:|---:|---:|---:|---:|
| Fixed lexical | .479555 | .840712 | 2417 | 0 | 6 |
| Fixed Vector Flat | .281444 | .583368 | 2417 | 0 | 1652 |
| Fixed Hybrid | .391429 | .744725 | 4834 | 0 | 878 |
| Fixed Multi-hop | .479555 | .840712 | 4834 | 0 | 6 |
| Query-aware/no-recovery | .437043 | .779065 | 2493 | 0 | 317 |
| Adaptive | .473900 | .829541 | 2810 | 317 | 6 |

Adaptive-minus-router paragraph recall +.036857 [95% paired CI .030651,.043339]
with 317 more calls; adaptive-minus-lexical -.005654 [-.008688,-.002689] with 393
more calls. Recovery yields 199 improvements/90 ties/28 regressions in annotated
paragraph recall; reassessment 311 sufficient/six uncertain. Final 2,411 sufficient
does not mean verified answers: 2,058 still lack complete annotated recall.
Nominal CAS recovery increment 34.87 abstract units is separate from actual work.
One timing pass excludes loading/index creation/full controller time; no money
or complete processed-work measurement. Bootstrap is descriptive (10,000 paired
question draws, seed 1729), limited by shared components/repeated questions.

Artifacts: [consolidated record](../outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73/EXPERIMENT_RECORD.md),
[results](../outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73/REPORT.md),
adjacent frozen/dataset/cohort manifests, six per_case.jsonl/aggregate.json pairs,
analysis.json, validation.json, runtime_replay_validation.json and checksums.
Commands (PowerShell, C:/ear-rag, existing environment):

```powershell
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.musique_experiment run --output outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.musique_experiment verify --output outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73
.\ai-proj-new\Scripts\python.exe -B outputs/phase5-musique-development-internal-20261022T153801Z-cfdcea73/validate_saved_runtime.py
```

Do not repeat run into that directory; verify performs no retrieval. Exact test/
type-check commands are in the consolidated record. Saved validation reproduces
29,004 paragraph metric stages, exact analysis/report, 29,004 ESA assessments,
14,502 exact policy decisions and 1,268 candidate entries. Seven negative controls
reject corrupt rows/config/recovery/paragraph metrics; an injected in-memory
failure reduces pairing while retaining its ID. No saved data were changed.

Development/internal integration/evaluation complete; independent exposure
clearance and verified official labelled-test/scoring remain unresolved. No answer
generation, hallucination reduction, unseen generalization, or published-method
superiority established. No new downloads/dependencies/splits/training; prior
outputs and source bytes preserved. No meaningful resolved bug/error note.


