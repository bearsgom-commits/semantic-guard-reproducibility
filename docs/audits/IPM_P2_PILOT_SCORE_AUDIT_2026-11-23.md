# P2 SciFact seed-7 factorial attack pilot — score-audit review
Date: 2026-11-23 KST

**Status: saved-score arithmetic audited by author (4/4); substantive security validity unresolved.**
These are user-reported execution logs, not independently accessible raw research output, so this note does not claim an independent scientific rerun.

## Empirical results (user-reported)
| D | bits | AUROC | one shuffled-score control |
|---:|---:|---:|---:|
| 128 | 4 | 0.494510 | 0.495682 |
| 128 | 10 | 0.494094 | 0.504328 |
| 320 | 4 | 0.500160 | 0.486790 |
| 320 | 10 | 0.497603 | 0.493186 |

Observed console assertions:
- `P2_PILOT_PASS dataset=scifact seed=7 cells=4 sample_per_class=2500`
- `RETRIEVAL_EXECUTED=NO`
- `ORIGINAL_INPUT_HASHES_UNCHANGED=YES`
- `P2_OUTPUT_AUDIT=PASS_4`
- `P2_SCORE_CONTROLS=PASS_4`
- `ATTACK_POSITIVE_SENSITIVITY=NOT_TESTED`

## What has been established
The author successfully ran the separate four-cell experiment and the score-file auditor. The auditor checks matched ordered row indices, balanced classes, source item-file SHA-256, reconstruction of all stored attack scores from individual feature values, AUROC re-calculation, and trivial score-ranking arithmetic controls. A single label-shuffle draw per cell is **not** an inferential permutation test.

## Critical attack-definition issue
The current matched attack creates its index from the **exact member representation rows** but explicitly excludes their self-similarity during member feature extraction. This answers a leave-one-out *local neighborhood* distinguishability question, not the strongest index-membership attack available to an adversary able to inspect the entire index. With exact vector access and deterministic equality, a direct self-lookup can reveal sampled index membership; an explicit self-inclusion positive control is required before treating the near-0.5 leave-one-out result as evidence of confidentiality.

Hence none of the following is supported by the four AUROCs alone:
- protection from membership inference in general;
- general low information exposure or confidentiality;
- no dimension/bit effect (single dataset, one projection seed, limited attack);
- the final Utility–Stability–Exposure trade-off.

## Next bounded falsification gate (one cell only)
For SciFact, seed 7, D=128, B=4, and the **identical** saved cohort:
1. Reconstruct sampled Guard rows from the same frozen E5 corpus and Guard source; verify input/cohort fingerprints;
2. Recalculate member and nonmember scores with **self-exclusion** and compare to saved attack scores (numerical replay control);
3. Recalculate with **member self-match allowed** and report both the original fixed weighted score AUROC and a direct maximum-similarity AUROC;
4. Verify this positive-control path distinguishes an exact index self-match; if it does not, inspect code/ties/numerical identities and halt;
5. Never merge self-inclusive and leave-one-out values as the same attack or silently change existing results.

**Stop rule:** do not expand to 36 security cells before this attack-semantic gate. After the gate, distinguish a strong T2/exact-index observer from the narrower leave-one-out neighborhood-proxy adversary, then select a defensible prospective security endpoint.

Source code: `reproducibility/ipm_p2_security_20261123/scripts/ipm_p2_index_membership_pilot_v1.py` and `reproducibility/ipm_p2_security_20261123/scripts/ipm_p2_score_controls_v1.py`.
