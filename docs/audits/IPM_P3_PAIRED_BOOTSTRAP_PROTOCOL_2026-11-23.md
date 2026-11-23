# IP&M P3 query-paired bootstrap analysis contract — 2026-11-23 KST

Status: **ANALYSIS SCRIPT READY; LOCAL SCIENTIFIC RUN PENDING.** Prior author-reported 12/12 ranking and hash audits PASS.

## Inputs
- Immutable GTE SciFact encoded corpus and judged-query vector manifest.
- Three 4-cell pilot folders (projection seeds 7, 13, 42), 300 *identical, identically ordered* judged test query IDs per cell.
- Audited 12-cell record `IPM_P3_GTE_12CELL_AUDIT_20261123/audit_manifest.json`.
- No retraining, re-embedding, new retrieval, original manuscript/code change.

## Estimands and uncertainty
- Primary metric: per-query nDCG@10, extracted from each cell's Top-100 ranking JSONL.
- For every same query and fixed seed, define `dimension = ((nDCG_320_4 - nDCG_128_4)+(nDCG_320_10 - nDCG_128_10))/2`;
  `bits = ((nDCG_128_10 - nDCG_128_4)+(nDCG_320_10 - nDCG_320_4))/2`;
  `interaction = (nDCG_320_10 - nDCG_320_4) - (nDCG_128_10 - nDCG_128_4)`.
- Average each contrast over the three **fixed projection seeds** for each of 300 query IDs, then average over 300 queries.
- Nonparametric paired bootstrap: sample *300 query IDs* with replacement, keeping all 12 scores for each sampled ID paired; 10,000 replicates, RNG seed 20261123.
- Prespecified single family of three contrasts: Bonferroni familywise alpha 0.05; two-sided percentile quantiles alpha/(2×3) and 1-alpha/(2×3); no joint coverage claims with existing E5 18-contrast or stability 45-contrast families.
- The interval quantifies conditional query-sampling uncertainty for the **three fixed projection seeds**, not generalization over random projection seeds (n=3 insufficient for reliable seed-population inference). Percentile intervals are approximate.
- No raw original data, manuscript, or existing rankings overwritten.

## Existing audited descriptive results
`dimension=+0.06519374`, `bits=+0.14505093`, `interaction=+0.00434952`. Statistical confidence bounds not yet measured; do not invent them.

## Acceptance gate
1. input manifests/ranking SHA-256 checked, identical qid order across 12 files;
2. calculated means agree with audited 12-cell descriptives;
3. exactly 3 valid finite intervals, lower<=estimate<=upper where applicable, documented seed-level contrasts;
4. output to *new*, separate path with input/output hashes;
5. preserve full source code, full execution stdout and outputs in the evidence archive before final submission.

Implementation currently delivered to author's conversation as `ipm_p3_scifact_paired_bootstrap_v1.py` (SHA-256 `67fa102574cabd7e232c9e1bb33754ede4eb5427da3ccccb77efb009356ade9c`); **not claimed to be present in GitHub**, pending repository source publication. The script received a local Python syntax compilation and synthetic contrast/bootstrap self-test.
