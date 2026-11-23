# IP&M P3 — SciFact GTE paired bootstrap result (2026-11-23 22:31 KST)

**Evidence status:** author-reported Mac execution passed; 12-cell prior ranking audit was also author-reported PASS_12. Do not describe this as independent third-party reproduction. Row-level data and statistical output JSON are retained on the author's Mac.

## Reported execution
- `P3_PAIRED_BOOTSTRAP=PASS_3`
- `BOOTSTRAP_UNIT=300_MATCHED_QUERY_IDS`
- `FAMILYWISE_95=BONFERRONI_3_CONDITIONAL_ON_FIXED_SEEDS`
- Output `~/Downloads/IPM_P3_GTE_PAIRED_STATS_20261123`.
- Dataset: BEIR SciFact; judged test queries=300; fixed projection seeds=7,13,42; GTE additional model, 2×2 Guard conditions D={128,320} and quantization bits={4,10}.
- Prespecified effect family: dimension main effect, bits main effect, 2×2 difference-in-differences interaction. Query IDs paired across all 12 cells; bootstrap resamples query IDs, keeping all 12 scores on each sampled query. Percentile 95% Bonferroni familywise confidence limits for 3 contrasts, *conditional on three fixed seeds*.

## Three contrasts
| Contrast | point effect on nDCG@10 | Bonferroni-3 conditional simultaneous 95% percentile interval |
|---|---:|---|
| Dimension 128→320 | +0.06519374 | [+0.04517188,+0.08625652] |
| Bits 4→10 | +0.14505093 | [+0.12385282,+0.16704844] |
| Difference-in-differences | +0.00434952 | [−0.02956088,+0.03731352] |

## Interpretation
- Within the fixed SciFact/query/seed set, both main effects have conditional interval lower bounds above zero.
- The interaction interval includes zero: this **does not establish a zero interaction**, only that no nonzero interaction is distinguished under this limited analysis.
- CIs are not simultaneous with E5's previous separate 18-contrast and 45-contrast families; `95%` does not mean joint protection across all historical/new tests.
- The same 300 queries are observed under three seeds. They **must not** be regarded as 900 independent queries. Seed population uncertainty is not covered.
- The new GTE embedding protocol is not yet proven strictly comparable to historic E5 preprocessing; comparative superiority and generalization beyond SciFact are unproven.
- This does not measure or establish security/privacy.

## Gate
**P3 scientific minimum=PASS (12 factorial cells + audit + paired conditional intervals).**
**P3 final-paper reporting=CONDITIONAL**, awaiting exact cross-encoder pipeline comparability, independent validation of locally retained summary/hash files, and archival of the statistical Python script in GitHub. The original manuscript and E5 36-condition runs remain frozen.

## Script provenance
Statistical script `ipm_p3_scifact_paired_bootstrap_v1.py` was delivered as a separate conversation artifact, not yet committed to the public repository. Do not misrepresent this document as a published executable.
