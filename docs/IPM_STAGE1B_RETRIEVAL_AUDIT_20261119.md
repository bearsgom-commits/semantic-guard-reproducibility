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


## Author-run v13: validated test-qrels cohort and 37→34 flag sensitivity (2026-11-19 KST)

Author ran local read-only `audit_ipm_stage1b_test_qrels_v13.py` against frozen Cleanroom joined SHA256 `9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63`, with all 3 official test-qrel file hashes verified. All test qids are present in the embedding-query IDs; all positively judged doc IDs are in corpus doc IDs, no duplicate qrel pairs; FiQA all queries 6648 vs test 648, SciFact 1109 vs test 300, TREC-COVID 50 vs test 50 (2 negative-grade judgments). Test-only reaggregation of stored per-query metrics and raw-vs-guard Top1/Flip passed across 63 Guard + 9 Raw conditions. **This recalculates stored outcomes under a new query denominator, not retrieval/encoder execution.**

Notable descriptive mean differences (3 seed means):
- FiQA ε2 Decision Flip@10 all-query 0.035800 vs test-only **0.367284** (flags 0→0); ε0 0.055004 vs test 0.564300.
- SciFact ε2 all-query 0.091674 vs test-only **0.338889**: author-rule flags **3→0**; ε0 0.165314 vs test 0.611111.
- TREC-COVID unchanged by query split (50/50). All 63 exploratory region flags **37→34**, changed exactly SciFact ε2 for 3 seeds. This is not a recalibrated, certified operating/security region.
- Guard ε64 **test-only** mean Recall/nDCG: FiQA 0.456723/0.381432; SciFact 0.807222/0.693833; TREC-COVID 0.019189/0.674416. Raw reference nDCG is slightly different: from frozen retrieval_all source and test qrels denominator FiQA 0.381459 and SciFact 0.693895 (Raw recall same to six decimal). Do not mislabel Guard as Raw.
- The v13 terminal log's `RAW_EXAMPLE` field is **misnamed**: source line reads `results[(ds,7,0)]['guard']['all_recall']`, i.e., ε0 Guard all-query Recall, NOT Raw. This affects only printed label, not 63-row test reaggregation or flags.

**Scientific impact:** Reported BEIR test retrieval Recall/nDCG must be recomputed/reported for the judged query cohort, with raw/guard and stability on the same qids. Historical all-query results remain valid as explicitly defined *all-embedded-query, missing-qrels=zero* diagnostics but not apples-to-apples test-set BEIR evaluation. The original exact NumPy run source and 63 config files claiming `faiss_hnsw` remain discordant; historical execution path not proven. TREC-COVID source qrels include -1 grade and original nDCG code computes `2**(-1)-1=-0.5` if such a doc ranks in top10; impact not yet tested directly from saved rankings.

**Next finite verification:** local read-only `audit_ipm_stage1b_rank_qrels_v14.py`, SHA256 `d4f5d84ab7cea777ee1553625190e1f51284531172871b8d1640bf8f07af45d8`, independently re-scores saved `rankings_top100.jsonl` using frozen test qrels (Recall@10, nDCG@10, Hit@10, Top1 rel) and checks original per-query `metrics_query.csv` for all **72 runs** (Guard63+Raw9); counts retrieved negative grade top10 judgments, validates document/query identity without exposing IDs. **Not yet run on original Mac**. Python syntax, independent small synthetic positive-score and intentionally corrupted-nDCG rejection tests PASS. Source does **not** rerun similarity ranking, distinguish exact vs HNSW, or verify model revision. It writes no files. A downloadable ZIP of the source was prepared, all research originals untouched. Stage 1B remains OPEN, and Stage 1A integrated Korean review remains a separate draft, not original `main.tex`.

## Author-run v14: saved Top-100 rank-to-qrels metric consistency PASS (2026-11-20 06:22 KST)

Source: author-supplied v14 full stdout and the directly inspected read-only audit_ipm_stage1b_rank_qrels_v14.py. Frozen Cleanroom joined SHA256 9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63 PASS. All three test qrels hashes PASS. Saved Top100 rankings independently rescored from qrels match per-query Recall@10, nDCG@10, Top10 relevance hit and Top1 relevance for all 72 archived runs (Guard63 + Raw9); 72/72 PASS. No negative-grade TREC-COVID test judgments appeared within reviewed Top10 lists. No original files modified.

Raw reference test-only Recall/nDCG for FiQA 0.456723/0.381459, SciFact 0.807222/0.693895, TREC-COVID 0.019189/0.674416 (same across seeds). Guard ε0 test nDCG: 0.038840, 0.129212, 0.141321 respectively. The TREC-COVID large Recall/nDCG difference is possible because Recall uses ALL relevant documents as denominator, nDCG grades only top-10 ordering. Do not call it an evaluation defect without per-query evidence.

Scientific scope: v14 validates given rankings vs judged scores, not stored embeddings-to-rankings, encoder/model version, or historical command. v13 confirmed original all-embedded-query denominators incorrectly treated unjudged FiQA/SciFact test queries as zero and flags shift from 37 to 34 under test-only query cohort; any manuscript results must be revised consistently without promoting 34/63 to a validated secure zone.

## v15 planned sampled embedding-to-rank diagnostic (2026-11-20 KST; not executed on original Mac)

Separate read-only script audit_ipm_stage1b_exact_rank_probe_v15.py SHA256 1bfcc7d966a7f025d41008d201e9defb8eea13fb4e2a4b09191c5aebc3108b82. It validates frozen Cleanroom joined/qrels hashes and samples two judged qids per dataset, seed7, across Raw + Guard eps {0,32,64}: 12 run directories / 24 query-run probes. It streams the saved NPY vectors in bounded chunks, computes L2-normalized exact cosine/inner-product, and compares Top1, Top10/Top100 ordered/set matches and stored scores. It does NOT print qids/docIDs/vectors or change any research file. Python syntax PASS; independent synthetic d128/d320/d768 original-runner ranking consistency PASS; mutation detection PASS; ZIP download integrity PASS. No original Mac output yet.

Even an exact Top100 match only establishes computational compatibility with an exact ranker; FAISS HNSW could also retrieve identical rankings. The resolved configs say faiss_hnsw while the available run_dense_retrieval.py computes NumPy exact dot product, and the reconstructed driver acknowledges the historical execution shell command is unavailable. Do not assert the actual historical engine based on this probe; continue to seek original run logs/command/hash or clearly mark historical provenance unrecovered. Stage1B remains open and original main.tex unchanged.


## Author-run v15 bounded embedding-to-ranking check: one discrepancy (2026-11-20, log 06:22 KST)

**Source:** author-provided exact v15 terminal log, inspected `audit_ipm_stage1b_exact_rank_probe_v15.py` and prior uploaded `IPM_stage1b_evidence_v1.zip/source/run_dense_retrieval.py`. Cleanroom joined SHA and three test-qrel SHA guards PASS. At seed7, all three datasets, Raw + Guard epsilon {0,32,64}, two judged qids per dataset: **12 saved runs / 24 query-run probes**, with **PASS_ORDER=22, PASS_SET_ONLY=1, MISMATCH=1, INCONCLUSIVE=0**. FiQA Guard epsilon0 has one identical Top100 set with different ordering (its other query PASS_ORDER), maximum shared-score drift `2.38e-7`. SciFact Guard epsilon0 has one `MISMATCH` (other query PASS_ORDER), maximum shared-score drift `1.79e-7`. All remaining selected runs have exact Top100 ordering match. All run configs specify `faiss_hnsw` while available `run_dense_retrieval.py` source computes normalized NumPy inner products and uses `argpartition`. **Historical executed runner is not proven.**

**Classification caution:** v15 checks near-tie only at **Top1 gap**; it does not examine Top100 cutoff rank 100/101. Thus a near-tied Top100 membership swap can be called `MISMATCH` even when max shared scores differ by ~1e-7. The failing output does not indicate which rank boundary or how many IDs diverged. Do not infer actual HNSW usage or declare a ranking error until discrepancy ranks/candidate cutoff gaps are observed.

**Targeted read-only v15b prepared, not yet author-run:** `audit_ipm_stage1b_rank_tie_diagnosis_v15b.py` local SHA256 `04ec9dcc4516aca3a50b5ea1439a7700b3c18c46519cf40893fbde95d3f79d51`. It selects the **same two test qids per dataset** for FiQA/SciFact Guard epsilon0 seed7, recomputes exact ranking (a) using v15's 8192-row chunked float32 dot products and (b) using archived source-runner-style **whole-matrix** float32 normalization and dot product, then prints ID-free Top1/Top10/Top100 set/order, first rank divergence, adjacent ranking inversions, cutoff score gap and saved-score drift. Local Python compilation and synthetic known-order/score test PASS. Reads no original raw text, writes no source file, publishes no query/doc IDs, and uses only small in-memory FiQA/SciFact eps0 arrays. **No original Mac output yet.**

Decision gate: if whole-matrix source-style ranking matches saved rankings, mark v15 numerical chunking as plausible source of difference; if only ~floating-point near ties remain, qualify rank-order reproducibility and assess Top10/metric impact. Otherwise preserve the historical engine/provenance issue and do not assert exact-vs-HNSW resolution. v14 rank-to-qrels 72/72 PASS and v13 test-qrel denominator correction remain supported independently. Stage1B not closed; original `SCI_First.zip/main.tex` unchanged.
