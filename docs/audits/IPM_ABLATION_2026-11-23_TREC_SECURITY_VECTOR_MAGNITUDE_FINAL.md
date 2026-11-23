# TREC-COVID historical attack-input versus factorial canonical vector discrepancy — final sampled numerical audit

**Date:** 2026-11-23 (KST). **Source:** author's pasted read-only Mac terminal output. Not an independently executed attack or full-vector audit.

## Numeric evidence

Historical attack-referenced representation: `artifacts/trec-covid/intfloat_multilingual-e5-base/seed{seed}/L3_a0.2_eps{eps}/guard_embeddings.npy` (5000 rows).

Canonical new factorial diagonal representation: `artifacts/trec_covid/intfloat_multilingual-e5-base/stage3/seed{seed}/eps_{eps:02d}/guard_embeddings.npy` (171332 rows).

The prior check established matching first 5000 corpus IDs (`FIRST_5000_IDS_MATCH=True`) and 6/6 compatible shape/dtype. The following compares **64 evenly spaced rows per condition** with 64-bit arithmetic on the sampled float32 vectors. `np.allclose(..., atol=1e-6 or 1e-4, rtol=0)` failed in all cases.

| seed | eps | maximum absolute difference | mean absolute difference | close 1e-6 | close 1e-4 |
|---:|---:|---:|---:|---|---|
| 7 | 0 | 0.134723574 | 0.0122211296 | False | False |
| 7 | 32 | 0.108489573 | 0.00773082762 | False | False |
| 13 | 0 | 0.133887704 | 0.0133298858 | False | False |
| 13 | 32 | 0.10216685 | 0.00772690283 | False | False |
| 42 | 0 | 0.131598283 | 0.0120826732 | False | False |
| 42 | 32 | 0.103409547 | 0.00791289256 | False | False |

`READ_ONLY_COMPLETE` was reported.

## Conclusions

- These are **material observed vector deviations**, not a bytewise identity issue that disappears with an absolute tolerance of 1e-4.
- The precise root cause (legacy projection seed or algorithm, embedding/version/input differences, transformation order, normalization, row ID lineage beyond examined prefix) is **not established**. Do not assert a particular cause or that historical attacks were invalid.
- No numeric security estimate from TREC-COVID historical MIA/Re-ID should be transferred as a measured exposure of the new factorial diagonals. The historical 5000-row scope and vector differences should be reported separately.
- The prior 18/18 sampled-vector PASS tested canonical `stage3` arrays against prospective regenerated *diagonal* vectors. It did **not** test legacy `L3_a0.2` attack arrays; the two observations are not contradictory.
- Historical matched MIA has separately checked path/labels, but attack conditions still require separate threat-model validation. The two *off-diagonal* new factorial representations have no directly measured security exposures.
- Avoid broad Utility–Stability–Exposure causal inference across these different representation/attacker conditions; limit factorial claims to measured retrieval and stability.
- Do not modify source Guard code, old security runs, new factorial outputs or v18 manuscript.

## Next gates
1. Freeze this evidence as an explicitly separate security-analysis limitation (no further ad hoc reruns necessary to establish mismatch).
2. Finish GitHub reproducibility package by committing executed code and permitted safe result tables with checksums; ledger + hash index alone are not complete reproduction.
3. Produce review-by-review proposed manuscript edits for author approval, explicitly noting unmeasured off-diagonal attack exposure and fixed-seed inference limitations.

This document is post-execution evidence. The numeric results derive from the author's local command output and are not separately verifiable from raw embedding arrays on GitHub.