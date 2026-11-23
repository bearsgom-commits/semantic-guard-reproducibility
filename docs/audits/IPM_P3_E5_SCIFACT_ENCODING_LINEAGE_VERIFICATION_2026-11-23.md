# IP&M P3 E5 SciFact embedding provenance reconciliation — 2026-11-23 KST

**Evidence level:** author-provided local terminal extracts of WBS05A and WBS05B records, plus script line excerpts. Not independently read from the author's Mac in this review.

## Source, model and independently regenerated embeddings

Original candidate source:
`repo/src/stage3/build_embeddings.py`
SHA-256 `984e33c4ba84726bcfb2506a21bbc740bb7b52136acb7b2bbc5d551af7650b2c`.

SciFact WBS05B `wbs05b_scifact_clean_reproduction_20260826_224311.json`:
- `status=PASS`, `execution.build_return_code=0`, `execution.guard_return_code=0`.
- pinned E5 snapshot revision `d128750597153bb5987e10b1c3493a34e5a4502a`.
- clean/canonical byte-identical (SHA-256) SciFact embeddings:
  - RAW_CORPUS `f332ab059f57d4e274ff5e7b513ee19d27104a3f47c7bb98f0b0f93d643716d4`, shape (5183,768).
  - RAW_QUERY `f5b831540582d681f9c2ce9abb8c14e551bc03617180db9a551fa198a0b57f92`, shape (1109,768).
  - GUARD_CORPUS `b5065c963463bee69fea5c18b655f0d6d97c6ffc2f9a5c3766666f19b27ef49b`, shape (5183,320).
  - GUARD_QUERY `34f72f9e11051b8ebd2a77beba1b9610e563c9521a932abd7492bde3cdd9536e`, shape (1109,320).
  - zero mean/max absolute differences, exact hashes and WBS05B numerical gate PASS.
- Scope: single archived SciFact seed7 eps32 reproducibility branch, **not** new 36-cell independent replication or original vector encryption guarantee.

WBS05A `wbs05a_r1_data_prep_contract_20260826_223417.json`:
- SciFact BEIR corpus sha256 `dec31c8182f3d744c7d2c09423756fd1d17cbef75808db13ba01cc0aab4d1ac6`; queries sha256 `8ff84a7c903f722981cd8d595c022660140c51867b27608a6d4910db86080313`.
- raw corpus/query embed path matching status PASS; overall `status=REVIEW_REQUIRED`, due to `gates.build_contract=false`, `gates.guard_contract=false`; this is a separate audit and **must not** be silently upgraded to PASS based on WBS05B.
- Original build script uses title + newline + body if both; corpus prefix `passage: `, query prefix `query: `, apparent `SentenceTransformer.encode` with `normalize_embeddings` from config. Exact tokenizer model, pooling and max length require inspecting the loaded model/config in execution path.

New GTE second-encoder SciFact:
- model revision `9bbca17d9273fd0d03d5725c7a4b0f6b45142062`; separate code revision `40ced75c3017eb27626c9d4ea981bde21a2662f4`.
- GTE per-corpus text matches title+newline+body; model-native input uses no E5 instruction prefixes.
- Previously audited exact same SciFact corpus ID order and same 300 judged-query order; data/qrels alignment NOT reason for observed raw result differences.
- GTE SciFact 12-cell effects + query-paired 3-contrast conditional intervals separately archived.

## Gate outcome
**E5 SOURCE_AND_SCIFACT_REGENERATION_EVIDENCED** (from user-shared audit logs).
**E5_MODEL_ENCODING_CONFIG_AND_LOW_NDCG_CAUSE_OPEN**.
**WBS05A_BUILD_CONTRACT_REVIEW_REQUIRED**.

Do not regenerate source embeddings, overwrite original experiments, imply encoder superiority, or claim all 36 conditions were independently rerun.

Next narrowly scoped task: read the relevant config file and E5 script lines 140–260, correlate precise pooling/preprocessing/token length/snapshot and original E5 SciFact nDCG results; compare raw-vs-Guard ranks on unchanged 300 judged queries and inspect raw vector/norm anomalies only if existing rankings and outputs permit read-only audit.
