# Matched-MIA attack-stage replay audit (2026-11-18)

## Evidence scope

A local replay-evidence archive was inspected and sanitized for disclosure. The published `condition_comparison_63.csv` is a condition-level extraction from its 63 JSON reports. This is **not** a complete release of those reports or of the original input embeddings.

- Conditions: 3 datasets (FiQA, SciFact, TREC-COVID) × 3 seeds (7, 13, 42) × 7 Guard epsilon settings (0, 2, 4, 8, 16, 32, 64) = **63**.
- Recorded result: **63/63 PASS**, all recorded exit codes 0.
- Evidence provenance: **42 `existing_report`** (FiQA 21, SciFact 21), **21 `executed`** (TREC-COVID 21) in the final driver run. The 42 existing reports were not freshly executed in that invocation.
- Each report recorded 2,500 sampled members and 2,500 nonmembers, equality of sampling indices and condition identity, and zero differences in recorded AUROC, accuracy, member/nonmember mean scores, and item-feature maxima.
- Historical attack runner SHA-256: `c16963905f4561d8fe15121d6f92c66abbf8486cac9ab34da97415a48ced0d2d`.
- Private original evidence ZIP SHA-256: `07d09947ec64b683fae0fa47a1e49692bc5a180a93215f846f767d5e7625688c`.
- Sanitized public-review ZIP SHA-256: `6f1a46bc40db311cb86a9eb63d45566f9c72bec704f9ae61623aad334a86235c`. **This ZIP is not yet hosted in this repository**.
- The `report_sha256_prefix16` column refers to the first 16 hexadecimal characters of each sanitized JSON report's SHA-256; it is a truncated identifier, not a full-file checksum.
- Dataset aliases `trec_covid` and `trec-covid` refer to the same dataset.

## What is and is not verified

The records support agreement between locally recorded attack-stage replay results and locally available canonical outputs for 63 conditions. This strengthens the earlier source-inspection, synthetic smoke-test and derived-table audit. It **does not** establish independent third-party reproduction from public inputs, historical run provenance, raw score publication, input embedding identity by SHA-256, BEIR preprocessing, E5 encoding, Guard transformation, retrieval reruns, or full manuscript table/figure lineage.

The public CSV is a **derived comparison audit**, not 63 independently executable experiments. Its `PASS` labels reflect the source reports; public verification of the individual JSON reports remains outstanding until the sanitized archive or reports are published.

A near-chance protocol-specific membership-related exposure AUROC is not a general privacy guarantee. Guard epsilon is **not** a differential-privacy budget.

## Outstanding evidence

1. Publish sanitized 63 condition-level JSON reports and summary after final review, or retain an explicit disclosure limitation.
2. Publish an input-embedding SHA-256 manifest and accessible/authorized input generation route where permissible.
3. Publish exact replay driver, environment/dependency lock and historical command/log provenance.
4. Establish complete retrieval and manuscript table/figure generation lineage.

The repository remains **IN PROGRESS** as a full independent reproduction package.
