# Security-lineage gate: review required (2026-11-23)

**Status:** author-provided Mac terminal result, not independent attack replay.

```text
EXIT_CODE=2
LINEAGE_RECORDS=54
LINEAGE_ISSUES=12
LINEAGE_STATUS=REVIEW_REQUIRED
ORIGINALS_AND_EXPERIMENT_RESULTS_WRITTEN=NO
```

The attempted read-only audit checked 3 datasets × 3 seeds × two diagonal configurations (epsilon 0→128D 4bit; epsilon 32→320D 10bit) × three historical attack families (MIA, matched MIA, Re-ID). **12 of 54 require review**, confined to TREC-COVID legacy MIA and Re-ID attack guard path comparison. The TREC-COVID matched-MIA cases shown in terminal output were labeled `PATH_AND_LABEL_ALIGNED_NOT_SECURITY_EQUIVALENT`. Hence do NOT report overall PASS or security equivalence.

## Diagnostic uncertainty

Source checker `ipm_security_lineage_audit_v1.py` constructs canonical artifact path using `artifacts/trec_covid/...`, and resolves each attack `run_meta.json.guard_embedding_path` using `Path.resolve(strict=False)` then string-compares it with canonical. TREC-COVID histories have used both `trec_covid` and `trec-covid` directories. This failure could be a spelling/path alias or could indicate a genuinely different input. **The provided output does not distinguish them.** Do not edit metadata or reinterpret a different path as canonical without actual evidence.

## Required narrow read-only triage

For TREC-COVID seeds 7,13,42 and epsilon 0,32, inspect literal `guard_embedding_path`, resolved path, whether it exists, file size/shape and whether it is same inode or matching SHA256 with the canonical Guard file. Also check the run-meta and attack-summary dataset/seed/epsilon. Preserve original files and record outcomes. Avoid expensive hashing unless paths are both present and not the same file. After triage, either amend **only the audit path equivalence detection** (not research methods) with justification, or keep relevant exposure linkage unverified.

## Other boundaries

- Previously reported 18/18 diagonal sampled corpus vectors match exactly; this does **not** establish security attack equivalence.
- Matched MIA and old MIA have different attack definitions; cross-cell off-diagonal exposure is unmeasured.
- Full Mac outputs / scripts must still be deposited if authorized. Original Guard, historical experiments, and v18 manuscript remain unchanged.

This is an **exception record** committed immediately upon the observed failure, not a claim of completed resolution.
