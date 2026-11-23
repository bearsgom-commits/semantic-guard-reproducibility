# IP&M P2 historical Re-ID code semantics — 2026-11-23 KST

## Evidence and scope

Directly examined author-provided extracts from original `repo/scripts/stage3/run_attack_reid.py` (expected SHA-256 `e934489d54acbf83592a7de25ef5bb2a5b72dc57f33853e50ef4ca3363710bca`) and `repo/src/guard_repr.py` (expected SHA-256 `8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d`). Original hashes were reported locally; full runnable attack protocol was not executed in this audit.

## Verified source-level facts

- ReID `align_by_prefix` lines 162–170 truncates ordered IDs, raw embeddings and Guard embeddings to their minimum length, **without comparing per-row document IDs**. This yields potential false correspondence if prior stages differ in ordering. A matching prefix length is not proof of true alignment.
- ReID `project_raw_to_guard_dim` lines 173–185: if dimensionality equal, raw embeddings are passed through; if raw dimension greater, independently generated Gaussian projection uses `default_rng(20260401 + target_dim).standard_normal(..., dtype=float32)/sqrt(target_dim)`; this projection is not the canonical Guard seed-specific W.
- Original Guard `make_projection_matrix` lines 40–48: `default_rng(seed).normal(0,1,size=(d_in,d_out)).astype(float32)/sqrt(d_out)`, seeds of the Guard run, e.g., 7,13,42. These differ in seed and NumPy sampling implementation.
- Guard source lines 65–86 normalizes, projects where dimension decreases, uniformly quantizes to q_bits and renormalizes. ReID reference projection does not reproduce the Guard quantization.
- ReID lines 188–229 compare `guard_emb[start:end] @ raw_proj.T`, argmax across **all aligned raw-reference rows**. Success is `nn_idx == global_i`, Top5 and Top10 analogous. This is paired-row retrieval against an auxiliary raw-embedding reference corpus, not text reconstruction or ordinary training-data membership inference.
- For d_out==d_in (historical eps64), ReID reference is raw (normalized), while Guard mostly retains 768 dimensions and applies quantization; a high rank-identity score is unsurprising under the stronger auxiliary-reference assumption but is not text recovery.
- No chance-baseline, candidate-set size control, reference-access validation or same-cell 2x2 D/B exposure endpoint can be inferred from the shown code excerpts.

## Decision

**HISTORICAL_REID_SOURCE_RECOVERED=YES**.
**HISTORICAL_REID_AS_SECURITY_OR_PRIVACY_ENDPOINT=NOT_VALIDATED**.
**HISTORICAL_REID_AS_AUXILIARY_PROXY=CONDITIONALLY_DESCRIPTIVE** only with explicit independent-projection and full raw-reference assumptions, qualified prefix alignment, and audited candidate cohort.
**P2_36_CELL_EXPOSURE_INTEGRATION=BLOCKED** pending valid same-cell prospective endpoint.

The existing historical Re-ID results remain frozen and must not be relabeled a known-matrix attack or linked with new factorial cells. This code audit identifies confounding factors; it does **not** prove all previous observations numerically wrong.

## Next minimal gates

1. Read-only original output-manifest and source pairing: inspect existing historical attack candidate count/row order versus canonical corpus ID list and selected original run, without re-running attack.
2. Specify prospectively a defensible attacker model: known-matrix T2 (raw reference and exact W) vs no-matrix T1. Avoid using exact Guard query self-matching as privacy measure.
3. Run a four-condition same-seed matched-ID **pilot only if** scorer and attacker knowledge are pre-specified, compare Top1/Top5 and simple 1/N baseline, and document full-corpus vs sampled candidate-set sizes. Model data access may itself imply additional disclosure; do not claim privacy guarantee.
4. If T1 candidate matching is intrinsically uninformative and T2 is trivially saturated, report the limitation and redesign the security outcome instead of expanding all 36 cells without justification.
5. Keep v18 frozen; prepare a separate v19 interpretation/terminology correction and professor response entry.

Evidence tier: code text provided by author and pre-existing audit metadata, not an independent empirical validation.
