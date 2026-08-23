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
**Phase 1.1 — Project Foundation**: Project structure, configuration, and minimal dependencies created.
- Python package `src/ear_rag/` initialized
- Configuration `configs/config.yaml` with placeholder categories
- Minimal `requirements.txt` (no large ML dependencies)
- `.gitignore` configured
- Basic testing framework setup

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
- **Phase 1.1**: Project foundation ✓ (current)
- **Phase 1.2**: Configuration and Core Interfaces
- **Phase 2.x**: RAG pipeline implementation
- **Phase 3.x**: Evaluation and baselines

## Note
Experiments, datasets, and model downloads will be added in later phases after hardware and model strategy are finalized. This repository currently contains only the project foundation scaffolding.