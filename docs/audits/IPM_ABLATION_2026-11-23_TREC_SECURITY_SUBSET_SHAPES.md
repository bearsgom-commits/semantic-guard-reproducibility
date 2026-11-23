# TREC-COVID historical security input sizes — subset finding (2026-11-23 KST)

**Evidence:** author-supplied read-only Mac terminal output; these .npy files were not independently fetched from the Mac by this GitHub record.

## Six unique source-file comparisons

Historical TREC-COVID MIA and Re-ID `run_meta.json` refer to:
```
artifacts/trec-covid/intfloat_multilingual-e5-base/seed{seed}/L3_a0.2_eps{eps}/guard_embeddings.npy
```
Factorial diagonal/canonical stage3 array:
```
artifacts/trec_covid/intfloat_multilingual-e5-base/stage3/seed{seed}/eps_{eps:02d}/guard_embeddings.npy
```

| Seeds | Epsilon reference | Historical attack input .npy | Canonical stage3 .npy | dtype |
|---|---|---|---|---|
| 7,13,42 | 0 (128D 4bit) | (5000,128), 2,560,128 bytes | (171332,128), 87,722,112 bytes | float32 |
| 7,13,42 | 32 (320D 10bit) | (5000,320), 6,400,128 bytes | (171332,320), 219,305,088 bytes | float32 |

All 6 seed/epsilon comparisons have those same shapes and corresponding sizes. Both files exist but are not the same file or size. The 12 lineage issues correspond to these 6 unique attack input arrays, used by two historical attack families (MIA and Re-ID). Thus the **immediate divergence is corpus coverage (5000 vs 171332 rows)**, rather than mismatched projected vector dimensionality or numeric dtype.

## Conclusions we can and cannot reach

- Historical TREC-COVID MIA/Re-ID operate on a **5000-row input representation**, while the prospective full-corpus factorial runs use **171332 rows**. Historical attack observations must be reported with this scope.
- Cannot yet assert the 5000 rows are the *first* 5000 full-corpus rows, are the same document IDs, or contain equal transformed vectors. Any such claim requires documented sampling/row IDs and value comparisons.
- This is not proof that historical security experiments are invalid; it is **not comparable full-corpus exposure evidence** without additional scope qualification.
- Earlier 18-cell sampled diagonal identity checked *canonical stage3* arrays against regenerated prospective diagonal representations; it did **not** validate the historical TREC-COVID attack subset arrays.
- MIA and Re-ID differ in attacker model; matched MIA must not be conflated with those two, and off-diagonal prospective conditions have no attacks measured.

## Next narrow read-only gate

Find historical TREC-COVID 5000-row source IDs/sampling manifest, compare with canonical corpus IDs, and only where row alignment is evidenced compare a small vector sample. Avoid repeating 36 retrieval cells or any existing attacks. All historical source data and v18 manuscript remain unchanged.

**Status:** six source-pair sizes explained by row count; row ID alignment and historical attack equivalence **not yet proved**.