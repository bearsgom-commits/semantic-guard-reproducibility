# TREC-COVID 5000-document selection: source-code inspection (2026-11-23 KST)

**Provenance:** author pasted read-only `grep -n -C 10` output from local `repo/src/eval_trec_covid_v2.py` and `eval_trec_covid_v3.py`. This is inspection of evaluator code, **not proof of the separate historical MIA/Re-ID attack artifact generator**.

## Confirmed source logic

Both v2 and v3 declare `--doc_limit` with default `5000` (line 77). Both load a Guard document embedding file with:

```python
doc_emb = np.load(doc_path).astype("float32")[: args.doc_limit]
```

(v2/v3 line 111). Both read `beir_root / ds / "corpus.jsonl"`, append document `_id` in file order and break if `i >= args.doc_limit` (v2 lines 124–130; v3 lines 127–133). Thus **for these evaluator scripts, given the default doc_limit 5000**, the document selection is an ordered prefix of the loaded Guard file and the BEIR corpus ID file, not randomly sampled within these displayed code blocks. The two sources do not alone prove that the loaded Guard array rows were actually generated and stored in the same order as corpus.jsonl; that remains a separate input-lineage check.

v3 also prefers `queries_test.jsonl` if present and filters qids to qrels; v2 uses `queries.jsonl`; both set query_limit default 200, though the dataset may have fewer judged qids. These are **legacy evaluator settings**, not prospective 36-cell test-only evaluation definitions.

## Relation to historical TREC-COVID security files

Previous read-only checks found legacy MIA/Re-ID metadata references to a 5000-row `artifacts/trec-covid/.../seed{seed}/L3_a0.2_eps{eps}/guard_embeddings.npy` array while canonical full-corpus `artifacts/trec_covid/.../stage3/seed{seed}/eps_{eps:02d}/guard_embeddings.npy` has 171332 rows, for seeds 7,13,42 and eps 0,32. The evaluator's 5000-row prefix convention **plausibly explains the scope** but does **not prove** the attack artifacts used this evaluator or the same row-ID mapping. MIA/Re-ID attack scripts and actual command/config provenance must be checked before linking their results to new factorial diagonal cells.

## Narrow next validation

1. Read-only compare the IDs in `private_data/beir/trec-covid/corpus.jsonl` first 5000 rows to canonical `artifacts/trec_covid/.../shared/corpus_doc_ids.json` first 5000.
2. Read-only inspect the 5000-row legacy Guard array versus canonical full-stage3 Guard prefix: exact sample differences (after checking shapes), NOT assume equality merely from prefix selection in evaluator.
3. Even a prefix vector match does not prove identical attack methodology, cohort sampling, or full-corpus exposure. Report old security outcomes for their actual evaluated scope; no off-diagonal attacks measured.

**Protection:** Do not edit original Guard code, data, attack records, factorial runs, or v18 manuscript without explicit author approval. This commit only appends evidence documentation.
