# IP&M P2 prospective anchor-assisted ReID paired inference result — 2026-11-24 KST

## Evidence provenance
Author-reported Mac terminal output from `ipm_p2_anchor_reid_paired_inference_v1.py` committed at `49eedd0b6790eff19b308966d2f8af42b6eb9183`. The source script cross-checks SHA256 for `reid_manifest.json`, `target_hits_PRIVATE.csv` and `reid_4cell_summary.csv`, paired 256-row total hits, and previously documented cell totals. Source files were kept locally private; no independent third-party re-execution is claimed.

Reported log:
- `P2_ANCHOR_REID_PAIRED_AUDIT=PASS_6`
- `NO_ATTACK_RERUN=TRUE`
- `PRIVATE_TARGET_ROWS_NOT_EXPORTED=TRUE`
- Local output `~/Downloads/IPM_P2_ANCHOR_REID_STATS_20261124`.

## Top-1 prospective fixed-seed effects

| contrast | point probability difference | Bonferroni-3 familywise 95% paired-target percentile interval |
|---|---:|---|
| Dimension 128→320 | +0.076172 | [+0.046875,+0.107422] |
| Bits 4→10 | +0.103516 | [+0.072266,+0.136719] |
| Interaction (D320B10−D320B4)−(D128B10−D128B4) | −0.152344 | [−0.214844,−0.093750] |

## Top-5 prospective fixed-seed effects

| contrast | point probability difference | Bonferroni-3 familywise 95% paired-target percentile interval |
|---|---:|---|
| Dimension 128→320 | +0.021484 | [+0.007812,+0.037109] |
| Bits 4→10 | +0.021484 | [+0.007812,+0.037109] |
| Interaction | −0.042969 | [−0.074219,−0.015625] |

Four-cell Top1 counts: D128B4 210/256, D128B10 256/256, D320B4 249/256, D320B10 256/256.
Four-cell Top5 counts: D128B4 245/256, all other conditions 256/256.
The target candidate reference pool has 4744 rows; 256 known raw-Guard anchor pairs train a fixed-alpha ridge reference estimator with unknown actual projection matrix, and the same 256 target IDs are ranked at every cell. The attacker can access identifiable raw vectors for **all** candidate documents. This is an auxiliary-information cross-representation document linkage experiment, NOT plaintext recovery or training-data membership inference.

## Statistical meaning and boundaries

- All six reported intervals exclude 0 within their respective **separate Top1 vs Top5 three-contrast families**. There is NO simultaneous six-contrast or combined utility/stability/security 95% guarantee.
- Bootstrap target IDs are paired across cells, conditional on fixed anchors, fixed seed7, fixed candidate reference set, attack estimator and dataset. This does not capture variation due to projection seeds, independently selected anchor sets or dataset populations.
- Scores at ceiling induce discrete/asymmetric uncertainties. Bootstrap methods may be fragile at boundary probabilities; interpret inferential reach conservatively.
- The negative interaction reflects saturation in 10-bit cells, not proof of a universal nonlinear privacy law.
- Very high linkage under strong auxiliary information is evidence against general non-linkability **for that specified attacker**, not against nonpersistent plaintext storage in general. No generic privacy guarantee or legal privacy claim follows.
- The comparison to historical ReID is qualitative only; historical independent random projection and fragile prefix alignment were different protocols. The prior matched index-membership AUROCs address yet another endpoint.
- The four-cell pilot was prospectively configured, but its 256 targets are only one fixed selection; no independent holdout across alternate anchors has been shown.

## Decisions

**Gate P2 pilot + paired inference:** PASS from author output (not external independent replication).
**Gate cross-seed external validity:** OPEN.
**Gate simultaneous 3-axis factorial utility/ranking/exposure claim:** OPEN; requires matched dataset/cell/seed and valid uncertainty per endpoint.
**No repeat of original 36-cell retrieval.**

Recommended next **bounded** step: a second/third seed and a prespecified alternative disjoint anchor selection sensitivity with unchanged attack settings, with explicit stop criteria, *only if* manuscript's headline requires a general D/B security trade-off. In parallel, begin v19 source claim corrections and comparator P4; do not hold the entire manuscript hostage to security extension.
