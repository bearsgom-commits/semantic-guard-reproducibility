# IP&M P2 — self-match threat-model gate decision (2026-11-23 KST)

**Status:** empirical result **author-reported**, source-input-replay digest **author-reported PASS**; independent third-party reproduction not claimed.

## Reported run
Source: `reproducibility/ipm_p2_security_20261123/scripts/ipm_p2_self_match_gate_v1.py`, committed `fa40336055165757dca63b675b790af04ddb2bc7`.
- SciFact, seed=7, D=128, B=4; 2500 sampled member and 2500 sampled nonmember rows.
- `P2_SELF_MATCH_GATE=PASS`
- `LEAVE_ONE_OUT_AUROC=0.494510`
- `SELF_INCLUDED_WEIGHTED_AUROC=1.000000`
- `SELF_INCLUDED_MAX_AUROC=1.000000`
- `GUARD_DIGEST_REPLAY=PASS`, `RETRIEVAL_EXECUTED=NO`
- Local author output: `~/Downloads/IPM_P2_SELF_MATCH_GATE_20261123/self_match_gate.json` (not publicly uploaded).

## Interpretation and decision
Self-excluded neighbor similarity and self-inclusive exact-index matching measure **different attacker capabilities**. Under this constructed experiment, member candidates are exact copies of sampled index vectors, making a self-inclusive equality/matching oracle able to distinguish index inclusion. This **does not** show document-text reconstruction, linkage by an external candidate lacking the exact Guard vector, or generic training-set membership inference.

The near-chance leave-one-out AUROC is therefore **not** evidence that the stored vector index protects against an attacker who can perform exact self-lookup. It is also not evidence of universal absence of leakage. The 4-cell pilot and one-cell positive control validate program behavior and expose an important threat-model fork.

## Next scientifically bounded actions
1. **Do not automatically expand the index-membership proxy to 36 cells** as an all-purpose security endpoint; a saturated self-inclusive 1.0 on the pilot would give little meaningful factorial comparison, while the self-excluded 0.5 proxy does not address the stronger exact-index observer.
2. Pre-specify an **external linkability/ReID** attack for a more meaningful security endpoint: T0 (Guard index and retrieval observations, no raw reference), T1 (extra same-corpus raw reference with independently projected raw vector), T2 (raw reference and true Guard projection matrix). Do not treat T1/T2 as realizable without their stated knowledge assumptions.
3. Recover historical ReID source and reconcile scoring, corpus order, candidate availability and projection knowledge before a *new, separately named* four-cell SciFact pilot. No source recovery => no false historical replay claim.
4. If the pilot can discriminate across adversarial conditions and respects fixed matched IDs and corpus, expand only the necessary attack metric across 36 cells, with uncertainty and explicit interpretation.
5. In parallel, run the already committed P3 model preflight; P2 endpoint selection must not block independent P3 progress.

## Claims excluded from publication
- AUROC≈0.5 proves security.
- AUROC=1 proves arbitrary-document identity/text recovery.
- The current 4-cell leave-one-out results establish an exposure trade-off.
- This author's local execution is an independent full rerun.

No frozen manuscript, original Guard code, 36-cell prior result or historic attack file was changed.
