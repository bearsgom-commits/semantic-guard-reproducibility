# Reproducibility scope and evidence status

Date: 2026-11-17 (KST)

## Confirmed from supplied archives
- Matched MIA and legacy results joined by (dataset, seed, epsilon) after normalizing `trec_covid` and `trec-covid`.
- 63/63 condition joins; author-defined operating-region flags: legacy 0/63; matched 37/63.
- Epsilon-specific matched counts: 0:0, 2:3, 4:8, 8:8, 16:9, 32:9, 64:0.
- Recomputed security aggregates matched supplied derived results to approximately 1.11e-16.
- Guard implementation snapshots in IP&M and a separate Electronics evidence package had identical SHA-256: `8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d`. This does not prove historical execution provenance.

## Not yet independently reproduced
- BEIR corpus preparation, E5 embedding and all retrieval runs.
- Original matched-MIA attack generation and raw attack scores.
- Original execution-time model revision, environment lock, seeds and CLI provenance.
- Full paper table/figure generation lineage.
- Historical guard mapping: a supplied mapping JSON labels itself reconstructed, not original execution evidence.

## Interpretation constraints
- `epsilon` is not differential-privacy epsilon.
- 37/63 is a count under author-defined thresholds, not a validated security guarantee.
- Near-chance MIA AUROC is protocol-specific.
- Supplied Stage 3 dense retrieval code uses NumPy dot-product ranking; HNSW is mentioned in a configuration but not established as the executed retrieval path.

## Completion criterion
A third party can obtain permitted inputs, execute documented commands, regenerate result tables and figures, and distinguish independently reproduced steps from consistency checks. Until then, label the repository IN PROGRESS.
