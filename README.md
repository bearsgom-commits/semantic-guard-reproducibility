# Semantic Guard — IP&M Reproducibility Materials

This repository is being assembled as a **public evidence and reproducibility companion** for a manuscript intended for *Information Processing & Management* (IP&M).

**Status (2026-11-17): IN PROGRESS — not a complete independent reproduction.**

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

## Manuscript use

Do not describe this repository as fully reproducible or cite a release until the missing inputs, scripts, execution instructions, figure lineage, and public-access checks are completed. This README will be updated as those checks are resolved.

## Attribution and licenses

Dataset licenses and model terms must be respected. A software license for this repository has **not yet been selected**; no reuse permission beyond applicable law should be inferred from public visibility.
