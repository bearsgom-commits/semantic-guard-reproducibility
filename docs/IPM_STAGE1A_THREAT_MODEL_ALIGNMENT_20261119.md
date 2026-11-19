# IP&M Stage 1A: attacker-knowledge sensitivity and manuscript-method reconciliation

**Dated 2026-11-19 (KST). Status: evidence reconciliation, not original-result rewrite or a formal security certification.**

## Scope and principal evidence

- Author-run v10 (read-only): FiQA, SciFact, TREC-COVID × seeds 7/13/42 × epsilon 0/32 = 18 test cells. For each cell, fixed 128 query identities sampled from the first 5,000 corpus rows; 5,000 same-corpus Raw-reference candidates. All 18 stored cleanroom Guard prefixes numerically agree with public Guard formula at approximately 1e-7 maximum coordinate error, but bytewise equality does **not** hold. Across cells, using an independent Raw-side random projection yielded **Top1=0/128 per cell**; using the Guard's known projection matrix yielded **Top1=128/128 per cell**. Totals 0/2,304 versus 2,304/2,304 describe *condition–query pairs*, **not independent documents**; no full-corpus attack or text reconstruction is claimed.
- Original `run_attack_reid.py`, source SHA256 `e934489d54acbf83592a7de25ef5bb2a5b72dc57f33853e50ef4ca3363710bca`, generates an independent Raw-side matrix with `PROJ_SEED + target_dim` for D<768; Stage 3 `src/guard_repr.py` uses the Guard generation seed. The source algorithm also uses same n for Guard queries and Raw candidates; old ReID 5,000 versus cleanroom 171,332 are not equivalent conditions.
- For the distinct matched index-membership proxy, `scripts/stage3/run_attack_mia_matched.py` uses the score `sigmoid(8*(0.5*maxSim+0.3*meanTop5+0.2*margin-0.5))` and does not use recorded `self_norm` in this score. The provided original manuscript had **negative** 0.3/0.2 coefficients; the existing Korean working copy already fixes these to **positive**. One actual cleanroom TREC eps64 seed7 `run_meta.json` also explicitly records the positive formula, but bytewise original-run provenance across all 63 cells remains incomplete.
- `aggregate_stage3_ext.py` computes global min–max `(1-norm(ReID)+1-norm(Top10)+1-norm(AUROC))/3`; aggregation of multiple attack families through per-key `max` may select non-matched AUROC unless the source family is explicitly fixed. Given AUROC can be <0.5, `1-norm(AUROC)` is **not an attack-direction-invariant advantage measure**.
- Existing five-gate `region_flag_v3` yields 37/63 selected outputs with threshold conjunction (Utility<0.98, Top1 stability>=0.20, Flip10<=0.30, ReID<=0.20, matched AUROC<=0.60). Previous audit observed pass counts 63/63, 46/63, 61/63, 54/63, 63/63, respectively. This is an **author-defined diagnostic rule**, not a validated secure/efficient operational region. The T1 ReID gate has not been recalibrated for known-W T2.

## Defensible manuscript threat model

Define **T0**: observer has stored Guard vectors, minimal IDs/manifest and similarity/ranking responses; access to the original raw text or same-corpus Raw reference embedding pairs is not assumed. Define **T1**: linkability proxy with extra **same-corpus Raw reference vectors** and the original attack's independent Raw projection. Define **T2**: same Raw reference vectors but knowledge of Guard's actual projection matrix. Report v10 only as a bounded T1-vs-T2 sensitivity; T0 attack reconstruction, deployed data breaches and formal privacy guarantees are **not measured**. Raw vectors in a local evaluation do not establish that a deployed nonpersistent storage system retains them. Public deterministic projection code cannot be asserted secret without an actual secret-management assumption.

## Scientific decisions (provisional until integrated review)

1. Retain independently verified utility/ranking/decision findings subject to Stage 1B lineage; do not claim ReID is a general confidentiality demonstration. Clearly distinguish T1 linkability from T2 knowledge sensitivity and matched index-membership AUROC.
2. Preserve the original conditional security score and region count for *historical numerical provenance*, but exclude them from claims of formal security guarantees or optimal operating ranges.
3. **Do not silently replace paper numbers**: current paper ReID/Top10 per-epsilon means follow legacy TREC 5,000-prefix series, while the paper's composite epsilon means track cleanroom full-corpus TREC ReID. Cleanroom guard input and legacy guard input differ. Harmonize population/source per component across the entire 63-cell grid before deciding final tables/figures.
4. Produce a separate Korean methodology candidate and diff; **never overwrite original `main.tex`, historical attacks, embeddings or public results** prior to the final joint review.

## Evidence gates still open

- Correct single-source component lineage and attack-mode selection for all 63 rows; document source metadata and any missing source hash.
- Resolve source-aligned ReID/Top10/MIA/Score/Flag consistency in all paper tables and visualizations.
- Verify historical retrieval exact/HNSW execution and qrels separately in Stage 1B.
- Historical original code/input provenance for every MIA condition is not proven by numeric equality alone.

**Files created outside the public repository (not published):** `IPM_STAGE1A_METHOD_RECONCILIATION_20261119.md`, `IPM_stage1a_methods_candidate_20261119.tex` and its unified diff. Candidate source SHA256 `e2a685d8dfa9f033cb48bc0e16fee74321dbe86a26ff8022ef71430161c28233`. Compiled independently with XeLaTeX into 34 pages using prior fixed figures, but bibliography/citation warnings remain and the candidate is **not submission-ready**. Original reference manuscript SHA256 `66aded97658a11ade0ba954951d2e6d9152c7f18e75316dce65ee6475690241c` is unchanged.
