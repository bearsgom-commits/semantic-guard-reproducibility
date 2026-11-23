# TREC-COVID historical attack versus canonical Guard prefix — read-only comparison (2026-11-23)

**Evidence:** author's Mac terminal output pasted in conversation. This entry records observed facts only; it is not an independent file audit or attack rerun.

## Observations
- `FIRST_5000_IDS_MATCH=True`: first 5000 IDs in `private_data/beir/trec-covid/corpus.jsonl` equal the first 5000 IDs in `artifacts/trec_covid/intfloat_multilingual-e5-base/stage3/shared/corpus_doc_ids.json`.
- `FIRST_5000_IDS_UNIQUE=True`.
- For each seed 7, 13, 42 and epsilon 0,32, `SHAPE_COMPATIBLE=True` but `PREFIX_SAMPLE_EXACT=False`. Thus 6/6 legacy attack-referenced 5000-row Guard arrays fail strict equality on 64 evenly spaced sampled rows against the canonical full-stage3 array prefix. The read-only comparison did not print the magnitude of the difference or per-row exact counts.
- `READ_ONLY_COMPLETE` reported. No source/data modifications were requested.

Legacy MIA and Re-ID reference `artifacts/trec-covid/.../seed{seed}/L3_a0.2_eps{eps}/guard_embeddings.npy` (5000 rows), while canonical prospective diagonals compare to `artifacts/trec_covid/.../stage3/seed{seed}/eps_{eps:02d}/guard_embeddings.npy` (171332 rows). The first-5000 corpus IDs align, but the 64 sampled corresponding vector rows were **not strictly identical** for any of the 6 arrays.

## Scientific interpretation and caveats
- Shape and document order agreement are supported; **vector identity is not established** for historical TREC MIA/Re-ID inputs.
- Exact equality failure alone cannot determine whether differences are small numerical rounding or materially different transforms. Do **not** assert confirmed different projection algorithms, invalid attacks or invalid source data from this test alone.
- The earlier separate 18/18 diagonal sampled-vector PASS concerned canonical stage3 embeddings regenerated from the prospective generator; it **does not cover** the older `L3_a0.2` inputs.
- Historical TREC MIA/Re-ID outcomes must **not** be grafted onto new factorial diagonal exposure cells until discrepancy magnitude, transform and attack models have been established. Off-diagonal exposure remains unmeasured.
- Avoid changing Guard algorithm, old attack records, new factorial outputs or v18 manuscript. A targeted read-only discrepancy-magnitude audit is permissible if scientific linkage is essential; otherwise report legacy security as separate limited-scope evidence.

## Publication status
This is an exception/evidence note from author-supplied logs. Full script execution files and source arrays are not provided here. GitHub entry is not an independently rerunnable full experiment.