# IP&M P2 — T1b Anchor-assisted Re-ID 4-cell pilot result (2026-11-24 KST)

## Evidence tier and execution
Author-reported Mac terminal run of prospectively specified T1b script (source commit `f0d2420e764bac5d096d453555fd501ae8282537`). Source and remote-committed script are available; **per-target private CSV and original experimental result hashes were not independently transferred/re-executed**. Author console:
- `P2_ANCHOR_REID_4CELL=PASS_4`
- `RETRIEVAL_EXECUTED=NO`
- `ORIGINALS_MODIFIED=NO`
- New local directory: `~/Downloads/IPM_P2_ANCHOR_REID_4CELL_20261124`.

## Prospective fixed attack
SciFact seed7, D={128,320}, bits={4,10}; 256 disjoint labeled raw/Guard anchor pairs, 256 target documents, 4744 identified raw-reference candidates. Raw->Guard ridge alignment trained only on anchors with fixed alpha 1; attacker model does not receive true Guard projection matrix. Target IDs and candidates fixed across four conditions. Attack is **conditional auxiliary-reference linkage**, not plaintext recovery, training-set membership inference, or generic privacy guarantee.

| D | bits | Top1 hits/256 | Top1 % | Top5 hits/256 | Top5 % |
|---:|---:|---:|---:|---:|---:|
| 128 | 4 | 210 | 82.03125 | 245 | 95.703125 |
| 128 | 10 | 256 | 100 | 256 | 100 |
| 320 | 4 | 249 | 97.265625 | 256 | 100 |
| 320 | 10 | 256 | 100 | 256 | 100 |

Random uniform target candidate reference: Top1=1/4744, Top5=5/4744; this is not an attacker-reality baseline.

## Conditional descriptive effects, Top1
- D effect across both bit levels: 7.6171875 percentage points (because 4-bit D effect 39/256=15.234375 pp, while 10-bit D effect 0).
- Bits effect across both dimension levels: 10.3515625 pp (17.96875 pp at D128, 2.734375 pp at D320).
- D×bits difference-in-differences: -15.234375 pp, using (D320 B10 - D320 B4) - (D128 B10 - D128 B4). No interval yet; do not declare significance.
- All four Top5 values are near ceiling; Top5 is poor for detecting factorial differences under this attacker.

## Decision
**P2_ANCHOR_REID_PILOT_EXECUTED=PASS (author-reported).** High linkage observed even in 128/4, under strong 256-anchor and 4744-raw-reference assumptions. Such high success is **not proof of plaintext recovery**, nor does it refute representation constraints under all threat models.
**P2_STATISTICS_AND_EXTERNAL_VALIDITY=OPEN.** The next step is to validate private per-target files against the run manifest and calculate matched 256-target conditional uncertainties, not rerun retrieval or repeat the attack. New source `ipm_p2_anchor_reid_paired_inference_v1.py` was committed at `49eedd0b6790eff19b308966d2f8af42b6eb9183`.

The data have not been integrated into the paper because the attack assumptions and scope must be explicitly specified; independent evidence auditing, fixed-cohort sensitivity and manuscript claim mapping remain.
