# 2026-11-23 ablation tools and rerun commands — provenance index

This is a **source-file SHA-256 index from the ChatGPT-produced Python scripts** preserved in the conversation's generated-file working environment, computed 2026-11-23. **The executable source files are not in this GitHub commit**. On the author's Mac they must be deposited from the actual copies executed, and checksums compared against this index. A name and digest are not substitutes for source delivery.

## Script inventory and SHA256

| Generated script | SHA-256 (generated copy) |
|---|---|
| ipm_ablation_preflight_readonly_v1.py | c4eb128860eaf233bc4ff16c1cae90de829f8fc9a3d5aed890b5104b75481a41 |
| ipm_ablation_diagonal_reuse_gate_v2.py | f87ef9049a26a1f5dbcb437be1e2aeb7e19c15f06dcfbfcad5b6076c5ad061c1 |
| ipm_ablation_guard_lineage_gate_v3.py | 9e049a1895d3ec9789042982051b906f4cdad5e4b137209d62c43e1a6f370cf9 |
| ipm_ablation_crosscell_pilot_v1.py | d139f1878e663dc25295463e16f4de327bb43048eda7498c8f39728f98467623 |
| ipm_ablation_pilot_rank_compat_v1.py | b27c7eb19bc513f7ba208690c80e2035b603ecf19ad39677cd3bb345570b314c |
| ipm_ablation_factorial_runner_v1.py | 4c5a9bfa3f4f1a9d6107fe6c1e441426878f7ac055739b6a3f245b0602250f79 |
| ipm_ablation_factorial_runner_v2.py | a21ec63a5e7fa768a4bba0537c2c4212d6b52fe9b4d0043c1b96721f33c817a4 |
| ipm_ablation_audit_factorial_v1.py | 0011c3980657e60e540e7e24b6552640de81613df6ca768b1bbbea4b33890dfb |
| ipm_ablation_paired_factorial_stats_v1.py | d3d08595e780bde4b11e48f4e437ca173959f74f6dec6e8b8a4b2f2f62241ca2 |
| ipm_ablation_stability_factorial_v1.py | cad635923d628618181c0041014b6449afabe410b991cba2f3bd8cac254e479d |
| ipm_ablation_stability_paired_ci_v1.py | 9919b2ad7b5047932f03ce0a973b88025819fe67e6a602ca9992552c7b156e6b |
| ipm_guard_diagonal_vector_identity_v1.py | 0e44fb8a850d06fbfd1a6ab58465fd0991cedb01a32bea02458887c948af9885 |

## Command and environment provenance

Author Mac: Python 3.10.13, NumPy 2.2.6 in sample manifests. Research root `$HOME/Downloads/research/semantic-guard`. Below is a record of principal commands that **were reported run** or supplied in chat. Do not rerun without need; the existing outcomes are preserved.

```bash
# Pilot (reported PASS)
python3 "$HOME/Downloads/ipm_ablation_factorial_runner_v1.py" \
  --root "$HOME/Downloads/research/semantic-guard" \
  --out "$HOME/Downloads/IPM_ablation_v1_scifact_s7_D128_B10" \
  --one --dataset scifact --seed 7 --dimension 128 --bits 10

# First 36-cell run stopped at TREC-COVID qrels path after 24 conditions
set -o pipefail
python3 "$HOME/Downloads/ipm_ablation_factorial_runner_v1.py" \
  --root "$HOME/Downloads/research/semantic-guard" \
  --out "$HOME/Downloads/IPM_ablation_factorial_36_v1" \
  --all 2>&1 | tee "$HOME/Downloads/IPM_ablation_factorial_36_v1.log"

# Resume existing 24 conditions, do not overwrite
set -o pipefail
python3 "$HOME/Downloads/ipm_ablation_factorial_runner_v2.py" \
  --root "$HOME/Downloads/research/semantic-guard" \
  --out "$HOME/Downloads/IPM_ablation_factorial_36_v1" \
  --resume 2>&1 | tee "$HOME/Downloads/IPM_ablation_resume_v2.log"

# Whole-cell audit (reported PASS_ALL_36)
python3 "$HOME/Downloads/ipm_ablation_audit_factorial_v1.py" \
  --root "$HOME/Downloads/research/semantic-guard" \
  --results "$HOME/Downloads/IPM_ablation_factorial_36_v1" --check-input-hashes

# Query-paired 2x2 utility CIs (reported PASS)
python3 "$HOME/Downloads/ipm_ablation_paired_factorial_stats_v1.py" \
  --root "$HOME/Downloads/research/semantic-guard" \
  --results "$HOME/Downloads/IPM_ablation_factorial_36_v1" \
  --bootstrap 5000 --report-dir "$HOME/Downloads/IPM_ablation_statistics_v1"

# Original-code-proxy stability (reported PASS)
python3 "$HOME/Downloads/ipm_ablation_stability_factorial_v1.py" \
  --root "$HOME/Downloads/research/semantic-guard" \
  --results "$HOME/Downloads/IPM_ablation_factorial_36_v1" \
  --report-dir "$HOME/Downloads/IPM_ablation_stability_v1"

# 45-factor query-paired stability CIs (reported PASS)
python3 "$HOME/Downloads/ipm_ablation_stability_paired_ci_v1.py" \
  --root "$HOME/Downloads/research/semantic-guard" \
  --results "$HOME/Downloads/IPM_ablation_factorial_36_v1" \
  --input-dir "$HOME/Downloads/IPM_ablation_stability_v1" \
  --report-dir "$HOME/Downloads/IPM_ablation_stability_ci_v1" --bootstrap 5000
```

## Do not silently alter results
- Keep old v18 manuscript and source artifacts unchanged.
- Do not publish local raw embeddings, proprietary text, protected qrels, secret file paths, or personally identifying data.
- Local full result JSONL and per-cell manifests need an appropriate repository release or redacted hash list, plus SHA verification from the author's Mac.
- The diagonal vector identity checker is **prepared, not observed PASS**. Continue its read-only run and archive the terminal log.

## Publication status
Until the executed versions of scripts, 36 manifests, and safe output tables are deposited and checked, this GitHub repository contains **an audit trail of the experiment**, not a complete independent reproduction package.