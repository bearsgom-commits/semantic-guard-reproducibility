# Remote GitHub publication audit — 2026-11-23 KST

This is a **post-push, remote-read verification** of the publication committed by the researcher from their Mac.

## Confirmed remote facts

- Publication commit: `48e4e2808ecf9ae8325f124ea9f776bb00c2891a`.
- GitHub commit API returned 20 changed paths under `reproducibility/ipm_ablation_20261123/`: 13 Python scripts, 5 aggregate CSVs, `SHA256SUMS.txt`, `PUBLISH_MANIFEST.txt`.
- GitHub commit search returned publication SHA as the most recent commit **at verification time**; its predecessor was `f962fe62ed81b6a69e8bf914647ce9460b71d62d`.
- Remotely fetched content (at publication SHA): `SHA256SUMS.txt`, `PUBLISH_MANIFEST.txt`, `scripts/ipm_ablation_factorial_runner_v2.py`, `scripts/ipm_ablation_stability_paired_ci_v1.py`, `aggregates/IPM_ablation_statistics_v1/factorial_effects.csv`, `aggregates/IPM_ablation_statistics_v1/cell_means.csv`, `aggregates/IPM_ablation_stability_v1/stability_cells_36.csv`, `aggregates/IPM_ablation_stability_v1/stability_factorial_effects_descriptive_15.csv`.
- Mac run (author-provided transcript) reported `SOURCE_FILES=13 MAC_IDENTICAL=13 MAC_MISSING=0`, aggregate files 5, `PUSHED_COMMIT=48e4e2808ecf9ae8325f124ea9f776bb00c2891a`.
- Code SHA256 list exists on GitHub; the **remote script bytes have not all been independently recomputed with SHA256 against that list in this audit**.

## Residual reproducibility gaps — do not claim full replay

1. The published 5 CSV tables include **descriptive stability contrasts** but **do not include the separately reported 45 paired-bootstrap / Bonferroni stability inference output**. The paired-CI *script* is present; the underlying `stability_query_36.csv` is not published.
2. Historical/per-query evidence, 36 cell manifests and rankings, raw embeddings and licensed qrels are not deposited by this publication. Publication of sensitive/restricted files is not implied or requested.
3. Full independent reproduction needs exact original input data access, env/dependency lock, sufficient artifact provenance and matched command invocation evidence.
4. Security: historical TREC-COVID MIA/Re-ID 5000-row vector inputs materially differ from canonical full-corpus factorial diagonal vectors; the older attack results must not be presented as directly measured security exposure of factorial cells. Off-diagonal security unmeasured.
5. No update to the frozen v18 manuscript or original Guard source was made by this publication (per publisher manifest), and this remote audit does not independently inspect the author's Mac working tree.

## Next steps

- Determine locations of the existing 45-effect paired-CI output and its run manifest, register **safe aggregated inference table only**, with method, CI family size and hashes. Do not silently substitute descriptive 15-effect CSV for 45-effect inference.
- Record env/version lock and command-to-output provenance. Review paper edits against professor comments only after separating established evidence from remaining gaps.

**Overall status:** `SOURCE_AND_DESCRIPTIVE_AGGREGATES_REMOTE_CONFIRMED`; `FULL_INDEPENDENT_REPLAY_NOT_YET_DEMONSTRATED`.
