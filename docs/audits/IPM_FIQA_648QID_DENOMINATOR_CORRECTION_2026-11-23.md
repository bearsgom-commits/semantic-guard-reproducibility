# IP&M historical FiQA judged-query denominator correction — 2026-11-23 KST

## Execution evidence
Evidence status: **author-reported Mac console**, audit script committed at `8e72dd04c04937c1b1a99fff4dd1b481f93e209f`; not an independent third-party rerun. Original rankings unchanged. Local artifact: `~/Downloads/IPM_FIQA_HISTORICAL_648QID_AUDIT_20261123`.

Console markers:
- `FIQA_648QID_REAUDIT=PASS_12`
- `HISTORICAL_UNJUDGED_IN_DENOMINATOR=YES`
- `RETRIEVAL_EXECUTED=NO`
- For all 12 saved top100 ranking sets, `SUMMARY_MATCH=TRUE`.

## Exact reported 12-cell nDCG@10 values
| seed | mode | eps | historical (6648 qids) | judged (648 qids) |
|---:|---|---:|---:|---:|
| 7 | raw | 0 | 0.03718189 | 0.38145861 |
| 7 | guard | 0 | 0.00375929 | 0.03856757 |
| 7 | guard | 32 | 0.02921584 | 0.29973287 |
| 7 | guard | 64 | 0.03717931 | 0.38143221 |
| 13 | raw | 0 | 0.03718189 | 0.38145861 |
| 13 | guard | 0 | 0.00366183 | 0.03756768 |
| 13 | guard | 32 | 0.02785546 | 0.28577635 |
| 13 | guard | 64 | 0.03717931 | 0.38143221 |
| 42 | raw | 0 | 0.03718189 | 0.38145861 |
| 42 | guard | 0 | 0.00393654 | 0.04038594 |
| 42 | guard | 32 | 0.02782411 | 0.28545480 |
| 42 | guard | 64 | 0.03717931 | 0.38143221 |

## Finding
Historical stage3 FiQA had `n_queries=6648`, but BEIR test-qrels includes 648 judged query IDs. Recomputing from immutable Top100 files reproduces the historical all-6648 mean and recovers standard judged-648 mean. Consequently the historical metric is scaled downward by factor `648/6648` (correction multiplier `6648/648 = 10.259259...`). This is a **confirmed historical evaluation denominator issue**, not a broken encoder or a failed rerun.

Other datasets:
- SciFact separately confirmed 1109 vs 300 unjudged-as-zero denominator artifact in 12 paths (factor `1109/300`).
- TREC-COVID historical summary=50, test-qrels=50; no denominator mismatch in the preliminary count audit, but row-level scoring not independently checked here.

## Interpretation/next gate
1. Preserve immutable Stage3 results; publish separately named corrected judged-test-set metrics with an explicit migration map from affected historical tables/plots.
2. Existing prospective E5 2×2 36-cell runner intentionally evaluates qrels-judged queries only. Verify published manifests against that source before asserting no impact; do not rerun all 36 cells.
3. Same-denominator multiplicative corrections do **not** automatically imply all relative comparisons change. Absolute score thresholds, absolute effect contrasts and confidence intervals may require recalculation.
4. Do not compare historical full-query averages directly with the new GTE's 300 judged-query averages.
5. The original frozen v18 LaTeX manuscript is still missing from the current audit context; statement-by-statement change impact remains source-blocked.
6. Distinguish historical Stage3 denominator artifact from previously reported E5 36-cell clean judged-query design.
