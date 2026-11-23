# IP&M Guard factorial ablation: 2026-11-23 execution ledger

**Record type:** evidence-status ledger, committed after the work. **Evidence:** user-shared Mac terminal outputs, not an independent GitHub-hosted re-execution. Existing v18 manuscript, historical Stage1A/1B outputs, and Guard algorithm were not intentionally changed. Source scripts and local full outputs must be separately deposited and hashed before claiming independent end-to-end reproduction.

## Study design
Post-review prospective 2×2 factorial: D={128,320}, B={4,10}, datasets={fiqa,scifact,trec-covid}, seeds={7,13,42}: **36 conditions**. Off-diagonal conditions are not epsilon values. Diagonal reference labels: ε=0→(128,4) and ε=32→(320,10). Uses BEIR judged test cohorts, same E5 raw embedding stores, original seeded Gaussian Guard transform and exact float32 inner-product ranking (argpartition then argsort). **Historical HNSW/exact execution provenance remains unresolved** and new execution must not be misrepresented as original historical replay.

## Chronological verification evidence (author-reported)
1. Source/input reconnaissance: canonical full corpus embeddings and matching IDs; old diagonal reuse not established, so 36 prospective cells rerun.
2. SciFact seed7 D128 B10 pilot: corpus (5183,128), queries (1109,128), Top100 (1109,100), input unchanged; qrels test judged 300, 339 qrel rows; no duplicate IDs; pilot Recall@10=0.53022222, nDCG@10=0.40064887.
3. Rank-compatibility check against legacy argpartition→argsort: all Top10 order/set equal on 1109 queries, Top100 sets equal on 1109, Top100 exact orders 1088/1109; judged Top100 order 297/300. Hence prospective batch uses original source ordering convention; tie-breaking not guaranteed stable.
4. Factorial runner one-cell pilot reproduces SciFact values and input-hash unchanged.
5. First batch stops after FiQA 12 + SciFact 12 due to `trec_covid` artifact identifier vs `trec-covid` qrels path; resume runner v2 preserves 24 existing cells and completes remaining 12. Final `BATCH_RESULT completed=36/36 failures=0`, `BATCH_STATUS=PASS_ALL_36`.
6. 36 cell folders; zero missing `cell_manifest.json` or `test_rankings_top100.jsonl`. Whole-result audit reported `AUDIT_STATUS=PASS_ALL_36`, no original or experiment result writes.
7. Paired factorial utility statistics: 18 effects, 5000 query-bootstrap resamples and per-family Bonferroni(18); `STATS_STATUS=PASS_ALL_36`. Example nDCG@10 factors: SciFact D effect +0.13574811, bits +0.33684233, interaction +0.07287634 (Bonferroni interval [0.01613229,0.12885831]); TREC-COVID D +0.13642961, bits +0.29881494, interaction +0.08492818 (Bonferroni [0.00587464,0.16486739]). FiQA nDCG interaction +0.05583501 (Bonferroni [0.03284638,0.07933903]). SciFact Recall@10 interaction Bonferroni interval [-0.00655543,0.13174167] spans zero. Resampling holds three seeds fixed; no generalization across seeds/models established.
8. RAW ranking 9 files present. RAW qids 6648 FiQA, 1109 SciFact, 50 TREC; all judged test qids from all 36 prospective cells matched RAW records: `RAW_ALIGNMENT_STATUS=PASS_ALL_36`. RAW extra unjudged qids are not errors.
9. Stability original `repo/src/stage3/compute_stability.py`: Top1 same ID, overlap@10=intersection/10, custom `tau_on_union(..., pool_k=50)`, flip@10 = change in binary hit@10 (NOT a demonstrated human operational decision). Composite is 0.4*Top1 +0.4*Overlap10 +0.2*(1-Flip10). Original common.yaml overlap_k=10, kendall_pool_k=50. New stability `STABILITY_QUERY_RECORDS=11976`, `STABILITY_EFFECT_RECORDS=45`, `STABILITY_STATUS=PASS_ALL_36`; follow-up paired CI `DESCRIPTIVE_EFFECT_CROSSCHECK=PASS_45`, `STABILITY_CI_STATUS=PASS_ALL_45` with within-family Bonferroni(45). Utility 18 and stability 45 intervals are **not jointly 63-comparison corrected**.
10. Security inventory: 3 datasets × 3 seeds × 7 ε each for legacy MIA, matched MIA, ReID = 189 sets. Old MIA protocol differs from matched MIA; e.g. FiQA s13 ε16 old MIA AUROC 1.0, FiQA s13 ε0 matched MIA AUROC 0.49582096; not interchangeable. Re-ID proxy's attacker projection seed 20260401 is NOT necessarily Guard generation seed. New prospective 36-cell design **has no direct cross-cell security attacks**. Do not attach historical proxy measurements to cross-cells by dimensional match.
11. 18 diagonal old Guard corpus embedding arrays (3 datasets × 3 seeds × ε 0/32) have compatible corpus shape and projection dimension (FiQA 57638, SciFact 5183, TREC-COVID 171332). **Vector identity, algorithm provenance, and security attack comparability still unproven**. A sampled identity checker was prepared but no completed output was provided.
12. Existing GitHub protocol `docs/IPM_ABLATION_PROTOCOL.md` written 2026-11-19 said NOT EXECUTED at that time; this separate record reports subsequent 2026-11-23 execution, *not* retroactive preregistration.

## Source input evidence from one manuscript-reviewed factorial manifest
- Source `repo/src/guard_repr.py` SHA256: `8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d`
- Source `repo/src/stage3/run_dense_retrieval.py` SHA256: `09ecb4d855417189f9dca36dcf67913ac1b08cb2051f7a09bbfb8b7f5f16a3a5`
- Example fiqa seed7 D128 B4 matrix SHA256 `42fea5124bbe699d6dbd610629ee580e79522e740b19d2ac0577df3fe9b5256d`
- Example cell ranking JSONL SHA256 `ed41194bb7b9e50eab08a8b69919b37fcd3e48d7e52aad37048284e4ccb54766`.
These are **values copied from user-provided manifests**, not verified against local Mac files by this GitHub entry.

## Artifact locations on author's Mac (not yet automatically uploaded)
- `~/Downloads/IPM_ablation_factorial_36_v1/` — 36 per-cell manifests and test-ranking JSONL.
- `~/Downloads/IPM_ablation_statistics_v1/` — utility means, effects and protocol.
- `~/Downloads/IPM_ablation_stability_v1/` — per-query stability and factorial effects.
- `~/Downloads/IPM_ablation_stability_ci_v1/` — 45 paired CI comparisons.
- `~/Downloads/IPM_guard_diagonal_identity_v1.log` — **not reported complete**, do not infer PASS.

## Reproducibility publication gates
- Deposit source scripts, dependency snapshot, full executable commands, safe hashes, and appropriate aggregate CSVs with verifiable checksums; do not publish private raw text, source embeddings, or qrels without license review.
- Compare old and new diagonal **actual vector values**, not only shapes, if cross-study security claims are contemplated.
- Keep utility–stability factorial conclusions separate from original security proxies unless matched attack evaluation is performed under the same conditions.
- Do not overwrite historical source data, v18 or paper main.tex; future manuscript revisions require author approval.
- After every subsequent major test, **add commit or evidence record and verify remote SHA**. Local execution and ChatGPT chat logs are NOT GitHub synchronization.
