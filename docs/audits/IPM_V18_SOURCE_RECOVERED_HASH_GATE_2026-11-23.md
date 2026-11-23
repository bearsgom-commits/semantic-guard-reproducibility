# IP&M P6 frozen v18 source recovery and integrity gate — 2026-11-23 KST

## Outcome
**V18_SOURCE_MATCH=PASS**, author-shared local terminal transcript. Frozen source SHA-256 independently expected from prior v18 audit:
`08c0a2e6462c805b70fe3650d7c6bef28b359cb97759df3c0d64a3417dbafdc8`.
Author-reported ZIP-member actual SHA-256: identical.
ZIP SHA-256: `100bf496c900cf1217cde8c721f54071b4d435c0c0e3666f30868e424343ab8e`.

Validated archive location (author local):
`~/Downloads/research/semantic-guard/manuscript_review/20261120_stage1b_v18/IPM_STAGE1B_V18_VALIDATED_MANUSCRIPT_BUNDLE_20261120.zip`.

Archive members, author-reported:
- manuscript_v18_candidate.tex 101128 bytes
- references.bib 11476 bytes
- source_manifest_v18.json 22669 bytes
- README_v18.md 1142 bytes
- manuscript_review_v18.pdf 2094390 bytes
- IPM_STAGE1B_V18_EVIDENCE_REVIEW_20261120.md 4865 bytes

Source manifest top-level keys: `bootstrap,date_kst,limitations,run_scope,source_sha256`.
Original ZIP not modified. **Actual LaTeX text has not yet been supplied for line-by-line claims review**; its name and hash are not a substitute for that review.

## Next non-destructive tasks
1. Generate separate v18 numerical claim / table / section inventory from verified ZIP member; use a separate v19 working directory, never overwrite v18.
2. Match any references to historical FiQA 6648-denominator or SciFact 1109-denominator results to validated qrels-judged 648/300 metrics and report impacts; do not blindly scale inferential estimates.
3. Verify cited 36-cell prospective aggregate metadata and its judged-qid cohort; initial manifest search found zero E5 `cell_manifest.json` despite historic 36-cell summary and GitHub aggregates. Distinguish missing individual evidence from evidence of experiment failure.
4. P2 security model remains open; results from different attack/evaluation input cohorts must not be integrated as single causal or privacy tradeoff.

**Gate classification:** P6 exact source-location blocker CLEARED; P6 content/numerical revision NOT STARTED.
Evidence tier: author-shared local source checks, not independently inspected frozen TeX bytes on reviewer machine.
