# IP&M Stage 1B — v18 judged-test stability and paired-bootstrap source audit

**Date:** 2026-11-20 KST. **Status:** author Mac execution pending; do not claim source-result PASS yet. This is a verified code/protocol preparation step, not historical original-run reproduction.

## Reason for this task

The separate Korean v17 review candidate uses BEIR test-qrels for utility and Top1/Flip but leaves Overlap@10, custom Kendall-union50 and 5000-resample paired-bootstrap unsettled. The candidate's historical-uncertainty discussion incorrectly states that the judged-test paired-bootstrap has been completed, contradicting Section 3. A separate **v17b status-only** LaTeX candidate fixes this *one sentence* and does not modify the original `SCI_First.zip/main.tex`. The v17b draft has no newly confirmed metrics.

## Original code and sources

Frozen Cleanroom joined SHA256 `9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63`; retrieval runner SHA `09ecb4d855417189f9dca36dcf67913ac1b08cb2051f7a09bbfb8b7f5f16a3a5`; original stability code SHA `aee33fcda269e60b36454ee4e739cc71acecf744dd54cd4d8778357533462b03`. Three frozen test-qrel hashes as published in previous v13/v14 audit. User's local corpus and raw vectors remain private and unmodified.

Original `compute_stability.py` (the actual source snapshot) defines `kendall_tau_at_50` as a custom pairwise-order score on the union of the two Top50 lists with missing positions treated as ties/end rankings; it is NOT standard Kendall tau-b. Reproduce *the original formula* to audit it; do not silently change the estimand.

## Safe read-only v18 tool

Separate local author delivery: `audit_ipm_stage1b_stability_bootstrap_v18.py`, SHA256 `0ff0cac3187e3833c0930a05447ec7d5409384f5e198a13d66ce2e9f07f8fc3b`. For the complete 3-dataset ×3-fixed-seed ×7-epsilon Guard grid, verify **20,958 judged-test Raw↔Guard query-level ranking pairs** against saved top100 lists. Verify query identity, Top1, hit-based Flip, overlap@10, and exact-source custom union-order Kendall against `stability_query.csv`; verify all 63 all-query source aggregates and expected author-defined diagnostic flags 37→34.

Output a *sanitized, aggregate-only* ZIP (outside original research folder): 63 per-condition rows, 21 dataset×epsilon rows, 7 macro epsilon rows, and **42 paired-bootstrap transition CI rows** (3 datasets × 2 epsilon transitions {16→32,32→64} × 7 metrics). Each query is paired across the two epsilons, **three seeds averaged before bootstrapping queries**; 5000 deterministic percentile-bootstrap resamples and nominal 95% CIs. The CI is conditional on these fixed seeds, unadjusted for multiple comparisons and not a causal or security guarantee. The ZIP includes source SHA manifest and no raw query/document IDs, qrels lines, raw embeddings or ranking lists.

**Local tests PASS:** Python source compilation, exact source Kendall formula parity on 100 random full Top100 list pairs, 63/72 synthetic matrix complete execution, six-file ZIP CRC/integrity and no-ID exports; deliberately changing one synthetic per-query stability value causes a hard fail before creating output ZIP. Synthetic numbers are not research outcomes.

**Still required:** original author Mac run. Upload the generated `~/Downloads/IPM_stage1b_v18_test_stability_evidence.zip` for independent review; no per-query originals required. After PASS, correct separate manuscript figures/results and contradictory uncertainty wording. Comparator BM25/Gaussian judged-test alignment and the professor-requested dimension×precision ablation are subsequent gates. Do not make any `main.tex` submission edits yet.

## Related confirmed work

Stage1B v16 full-test exact-output computation passed 23,952/23,952 judged-test query-run ranking matches from stored embeddings; that proves exact-output reproducibility only, not the historical executable identity or original E5 inference. Stage1A T1/T2 attacker-projection sensitivity remains a separate security-proxy scope, not privacy certification.


## Author Mac execution and reviewed aggregate evidence — 2026-11-20 15:05 KST

**Execution now confirmed from user-uploaded artifact** `IPM_stage1b_v18_test_stability_evidence.zip` SHA256 `43436e7a15403de2d788bed80097600503b16fb5ea77dfc26c31ee01dcb37af0`. ZIP internal CRC PASS; six files include 63 condition records, 21 dataset-epsilon means, 7 epsilon macro means, 42 paired-bootstrap outcomes, 207 original-file SHA256 inputs and source provenance. Local script SHA256 `0ff0cac3187e3833c0930a05447ec7d5409384f5e198a13d66ce2e9f07f8fc3b` agrees with the pinned audited v18 script. Original joined, runner, stability source and qrels SHA gates are declared in the Mac-generated manifest. The run covers 20,958 judged-test Guard-vs-Raw query pairs over 63 conditions.

**Independent arithmetic consistency audit:** 63→21, 63→7 means agree at floating-point precision across 7 metrics; `Utility Mean = (Recall@10+nDCG@10)/2` exact within float precision; all 42 bootstrap point estimates equal differences of the matching dataset-epsilon means. No missing values or duplicated condition keys. Flag counts historical all-query 37/63 vs judged-test 34/63. Bootstrap label distribution: **35 favorable / 7 uncertain / 0 unfavorable** under nominal unadjusted percentile 95% intervals, chosen metric directions and fixed seeds. TREC-COVID 16→32 has 6/7 intervals including zero; TREC-COVID 32→64 Flip CI includes zero. Do **not** claim universal statistical improvements. There are 42 comparisons and **no multiple-comparison adjustment**.

**Scope limitation:** The uploaded ZIP has no per-query data; this cloud-side review *did not independently regenerate 5000 bootstrap draws from original query records*. The author's read-only Mac script had recomputed Top1, Top10 overlap, author-defined Kendall union50, Hit@10 Flip from original stored rankings and checked them against per-query source metrics before exporting the archive. Bootstrap resamples qids only after averaging three fixed seed outcomes. The custom union-order score is not Kendall tau-b. No raw query IDs, document IDs, corpus text, embedding matrices or ranking lists were shared.

**Separate v18 Korean manuscript candidate produced** (not final submission, original `SCI_First.zip/main.tex` untouched):
- Review ZIP SHA256 `100bf496c900cf1217cde8c721f54071b4d435c0c0e3666f30868e424343ab8e` — 18 files, integrity PASS, candidate TEX / source bibliography / figures / 63+21+7+42 derived CSVs / source manifest / diff and review report.
- Candidate PDF SHA256 `de38ae2c8a8e2c8d67a584a1dee0b20824757e1e843130dbec7584378a354ffd`, 39 pages. XeLaTeX/BibTeX compilation PASS. Key new stability and CI tables on PDF pp.21–22 were visually inspected and display correctly; font fallback and minor floats/line overflow remain editorial cleanup work.
- Separate review report SHA256 `0c29cc5b6020dd273beb29c234aa99d16b36929eacdfa225d7a06c64456c3498`.

**Open next scientific gates:** BM25/Gaussian matched test-cohort comparability; professor-requested dimension × quantization ablation and additional model experiment; source-limited security assertions (T1/T2); final English manuscript review. Nothing in v18 proves historical HNSW absence or E5 embedding recreation.
