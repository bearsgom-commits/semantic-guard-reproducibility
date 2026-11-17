# Matched-MIA execution and verification

Updated 2026-11-17. **Scope: source inspection and synthetic smoke test; not a reproduction of manuscript AUROC.**

## Verified input layout

The published historical script `scripts/stage3/run_attack_mia_matched.py` searches for:
```text
<PROJECT_ROOT>/artifacts/<DATASET>/intfloat_multilingual-e5-base/stage3/seed<SEED>/eps_<EPS:02d>/guard_embeddings.npy
```
It also supports a fallback recursive discovery. Dataset labels may use dashes or underscores.

## Historical default arguments and protocol

- `--sample_size 2500`, `--sampling_seed 20260822`, `--chunk_size 256`.
- Required: `--project_root`, `--dataset`, `--seed`, `--epsilon`, `--output_dir`.
- The embedding array must have at least 5000 rows.
- It samples 2500 member and 2500 disjoint nonmember rows; the index is exactly the sampled member rows.
- Member feature extraction excludes self-neighbor similarity; nonmembers are tested against the same member index.
- Attack scoring is based on three nearest-neighbor statistics, followed by a sigmoid and rank-based AUROC.
- Four outputs: `attack_item.csv`, `attack_summary.json`, `run_meta.json`, `sampling_indices.json`.

## Example command (NOT a recovered historical command)

```bash
python3 scripts/stage3/run_attack_mia_matched.py \
  --project_root /path/to/semantic-guard \
  --dataset fiqa --seed 7 --epsilon 8 \
  --sample_size 2500 --sampling_seed 20260822 \
  --output_dir /path/to/new/output/directory
```

Never execute against an existing output directory: the script refuses overwrite.

## Verified checks

The original script completed a small synthetic 48-row / 16-dimensional smoke test with 12 members and 12 nonmembers, producing four expected files. This checks basic code operation **only**. Historical runs across 63 conditions remain unverified.

The separate `scripts/check_published_validation.py` checks that the published 63-row audit table has unique keys, 37 matched-region flags, and epsilon-wise counts 0/3/8/8/9/9/0. It does **not** verify input embeddings or original attack score generation.

## Reproduction requirements

1. Original embedding files or deterministic encoding+Guard generation instructions.
2. Input SHA-256 manifest, exact model revision and environment.
3. Original run logs/metadata for 63 conditions and their published summary outputs.
4. Independent execution on public or appropriately accessible inputs, including checks of generated AUROC.
5. Full table/figure lineage to the submitted manuscript.

**Interpretation:** Protocol-specific near-chance AUROC is not a privacy guarantee, nor is `epsilon` a differential-privacy parameter.
