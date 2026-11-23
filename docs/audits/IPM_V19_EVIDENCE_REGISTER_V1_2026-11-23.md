# IP&M v19 evidence register v1 (2026-11-23 KST)

## Evidence standard
Source checks against GitHub and author-reported Mac audit outputs are explicitly distinct; no independent end-to-end reproduction is claimed. Historic experiment outputs, Guard source and frozen v18 remain immutable.

| ID | Evidence | Verified scope | State / publication gate |
|---|---|---|---|
| E01 | New E5 crossed D={128,320}, B={4,10}; FiQA/SciFact/TREC-COVID × seeds 7/13/42 | GitHub runner selects only judged qrels IDs; 36-cell aggregate and CI audit previously reported | 36-condition summary exists; individual E5 cell manifests not found in Downloads scan. **Do not claim manifest-level independent PASS** |
| E02 | GTE 12-cell SciFact crossed factorial | 300 matched judged qids; three fixed seeds; separate Bonferroni-3 CIs | Author-reported PASS_12 and PASS_3; statistical script is not yet committed. Cross-encoder performance comparison requires matched transformations |
| E03 | Historical E5 FiQA | 6648 qids originally averaged, only 648 qrels-judged | Ranking read-only re-audit PASS_12. RAW nDCG@10 0.03718189 historical versus 0.38145861 corrected judged-only |
| E04 | Historical E5 SciFact | 1109 qids originally averaged, 300 judged | Ranking read-only re-audit PASS_12. RAW nDCG@10 0.18770835 historical versus 0.69389518 corrected |
| E05 | Historical TREC-COVID | 50 qids in both summary and test qrels | Denominator counts match; independent rescoring not performed here |
| E06 | E5 SciFact source lineage | mean pooling; E5 query/passages prefixes; normalize L2; model revision d128750597153bb5987e10b1c3493a34e5a4502a | SciFact clean replay and canonical raw embedding hash PASS (author log); not full 36-cell replay |
| E07 | P2 index-membership proxy | SciFact seed7 D128 B4, 2500 members and 2500 nonmembers | Leave-one-out AUROC 0.494510 and exact self-match AUROC 1.0 are different attacker assumptions; neither proves semantic ReID/privacy |
| E08 | Historical ReID/MIA | Older representation and candidate cohorts | Cannot directly integrate as factorial same-cell security measurements |
| E09 | Frozen v18 manuscript | SHA256 08c0a2e6462c805b70fe3650d7c6bef28b359cb97759df3c0d64a3417dbafdc8 | Verified from ZIP member on author's Mac. Full text not independently read; claim mapping pending |
| E10 | Utility/stability estimates | Separate Bonferroni-18 and Bonferroni-45 families | No joint 63-way simultaneous CI or general population-of-seeds coverage |

## Publication decision
- Historical FiQA/SciFact full-query averages must NOT be compared directly to qrels-judged new experiments.
- Re-score or correct old metrics as separately versioned outputs; never overwrite original results.
- P2 security effect comparisons are pending a realistic, explicitly specified attack; saturated self-inclusion is not an adequate factorial privacy endpoint.
- Original E5 36-cell run must not be repeated solely because current per-cell manifest discovery failed.
- Inferential estimates, raw baselines, document counts and model-specific input conditions must be disclosed explicitly.
- Frozen v18 text is recovered but detailed professor-comment-to-claim map remains pending.
- Preserve private line-level records and source text locally; public GitHub carries non-sensitive protocol and aggregates.

**G1:** numeric claim register traced to source and denominator. **G2:** P2 attacker capability and metric. **G3:** v18 manuscript text mapping. **G4:** P4 comparator cohort alignment.

Status: REGISTER_V1_CREATED / NUMERIC_AND_SECURITY_GATES_PENDING.
