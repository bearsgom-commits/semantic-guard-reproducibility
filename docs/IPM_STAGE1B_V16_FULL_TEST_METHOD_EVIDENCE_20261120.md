# IP&M Stage 1B — full judged-test retrieval method evidence (v16)

**Evidence date:** 2026-11-20 KST. **Source:** author-provided original Mac terminal output from `audit_ipm_rank_generation_proof_v16.py --all-test`, cross-checked against the source code bundled in `IPM_Stage1B_V16_proof_package.zip`. **Status:** FULL TEST-COHORT COMPUTATIONAL REPRODUCTION PASS; HISTORICAL PROCESS IDENTITY OPEN.

## Reported full-test result

```text
EXIT_CODE=0
SUMMARY run_count 72 expected 72 query_probes 23952
top100_exact_order 23952 top10_exact_order 23952 top100_same_set 23952
score_mismatch_gt_1e-6 0 max_score_delta 0 config_hnsw 72 run_mismatch_count 0
PROVEN source snapshot uses exact NumPy, resolved configs record HNSW, archive reproduced at stated probe coverage
NOT_PROVEN which executable generated ORIGINAL historical files; exact-vs-HNSW operational execution trace absent
NO_SOURCE_FILES_WRITTEN NO_RAW_IDS_PRINTED
METHOD_PROOF_PASS_FULL_TEST
```

Test-judged query counts: FiQA 648; SciFact 300; TREC-COVID 50. `(648 + 300 + 50) * 3 seeds * (1 Raw + 7 Guard) = 23952` probes over 72 runs. Original stored Top100 and exact recomputation agree **in ordered IDs** in all 23952; Top10 ordered IDs match in all 23952. Saved Top100 scores match recomputation with reported maximum absolute difference 0.

## What the source actually verifies

The inspected v16 source pins (a) frozen Cleanroom joined SHA256 `9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63`, (b) three frozen test qrels hashes, and (c) archived exact runner `repo/src/stage3/run_dense_retrieval.py` SHA256 `09ecb4d855417189f9dca36dcf67913ac1b08cb2051f7a09bbfb8b7f5f16a3a5`. It parses the runner AST and checks its `docs @ q` / `np.argpartition` / `np.argsort` behavior without FAISS import or index search in `main`. It loads saved raw/Guard float32 embeddings (not recreated by E5), L2-normalizes the **whole document matrix** and query matrix like the source, computes exact all-document inner products, and checks per-query archived top100 ordered IDs and stored scores. It also verifies run labels and that resolved config `index.type=faiss_hnsw` is present for all 72 runs.

This **proves reproducibility of the saved test-cohort rankings from the saved embeddings using the inspected exact search implementation**. It does **not** establish the historical executable that wrote the archive: HNSW can theoretically return identical top100 results, and `faiss_hnsw` config values alone do not prove actual use of an HNSW index. The source's bounded HNSW trace scan outputs were not provided in the pasted eight terminal lines; the full log is retained by the author as `~/Downloads/IPM_stage1b_v16_proof.log`, but has not been uploaded or independently inspected. The output alone does not establish embedding generation reproducibility.

## Decisions and scope boundaries

- The final paper may truthfully state that **the archived judged-test rankings were exactly re-created by a normalized-exact-inner-product search algorithm** from the archived embeddings. It must not state the historical runs were provably Exact or provably HNSW.
- The original HNSW config mismatch must be documented, corrected **prospectively** in any new experiment configuration, and never silently retroactively edited in archived config snapshots.
- Original all-query FiQA/SciFact scores remain **inappropriate as BEIR test-only metrics**. Rebase the manuscript's utility and relevance-based decision-flip on the v13 test qrels cohort and v14 rank-to-qrels verification, with author-rule flags descriptively 37/63→34/63, and regenerate remaining query-identity-based stability figures from the same test subset.
- Search speed is **not a paper contribution**. The original executable history is not a scientific blocker once final methods/results are traceable, but an independent examiner can still require full pipeline and execution provenance; document the limitation without promising complete historical provenance.
- This report is a **read-only evidence memo**, not a revision of `SCI_First.zip/main.tex`. Continue corrected manuscript candidate and dimension × quantization ablation after the evaluation cohort and retrieval method are explicitly fixed.
