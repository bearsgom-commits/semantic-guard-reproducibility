# TREC-COVID historical MIA/Re-ID: actual Guard input paths diverge (2026-11-23)

**Evidence source:** user's read-only Mac terminal output, not independently inspected original files. This note corrects the earlier hypothesis that the twelve failed checks may reflect only `trec_covid` vs `trec-covid` directory spelling.

## Observed results

For all 3 seeds {7,13,42} × two diagonal epsilon reference settings {0,32} × two historical attack families {mia,reid} = **12 cases**, `run_meta.json.guard_embedding_path` pointed to a real file under:
```text
artifacts/trec-covid/intfloat_multilingual-e5-base/seed{seed}/L3_a0.2_eps{eps}/guard_embeddings.npy
```
The canonical full-corpus Guard file for the new factorial diagonal and prior sampled vector audit was:
```text
artifacts/trec_covid/intfloat_multilingual-e5-base/stage3/seed{seed}/eps_{eps:02d}/guard_embeddings.npy
```
**For every one of these 12 cases:**
```text
RECORDED_EXISTS=True
CANONICAL_EXISTS=True
SAME_FILE=False
SAME_SIZE=False
```

Therefore this is **not merely a pathname alias / identical symlink**. At least the underlying file sizes differ. Neither dimensionality nor corpus row count nor document-ID alignment nor attack input equivalence have yet been established. Different sizes do not, by themselves, establish differences in all vector values, nor definitively prove an experiment is invalid. They do block direct evidence linkage without further examination.

The earlier 18/18 diagonal sampled-vector PASS compared historical canonical `artifacts/trec_covid/.../stage3` arrays with newly regenerated prospective representations. That **does not validate the different `artifacts/trec-covid/.../L3_a0.2...` files actually referenced by legacy TREC-COVID MIA/Re-ID.** Matched-MIA cases have separate metadata/path status; these must not be conflated.

## Narrow follow-up gate

Read-only inspect each of the 6 unique historical attack-referenced Guard files (one per seed × epsilon), comparing its `.npy` shape, dtype and byte size with its corresponding canonical full-corpus array. The same referenced file is used by both MIA and Re-ID within each seed/epsilon, so no need to duplicate work. If row count differs, investigate the exact dataset subset/row-ID mapping before any security linkage. Preserve hashes/metadata if safe, avoid copying or modifying protected embeddings or historical runs.

## Status and scientific interpretation

- TREC-COVID legacy MIA/Re-ID representation lineage **NOT VERIFIED** for six seed/epsilon pairs; 12 attack records remain REVIEW_REQUIRED.
- Do **not** replace failed metadata paths, relabel these historical attack values as factorial security measurements, or treat the original 189 attack experiments as a uniform comparable cohort.
- Cross-cell security exposure for prospective off-diagonal settings remains **unmeasured**.
- Preserve original source code, historical evidence, new factorial runs and v18 manuscript unmodified.
- Follow up with an additional GitHub evidence commit after read-only shape/lineage inspection.

This note is a post-experiment exception record grounded in user-provided terminal output.