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

## Manuscript Figure 4/5 uploads vs historical canonical PDF (2026-11-19 KST)

User explicitly confirmed current manuscript figures, and uploaded: `figure4.png` SHA256 `52e18adf788f89b015c4c756e0a05b40a1e72893c846a8956a3aace6b7863991`, `figure5_multi_axis_profile(1).png` SHA256 `ec4ad2ed7dc849484c7235946269da2cc558ef3ee36e2b907c1a957e979d1899`, and `fig_security_curve(1).pdf` SHA256 `051a9c910396ca946092e6a2d97fc6da62d310ed3fa5af5f61231750710e0f42`. SHA256 was computed directly from uploaded bytes.

- PDF **exactly matches** the historical cleanroom archived `fig_security_curve.pdf` hash reported by `wbs09_main_r16_r2_corrected_figure_reproduction.json`, establishing the identity of the attached PDF to that historical artifact. It is not the newly generated PDF (reported hash `d6c7fffe...`).
- The **uploaded** PNG hashes are **different** from historical WBS09 archived manuscript PNG hashes (`figure4_security_components.png=49ea0700...`, `figure5_multi_axis_profile.png=6dbb2242...`). Differences may arise from prior revisions, export or file contents; do not assert byte identity.
- Current Korean TEX references `figure4.png` and `figure5_multi_axis_profile.png`. Its Figure 4 caption explicitly describes a two-panel plot: (a) matched MIA with ReID/Top10 and (b) diagnostic matched-versus-mismatched AUROC. The uploaded Figure 4 visually shows these panels. Its Figure 5 caption describes utility/stability/flip and exposure-proxy panels; uploaded Figure 5 shows both. The old `fig_security_curve.pdf` shows ReID/Top10/MIA/aggregate in a single older plot and is **not semantically interchangeable** with Figure 4.
- Figure 4/5 provenance at the level of exact displayed values remains unverified against authoritative per-epsilon source CSV; PNG content visual/caption congruence does not imply pixel-for-pixel reproduction or historical source attribution. Keep both figures; do **not** silently substitute the PDF.
- Next gate: validate plotted values (incl. epsilon labels, matched/mismatched definitions) from the cleanroom source, identify PNG generator, compare against manuscript tables. Full final compile still needs other original assets and bibliography.

## Complete manuscript bundle and image inspection (2026-11-19 KST)

Source: user-uploaded `SCI_First.zip`, archive SHA256 `6d1128488dc5ff0b3d9c5c323dfd1b1410b97944af3a8aaf67056fe9d64bbe1e`. Independently opened and inspected all 21 archive members (9 TEX variants, one title page, 2 BIBs, 9 PNGs). The archive `main.tex` is the older source (86,182 bytes, SHA256 `66aded97658a11ade0ba954951d2e6d9152c7f18e75316dce65ee6475690241c`), **not** the current 2026-11-19 working TEX.

**Active figure names in both archive `main.tex` and current Korean working TEX**, all six present: `figure1.png`, `figure2.png`, `figure3.png`, `figure4.png`, `figure5_multi_axis_profile.png`, `figure6_guard_gaussian_comparison.png`. The extra `figure4_1.png`, `figure4_security_components.png`, `figure5.png` are historical alternatives and are not included by the active manuscript. `main_en.tex` references `figure4_security_components_final.pdf`, absent from this ZIP (English manuscript not selected for current processing).

**Specific hashes and historical audit linkage:** current `figure4.png` SHA256 `999dac5719085364b3cbf4239084d7cf42d96fb87fee533fcaf47fd74fa5da5c` (two-panel matched/mismatched); archived `figure4_security_components.png` SHA256 `49ea0700becb0892f98df08dc713a985b7d2aeb1f8bf2490e45cebca2bfd54d1` matches the old WBS09 audited figure4 alternative; current `figure5_multi_axis_profile.png` SHA256 `6dbb224254008386a3b4322db0b4f99cc4b96b9f6de51a4f0fa427600489bf11` matches the WBS09 audited Figure5 PNG. Historical provenance of the **current** `figure4.png` still needs a specific renderer-to-source CSV run. No original figure has been silently replaced.

**LaTeX reproducibility check:** a separate read-only copy of the current Korean working TEX was compiled *together with* uploaded PNGs and `references.bib`, via XeLaTeX + `/usr/bin/bibtex.original` (the shell alias `bibtex` was unavailable in the evaluation container). Successful 37-page review PDF with all six embedded images, bibliography beginning page 33, and no unresolved citations/cross references. All 29 cited key names resolve against the 32 `references.bib` entries. This establishes manuscript asset completeness/compilation on the review environment only, **not** submission readiness, exact figure-data reproducibility or full original experimental reproduction.

**Visual/layout issues in compiled 37-page PDF:** Fig.1 p8 complex diagram text becomes small; Fig.4 p21 two-panel chart is legible only at zoom; Fig.6 p27 comprises three 1.5-inch-wide mini-panels (326.4×106.6pt overall) and axis labels are too small at normal print view. The Table 8 sensitivity tabular p26 exceeds the column width by `35.2906pt` (XeLaTeX overfull hbox). Figure2 p19, Figure3 p20, Figure5 p24 are present and caption/series semantics visually consistent; numeric provenance remains a separate step. Separate `title_page.tex` is not imported by `main.tex` (consistent with a possible anonymous-review workflow, but submission policy and author metadata need separate verification). The title page contains organizational/contact details needing review before use.

**Disposition**: preserve current six active image selections; repair Table8 width, enhance Fig.1/4/6 print legibility using source-based graphics, and resolve current Fig.4 data provenance. Prefer the newer working TEX; the old archive `main.tex` must not overwrite it. Do not publish the complete manuscript ZIP or title-page personal contact information in this public repository.

## Layout-only Korean working-copy proof (2026-11-19 KST)

This is a local **working-TEX-only** layout proof after the complete `SCI_First.zip` inspection; the user's source `main.tex` and the original ZIP have **not** been modified or committed. Local working TEX SHA-256: `ecd78535735dd2cfe9ac583f29f48b2d7b70008a35f807a034fe335b6e8935f1`; layout review PDF SHA-256: `7633015185a25157d4ee48f89f6368c947d86955c0e5f1beb94c131e65f49977` (38 pages).

- Table 8 (Security Score sensitivity) was reformatted with a wrapping first column and multiline headers; the previous `35.2906pt` overfull table warning is absent on recompile, with **all six numeric rows preserved**.
- Fig.1 layout scaled from 0.82 to 0.98 `\\textwidth`; original raster bytes unchanged.
- Fig.4 and Fig.6 were **not replotted**. Each original PNG was split into contiguous, non-overlapping pixel-exact vertical crops and arranged for enhanced print legibility (Fig.4 stacked 2 panels; Fig.6 2 panels above 1). Concatenating the cropped NumPy pixel arrays reproduces the original pixel arrays exactly. Figure captions, data points and axis descriptions are unchanged.
- XeLaTeX + BibTeX produced 38 pages (original review PDF 37 pages); all 6 figure environments and 9 table environments retained, cited keys resolved and no unresolved LaTeX cross-references. Three minor overfull boxes (1.445pt, 0.359pt, 5.657pt) remain elsewhere; they are separate from the fixed 35.291pt Table 8 overflow.
- This is **presentation verification only** and does not validate the figures' plotted values against original retrieval/security CSVs. Cropped panel PNGs must accompany the working TEX in any portable build. Original `main.tex` is held for one final integration stage only.

## Critical Figure 4/5 numeric-source discrepancy found by local read-only audit (2026-11-19 18:08 KST)

**Evidence source**: user-pasted stdout from `audit_ipm_figure45_source.py`, cross-checked against the uploaded checker implementation and the Korean working manuscript's numeric table; aggregation contract independently inspected in this repo's `scripts/stage3/aggregate_stage3_ext.py`. The local CSV bytes have not been directly acquired in this audit turn.

Verified report:
- All four Cleanroom source CSV SHA-256 hashes match WBS09 historical records; the canonical dataset × seed × epsilon grid is 63/63 unique; common joined-to-figure-input fields match exactly (`max_delta=0`).
- Manuscript means: utility, Top-1 stability, decision-flip, composite `security_score_mean`, region flag counts, matched AUROC and diagnostic mismatched AUROC all match their checked source means at four decimals.
- **12 substantive discrepancies** occur for manuscript table `reidentification_accuracy` (5 epsilon rows) and `top10_leakage_rate` (all seven epsilon rows). At epsilon64: manuscript ReID `0.9821` vs Cleanroom CSV `0.99966177`; manuscript Top10 leakage `0.9827` vs Cleanroom CSV `0.99983807`. Other mismatches are small in magnitude but exceed the 4-decimal display tolerance. The quantitative provenance for the active current `figure4.png` and `figure5_multi_axis_profile.png` is consequently **NOT RESOLVED**. Qualitative high-exposure observation at epsilon64 persists, but exact plotted values and table claims cannot be certified.
- The script's 13th item, `DUPLICATE_KEY: utility_baseline_compare.csv, ('fiqa', 7, 0)`, is a **checker defect**: the baseline-comparison file contains multiple method families/target modes at the same dataset/seed/epsilon. It must be validated on a method-aware key or treated as a multi-row baseline table, NOT a unique experimental-condition table. Do not count it as a scientific anomaly.
- Per-`epsilon` numeric coincidence of the composite score does not independently validate raw proxy values: the score uses each metric's global min–max normalization (`1-norm01`) over all rows; this can mask differences in raw component magnitudes.
- The manuscript's reported `ReID=0.9821, Top10=0.9827` may derive from another experiment version, cohort, or metric definition. This is **a hypothesis only**. Do not swap the manuscript numbers for the Cleanroom numbers, do not retrospectively select a candidate version on numerical fit alone, and do not assert that the manuscript table is wrong pending metric lineage investigation.

**Next decision**: use a read-only local comparison across all 8 `joined_stage3_ext.csv` versions and all epsilon means for ReID/Top10, review experiment/attack metadata for the winning candidate, and identify the actual producer for Figure4/5 before final manuscript edits or 2×2 ablation integration. The original `SCI_First.zip/main.tex` remains untouched by user instruction.

## Stage 3 security version mixing identified from local v2 audit output (2026-11-19 KST)

Source: author-run read-only `audit_ipm_security_lineage_v2.py` terminal output; no original local CSV bytes were uploaded in this step. The earlier source-lineage conclusion **must be qualified**: recovering Cleanroom mean Security Score values does **not** establish a single consistent source for every security figure/table component.

- `semantic-guard/runs/_summary/stage3_all3/joined_stage3_ext.csv` (legacy SHA256 `d7d6237eac0e051f719b125af5bc6f91b5a756fd3e689c4c0a1744cb25a6ae56`, 63 rows, Region Flag 0/63) reproduces **all 14/14** manuscript rounded Re-ID and Top10 Leakage table values. At ε=64: ReID `0.9820904`, Top10 `0.9827047`, MIA AUROC `0.5534192`, Security Score `0.3088723`.
- `wbs08_cleanroom/.../joined_stage3_ext.csv` (SHA256 `9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63`, 63 rows, Region Flag 37/63) reproduces **all seven** manuscript rounded Security Score entries and matches the matched MIA AUROC series, but only **2/14** rounded Re-ID and Top10 Leakage values. At ε=64: ReID `0.99966177`, Top10 `0.99983807`, MIA AUROC `0.4960768`, Security Score `0.2073826`.
- The previous Figure4/5 audit found the old manuscript PNG hashes/figure generator were not always identical to current images. Source version mixing is now a credible explanation for observed figure/table inconsistencies, not merely a rounding discrepancy.
- The 72-row `utility_baseline_compare.csv` contains 63 `dense_guard` plus 9 `dense_raw`; its nine overlapping (dataset,seed,epsilon) keys reflect **different methods**, not duplicate rows.
- **Required next gate:** on matched dataset×seed×epsilon rows compare old vs cleanroom components and source attack types; reproduce each archive's composite from its own components; compute a *diagnostic-only* old ReID+old Top10+matched AUROC counterfactual with the original global min-max rule; recompute per-gate Region Flag pass counts. Avoid presenting the hypothetical cross-version score as a measured observation.
- **Editorial disposition:** Do not update the user-preserved original `main.tex` or silently substitute paper values. Do not claim that mixing two lineages is scientifically acceptable until component definitions, sampled inputs, aggregation scripts and original figure-generation source are reconciled. The matching of seven aggregate score means alone is insufficient to close this gate.

## Author-run v3 rowwise audit — exact observed findings (2026-11-19 KST)

Source: user-supplied full terminal output from `audit_ipm_mixed_lineage_v3.py` (read-only, original local CSVs not uploaded here). `legacy` SHA-256 `d7d6237eac0e051f719b125af5bc6f91b5a756fd3e689c4c0a1744cb25a6ae56`; `cleanroom` SHA-256 `9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63`. Both exact source hashes PASS. Full 63/63 unique dataset×seed×epsilon grid PASS.

Compared by 63 exact row keys (strict tolerance 1e-10): reidentification_accuracy differs 20/63 (max 0.052714006, mean absolute 0.002560429); top10_leakage_rate 21/63 (max 0.051400000, mean 0.002962584); membership_inference_auroc 63/63 (max 0.513932320, mean 0.438361629); security_score_mean 63/63 (max 0.333296745, mean 0.170038422); region_flag_v3 37/63; utility_score_mean, mean_top1_stability, decision_flip_probability_at10 each 0/63. All old and cleanroom observed per-condition `security_score_mean` values were independently reproduced **exactly** by the common three-component global-minmax formula (maximum reconstruction error zero).

The mixed-component diagnostic (legacy ReID and leakage plus cleanroom matched MIA, recomputed with global minmax) gives epsilon 0/2/4/8/16/32/64 means `0.8062463/0.8627224/0.8301320/0.8696738/0.8794249/0.8369644/0.2189515`; these match the previous public `verified_epsilon_summary.csv` means. **This identifies the public summary as numerically consistent with an inter-version counterfactual but does NOT establish how the public table was originally constructed or its intended scientific meaning.** No composite from mixed-version input should be treated as primary measured evidence without an explicit validated protocol.

Cleanroom gate standalone passes: utility<0.98:63/63; top1>=0.20:46/63; flip10<=0.30:61/63; ReID<=0.20:54/63; matched AUROC<=0.60:63/63. Joint positive:37/63, exact flag reconstruction mismatch=0. Leave-one-gate-out additional positives: utility 0, top1 +15, flip10 0, ReID +9, MIA 0. Thus **for this evaluated grid** the binary Region Flag is discriminated only by Top1 and ReID; a marginal zero effect is not proof of universal logical redundancy. The utility threshold sign/scale and matched-AUROC threshold require methodological rationale or redefinition before substantive region claims.

**Next upstream audit required:** `scripts/stage3/aggregate_stage3_ext.py` aggregates numeric attack values with `max` across attack families for each (dataset,seed,epsilon), while text attack metadata take first non-null after sorting. This permits per-column contributions to originate from different source attack summaries. Audit original `attack_summary.json` records, matched/legacy run_meta, sampling indices, and the exact selection for each metric in both local lineages. This potential within-row mixing is a *source-code risk to investigate*, not yet an observed proven flaw in the 63 actual runs. Do not amend the original `main.tex` until the lineage choice and operational interpretation are justified.

## Attack-family component provenance from author-run v4 (2026-11-19 KST)

The author ran local `audit_ipm_attack_component_origins_v4.py` on preserved local directories and supplied the full stdout. This evidence identifies **saved individual attack_summary JSON rows**, not the underlying independently re-executed attack computations.

- Both joined files retain expected SHA256 (`legacy=d7d6237eac0e051f...`, `cleanroom=9038fa6947ff31ab...`); all per-component `max` selectors match the joined entries for 63/63 dataset×seed×epsilon conditions (`vs_joined_max_mismatch=0/63` for all three components in both versions). Source metadata issues 0; run_meta files missing 0.
- Legacy: 189 attack summaries, exactly 3/condition (`mia`, `mia_matched`, `reid`, each 63). Per-condition ReID and Top10 come from `reid`; selected membership AUROC comes from `mia` in **all 63**. The legacy `mia_matched` AUROC is present but **never selected** by the `max` aggregation in the recorded audit. Example fiqa seed7 ε64: old `mia=0.49901756`, `mia_matched=0.49552264`.
- Cleanroom: 126 summaries, exactly 2/condition (`mia`, `reid`, each 63). ReID/Top10 still from `reid`, MIA AUROC from `mia`. Example fiqa seed7 ε64: `mia=0.49552264`, which **equals legacy matched** for that single example; establish 63/63 equality before claiming the cleanroom MIA is the same protocol or derivation. The `reid` example fiqa seed7 ε64 is `0.99927131/0.99951421` in both, although aggregate ReID/Top10 differs across versions; localize differences by dataset and epsilon.
- The v4 label `conditions_with_forced_per_column_source_mixing=63/63` means **attack-specific heterogeneous components** (ReID/Top10 from ReID attack, MIA from MIA attack); this is *not inherently a defect*. The actual methodological issue is the unqualified substitution of legacy unmatched MIA for the intended matched primary and the incomplete reconciliation of differing ReID/Top10 source outputs.
- **Next required test (read-only):** compare all legacy `mia_matched` source summary AUROCs vs cleanroom `mia` per condition; verify semantic protocol metadata and input embeddings, compare ReID attack JSON results and parameters per dataset/seed/epsilon; audit provenance of changed ReID rows. Run-meta presence alone cannot prove identical command or input identity. Do not edit original `main.tex`.
