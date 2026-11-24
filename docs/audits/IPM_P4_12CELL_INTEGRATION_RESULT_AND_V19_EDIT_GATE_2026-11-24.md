# IP&M P4 12-cell integration and manuscript edit gate — 2026-11-24 KST

## Actual GitHub data sources fetched and cross-checked
- `reproducibility/ipm_ablation_20261123/aggregates/IPM_ablation_statistics_v1/cell_means.csv`: E5 judged-query nDCG@10 and Recall@10, 3 datasets, D={128,320}, bits={4,10}, fixed seeds 7,13,42, 12×2 metric rows; judged QIDs FiQA648/SciFact300/TREC-COVID50.
- `reproducibility/ipm_ablation_20261123/aggregates/IPM_ablation_statistics_v1/factorial_effects.csv`: 18 contrasts, each confidence family of 18, conditional on fixed seeds; for E5 nDCG all three contrasts each dataset were independently recomputed from downloaded cell means and matched the published point effects.
- `reproducibility/ipm_ablation_20261123/aggregates/IPM_ablation_stability_v1/stability_factorial_means_12.csv` and `stability_cells_36.csv`: RAW-relative top1_same, overlap_at_10, flip_at_10 proxy and additional descriptive stability metrics.
- `reproducibility/ipm_ablation_20261123/aggregates/IPM_ablation_stability_ci45_v1/stability_factorial_effects_ci45.csv`: 45 stability contrasts and Bonferroni-45 intervals. CI family NOT combined with utility or T1b ReID.
- `docs/audits/IPM_P3_GTE_SCIFACT_12CELL_AUDIT_RESULT_2026-11-23.md`: author-reported GTE SciFact 12-condition nDCG values. Four means recomputed from the 3-seed cell values and cross-checked against the reported 3 GTE factorial effects.
- `docs/audits/IPM_P2_T1B_3SEED_SENSITIVITY_CLOSEOUT_2026-11-24.md`: author-reported T1b re-identification success counts for three seeds and four matching D/B settings. ReID means recomputed from 12 cell counts, **not** private row-level evidence.
- Generated integrated aggregate CSV `reproducibility/ipm_p4_integration_20261124/aggregates/IPM_P4_12CELL_BOUNDARY_AWARE_INTEGRATION_V1.csv`, GitHub commit `bb6d781c3eff9e493fc4fd476ba435ff947f3c86`.

## SciFact: 3-fixed-seed 2x2 descriptive overview

| D | bits | E5 nDCG@10 (300 judged QIDs) | E5 top1_same to RAW | E5 flip@10 relevance proxy | GTE nDCG@10 (300 judged QIDs) | T1b ReID top1 (256 fixed docs ×3 projection seeds) |
|---|---|---:|---:|---:|---:|---:|
| 128 | 4 | 0.128080 | 0.085556 | 0.613333 | 0.456711 | 0.8203125 |
| 128 | 10 | 0.428484 | 0.392222 | 0.271111 | 0.599587 | 1.0000000 |
| 320 | 4 | 0.227390 | 0.170000 | 0.504444 | 0.519730 | 0.9687500 |
| 320 | 10 | 0.600671 | 0.634444 | 0.118889 | 0.666955 | 1.0000000 |

The same D/B **factor settings** can be aligned across these measures, but they are NOT the same evaluated units: retrieval/stability 300 judged query IDs vs 256 targeted document IDs, and E5/GTE encoding pipelines differ. New T1b attack is 256 identified raw/Guard anchors + identifiable raw vectors of 4744 candidate documents and a learned alignment with unknown true projection matrix. The 3 seed runs share target IDs, anchor IDs and candidate IDs; 768 observations are NOT independent documents.

## Supporting factorial evidence

- E5 SciFact nDCG@10 contrasts from utility CSV: D main +0.13574811, Bonferroni-18 CI [+0.10535545,+0.16625881]; bits main +0.33684233 CI [+0.29461565,+0.37859923]; interaction +0.07287634 CI [+0.01613229,+0.12885831].
- E5 SciFact RAW-relative top1_same from stability CI45: D main +0.16333333, Bonferroni-45 CI [+0.12246698,+0.20635864]; bits main +0.38555556 CI [+0.33086358,+0.43481574]; interaction +0.15777778 CI [+0.08283827,+0.23987901].
- GTE SciFact nDCG@10 contrasts from separate matched 300-QID bootstrap Bonferroni-3: dimension +0.06519374 CI [+0.04517188,+0.08625652], bits +0.14505093 CI [+0.12385282,+0.16704844], interaction +0.00434952 CI [−0.02956088,+0.03731352]; conditional on 3 fixed seeds and GTE method.
- T1b SciFact Top1 seed7 fixed-target bootstrap Bonferroni-3: D +0.076172 [0.046875,0.107422], bits +0.103516 [0.072266,0.136719], interaction −0.152344 [−0.214844,−0.093750], conditional on seed7, fixed target/anchor/reference and assumed auxiliary access. Across seeds 7/13/42, mean D +0.07421875, mean bits +0.10546875, interaction −0.1484375 (DESCRIPTIVE ONLY).

## Interpretation and scientific warning

- E5 retrieval and RAW-relative ranking stability improve toward D320/B10 on SciFact; the high-information T1b reference-linkage attack also saturates at 10-bit.
- These are aligned factor **settings**, not a single joint causal statistical test of utility, stability and exposure. There is no joint three-axis CI or universal optimization threshold.
- ReID is NOT plaintext inversion, extraction risk, unconditional membership inference or differential-privacy protection. Do not write that storing no plaintext proves no privacy exposure. `epsilon` is a structural constraint label, not formal DP epsilon.
- GTE values are higher than E5 in this table, but E5/GTE preprocessing (E5 query/passage prefixes, tokenization, pooling and input alignment, GTE remote-code implementation) has a separate verification history. E5 model/protocol superiority or intrinsic inferiority is not established by this table.
- Fixed 3 seeds are not three independent datasets. Query percentile bootstrap conditions on fixed seed set. The 256 ReID targets differ from 300 judged QIDs.
- The historical all-query denominator bias was corrected for FiQA/SciFact in the prospective factorial work. **Do not reuse old unjudged-query means as if on the judged-query scale**, and do not claim historical results were retroactively rerun.
- RAW-relative `top1_same` is rank identity stability, not semantic correctness; `flip_at_10` is a relevant-document Hit@10 proxy, not human operation or action reversal. `kendall_tau_at_50` is a custom union-ranking convention, not canonical tau-b.
- Lack of 36 individual E5 cell manifests and row-level independent replay is a reproducibility qualification, not proof of fabricated results. GitHub aggregate tables and source code are deposited, while per-query/row-level data are restricted to the original environment.
- No inferential statement jointly covers Bonferroni-18 E5, Bonferroni-45 stability, Bonferroni-3 GTE and Bonferroni-3 T1b attack families.

## P4 status and direct v19 handoff

**P4_SOURCE_AGGREGATE_ALIGNMENT=PASS_12_ROW_INTEGRATION**: remote aggregate CSV assembled and verified against 3 datasets × 4 cells; E5 3×3 nDCG factorial point effects and GTE 3 contrasts cross-checked.
**P4_INDEPENDENT_REPLICATION=NOT_DEMONSTRATED**: local rank files, unpublished per-query rankings and seed/encoder lineage beyond audited sources not independently rerun.
**P4_JOINT_THREE_AXIS_STATISTICAL_CLAIM=NOT_SUPPORTED**; retain separate outcome families and a side-by-side design-level comparison.

Manuscript scope to revise once actual frozen v18 LaTeX is inspected:
1. Present 2×2 factorial vs earlier diagonal ε configurations with clear distinction.
2. Replace unjudged historical qid means in narratives with audited judged-qid results where the claim relies on corrected denominator, and distinguish historical vs prospective estimates.
3. SciFact side-by-side table with explicit different observations and threat conditions.
4. No blanket privacy/security guarantee.
5. Explicit quantization vs dimension interaction and multiple-test family distinctions.
6. Address E5/GTE method uncertainty, reproducibility limitations and professor comments.

The v18 original source is frozen and was NOT modified. This is an isolated evidence and revision specification.
