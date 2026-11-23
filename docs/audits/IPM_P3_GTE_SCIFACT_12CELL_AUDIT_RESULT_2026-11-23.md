# IP&M P3 — GTE SciFact 12-cell results and audit closeout
Date: 2026-11-23 KST

## Status and evidence tier
**Author-reported local audit: PASS_12.** Not an independent third-party replication. The raw rank files and output manifests remain in the author's local Mac and have not been transmitted to this reviewer; therefore original file SHA-256 values cannot be independently confirmed from this note alone.

- Second encoder: `Alibaba-NLP/gte-multilingual-base`
- Resolved model SHA: `9bbca17d9273fd0d03d5725c7a4b0f6b45142062`
- Remote-code SHA: `40ced75c3017eb27626c9d4ea981bde21a2662f4`
- Dataset: SciFact, 5,183 corpus docs, 300 test-qrels judged queries.
- Seeds: 7, 13, 42; factorial D={128,320}, bits={4,10}.
- Exact audit runner: `reproducibility/ipm_p3_second_encoder_20261123/scripts/ipm_p3_scifact_12cell_audit_v1.py` committed `cd532f1a4c28c26652f93a671847ce9c7f4f1aab`.
- Author output: `~/Downloads/IPM_P3_GTE_12CELL_AUDIT_20261123`
- Console result: `P3_12CELL_AUDIT=PASS_12`.

## Results as reported
| seed | nDCG@10 D128/B4 | D128/B10 | D320/B4 | D320/B10 |
|---:|---:|---:|---:|---:|
| 7 | 0.44625966 | 0.58397886 | 0.49484356 | 0.65622941 |
| 13 | 0.45664251 | 0.59968066 | 0.54005247 | 0.68452323 |
| 42 | 0.46723028 | 0.61510143 | 0.52429335 | 0.66011382 |

Computed 3-seed average contrasts (all are **descriptive**, not inferential):
- Dimension main effect: `+0.06519374` nDCG@10.
- Bit-precision main effect: `+0.14505093` nDCG@10.
- Difference-in-differences interaction: `+0.00434952` nDCG@10.

These four cells share the same model and judged-query IDs, and the audit checks each ranking's source hashes, query order, ranking/metric consistency and the common qrels.

## Interpretation boundaries and important counterarguments
1. Seed=3 represents only three projection seeds, **not independent sets of 300 queries**. Do not treat 900 query/seed observations as independent in an unclustered CI. A paired-by-query analysis across the same 300 qids, with seed-level sensitivity explicitly shown, is a defensible next descriptive/uncertainty step. Seed-to-seed generalization is very limited at n=3.
2. The average bit effect is greater than the average dimension effect in this experimental range, **not universally for Guard nor all encoders/data**.
3. No privacy, protection or information-leakage conclusion is established by these GTE retrieval results.
4. Cross-encoder superiority cannot be claimed by comparing these numbers with historical E5 before confirming E5's language prefixes, query/corpus text processing, aligned BEIR qrels IDs, ranking and any prior anomaly.
5. Factor interactions vary in sign across seeds; a small pooled interaction does not prove zero interaction.
6. The original E5 36-cell experiment and frozen manuscript/Guard source remain untouched.

## Gate decision
**P3-empirical-12 PASS; P3-paper-statistics PENDING.**
Next: (i) paired query-level effect confidence interval/audit with explicit family and seed dependence; (ii) exact E5 preprocessing/cohort/method comparability audit; (iii) integrate into P4 only after scope checks.
No automatic GTE 36-cell expansion without scientific necessity.
