# IP&M P2 historical Re-ID source recovery gate — 2026-11-23 KST

Evidence: user-reported local output of `ipm_p2_p6_readonly_source_gate_v1.py`, commit `2a9bd285f634ac36f9d976bddf0e307c701098ce`; original local files were not fetched by reviewer.

```text
V18_SOURCE_GATE=PASS
V18_RELEVANT_LINES=200
REID_CANDIDATES=2
REID_SOURCE=repo/scripts/stage3/run_attack_reid.py
SHA256=e934489d54acbf83592a7de25ef5bb2a5b72dc57f33853e50ef4ca3363710bca MATCH=TRUE
REID_SOURCE=_reproducibility_runs/wbs08_cleanroom_20260829_172931/wbs11_public_package_staging/code/run_attack_reid.py
SHA256=e934489d54acbf83592a7de25ef5bb2a5b72dc57f33853e50ef4ca3363710bca MATCH=TRUE
HISTORICAL_REID_SOURCE=FOUND
ORIGINALS_MODIFIED=NO
```

## Gate
**HISTORICAL_REID_SOURCE_RECOVERY=PASS** (author-reported exact SHA matched); two redundant locations. **ATTACK_SEMANTICS_VALIDATION=OPEN**. Do not infer realistic attacker access, exposure or E5-36-cell same-cohort results from source presence.

Next:
1. Read specific original Re-ID source functions and execution args to document reference/index inputs, identity labels, self-inclusion, attacker-known matrices, matching score and aggregation.
2. Align historic corpus/vector IDs and candidate populations with new D/B factorial. Preserve historic input differences and refrain from calling new inputs a replay.
3. Identify a realistic four-cell pilot with explicit T0/T1/T2 threat assumptions only if technically possible and scientifically discriminating.
4. Review v18 claim-inventory privately; 200 matched lines is an inventory, **not** proof of 200 invalid claims.

Frozen v18 SHA256: `08c0a2e6462c805b70fe3650d7c6bef28b359cb97759df3c0d64a3417dbafdc8`.
