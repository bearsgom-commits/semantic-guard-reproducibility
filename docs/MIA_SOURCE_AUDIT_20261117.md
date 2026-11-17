# MIA source audit — five files received

Date: 2026-11-17 (KST). Source: user-supplied `ipm_mia_source_5files.zip`.

| Source path | SHA-256 | Bytes |
|---|---|---:|
| `repo/scripts/stage3/run_attack_mia_matched.py` | `c16963905f4561d8fe15121d6f92c66abbf8486cac9ab34da97415a48ced0d2d` | 9488 |
| `repo/scripts/stage3/run_attack_mia.py` | `5a50ed278591c1e9d08c4367bd1ba1e55456534289fe5f54464c919c29da8d3a` | 14597 |
| `repo/scripts/stage3/aggregate_stage3_ext.py` | `6b9fb79ae5bfec06febeabdab82e6fd3d3f680d2b31a3e84dc5c56722acd1486` | 13574 |
| `_reproducibility_runs/wbs08_cleanroom_20260829_172931/wbs11_public_package_staging/code/run_attack_mia_matched.py` | `c16963905f4561d8fe15121d6f92c66abbf8486cac9ab34da97415a48ced0d2d` | 9488 |
| `_reproducibility_runs/wbs08_cleanroom_20260829_172931/wbs11_public_package_staging/code/aggregate_stage3_ext.py` | `6b9fb79ae5bfec06febeabdab82e6fd3d3f680d2b31a3e84dc5c56722acd1486` | 13574 |

## Comparison result

The WBS11 copies are **byte-identical** to their corresponding `repo/scripts/stage3` files. Thus there are three unique source files, not five distinct implementations.

## Confirmed behavior

- `run_attack_mia_matched.py`: requires a Guard embedding `.npy` array, `--project_root`, `--dataset`, `--seed`, `--epsilon`, and `--output_dir`. Defaults: sample size 2500, sampling seed 20260822, chunk size 256. It samples disjoint member and nonmember rows, uses member rows as its index, excludes self-matches for member feature extraction, and writes `attack_item.csv`, `attack_summary.json`, `run_meta.json`, and `sampling_indices.json`. Requires NumPy.
- `run_attack_mia.py`: older MIA protocol with separate raw and Guard embedding discovery and default seed/epsilon lists. **Not equivalent to the matched protocol**.
- `aggregate_stage3_ext.py`: requires `retrieval_all.csv`, `stability_all.csv` and run output directories; writes joined and figure/table input CSVs. Requires NumPy and pandas.

## Remaining checks

- Historical logs tying each of 63 published MIA conditions to the exact code revision and input embedding SHA-256.
- Raw `guard_embeddings.npy` arrays or a reproducible generation workflow.
- Full aggregation/region-flag lineage, including any later corrections.
- Clean-room execution of source scripts and output comparison.

## GitHub publication verification (2026-11-17)

The three unique original scripts were published to `main` in commit [`cbe8fa68f0ec44d36b1f9a574bc4a4a05186d348`](https://github.com/bearsgom-commits/semantic-guard-reproducibility/commit/cbe8fa68f0ec44d36b1f9a574bc4a4a05186d348):

| Published path | Git blob SHA-1 (matches supplied ZIP) |
|---|---|
| `scripts/stage3/run_attack_mia_matched.py` | `5e9c63ec385af1c7fa217a8a526ba251621fe76a` |
| `scripts/stage3/run_attack_mia.py` | `c92d71c6acd6b5e8bbc949049e192ea808454fb0` |
| `scripts/stage3/aggregate_stage3_ext.py` | `2b3671738b6dcc89634f820dedaaac4a7ad2b920` |

The published source files are byte-identical to the corresponding three files in the supplied ZIP, as established by matching Git blob hashes and recorded local SHA-256.

On a synthetic 48-row, 16-dimensional embedding array, the matched runner completed a small functional smoke test with sample_size=12, producing 24 attack items and the four expected output files. This is **not** a rerun or reproduction of any of the manuscript's 63 conditions. The original empirical inputs and execution logs remain outstanding.

