# 2026-11-23 Guard diagonal vector identity — sampled retrospective evidence

**Provenance:** This document records terminal output supplied by the researcher for a read-only Mac execution of `ipm_guard_diagonal_vector_identity_v1.py`. This GitHub entry does **not** claim to have independently executed the script or received the original local log.

## Result

```text
EXIT_CODE=0
SAMPLED_VECTOR_CHECK completed=18/18 mismatches=0
HISTORICAL_AND_ABLATION_FILES_WRITTEN=NO_BY_THIS_SCRIPT
VECTOR_IDENTITY_STATUS=PASS_SAMPLED_18
LIMITATION=SAMPLED_CORPUS_VECTORS_ONLY_NOT_FULL_IDENTITY_OR_SECURITY_EQUIVALENCE
```

For each of FiQA, SciFact and TREC-COVID, with seeds 7, 13, 42 and original epsilon references 0 (D=128, B=4) and 32 (D=320, B=10), the program output:
```text
sampled=66 max_abs=0 exact=1 close_1e-6=1 status=PASS
```
All eighteen combinations passed; 66 sampled corpus vectors per condition, 1188 **sampled vector comparisons** across cells (not necessarily 1188 distinct documents, and not a full-corpus equality audit). No modifications were reported.

## Interpretation and boundaries

- Supports **sample-exact corpus Guard vector identity** between stored historical ε=0/32 artifacts and vectors regenerated with the original Guard transform at the prospective factorial diagonal settings.
- Earlier size audit also found all 18 stored legacy arrays had matching corpus row counts and representation dimension.
- Does **not** certify equality for unsampled corpus rows, any query embeddings, input row-ID lineage, security scoring pipeline, sampling cohorts or attack knowledge assumptions.
- Historical MIA, matched MIA and Re-ID results were generated under differing attacker models. Never present the old MIA AUROC 1.0 as proof of real membership success, nor matched MIA ~0.5 as a privacy guarantee.
- No direct attacks were run for off-diagonal (D=128,B=10) or (D=320,B=4) conditions. Cross-cell exposure is **unmeasured**; do not impute it from ε or diagonal observations.
- The historical HNSW config versus exact search execution-provenance gap remains distinct from the Guard representation equality result.

## Follow-up reproducibility gates

1. Preserve the researcher's executed `ipm_guard_diagonal_vector_identity_v1.py` and full local log with their SHA-256, publish only non-sensitive permitted evidence.
2. If broader historical-security linkage is claimed, independently check corpus IDs, query-vectors, scorer definitions, source hashes and attack sampling; a sampled vector match alone is insufficient.
3. Maintain prospective results separate from historical manuscript values; **do not modify Guard source, original experiments or v18 manuscript without approval**.

**Commit purpose:** update the 2026-11-23 factorial execution ledger's previously pending sampled-identity gate with the newly supplied PASS evidence. This is *post-experiment documentation*, not preregistration.
