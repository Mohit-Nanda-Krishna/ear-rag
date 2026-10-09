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

## Run and validate

From this repository's root in PowerShell, using its existing virtual environment:

```powershell
$env:PYTHONPATH = "$PWD\src"
.\ai-proj-new\Scripts\python.exe -m ear_rag.demo
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.evaluate_initial --smoke --examples 5
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.evaluate_initial --dataset hotpotqa --examples 20
```

The offline evaluation compares available fixed strategies with query-aware
routing using a common corpus and **recovery disabled in every condition**. It
reports supporting-document recall@k, routing distribution/fallback, router and
retrieval latency, underlying retrieval calls, passages, and final context size.
The synthetic smoke fixture is tracked; real evaluation requires local normalized
datasets under `data/processed`. PyYAML and pytest are listed in `requirements.txt`;
dataset preprocessing tests also require `pyarrow`, installed in the existing
environment but not yet listed there. No new model downloads are required.

The initial 20-question HotpotQA development check did not establish improvement:
routed local-support recall@5 was 75%, versus fixed lexical 87.5%, among 16 queries
with locally resolved support labels. Rules are provisional and need development-set
calibration; freeze settings before independent test evaluation. Details and label
coverage caveats are in the [evaluation report](docs/initial_routing.md#measured-development-check-2026-10-09).

## Repository Structure
```
ear-research/
├── src/ear_rag/          # Python package
├── configs/              # Configuration files
├── data/                 # Raw and processed data
├── tests/                # Test suite
├── outputs/              # Logs and results
├── configs/              # Configuration files
├── notebooks/            # Jupyter notebooks
└── docs/                 # Documentation
```

## Implementation Phases
- **Phase 1.1**: Project foundation ✓
- **Phase 1.2**: Configuration and Core Interfaces
- **Phase 2.x**: RAG pipeline implementation
- **Phase 3.x**: Evaluation and baselines

## Note

Consult [PROGRESS.md](PROGRESS.md) for phase history. Current routing and ESA are
deterministic baselines, not learned or calibrated policies; generation and
dataset-scale research evaluation remain future work.
