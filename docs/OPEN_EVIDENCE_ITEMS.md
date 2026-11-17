# Outstanding source evidence — action required

Last reviewed: 2026-11-17.

## Files already public
- Guard representation snapshot (functionally transcribed from provided audit ZIP; comments shortened, **not byte-identical to the archived source**): `src/guard_repr.py`.
- Reconstructed mapping, explicitly non-original: `configs/guard_mapping_reconstructed.json`.
- 63-row matched-vs-legacy MIA derived comparison, epsilon summary and consistency checks.
- `scripts/check_published_validation.py`: verifies the published derived tables only.

## Required to complete independent experiment reproducibility
1. **Original matched-MIA attack execution script**, particularly any `run_attack_mia_matched.py`, with its dependency modules and CLI invocation.
2. **Original MIA attack score inputs** or an authorized reproducible data-generation path, and original command logs/seed.
3. **BEIR experiment runner and inputs**, including dataset acquisition, exact preprocessing, qrels and model revision.
4. **Retrieval implementation provenance** resolving NumPy exact dense vs configured FAISS HNSW.
5. **Final manuscript figure/table generation scripts** and source input files with hashes.
6. **Frozen environment**: dependency lock, Python version, device/backend, and checkpoint revision.
7. **Historical provenance** for the reconstructed epsilon mapping, or a clear statement that historical source is unavailable.

## Required user action
Please supply the actual IP&M local project source directory or a ZIP containing the missing original attack scripts and run manifests, after reviewing for credentials and restricted data. Do **not** upload secret keys, tokens, private corpora, or materials without redistribution rights.

If the original execution artifacts cannot be recovered, publish the limitation and describe the package as **result-verification materials**, not full experiment reproduction.

## Completion standard
From a clean environment and public/authorized inputs, an independent reviewer should be able to run documented commands to reproduce the claimed tables and figures. The current repository does not meet that standard.
