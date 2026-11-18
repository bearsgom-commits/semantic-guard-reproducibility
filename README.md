# Semantic Guard — IP&M Reproducibility Materials

This repository is being assembled as a **public evidence and reproducibility companion** for a manuscript intended for *Information Processing & Management* (IP&M).

**Status (updated 2026-11-18): IN PROGRESS — not a complete independent reproduction.**

## Scope

- BEIR evaluation datasets: FiQA, SciFact, TREC-COVID.
- Guard representation transformation and dense retrieval experiments.
- Stage 3 evaluation, including matched membership-inference analysis (MIA).
- Aggregation checks linking reported operating-region counts to provided result tables.

The experimental control parameter `epsilon` is **not** a differential-privacy guarantee.

## Directory guide

- `src/` — original Guard representation snapshot; historical execution provenance may be incomplete.
- `configs/` — supplied experimental settings, with provenance labels.
- `environment/` — environment details and known gaps.
- `data/` — dataset acquisition and redistribution notes.
- `results/stage3/matched_mia/` — Stage 3 result tables and validation artifacts.
- `scripts/` — reproducibility and validation scripts when verified.
- `docs/` — reproducibility scope and unresolved evidence gaps.

## Current verification boundary

A read-only audit of provided evidence independently recomputed 63 condition-level matched-MIA joins and reproduced **37/63 author-defined region flags** (epsilon breakdown: 0, 3, 8, 8, 9, 9, 0). This verifies aggregation consistency **only**; it does not independently rerun the BEIR retrieval, E5 encoding, or MIA attacks. The original matched-MIA, legacy-MIA, and Stage 3 aggregation source files were recovered and published in commit `cbe8fa6`. Their source bytes match the supplied ZIP. Full execution provenance and source embedding inputs have **not** yet been recovered.

The source snapshot for Stage 3 dense retrieval uses NumPy inner-product ranking. A separate YAML setting mentions FAISS HNSW; the configuration alone does not establish that HNSW was used in the reported execution.

Do not interpret near-0.5 matched-MIA AUROC as a general privacy guarantee.

## Matched-MIA local replay evidence (2026-11-18)

A later local audit recorded 63/63 PASS comparisons of matched-MIA attack-stage replay outputs against local canonical outputs. The final driver run freshly executed 21 TREC-COVID conditions and reused 42 earlier PASS reports for FiQA and SciFact. A sanitized condition-level CSV and an evidence-scope README are now public at [results/stage3/matched_mia/replay_20261118/](results/stage3/matched_mia/replay_20261118/). The 63 sanitized JSON reports and source embeddings are **not yet published** here. This extends the earlier aggregation-only audit but does not establish complete independent reproduction.

## Manuscript use

Do not describe this repository as fully reproducible. Cite only the specific publicly accessible audit materials and their limited verification scope until missing inputs, scripts, execution instructions, figure lineage, and public-access checks are completed. This README will be updated as those checks are resolved.

## Attribution and licenses

Dataset licenses and model terms must be respected. A software license for this repository has **not yet been selected**; no reuse permission beyond applicable law should be inferred from public visibility.
