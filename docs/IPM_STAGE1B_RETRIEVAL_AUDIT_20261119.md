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


## Independently inspected author-uploaded Stage1B ZIP (2026-11-19 KST)

The actual `IPM_stage1b_evidence_v1.zip` was opened and all 21 files inspected. ZIP integrity PASS; 20/20 internal `bundle_manifest.json` SHA256 matches. Full audit report remains author-local: `IPM_STAGE1B_EVIDENCE_AUDIT_20261119.md` (SHA256 `8ead6c55af0229fe8fbc65302f597d7607a386f9c5a4456666b46c680dbcf1bc`). The public note contains no source text, embedding vectors, corpus/query IDs or local path identities.

**Aggregation checks:** Cleanroom has 72 retrieval rows (63 Guard + 9 Raw), 63 raw-reference stability rows, 63 joined rows, 63 Guard configs/summary/query-stat aggregates, 9 raw configs. All 63×12 = **756** checks comparing Guard retrieval and stability joined metrics to the source CSV/stability JSON and query-level numeric summaries PASS; 0 numeric disagreements. 72/72 retrieval metric results identical between legacy and Cleanroom; 63/63 raw-reference stability conditions identical. Legacy stability CSV also contains separate guard-internal comparisons (total 117 rows), which must not be conflated with its 63 raw-reference records. These tests **do not rerun source rankings**, E5 or per-query relevance judgments.

**Major cohort risk:** All 63 resolved Guard configs point at `qrels/test.tsv`. BEIR qrels aggregate metadata reports 648 FiQA, 300 SciFact and 50 TREC-COVID distinct *test-judged* qids, while every retrieval and stability run reports 6,648, 1,109 and 50 evaluated embedding queries respectively. Directly inspected `run_dense_retrieval.py` loops over **all** `query_ids.json`, evaluates `qrels.get(qid,{})` and returns zero Recall/nDCG on unjudged queries before dividing by **all query count**. The `compute_stability.py` code similarly uses all shared qids to define `flip_at_10 = [ref_hit_at_10 != target_hit_at_10]`. Under the test qrels protocol, FiQA and SciFact retrieval and relevance-based Flip have **test-qrel denominator dilution**, unless declared as an intentional all-query denominator. This is not proof that qrel qids actually align to embedded IDs; exact qid intersection and corrected query-level scores are still needed. Numeric conditional scaling factors are 6648/648 = 10.259259 for FiQA, 1109/300 = 3.696667 for SciFact. Do **not** silently replace published metrics or infer final corrected rates from factors alone.

**Search implementation:** 63/63 config JSONs specify `index.type=faiss_hnsw` and HNSW M32/efC200/efS128, while uploaded execution `run_dense_retrieval.py` uses exact normalized NumPy `docs @ query` and `argpartition`, never calls FAISS. Source-level implementation is exact dense and configuration-level index is HNSW. The separate reconstructed `reproduce_stage3.py` explicitly warns that the historical shell command was not recovered; do not assert historic execution code identity without evidence.

**Stability metric semantics:** Top1 identity and Top10 set overlap are query-set comparisons; `decision_flip_probability_at10` is a relevance-hit binary transition proxy, not an observed operational decision. `tau_on_union` treats tied missing positions as discordant against untied positions, and is a custom union-order statistic, not guaranteed to equal standard Kendall tau-b. TREC test qrels include 2 negative (-1) grades; numeric impact of the source nDCG gain transform is unquantified.

**Next single read-only verification:** Local script `audit_ipm_stage1b_test_qrels_v13.py` (SHA256 `9fb6fa443fdbc42dfa6eb6ffaad2f4e63b2d3e39711433bf68455dd56bf275ec`) checks frozen joined SHA plus three test qrels SHAs, corpus/query ID coverage and uniqueness, all 72 metrics_query CSVs and 63 stability_query CSVs, recalculates all-query original means, and then test-qrels-only Recall/nDCG/Top1/Flip and exploratory Region Flag sensitivity. It exports **no raw IDs or data** and writes **no files**. Python compile and synthetic positive+mutation tests PASS; **no author Mac real-data execution yet**. Do not label 1B closed until qid-level test and retrieval execution provenance are resolved. Original `main.tex` and Stage1A approved *separate candidate* remain unmodified.
