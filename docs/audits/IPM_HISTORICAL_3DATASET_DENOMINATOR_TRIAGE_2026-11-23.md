# IP&M Stage3 historical three-dataset evaluation denominator triage — 2026-11-23 KST

**Evidence tier:** author-reported local source counts and SciFact ranking re-audit, not independent remote execution.

| Dataset | Historical summary n_queries | Test qrels judged query count | Mismatch | Evidence level |
|---|---:|---:|---|---|
| FiQA | 6648 | 648 | YES | Query-count mismatch established; historical metric averaging procedure **not yet verified** |
| SciFact | 1109 | 300 | YES | Existing 12-path ranking re-audit PASS; 809 unjudged queries counted as zero in historical nDCG denominator |
| TREC-COVID | 50 | 50 | NO | Query counts match only; no independent ranking-metric re-audit in this gate |

FiQA raw counts must not be asserted as scoring artifact before actual 648 judged-qid ranking recalculation. If historical FiQA all-6648 values match re-scores and judged-648 values differ by factor 6648/648, prior Stage3 FiQA aggregate performance is denominator-biased. E5/GTE or cross-dataset conclusions must use a common judged test-qrels denominator.

Prospective E5 36-cell factorial source `ipm_ablation_factorial_runner_v2.py` evaluates judged qids only; **do not rerun the completed 36 retrieval cells**. Keep historic original files immutable. Auditor for FiQA 3 seeds × RAW/Guard eps0/32/64 at `reproducibility/ipm_p3_second_encoder_20261123/scripts/ipm_fiqa_historical_648qid_reaudit_v1.py` (commit `8e72dd04c04937c1b1a99fff4dd1b481f93e209f`); author execution not yet confirmed.

If the FiQA audit fails, inspect missing/mixed-ranked qids or alternate summary lineage; do not relabel failure as a successful denominator correction. The revised manuscript must identify affected original figures, tables and statistical inferential denominators after obtaining exact frozen v18 source.
