# Matched MIA: historical AUROC recalculation log audit

Evidence source: user-supplied `ipm_stage2_evidence.zip`, entry `_reproducibility_runs/mia_auc_exact_match.log` (reviewed 2026-11-17).

## What the archived log supports

- Exactly **63** rows matching the expected key pattern `(dataset, seed, epsilon)`.
- All 63 keys unique: FiQA, SciFact, TREC-COVID have 21 rows each (3 seeds × 7 epsilon levels).
- All seven epsilon levels have nine rows each.
- `recalc_auc` vs `canonical_auc` delta: maximum **1.110223e-16** in the archived log.
- Each row's `canonical_rows` equals 1, indicating unique canonical mapping in that logged check.
- Comparing displayed 6-decimal `canonical_auc` to full-precision values from `runs/_summary/stage3_all3/mia_matched_all.csv` shows discrepancies up to **4.8e-7**, consistent with the *display rounding* in the log. Do not misinterpret this display precision loss as a mismatch of the underlying recomputation.

## Important evidence boundary

The supplied evidence ZIP includes the above log and `mia_matched_all.csv`, but contains **zero** raw `attacks/stage3/mia_matched_eps_*/attack_summary.json` source files. A diagnostic log prints one example run summary and identifies local paths, but does not bundle the full source outputs.

Therefore the available audit supports **historical AUROC recomputation consistency**, not an independent re-execution of MIA from `guard_embeddings.npy` or a complete, published raw-score audit.

The original MIA source scripts are now public at `scripts/stage3/`; the original run input arrays, source attack items and complete historical log outputs remain the principal evidence gap.

## Avoiding overclaim

Permitted: \"An archived 63-condition MIA AUROC recalculation log reported exact agreement to floating precision; its condition keys and summary values were cross-checked against the supplied Stage 3 table.\"

Not permitted: \"All 63 matched-MIA experiments were rerun independently from public embeddings.\"
