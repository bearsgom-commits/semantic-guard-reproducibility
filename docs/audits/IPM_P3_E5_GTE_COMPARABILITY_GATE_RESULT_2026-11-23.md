# IP&M P3 — E5/GTE SciFact input comparability gate (2026-11-23 KST)

**Evidence level: user-reported Mac output; not independent external reproduction.**

## Reported execution
- `P3_E5_GTE_COMPARABILITY_AUDIT=ID_ORDER_AND_COHORT_MATCHED_PREPROCESSING_UNVERIFIED`
- `CORPUS_ID_ORDER_MATCH=TRUE`
- `JUDGED_QID_ORDER_MATCH=TRUE`
- `RETRIEVAL_EXECUTED=NO`
- `E5_ENCODING_PROVENANCE_VERIFIED=NO`
- Author's local output: `~/Downloads/IPM_P3_E5_GTE_COMPARABILITY_20261123`
- Source: `reproducibility/ipm_p3_second_encoder_20261123/scripts/ipm_p3_e5_gte_comparability_audit_v1.py`, committed at `09479c3bc9de5548c85564eb04e9eb388d6794da`.

## Gate
- E5/GTE corpus ID order and the judged SciFact query IDs/order are matched. GTE's prior qrels/embedding SHA lineage was checked against the locally preserved audit metadata.
- This **does not** verify the historical E5 model snapshot, tokenizer, pooling, prefixes, max length, corpus text joining, or encoder execution provenance.
- Historical E5 SciFact low nDCG therefore remains a model/protocol audit issue. Do not assert GTE is intrinsically superior on this comparison.
- Do **not** re-run E5 embeddings or 36-cell retrieval simply to discover provenance.

## Next bounded step
Run new local *read-only* candidate discovery `reproducibility/ipm_p3_second_encoder_20261123/scripts/ipm_p3_e5_encoder_lineage_scan_v1.py` (GitHub commit `1814d48574f115401f1d5edbc4c7afc535394406`). It reports file paths, file hashes, and matched source-line hashes only, avoiding BEIR text or source content disclosure. Review candidate E5 source code and manifests and reconcile against frozen input hashes before revising any paper claim.

Classification: **COHORT_MATCHED / E5_ENCODER_PROVENANCE_OPEN**.
