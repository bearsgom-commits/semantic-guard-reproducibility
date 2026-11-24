# IP&M P2 — T1b three-seed sensitivity closeout (2026-11-24 KST)

## Provenance

Author-reported local stdout from `ipm_p2_anchor_reid_seed_sensitivity_v1.py` at GitHub commit `2994c0c81dcdbea00e893f35589bce7b1f29fc0b`; new runs completed with `P2_T1B_SEED_SENSITIVITY=PASS_8`, `RETRIEVAL_EXECUTED=NO`, `ORIGINALS_MODIFIED=NO`. Seed-7 original T1b output previously reported `PASS_4`. Reviewer did not independently execute local experiment or access private per-target rows.

Same SciFact 5000-row sampled candidate union; 256 known raw/Guard anchors, 256 disjoint fixed target rows, 4744 candidate references. Projection seeds 7, 13, 42; 2×2 factors D=128/320, bits=4/10; exact Guard matrix not given to attacker. Fixed ridge alignment (alpha 1). Same target IDs and anchor IDs reused **across seeds** (not 768 independent targets). Original index-membership MIA labels play no role in the new ReID outcome.

## Raw success counts (Top1/Top5 out of 256 fixed target rows)

| seed | 128/4 | 128/10 | 320/4 | 320/10 |
|---|---|---|---|---|
| 7 | 210/245 | 256/256 | 249/256 | 256/256 |
| 13 | 218/245 | 256/256 | 246/255 | 256/256 |
| 42 | 202/240 | 256/256 | 249/256 | 256/256 |

Numbers above in each cell are `Top1_hits / Top5_hits`, each with denominator 256.

## Descriptive across-seed means

| condition | mean Top1 | mean Top5 |
|---|---:|---:|
| D128 B4 | 630/768 = 0.8203125 | 730/768 ≈ 0.9505208333 |
| D128 B10 | 768/768 = 1 | 768/768 = 1 |
| D320 B4 | 744/768 = 0.96875 | 767/768 ≈ 0.9986979167 |
| D320 B10 | 768/768 = 1 | 768/768 = 1 |

The 768 here is a sum of 3 runs over the SAME 256 target documents; **it is not an independent document sample size**. 3-seed means are descriptive, with no valid independent-sample CI for 768 documents.

Descriptive Top1 marginal D effect (128→320) = +0.07421875; marginal bits effect (4→10) = +0.10546875; interaction (D320B10−D320B4)−(D128B10−D128B4)=−0.1484375, all as probability differences. These values are **not** accompanied by inferential intervals here. Fixed seed7 separately had paired Bonferroni-3 CIs.

## Methodological conclusion

- Directional ranking is consistent across all three tested projection seeds: 128/4 least re-identifiable, both 10-bit cells fully re-identified, and higher D at 4-bit yields higher Top1 linkage. No monotonicity outside these four settings is established.
- Attack's high success (even at 128/4) demonstrates conditional linkage exposure **given attacker access to identified raw references for all candidates and 256 paired anchors**; not direct text reconstruction, not training-data MIA, not a universal privacy failure.
- Top5 near saturation and Top1 at 10-bit ceiling limit discriminating ability.
- Fixed-cohort seed sensitivity reduces the concern that the result is unique to seed7 but does not establish across-corpus or across-anchor generality.
- Earlier independent-random-projection historical ReID and the four-cell index-membership AUROC≈0.5 results refer to distinct threat models; do not pool or represent as contradictory measurements of the same endpoint.
- E5 36-cell utility/ranking and ReID 12-cell SciFact-only security datasets are not a fully matched 36-cell 3-axis statistical factorial design.

## Decision / stop rule

**P2_SECURITY_PILOT_GATE=CLOSED_CONDITIONALLY** (12 cells author-reported PASS: seed7 initial 4 + seed13/42 additional 8). No further security runs are authorized by this record; further seeds, anchors or datasets require a specific manuscript claim or reviewer request and explicit new prespecification.

Next: P4 evidence reconciliation and v19 manuscript claims. P4 must map actual factorial results to D/B settings and not create artificial joint CIs; final manuscript can state bounded SciFact T1b results under explicitly specified auxiliary-reference access. Keep all private row-level outputs local; publish only aggregate results/protocols with approval.

Sources: `docs/audits/IPM_P2_ANCHOR_REID_4CELL_PILOT_RESULT_2026-11-24.md`, `docs/audits/IPM_P2_ANCHOR_REID_PAIRED_CI_RESULT_2026-11-24.md`, `docs/audits/IPM_V19_P2_SECURITY_CLAIM_DRAFT_2026-11-24.md`, and user-provided Mac stdout dated 2026-11-24.
