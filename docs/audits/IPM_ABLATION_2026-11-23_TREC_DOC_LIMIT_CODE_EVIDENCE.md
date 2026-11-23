# TREC-COVID historical 5000-row evidence: source-code option found (2026-11-23)

**Evidence type:** user's local Mac grep output, not an independently verified source-code execution.

The existing TREC-COVID legacy MIA/Re-ID Guard inputs have 5,000 rows whereas the canonical full-stage3 input has 171,332 rows. A read-only search of repository Python source found:

- `repo/src/eval_trec_covid_v3.py:77`: `ap.add_argument("--doc_limit", type=int, default=5000)`
- `repo/src/eval_trec_covid_v2.py:77`: same option and default
- `repo/src/eval_scifact_v4.py:77`, `repo/src/eval_scifact_v2.py:77`, `repo/src/eval_fiqa_v3.py:77`, `repo/src/eval_fiqa_v2.py:77`: corresponding 5000 defaults

**Interpretation:** This provides plausible source-code explanation for a 5000-document historical experiment. **It does not prove** which entry point or command generated the old attack input, whether the default was used, whether selection was head-5000 or random sampling, or whether row IDs and vectors align with the canonical full corpus.

No matching `*ids*.json`, `*manifest*.json`, `*indices*.json`, or `*config*.json` was returned by the author's search under `artifacts/trec-covid`, within that filename filter.

## Next narrow read-only evidence gate

Inspect the relevant source's actual `doc_limit` application, corpus order, sampling and any run configuration/log. Verify row-ID mapping before making claims about the historical attack results' identity or comparability. No re-execution of the 36 factorial cells or historical attacks required for this inspection. Preserve original Guard code, data, v18 manuscript and completed results.

Related records: `IPM_ABLATION_2026-11-23_TREC_SECURITY_INPUT_DIVERGENCE.md` and `IPM_ABLATION_2026-11-23_TREC_SECURITY_SUBSET_SHAPES.md`.