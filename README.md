# EAR-RAG: Evidence-Aware Adaptive Retrieval with Selective Query Recovery

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

The [500-query validation study](docs/query_analysis_validation.md) adds per-query
fallback causes, evidence-label coverage, decision regret, paired comparisons and
JSON/CSV reports. It preserves the existing routing policy and documents where
its features and prototype backends fail.

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
the fresh installation passed **244 tests**, with no skips. Full interactive demo
behavior, Python 3.11 execution and standalone wheel deployment were not verified
in this phase. No datasets or models were downloaded.

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
