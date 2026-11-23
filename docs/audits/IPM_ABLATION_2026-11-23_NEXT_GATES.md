# IP&M ablation follow-up gates — 2026-11-23

Status of author-reported experiments: 36/36 factorial cells passed, utility effects 18, stability effects 45, and 18/18 old-vs-prospective diagonal *sampled corpus vector* exact matches (66 per condition). Source evidence is in sibling dated audit notes; historical code/manuscript not to be modified. This note is a **work plan**, not a completed validation.

## Gate 1 — legacy security input lineage (next)
Read-only checker `ipm_security_lineage_audit_v1.py` (generated checksum SHA256 `657d4dbdf0e867bbbea11f10950f6308d94e12ee9bc3f041c390ebd233e6f623`) prepared separately. Checks 3 datasets × 3 seeds × {ε0,ε32} × {MIA,matched MIA,Re-ID} = 54 metadata combinations; verifies dataset, seed, ε and linked canonical Guard artifact paths, with both `trec_covid` and `trec-covid` search spellings. Does not run attacks or establish security equality. **No actual Mac output has been received at record creation.** Script source not yet committed here.

## Gate 2 — interpretation
Separate prospective retrieval/stability 2×2 observations from historical ε-dependent exposure proxies. Even sampled identical diagonal vectors cannot prove identical attacker configuration. Off-diagonal security is unmeasured. Existing matched-MIA ~0.5 only describes tested attack; no formal privacy guarantee. Historical HNSW vs exact ranker ambiguity remains flagged.

## Gate 3 — evidence deposit
Publish scripts actually executed (compare Mac SHA256), safe aggregate CSVs and audit manifests; retain large per-query records, qrels and embeddings locally unless publication is license- and privacy-permitted. Archive exact commands, environment, provenance and remote commit SHAs. Previous code-index document does not contain executable sources.

## Gate 4 — manuscript revision
Prepare comparison table against professor comments; independently inspect generalization/extra-encoder need. Submit a proposed v19 change list for author authorization. Do not overwrite v18, historical sources or paper main.tex. Finish English/LaTeX/Elsevier submission verification only after evidence and wording are checked.

This plan shall be updated when each verification gate finishes, with GitHub commit SHA checked after publication.
