# EAR-RAG Development Progress

## Reliability Phase 1 (2026-10-20) — completed and verified

This section is the current status. Dated entries below are historical snapshots;
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
