# IP&M Stage 1B HNSW provenance decision and corrected test-cohort audit
Date: 2026-11-20 KST. Status: REVIEW EVIDENCE — original manuscript and experiment inputs unchanged.

## Historical execution — bounded finding
- The `SCI_First.zip` manuscript variant `main_en_1.tex` asserts FAISS HNSW (line 165 and experimental setting table), while `main.tex` and other later variants specify exact L2-normalized inner-product retrieval. Manuscript source variants conflict.
- The author's `IPM_stage1b_evidence_v1.zip` contains 63 Guard `config_resolved.json` records, all with `index.type=faiss_hnsw` (M=32, efConstruction=200, efSearch=128).
- The same collected source snapshot `run_dense_retrieval.py`, SHA256 `09ecb4d855417189f9dca36dcf67913ac1b08cb2051f7a09bbfb8b7f5f16a3a5`, actually performs `sims = docs @ q` and NumPy `argpartition`/sorting; it has no FAISS import, HNSW index creation or use of the `index` configuration. This proves the **supplied implementation** is exact, NOT what a separate historical executable used.
- v15b original-Mac author log: all 4 of the previously divergent FiQA/SciFact ε0 seed7 saved Top100 rankings exactly reproduced using whole-matrix float32 exact calculations; earlier chunked rank changes were <=2.38e-7. This supports exact-output compatibility but cannot exclude HNSW obtaining identical results.
- Previous project `semantic-guard-framework/configs/base.yaml` contains HNSW configuration, while `guard-semantic-defense/src/pipeline/search.py` is an exact dot-product implementation. No historical executable command, run timestamp+code hash, or FAISS index linked to the 63-paper results has been shown. History unproven, not disproven.

**Decision**: preserve originals, label historical HNSW provenance OPEN, do not silently assert exact/HNSW historical execution. Retrieval *evaluation and source-derived corrections* can continue independently. A final ablation protocol must explicitly fix and log a common retrieval backend.

## Test-qrels corrected metrics
Author-run v13 validates all qrels IDs and zero unjudged-query relevance metrics; v14 independently re-scores archived Top100 rankings for all 72 runs (63 Guard+9 Raw) without discrepancy. The locally uploaded sanitized Cleanroom joined CSV SHA256 is `f56558f1e05e2ed2214eafa993797bc9c5d6cf1e280ac9033633fc2695646865`, corresponding to original-local source SHA256 `9038fa6947ff31ab0ff20d26ac72a7a3b8b1eaa17e737dadf62317e7da09ed63` in its collector manifest.

For Recall@10, nDCG@10 and relevance-based Flip@10, using the validated test-only cohort means arithmetic re-expression `mean_test = mean_all × N_all/N_test`. N all/test: FiQA 6648/648, SciFact 1109/300, TREC-COVID 50/50. **This does not hold for qrels-independent Top1 identity, Top10 set overlap or Kendall tau; Top1 corrected three-seed means come from v13 author output.** The stage3_ext main paper's Utility Score Mean is (Recall@10+nDCG@10)/2, not the separate raw-normalized score of an older aggregation implementation.

| epsilon | Old Utility all queries | Corrected Utility test only | Old Top1 all queries | Top1 test-only v13 | Old Flip10 all queries | Flip10 test only | Old flagged /9 | Test flagged /9 (exploratory) |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|
|0|0.0406|0.0948|0.0522|0.0491|0.2201|0.5385|0|0|
|2|0.1039|0.2532|0.1800|0.1842|0.0758|0.2687|3|0|
|4|0.1367|0.3395|0.3158|0.3199|0.0501|0.1812|8|8|
|8|0.1484|0.3733|0.3649|0.3740|0.0301|0.1363|8|8|
|16|0.1604|0.3978|0.3976|0.4096|0.0270|0.1228|9|9|
|32|0.1686|0.4252|0.4673|0.4766|0.0180|0.0936|9|9|
|64|0.1969|0.5055|0.9996|1.0000|0.0000|0.0000|0|0|

The author-defined Flag changes **37/63 to 34/63**, with only SciFact epsilon2 all three seeds losing a flag. Not a validated safe region and does not prove a new security guarantee. The 63-row derived metric table and the 21 dataset×epsilon aggregates were created locally and are kept as reviewer working artifacts pending broader manuscript reconciliation.

## Required before final manuscript
1. Recalculate per-seed judged-only Top1, Top10 overlap, Kendall tau and all retained stability plots, not by scaling all-query means.
2. Confirm BM25 source and its test-cohort denominator before claiming dense/BM25 comparison.
3. Reconcile all manuscript tables/figures/results against unified test-cohort data; keep the legacy table as a separate historical audit not primary corrected findings.
4. Document actual evaluation backend of new ablation executions. Declare missing historical HNSW provenance as limitation unless hard execution evidence is recovered.
5. Preserve 1A security threat-model restrictions and avoid treating the exploratory author-defined flag as security protection.

**Provenance:** original author uploaded sources and v13/v14/v15b terminal output, independent direct code/config inspection. This note is NOT a full rerun of embeddings, rankings, or historical HNSW execution.
