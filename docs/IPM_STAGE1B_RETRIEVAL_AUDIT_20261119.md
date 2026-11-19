# IP&M Stage 1B — retrieval/stability provenance audit started

**Date:** 2026-11-19 KST. **Status:** collection/preflight prepared, no original Mac run of collector yet. Not independent reproduction.

## Transition from Stage 1A

The author completed v11 arithmetic lineage and v12 cleanroom figure regeneration/integrated separate Korean manuscript review. Stage 1A privacy threat-model and historical source-command limitations remain explicitly open. The original SCI_First.zip/main.tex was not modified. Stage 1B now concerns the *separate* BEIR/qrels, retrieval ranking, exact/HNSW, query-level stability, and original execution source questions.

## Source paths identified (inventory, not content verification)

The existing author's local inventory reports retrieval_all.csv and stability_all.csv under both original runs/_summary/stage3_all3 and WBS08 cleanroom reproduction/runs/_summary/stage3_all3, plus 63 Guard config_resolved.json entries, 63 Guard stability_summary.json entries and 63 stability_query.csv entries in the cleanroom; 9 raw retrieval configs also identified. Source runners under repo/src/stage3 include run_dense_retrieval.py and compute_stability.py; reproducibility/reproduce_stage3.py also identified. These filename counts do **not** prove qrel alignment, metrics or runner execution provenance.

Known unresolved risks are:
1. SciFact unusually low utility: investigate qrels split, query ID pairing and encoder/query preprocessing instead of declaring numerical error without evidence.
2. Manuscript says exact normalized-inner-product retrieval; other config mentions HNSW. Check original resolved configs and actual source/commands before selecting either.
3. Confirm which query-level samples and raw ranking baseline were used for Top1 Stability and Decision Flip@10.
4. Verify BEIR qrels graded gains/denominators and source rankings; derived tables alone cannot reproduce relevance judgments.

## Safe one-time collector prepared

Local separate script: collect_ipm_stage1b_evidence_v1.py, SHA256 321612eba4a339ae16478dc07905802b159bb74669f1b61c8997bbf6911d8780. Reads sources without modifying them. Checks frozen Cleanroom joined SHA256 9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63 and legacy joined SHA256 d7d6237eac0e051f719b125af5bc6f91b5a756fd3e689c4c0a1744cb25a6ae56, requires all 63 configs+stability summaries+per-query numeric aggregates and 9 raw baseline configs. Copies sanitized source scripts and six sanitized summary CSVs. It includes only qrels counts/hash and embedding array metadata; **no raw text, query/document IDs, qrels lines, embeddings or ranking rows are uploaded**. It refuses source SHA mismatch, source errors or existing output ZIP. Keep collector output private pending content review.

Python compilation, isolated synthetic qrels metrics and path sanitization tests and a complete 3x3x7 synthetic end-to-end archive+integrity+redaction test PASS. **No actual author's local input run is claimed.**

Suggested local execution:
```bash
python3 "$HOME/Downloads/collect_ipm_stage1b_evidence_v1.py" --root "$HOME/Downloads/research/semantic-guard"
```
Output to submit for private review: Downloads/IPM_stage1b_evidence_v1.zip. Do not publish this ZIP to GitHub.

## Stage 1B exit gate

Must verify (i) cleanroom numeric summary ↔ original config and stability summaries, (ii) qrels and query/corpus ID alignment, (iii) executed exact vs HNSW path, (iv) per-query/source-ranking recomputation or label its unavailability, (v) figure/manuscript consistency. Stage 1B is currently **OPEN**. No manuscript original or previously published experimental values have been changed.