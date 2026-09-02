# EAR-RAG Development Progress

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

## Current Status

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
- `src/ear_rag/retrieval/`: deterministic document chunking and local lexical
  retrieval, with retrieval-cost metadata.
- `src/ear_rag/data/`: normalized local dataset adapters, preprocessing,
  deterministic artifact persistence, and persisted-index reload support.
- `configs/config.yaml`: initial project, path, query-analysis, retrieval, ESA,
  recovery, generation, evaluation, and logging settings.
- `tests/`: foundation smoke tests for imports, models, interfaces, and
  configuration.

The named directories for baselines, data, evaluation, evidence, generation,
retrieval, routing, and utilities exist under `src/ear_rag`, but currently have
no implementation files.

## Current File Structure

```text
src/ear_rag/
  __init__.py
  config/{__init__.py, loader.py}
  core/{__init__.py, models.py, interfaces.py}
  data/{__init__.py, datasets.py, preprocessing.py, persistence.py, pipeline.py}
  retrieval/{__init__.py, chunking.py, local.py}
  {baselines,data,evaluation,evidence,generation,routing,utils}/
configs/config.yaml
tests/{test_config.py,test_contract_hardening.py,test_core_models.py,test_interfaces.py,test_local_retrieval.py,test_project_setup.py}
data/{raw,processed,indexes,fixtures}/
outputs/{logs,results,demos}/
```

## Dependencies

- Python 3.11.9 virtual environment.
- Installed: `pytest==9.1.1`, `PyYAML==6.0.3` and their small runtime
  dependencies.
- Declared but not installed in the existing environment: `mypy`, `pre-commit`.
- No large ML dependencies are installed.

## Models

No models selected, configured beyond placeholder strings, or downloaded.

## Datasets

The local deterministic fixture is configured for development. Natural Questions,
HotpotQA, and 2WikiMultihopQA are supported through a normalized local JSONL
adapter contract only; none of their source datasets have been downloaded.

## Experiments

No experiments have been run.

## Known Issues

- `src/ear_gr/` contains only a generated `__pycache__`, and the empty
  `src/ear_rag/config/_/` and `src/ear_rag/core/_/` directories remain because
  the environment blocked their deletion. They contain no active source code and
  do not affect package imports or tests.
- The requirement file lists development tools not present in `.venv`.
- Natural Questions, HotpotQA, and 2WikiMultihopQA still require user-supplied,
  locally normalized JSONL files; no native source-format parser exists yet.

## Next Phase

Phase 1.5 — Lightweight Evidence Sufficiency Assessment and 40% Research Demonstrator.
