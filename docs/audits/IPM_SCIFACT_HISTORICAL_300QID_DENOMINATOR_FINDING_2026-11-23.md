# IP&M SciFact historical nDCG denominator finding — 2026-11-23 KST

## Status and evidence tier
Author-reported Mac re-audit **PASS_12** on stored historical Top-100 rankings, using `reproducibility/ipm_p3_second_encoder_20261123/scripts/ipm_scifact_historical_300qid_reaudit_v1.py` (script commit `6f6e8e37e103ffac45e0d957bbf9c5fd715963d4`). No retrieval/embedding rerun. Raw local audit outputs were not transferred to this reviewer.

The original `runs/_summary/stage3_all3/retrieval_all.csv` SciFact rows report 1,109 evaluated queries, while BEIR SciFact test qrels contain 300 judged qids. Recomputing directly from stored 1,109-qid rankings gives exactly the historical aggregated nDCG@10 for all 12 checked paths, and recomputing on 300 judged qids gives approximately `1109/300` times the historical metric. **809 unjudged queries had been included with zero relevance in the historical mean.**

## Author-reported values
| seed | mode | epsilon | historical nDCG10 / 1109 | judged nDCG10 / 300 |
|---:|---|---:|---:|---:|
| 7 | raw | 0 | 0.18770835 | 0.69389518 |
| 7 | guard | 0 | 0.03698169 | 0.13670896 |
| 7 | guard | 32 | 0.16087929 | 0.59471709 |
| 7 | guard | 64 | 0.18769140 | 0.69383255 |
| 13 | raw | 0 | 0.18770835 | 0.69389518 |
| 13 | guard | 0 | 0.03762766 | 0.13909693 |
| 13 | guard | 32 | 0.16524318 | 0.61084894 |
| 13 | guard | 64 | 0.18769140 | 0.69383255 |
| 42 | raw | 0 | 0.18770835 | 0.69389518 |
| 42 | guard | 0 | 0.03025149 | 0.11182967 |
| 42 | guard | 32 | 0.16134702 | 0.59644613 |
| 42 | guard | 64 | 0.18769140 | 0.69383255 |

All 12 reported `SUMMARY_MATCH=TRUE`; `SCIFACT_300QID_REAUDIT=PASS_12` and `HISTORICAL_UNJUDGED_IN_DENOMINATOR=YES`.

## Research implications
1. Historical low E5 SciFact nDCG was substantially an **evaluation denominator artifact** rather than proof the encoder failed. The E5 RAW judged-query nDCG@10 = 0.69389518, versus 0.18770835 previously reported on 1109 queries.
2. GTE second encoder was evaluated on 300 judged SciFact queries. Published comparisons of old E5 1109 means vs GTE 300 means are invalid. E5 RAW judged value is greater than the reported GTE Guard-320/10 3-seed mean (~0.667), but RAW vs protected-Guard is not a same-factor encoder performance comparison.
3. E5 historical eps32 and prospective E5/GTE 2×2 factorial should **not** be treated as interchangeable merely because labels/projection dimensions coincide. Match code, raw sources, ranking and qrels before cross-encoder contrast.
4. Retrieval recall@10 is also affected; re-audited 300-qid estimates and per-qid effects are retained in separate local CSV; no original results are overwritten.
5. Scope: SciFact only. Inspect FiQA and TREC-COVID qrels denominator/evaluation before assuming the artifact is universal. Review manuscript statistical tables/figures and any conclusions that depend on the original E5 SciFact low baseline; resolve frozen v18 source blocker.
6. This verification is source-consistent recalculation, not independent new model generation or full reproduction. Old full-1109 metrics remain historical records for traceability, **not** valid standard judged-test-set estimates.

## Next decision gate
Perform a **read-only three-dataset qrels coverage audit** on historical retrieval summaries/rankings. If denominator issues extend beyond SciFact, define a separate corrected 300/648/50 judged-query metric table and paired query analysis, retaining immutable originals. Verify whether the previously completed prospective 36-cell 2×2 results were already judged-qid-only (the factorial source says YES), to avoid unnecessary repetition. Do not submit a manuscript mixing different denominator definitions.

No manuscript, original Guard code, frozen run output or prior 36-cell result was modified.
