# Remote confirmation: prospective stability CI45 table deposited

Date: 2026-11-23 KST. Verified via GitHub connector, following author's Mac publication log.

## Remote verification
- Author's push: `af8a53ec3775c2126b22d90197c2e119ba136e9c`, verified as GitHub repository commit and most recent commit at audit time.
- Two files in that commit:
  - `reproducibility/ipm_ablation_20261123/aggregates/IPM_ablation_stability_ci45_v1/stability_factorial_effects_ci45.csv`
  - `reproducibility/ipm_ablation_20261123/aggregates/IPM_ablation_stability_ci45_v1/analysis_protocol.json`
- Fetched the actual remote CSV. It has 45 data rows, FiQA 15, SciFact 15, TREC-COVID 15. Columns: dataset, metric, effect, delta, ci95_low, ci95_high, ci_bonf45_low, ci_bonf45_high, bootstrap_reps, query_count, fixed_seeds.
- Fetched the remote JSON: 5000 percentile query bootstrap replicates, seed 20261123, 45-comparison Bonferroni family, seeds 7/13/42 fixed and averaged within query. This does not give simultaneous coverage over the 18 utility contrasts and 45 stability contrasts together.
- Author's Mac log recorded `CI45_SCHEMA_CHECK=PASS_45`, `CI45_PROTOCOL_CHECK=PASS`, `DESCRIPTIVE_EFFECT_CROSSCHECK=PASS_45` and `PUBLICATION_COPY_LINE_ENDINGS=LF`. Remote inspection independently confirms the presence and row count, but does not reproduce the full query-level inference.

## Evidence boundary
- The source stability_query_36.csv used for paired inference remains local and unpublished in this deposit; privacy/licensing assessment would be required before sharing.
- No end-to-end independent rerun or full environment lock is established by this check.
- The operational “flip” in this statistical result is a Hit@10 binary relevance proxy, **not human operational decision reversal**. Kendall tau on a top50 union uses a nonstandard missing-item treatment.
- Do not infer privacy or newly measured security for off-diagonal factor cells. Historical TREC-COVID MIA/Re-ID attack matrices differ materially from factorial diagonal matrices.
- Existing frozen manuscript, Guard algorithm and historical experiments are unchanged.

## Project gate
**STABILITY_CI45_PUBLICATION=REMOTE_VERIFIED.**
Next: produce professor-review response matrix and a change proposal based on v18 source text; first establish precise manuscript and comment provenance. Final reproducibility checklist still requires environment and run lineage details.