# IP&M professor-review response matrix — preliminary update (2026-11-23 KST)

**Status:** DRAFT, revision-planning only. This matrix updates the **2026-11-20** historical feedback-alignment audit with verified **2026-11-23** factorial evidence. It is **not** a line-by-line review of frozen v18 manuscript or an independently re-read copy of the original seven-page professor PDF. No original manuscript, algorithms or run artifacts changed.

## Baseline
Historical manuscript reference: `main(20261118-095709).tex`, SHA-256 `66aded97658a11ade0ba954951d2e6d9152c7f18e75316dce65ee6475690241c`. Separately prepared v18 candidate `manuscript_v18_candidate.tex`, SHA-256 `08c0a2e6462c805b70fe3650d7c6bef28b359cb97759df3c0d64a3417dbafdc8`. These are *different* artifacts; exact frozen v18 contents must be retrieved before line-numbered changes.

Professor's 2026-11-18 seven-page review was summarized in the dated `IPM_PROFESSOR_FEEDBACK_ALIGNMENT_AUDIT_20261120.md`, with six priorities:
1. Prior art and novelty
2. Separate dimensionality from quantization precision
3. Security threat/proxy assumptions
4. Additional encoder model
5. Quantitative utility–stability–exposure tradeoff
6. English manuscript and IP&M submission style

## Evidence updated as of 2026-11-23

| No. | Request | Status | Verified evidence / remaining blocker | Draft editorial resolution |
|---:|---|---|---|---|
| 1 | Prior work / novelty | PARTIAL | Earlier narrative audit exists, but named prior-paper claim matrix and manuscript paragraph trace unavailable in this phase | Describe multi-axis matched factorial evidence and cautious non-persistent representation threat model, do not claim a new privacy mechanism |
| 2 | Dimension × quantization isolation | EXPERIMENT COMPLETED; manuscript pending | Prospective 3 datasets ×3 fixed seeds × (128,320 dimensions) × (4,10 bits) =36 cells, matched test-only qrels; 18 utility contrasts and 45 stability contrasts; separately published 18- and 45-family Bonferroni percentile query-bootstrap CIs | Add prospective design, main/interaction effect tables, query resampling limits and distinguish diagonal reference from historical epsilon |
| 3 | Threat model / security proxy | PARTIAL | Historical matched-MIA near 0.5 only under tested attack; old MIA score can be confounded; old TREC-COVID MIA/Re-ID (5000-row legacy L3) differs materially from canonical factorial diagonals at 64 sampled rows each, all 6 conditions fail atol1e-4. No factorial off-diagonal security attacks. | Clarify A1/A2/A3 and T0/T1/T2 where defined; explicitly separate historical attacks from prospective retrieval cells and report no formal privacy guarantee |
| 4 | Additional embedding model | OPEN | All prospective factorial results from single `intfloat/multilingual-e5-base`. No independently verified second encoder in current evidence. | Explicit GO/NO-GO decision; until independently tested, no cross-encoder generalization claim |
| 5 | Utility–stability–exposure | PARTIAL | Utility and RAW-relative stability for same 36 cells; **no same-cell exposure measurement** for off-diagonals; historical TREC exposure not comparable as direct measure. | Present utility–stability association / factorial contrasts only; discuss security evidence separately, not causal 3-way trade-off |
| 6 | English / submission style | OPEN | v18 Korean candidate is not final manuscript; Elsevier guide available in prior project | Only after author-approved Korean v19 changes: English terminology, non-exaggerated positive result-first structure, figures, citations and compliance |

## Required statement guardrails
- `epsilon` is a Guard configuration strength label, **not** formal differential privacy epsilon.
- Factorial off-diagonal cells are **D/B settings**, not new epsilon values.
- Stability flip@10 is a binary relevance Hit@10 proxy, **not** human operator decision reversal.
- Top-50 union order agreement is custom, **not** canonical Kendall tau-b.
- Fixed 3-seed, query-resampling CIs do **not** cover variability across seed populations, encoders or corpora; Bonferroni18 for utility and Bonferroni45 for stability do not imply joint 63-comparison family coverage.
- Explicitly state old exact/HNSW execution lineage limits where claims depend on it.
- Report outcomes and meaningful research contributions before consolidated limits; do not hide required methodological qualifications.

## Next immediate tasks
1. Retrieve frozen v18 manuscript text and exact professor-review original to create sentence/section/page/line-level change proposals. Earlier file index identifies the source but does not supply these texts in this phase.
2. Reuse existing GitHub `reproducibility/ipm_ablation_20261123/aggregates` results; do not rerun 36 cells.
3. Decide whether a second encoder is scientifically essential and computationally feasible; do not silently mark professor item 4 complete.
4. Prepare isolated `v19` **proposal** only. Author's explicit approval required before modifying any frozen manuscript, research code or historical results.

## Reproducibility anchors
- Source and descriptive aggregates: commit `48e4e2808ecf9ae8325f124ea9f776bb00c2891a`.
- Utility paired contrasts: `reproducibility/ipm_ablation_20261123/aggregates/IPM_ablation_statistics_v1/factorial_effects.csv`.
- Stability CI45 and protocol: commit `af8a53ec3775c2126b22d90197c2e119ba136e9c`.
- Historical TREC input divergence: `docs/audits/IPM_ABLATION_2026-11-23_TREC_SECURITY_VECTOR_MAGNITUDE_FINAL.md`.
