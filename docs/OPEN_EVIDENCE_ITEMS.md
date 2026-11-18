# Outstanding source evidence — action required

Original evidence audit: 2026-11-17. Updated for local replay comparison: 2026-11-18.

## Files already public
- Three original execution and aggregation Python scripts published in commit [`cbe8fa6`](https://github.com/bearsgom-commits/semantic-guard-reproducibility/commit/cbe8fa68f0ec44d36b1f9a574bc4a4a05186d348). Their contents match the supplied source ZIP.
- Guard representation source `src/guard_repr.py`, restored byte-for-byte from the supplied archive; SHA-256 `8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d`. This does not prove historical execution code identity.
- Reconstructed mapping, explicitly non-original: `configs/guard_mapping_reconstructed.json`.
- 63-row matched-vs-legacy MIA derived comparison, epsilon summary and consistency checks.
- `scripts/check_published_validation.py`: verifies the published derived tables only.

## New local replay evidence (2026-11-18)

A sanitized **63-row condition-level CSV** and provenance notes were added under `results/stage3/matched_mia/replay_20261118/`. The underlying local replay evidence archive contained 63 PASS reports: 42 pre-existing report comparisons and 21 freshly executed conditions in the final driver invocation. Recorded metric differences were zero. **The 63 individual sanitized JSON reports and original Guard embeddings are not yet public in this repository.** This supports a local attack-stage replay comparison, not independent reproduction from public inputs.

## Required to complete independent experiment reproducibility
1. **Original execution commands, input embeddings, raw MIA outputs, and logs** for all conditions; scripts and a derived 63-condition replay comparison CSV are available, but historical run provenance and complete public report-level evidence remain incomplete.
2. **Original MIA attack score inputs** or an authorized reproducible data-generation path, and original command logs/seed.
3. **BEIR experiment runner and inputs**, including dataset acquisition, exact preprocessing, qrels and model revision.
4. **Retrieval implementation provenance** resolving NumPy exact dense vs configured FAISS HNSW.
5. **Final manuscript figure/table generation scripts** and source input files with hashes.
6. **Frozen environment**: dependency lock, Python version, device/backend, and checkpoint revision.
7. **Historical provenance** for the reconstructed epsilon mapping, or a clear statement that historical source is unavailable.

## Required user action
Please supply original run manifests, raw outputs and model/input provenance, not the already uploaded attack scripts, after reviewing for credentials and restricted data. Do **not** upload secret keys, tokens, private corpora, or materials without redistribution rights.

If the original execution artifacts cannot be recovered, publish the limitation and describe the package as **result-verification materials**, not full experiment reproduction.

## Completion standard
From a clean environment and public/authorized inputs, an independent reviewer should be able to run documented commands to reproduce the claimed tables and figures. The current repository does not meet that standard.
