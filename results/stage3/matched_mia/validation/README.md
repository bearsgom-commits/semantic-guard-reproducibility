# Stage 3 matched-MIA validation

This directory is reserved for derived consistency-check artifacts:

- `matched_vs_old_63_conditions.csv` — 63-row old-vs-matched comparison.
- `verified_epsilon_summary.csv` — epsilon-level aggregates.
- `verified_checks.json` — summary of consistency checks.

These artifacts originate from a read-only audit of two supplied archives dated 2026-11-17. They **do not** constitute the original MIA attack execution or a new independent attack run.

Dataset name alias: `trec_covid` = `trec-covid`. Joins use `(dataset, seed, epsilon)`.

Original input files and the validation script must be supplied and verified before describing the three outputs as independently regenerable from this repository alone.
