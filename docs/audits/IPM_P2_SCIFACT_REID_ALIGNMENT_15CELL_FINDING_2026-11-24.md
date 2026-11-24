# IP&M P2 SciFact historical ReID alignment audit — 2026-11-24 KST

## Status
**ID_ORDER_CHECK_PASS_15_WITH_ASSUMPTIONS** based on author-reported Mac console from read-only script `ipm_p2_historical_reid_alignment_audit_v1.py` (source commit `15e6574cb69c75c0d0efbf85205038d5b59f37ce`). Author-local machine execution; reviewer did not independently read the files.

- `CORPUS_CANONICAL_ID_ORDER_EQUAL=TRUE`.
- `PRESENT_ATTACK_ITEMS=15` out of 3 seeds (7,13,42) × 5 historical eps (0,8,16,32,64).
- Every observed attack item file: 5,183 rows, Guard representation shape 5,183 × the expected dimension (eps0=128, eps8=224, eps16=256, eps32=320, eps64=768).
- All 15 printed `status=ID_ORDER_GATE_PASS_WITH_ASSUMPTIONS`.
- No attack executed, no original modified.

**Output classification correction:** script overall status `PARTIAL_AUDIT_PASS_REVIEW_MISSING` is a logic/wording defect. It emits that value whenever at least one cell passed even if all 15 required files were present and passed. The per-cell results, not the misleading aggregate label, support a 15/15 ID-order check. This does **not** prove independent Guard document-ID lineage if the Guard files lack explicit row-to-ID identifiers; also does not independently verify attack model correctness.

## Remaining separate methodological problem
Original historical `run_attack_reid.py` compares Guard vectors against independent random projection of raw embeddings using RNG seed `20260401+target_dim`; actual Guard projection depends on experimental seed and uses different RNG call plus quantization. Its 1/5/10-row identity retrieval rates measure paired-row matching to known raw E5 candidate vectors under these reference assumptions, **not** text recovery or training membership. At historical eps64 raw reference dimensionality matches Guard so projection bypassed, altering the attacker comparison conditions.

## Decision
- Keep 15-cell historical ReID as auxiliary, explicitly conditional descriptive evidence.
- Do not use as directly comparable same-cell security endpoint for 2×2 factorial without prospective pre-specified scoring protocol.
- Do not repeat 15-cell alignment check.
- Next: inspect an existing P2 four-cell pilot manifest and fixed cohort, then design a paired 4-cell **known-matrix reference attack** with validated candidate-ID order and explicit assumed attacker knowledge. Include independent-projection T1 negative control only when scientifically defensible.
- Do not rerun historic 36-cell retrieval; new security analyses must be separately labeled.

Evidence tier: author-reported console transcript and previously audited source-line extracts.
