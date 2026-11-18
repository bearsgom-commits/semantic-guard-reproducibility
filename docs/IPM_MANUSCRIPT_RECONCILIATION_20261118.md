# IP&M manuscript/reproducibility reconciliation (2026-11-18 KST)

## Scope and immutable baselines
- Manuscript under editorial review: `main(20261118-095709).tex` (866 lines), SHA-256 `66aded97658a11ade0ba954951d2e6d9152c7f18e75316dce65ee6475690241c`. This manuscript is **not** published in this repository.
- Historical audit baseline: commit `fa2ce2a00dd913a883c911c81644e098ed33b137`. Never reinterpret subsequent documentation changes as proof of an older experiment.
- Editorial working candidate (local to author): not an approved final manuscript.

## Open finding MIA-01: score specification
The manuscript reports pre-sigmoid score `0.5*maxSim - 0.3*meanTop5Sim - 0.2*marginTop1Top2`.
Both public scripts `scripts/stage3/run_attack_mia_matched.py` and `scripts/stage3/run_attack_mia.py` implement **positive** 0.3 and 0.2 weights, then `sigmoid(8*(raw-0.5))`.
**Disposition:** manuscript correction candidate only; historical condition-level command logs/input embedding identity remain to be linked. No claim of independent experimental rerun made.

## Open finding SEC-02: manuscript vs. published aggregate
| epsilon | manuscript Table 4 | public `verified_epsilon_summary.csv` |
|---|---:|---:|
| 0 | 0.8064 | 0.8062463369597395 |
| 2 | 0.8629 | 0.8627224488457875 |
| 4 | 0.8303 | 0.8301319727723995 |
| 8 | 0.8699 | 0.8696738110797594 |
| 16 | 0.8796 | 0.8794248949217913 |
| 32 | 0.8372 | 0.8369644104436926 |
| 64 | 0.2074 | 0.2189515037115881 |

The published `aggregate_stage3_ext.py` uses the unweighted mean of `(1-global_minmax)` across reidentification accuracy, top-10 leakage, and membership AUROC. In `build_attack_wide`, the aggregation code uses **max** across numeric attack fields sharing the same (dataset, seed, epsilon) key. Whether this explains the observed discrepancy is **not established**; investigate source input versions, attack-family filtering, row sets, and normalization range **before** altering manuscript results.

## Existing replay evidence and its limits
- Published `results/stage3/matched_mia/replay_20261118/condition_comparison_63.csv` records 63/63 PASS and zero recorded output differences. Final replay driver classified 21 TREC-COVID conditions as freshly `executed` and 42 FiQA/SciFact conditions as `existing_report`.
- Individual sanitized reports, input Guard embedding SHA-256 manifest, command/environment provenance and end-to-end BEIR/E5/retrieval reproduction remain unavailable in this public repo as of the baseline audit. This is **not** third-party independent reproduction.
- Manuscript revision and reproducibility can proceed as parallel tracks. Final manuscript-to-artifact reconciliation and reproducibility freeze must occur **after** the scientific scope and revised tables are fixed.

## Required gates before final release
1. Trace historical MIA source version against condition logs, report digests and input embeddings.
2. Trace `security_score_mean` from exact per-condition input rows, normalization and attacked component selection into each manuscript table/figure.
3. Resolve retrieval execution mode (NumPy exact vs FAISS HNSW) using executed commands and logs, rather than configuration alone.
4. Record whether any adviser-requested ablation/comparator/statistical changes alter the experimental corpus; verify their own provenance if performed.
5. Confirm final manuscript values and claims against frozen public evidence; do not relabel consistency checks as full reproduction.

This file is an audit of outstanding issues, **not a PASS certificate**.

## Additional arithmetic check (2026-11-18 KST)
The current manuscript's discussion reports the mean exploratory Security Score across epsilon 0, 2, 4, 8, 16 and 32 as **0.8477**. The published `results/stage3/matched_mia/validation/verified_epsilon_summary.csv` values yield **0.8475273125038615** for the equally represented six epsilon levels (each nine conditions). This is another manuscript-to-public-data difference, not an independent recomputation from attack inputs. The previously recorded epsilon=64 mismatch and the 37/63 Region Flag agreement remain unchanged.

**Disposition:** keep original manuscript table values pending complete table/figure lineage review; do not silently replace numbers with public derived CSV values. The editorial LaTeX working copy is kept outside this public reproducibility repository.

## Manuscript methodology gate review (2026-11-19 KST)
**RULE-03 — Utility threshold discrimination not established:** `scripts/stage3/aggregate_stage3_ext.py` uses `utility_score_mean < 0.98` for `region_flag_v3`. The manuscript's representative aggregate utility scores span 0.0406–0.1969. These aggregate means suggest the rule may be permissive in the evaluated range, but **the 63 per-condition utility values and gate-wise counts have not been inspected here**; do not assert that all 63 records pass until checked.

**AUC-04 — Exploratory score directionality:** the composite currently applies `1 - global_minmax(membership_AUROC)`. AUROC 0.5 corresponds to chance-level ranking; lower-than-0.5 AUROC is not automatically a better privacy result if an attacker can reverse score orientation. The score is author-defined and should not be presented as a calibrated privacy measure. Recompute/sensitivity-check oriented AUROC (`max(AUC,1-AUC)`) or deviation from 0.5 before making stronger security-ordering claims. No new attack run or corrected security table is claimed.

These two open methodological concerns have been disclosed in the Korean editorial working manuscript, **without changing measured values or inventing a completed experiment**.

## Derived-data post-hoc orientation sensitivity (2026-11-19 KST)
A reproducible calculation based solely on public `results/stage3/matched_mia/validation/matched_vs_old_63_conditions.csv` was added as `scripts/check_auc_orientation_sensitivity.py`.

- The matched AUROC <= 0.60 membership gate passes **63/63** rows; the public primary Region Flag has **37/63** positive rows. Utility, stability and Re-ID individual-gate contribution counts **cannot be computed from the published CSV** because its source columns are absent.
- Algebraic counterfactual: keep the already published two nonmembership contributions fixed in each `security_score_matched` row; substitute only the matched AUROC component, from `1-minmax(AUROC)` to `1-minmax(abs(AUROC-0.5))` (global min–max over the 63 public rows, equal 1/3 weight).
- Across 63 rows, Spearman rank correlation with the public composite **0.0978584462**, mean absolute per-condition score change **0.1027341447**, maximum **0.3333333333**.
- This is a **post-hoc analysis of derived outputs**, not a new attack run, independent validation of the input embeddings, or evidence that the alternative composite measures privacy accurately. The old manuscript values in Table 4 remain **unreconciled** with public derived epsilon means and have not been overwritten.
- This reveals that monotonic scoring of un-oriented AUROC can heavily alter exploratory composite ordering. It is separate from the previously observed component-exclusion sensitivity and must not be conflated with a test of statistical significance.

## Local eight-version Stage 3 lineage discovery (2026-11-19 KST)

The user ran the read-only `scripts/audit_local_stage3_lineage.py` on 8 local `joined_stage3_ext.csv` versions. This evidence is based on **user-supplied local console output**; local CSV file contents and execution logs have not been directly ingested into this GitHub audit.

- Candidate numeric match: `semantic-guard/_reproducibility_runs/wbs08_cleanroom_20260829_172931/reproduction/runs/_summary/stage3_all3/joined_stage3_ext.csv`, SHA-256 `9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63` (reported 63 unique rows, 37 positive `region_flag_v3`). Its epsilon means, ordered 0/2/4/8/16/32/64, are `0.8064192 / 0.8628720 / 0.8303038 / 0.8698652 / 0.8796280 / 0.8371730 / 0.2073826`. All seven match Table 4 to four decimals; their epsilon 0–32 unweighted mean rounds to `0.8477`.
- Two local staging copies `wbs10b_public_docs_draft/results/joined_stage3_ext.csv` and `wbs11_public_package_staging/results/joined_stage3_ext.csv` have the same reported SHA-256 `3fea89b476820c6ff7ce5df3fb4d7ea9d4b5c6c96c77f346cd6cbf79beb07c1e` and the same means. Their row-level equality to the cleanroom file has **not** been established.
- Earlier `wbs07e_p3g_security_aggregation` also yields 37 positives and epsilon64 `0.2073508`, which matches epsilon64 at four decimals, but does not match the manuscript across all seven epsilon levels. The older `stage3_all3` and `wbs07e_p3j_canonical_mia_lineage` files give 0 positives and different security means.
- The public matched-MIA derived aggregate `verified_epsilon_summary.csv` was previously shown to differ from Table 4. That is now a **version-selection/numeric-lineage issue with a plausible matching local file**, not proof the manuscript numbers are unsupported or fabricated.
- **Still open:** verify the local cleanroom file's actual source inputs, matched attack selection, aggregation code/configuration, execution logs, corpus/embedding identity and table/figure generation path. Numerical matching alone is not historical execution provenance or end-to-end independent reproducibility. Preserve Table 4 values until provenance is established; do not silently replace them with current public derived means.

The Korean working TEX was updated with a carefully qualified local numerical-source match note; no measured value was overwritten.

## WBS09 historical figure-source audit, four uploaded JSONs (2026-11-19 KST)

The four original read-only audit JSON files were supplied for direct inspection; they report historical actions in 2026-08-30. No original PDF or generated PNG bytes were supplied in this round.

1. `wbs09_main_r14_downstream_and_figure_source_audit.json`: confirms candidate figure source, but `scientific_experiment_executed=false`; historical manuscript-specific PNG hashes `figure4_security_components.png=49ea0700...`, `figure5_multi_axis_profile.png=6dbb2242...`.
2. `wbs09_main_r16_figure_generator_contract_audit.json`: corrected local aggregate source SHA-256 `9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63` passes integrity check. Generator `repo/scripts/stage3/make_stage3_figures.py`, SHA-256 `6c91c10c99cebe26d4e657d46fc0d68250ec80fa8f3478f6a4ec412e786464c8`; generator did **not** name figure4/figure5 manuscript PNG outputs; initial output-name contract FAIL (not a scientific result failure).
3. `wbs09_main_r16_r1_figure_output_provenance_diagnosis.json`: generator outputs named `fig_phase_diagram_v2.pdf`, `fig_security_curve.pdf`, `fig_stability_curve.pdf`, and `fig_utility_curve.pdf`. Corrected source input hashes: `joined=9038fa69...`, `phase=3ea88219...`, `security=761f0cad...`, `utility=e6ace3f7...`. Source PDF generation alone does not prove separate manuscript PNG provenance.
4. `wbs09_main_r16_r2_corrected_figure_reproduction.json`: historical generator executed successfully (`generator_return_code=0`), but fresh `fig_security_curve.pdf` SHA `d6c7fffe...` != archived `051a9c91...`, and fresh `fig_phase_diagram_v2.pdf` SHA `31661455...` != archived `66d81739...`. `visual_compare_available=false`, both visual checks `NOT_RUN`, and `scientific_experiment_executed=false`. Therefore its `diagnostic_gate=PASS` refers to regeneration command completion, **not byte-identical, visually identical or scientifically equivalent figures**.

**Disposition**: corrected source-data-to-generator identity is supported by historical metadata; actual PDF-to-manuscript-PNG linkage, visual/content equivalence, and current LaTeX figure integration remain open. Manuscript uses `figure4.png` and `figure5_multi_axis_profile.png`; do not silently replace either with the historic PDF generator outputs. The Korean TEX now contains comments marking these two figure provenance gates and retains existing figure includes. Finish by inspecting original PNGs, corrected PDF outputs and script source, matching plotted series/captions to the paper, then recompile against real figure files. No claim of complete figure reproduction.
