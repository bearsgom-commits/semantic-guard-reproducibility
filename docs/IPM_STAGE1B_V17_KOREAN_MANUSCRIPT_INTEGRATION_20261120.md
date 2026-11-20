# IP&M Stage 1B v17 — corrected judged-test manuscript review candidate

Date: 2026-11-20 (KST). Status: REVIEW CANDIDATE, **not final submission**. No original manuscript overwritten.

## Inputs and immutable baselines
- Original author's `SCI_First.zip/main.tex` SHA256: `66aded97658a11ade0ba954951d2e6d9152c7f18e75316dce65ee6475690241c`, unchanged.
- Stage 1A source-lineage review v12 TEX SHA256: `3c0aa0585fe8b68035f1adbfb811ec20dd9f218beb198a7201635a78ca7c2f7c`.
- Stage 1B v13-v14 Mac judged-test qrels reaggregation and 72/72 rank-to-qrels consistency; v15b numerical batch-shape diagnosis.
- User-run v16 `--all-test` proves stored embeddings -> exact normalized full-matrix NumPy Top100 ordered retrieval and scores for all 72 archived Raw/Guard runs, 23,952 judged-test query-run combinations: **23,952/23,952 Top100 exact, max score delta=0**. It is NOT historical process identification or E5 re-embedding reproduction. Every archived config names `faiss_hnsw`; original historic executable remains unknown.
- Cleanroom 63-condition security proxy source reused unchanged, including source-aware Figure4 data and T1/T2 threat-model limitations.

## Candidate artifacts (author-local, not uploaded to GitHub)
- `IPM_stage1b_corrected_candidate_v17_20261120.tex`, SHA256 `b8ef126092a34a320917dad095bf2d2311a545067cb49de8c4c7b6120675756c`
- `IPM_stage1b_corrected_review_v17_20261120.pdf`, SHA256 `67340c2bd0f8b6079acf29fea2685b924750726ebc87561e3970b43ee5ea521c`, 37 pages, XeLaTeX/BibTeX compile pass; visually reviewed figures and results tables.
- `IPM_STAGE1B_V17_CORRECTED_MANUSCRIPT_REVIEW_BUNDLE.zip`, SHA256 `9fd909f9ecd9eb4f5f66644b1fe4702f8c23bcc1d962dcfd7a081e93849fcefd`, 17 files ZIP integrity PASS. Includes LaTeX, PDF, reference bib, figures, reproducibility build script, source manifest, v12→v17 diff and four derived metric tables. No raw text or embedding arrays.
- Detailed author-local `IPM_STAGE1B_V17_INTEGRATION_REPORT_20261120.md`.

## Scientific edits
- Judged-test cohorts FiQA 648 of 6648 embedded queries, SciFact 300 of 1109, TREC-COVID 50 of 50. Avoid dilution of test metrics by unjudged qids.
- Main 7-epsilon table and Fig2/Fig3/Fig5 regenerated to judged-test cohort; Fig4 security remains 1A Cleanroom lineage.
- Macro means at ε0/ε32/ε64: corrected Utility 0.0948/0.4252/0.5055; test-only Top1 identity 0.0491/0.4766/1.0000; test Hit@10 Flip 0.5385/0.0936/0.0000. Matching raw dense judged-test Utility ~0.505484.
- Author-defined region-flag sensitivity changes 37/63 historical all-query to **34/63 judged-test**, only SciFact ε2 three seeds differ. This is NOT a validated secure region. The 7 Top1 test means were copied from author's v13 console result; per-seed Top1 evidence not included in sanitized 63-row CSV.
- Existing BM25 ~0.1700 and Guard/Gaussian historical utility/stability cross-comparison tables removed pending comparable judged-test qrels and rankings; do not assert Guard ε32 matches BM25 or Gaussian dominance yet.
- Old paired bootstrap favorable-count claims cannot be transferred from old all-query cohort; withheld. Overlap@10 and author-defined Kendall-tau test-cohort metrics need independent query-level reaggregation before reinsertion.

## Next gates
1. Recompute judged-test Overlap@10, Kendall and paired-bootstrap CIs from original query-level records, recording hashes.
2. Confirm BM25 / Gaussian comparator equal evaluation cohort or leave comparison withheld.
3. Apply professor's priority 36-run dimension-by-precision ablation under a frozen **explicitly logged** backend and test cohort; no historical runner identity assumption.
4. Final full manuscript consistency review and English integration only after those gates.

This is a source/metric reconciliation candidate, not independent end-to-end reproduction or a final journal-ready manuscript.
