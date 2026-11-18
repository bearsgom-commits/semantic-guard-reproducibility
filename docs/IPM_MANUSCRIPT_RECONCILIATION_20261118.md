# IP&M manuscript/reproducibility reconciliation (2026-11-18 KST)

## Scope and immutable baselines
- Manuscript under editorial review: `main(20261118-095709).tex` (866 lines), SHA-256 `66aded97658a11ade0ba954951d2e6d9152c7f18e75316dce65ee6475690241c`. This manuscript is **not** published in this repository.
- Historical audit baseline: commit `fa2ce2a00dd913a883c911c81644e098ed33b137`. Never reinterpret subsequent documentation changes as proof of an older experiment.
- Editorial working candidate (local to author): not an approved final manuscript.

## Open finding MIA-01: score specification
The manuscript reports pre-sigmoid score `0.5*maxSim - 0.3*meanTop5Sim - 0.2*marginTop1Top2`.
Both public scripts `scripts/stage3/run_attack_mia_matched.py` and `scripts/stage3/run_attack_mia.py` implement **positive** 0.3 and 0.2 weights, then `sigmoid(8*(raw-0.5))`.
**Disposition:** manuscript correction candidate only; historical condition-level command logs/input embedding identity remain to be linked. No claim of independent experimental rerun made.

## Open finding SEC-02: manuscript vs. published aggregate
| epsilon | manuscript Table 4 | public `verified_epsilon_summary.csv` |
|---|---:|---:|
| 0 | 0.8064 | 0.8062463369597395 |
| 2 | 0.8629 | 0.8627224488457875 |
| 4 | 0.8303 | 0.8301319727723995 |
| 8 | 0.8699 | 0.8696738110797594 |
| 16 | 0.8796 | 0.8794248949217913 |
| 32 | 0.8372 | 0.8369644104436926 |
| 64 | 0.2074 | 0.2189515037115881 |

The published `aggregate_stage3_ext.py` uses the unweighted mean of `(1-global_minmax)` across reidentification accuracy, top-10 leakage, and membership AUROC. In `build_attack_wide`, the aggregation code uses **max** across numeric attack fields sharing the same (dataset, seed, epsilon) key. Whether this explains the observed discrepancy is **not established**; investigate source input versions, attack-family filtering, row sets, and normalization range **before** altering manuscript results.

## Existing replay evidence and its limits
- Published `results/stage3/matched_mia/replay_20261118/condition_comparison_63.csv` records 63/63 PASS and zero recorded output differences. Final replay driver classified 21 TREC-COVID conditions as freshly `executed` and 42 FiQA/SciFact conditions as `existing_report`.
- Individual sanitized reports, input Guard embedding SHA-256 manifest, command/environment provenance and end-to-end BEIR/E5/retrieval reproduction remain unavailable in this public repo as of the baseline audit. This is **not** third-party independent reproduction.
- Manuscript revision and reproducibility can proceed as parallel tracks. Final manuscript-to-artifact reconciliation and reproducibility freeze must occur **after** the scientific scope and revised tables are fixed.

## Required gates before final release
1. Trace historical MIA source version against condition logs, report digests and input embeddings.
2. Trace `security_score_mean` from exact per-condition input rows, normalization and attacked component selection into each manuscript table/figure.
3. Resolve retrieval execution mode (NumPy exact vs FAISS HNSW) using executed commands and logs, rather than configuration alone.
4. Record whether any adviser-requested ablation/comparator/statistical changes alter the experimental corpus; verify their own provenance if performed.
5. Confirm final manuscript values and claims against frozen public evidence; do not relabel consistency checks as full reproduction.

This file is an audit of outstanding issues, **not a PASS certificate**.
