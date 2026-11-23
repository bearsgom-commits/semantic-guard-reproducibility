# IP&M P1 review-evidence matrix and P2/P3 feasibility gate — 2026-11-23 KST

**Status:** `GO_WITH_SOURCE_BLOCKER` for P2/P3 read-only preflight; **NOT** a P1 full manuscript-trace PASS and **NOT** permission to edit frozen v18/main.tex.

## 1. Sources independently checked

- Public repository: `bearsgom-commits/semantic-guard-reproducibility`.
- v3 execution plan: `docs/audits/IPM_REVISED_EXECUTION_PLAN_V3_2026-11-23.md`; governing commit `b337a88d3fb85ba9f14412be71e9498d5984cd99`.
- Professor response matrix: `docs/audits/IPM_PROFESSOR_COMMENTS_RESPONSE_MATRIX_2026-11-23_DRAFT.md`.
- Original professor review PDF: `IP&M논문검토_261118.pdf`, independently reread as rendered pages; local SHA-256 `aba79637491afac9a606529e4e49ee874550414ee57428b4db6dc048583b64d1`.
- Frozen-v18 evidence record: `IPM_STAGE1B_V18_EVIDENCE_REVIEW_20261120.md`, which records `manuscript_v18_candidate.tex` SHA-256 `08c0a2e6462c805b70fe3650d7c6bef28b359cb97759df3c0d64a3417dbafdc8`.
- Exact `manuscript_v18_candidate.tex` contents were **not recovered** from the public repository or currently searchable project/library files during this P1 audit. Therefore sentence/line-level v18 trace remains blocked.
- P2 code evidence: `scripts/stage3/run_attack_mia_matched.py`, `scripts/stage3/run_attack_mia.py`, `docs/IPM_STAGE1A_THREAT_MODEL_ALIGNMENT_20261119.md`, `docs/MIA_SOURCE_AUDIT_20261117.md`, `docs/MATCHED_MIA_EXECUTION.md`.
- Factorial code evidence: `reproducibility/ipm_ablation_20261123/scripts/ipm_ablation_factorial_runner_v2.py` and immutable Guard implementation `src/guard_repr.py`.
- Environment evidence: `environment/KNOWN_ENVIRONMENT.md`.
- Local-input inventory confirms BEIR FiQA/SciFact/TREC-COVID corpus/query files exist in the research tree; this audit does not publish their contents.

## 2. Professor-comment resolution classification

| Professor issue | P1 status | Evidence-based decision | Required next action | Success / stop rule |
|---|---|---|---|---|
| Prior work and novelty | PARTIAL | Narrative differentiation alone is insufficient. Novelty must be tied to named prior work and own auditable results. | P5 literature-to-contribution matrix; no new retrieval rerun. | PASS only if each headline contribution has a cited comparator/evidence. Otherwise narrow the claim. |
| Dimension × quantization separation | EXPERIMENT COMPLETE / MANUSCRIPT PENDING | Prospective 2×2 D={128,320}, B={4,10}, 3 datasets ×3 seeds =36 cells already completed and audited. | Reuse committed aggregates only; integrate after P2/P3/P4 gates. | **Do not rerun 36 cells.** |
| Security-proxy validity / attacker assumptions | OPEN → P2 GO FOR PILOT DEVELOPMENT | Historical TREC 5,000-row attack inputs are not direct measurements of the new 171,332-row canonical factorial representations. Existing matched runner is technically reusable only after explicit-path adaptation. | New isolated same-cell index-membership-proxy pilot; separate ReID/T1/T2 branch only with recovered source or a prospectively specified new attack. | Stop expansion on cohort/order/input mismatch, nonfinite/degenerate scores, ambiguous attack semantics, or input provenance failure. |
| Additional embedding model | OPEN → P3 GO FOR PREFLIGHT | Current factorial evidence is single-encoder E5. A second encoder is required to answer the professor's requested sensitivity/generalization check. | Freeze a second multilingual retrieval encoder, exact revision, tokenizer/input rules and run SciFact 4-cell seed-7 pilot. | Stop before empirical run if exact model revision/input protocol cannot be pinned or dataset/qrels identity cannot be held fixed. |
| Utility–stability–exposure integration | BLOCKED ON P2 | Utility/stability are measured on the 36 cells; prospective off-diagonal exposure is not. | P4 integrates only same-cell metrics after valid P2. | No three-axis quantitative trade-off claim without jointly comparable exposure measurements. |
| BM25 / Raw / Gaussian comparator coherence | OPEN → P4 | Existing comparator claims require same test-qrels IDs, metric implementation and ranking-source audit. | Re-score/audit saved rankings; avoid 36-cell rerun. | If cohorts differ, label comparator illustrative/nonmatched instead of direct statistical comparison. |
| English/IP&M style | OPEN → P6/P7 | Professor requests result-first, less repetitive limitation language and English submission style. | Only after empirical gates and exact v18 source recovery. | No edit of frozen v18/main.tex before P6 candidate stage. |
| Reproducibility environment | OPEN | Historical Python 3.10.13 and E5 768d are known, but complete dependency/model-revision lock remains unverified. | Record source/input/output hashes and exact commands for every new branch; representative clean replay later. | Do not claim independent full reproduction until actually performed. |

## 3. P2 security feasibility — code-level finding

### 3.1 What is reusable

The published `run_attack_mia_matched.py` is a functioning **matched index-membership proxy**:
- deterministic sampling seed default 20260822;
- 2,500 sampled member rows and 2,500 disjoint nonmember rows;
- sampled member rows form the comparison index;
- member self-match is excluded;
- score uses max similarity, mean Top-5 similarity and Top-1/Top-2 margin;
- AUROC is computed from those scores;
- existing output refuses overwrite.

### 3.2 What is not directly reusable

The runner locates historical files through `dataset / intfloat_multilingual-e5-base / stage3 / seed / epsilon`. The new factorial cells are D/B conditions, including off-diagonals with **no epsilon label**. Therefore direct invocation would be scientifically and operationally wrong.

The correct minimal solution is a **new isolated script** that accepts an explicit `--guard-path` plus the factorial cell identity. The original script and historical results remain unchanged.

### 3.3 Semantic limitation

This protocol tests whether a representation row belongs to the sampled comparison index under the defined matched-index construction. It is **not equivalent to conventional training-data membership inference** and does not establish privacy or confidentiality. Report it as `index-membership proxy AUROC` unless a separately justified attack protocol supports stronger terminology.

### 3.4 Minimum P2 pilot

Use **SciFact, seed 7, all four D/B cells** as the low-cost protocol-validity pilot:
`(128,4), (128,10), (320,4), (320,10)`.

Use the exact same ordered corpus IDs and the same sampled row-index arrays across all four cells. The 2,500+2,500 sampling is feasible only if all four cell arrays expose the identical 5,183-row SciFact corpus order.

**Pilot PASS is methodological, not result-direction based.** Required:
1. four cell input hashes/manifests valid and immutable;
2. corpus row count/order and document-ID identity identical;
3. exactly the same member/nonmember/index rows across four cells;
4. balanced 2,500/2,500 labels, self-exclusion count=2,500;
5. finite, nonconstant attack scores and finite AUROC;
6. output created only in a new external path with source/input/output SHA-256;
7. metric named and interpreted as an index-membership proxy.

AUROC near 0.5 is **not** a pilot failure if the protocol is valid. It is a null empirical result. Expansion to 36 security cells is allowed only after these protocol checks pass.

### 3.5 ReID branch

The prior threat-model audit records historical `run_attack_reid.py` source SHA-256 `e934489d54acbf83592a7de25ef5bb2a5b72dc57f33853e50ef4ca3363710bca`, but that source is not present in the current public tree. Do not reconstruct or silently substitute it. If the exact source is recovered, audit T1/T2 assumptions and adapt prospectively; otherwise any new ReID attack must be separately specified and labeled new.

## 4. P3 second-encoder feasibility

### 4.1 Candidate

Primary candidate: `Alibaba-NLP/gte-multilingual-base` (mGTE family).

Rationale checked against the official model card/paper on 2026-11-23:
- multilingual retrieval model;
- 768-dimensional output, matching the current E5 input dimension and therefore avoiding an additional Guard-input-dimension confound in the first sensitivity experiment;
- Apache-2.0 model-card license;
- official Transformers usage is documented.

Fallback `BAAI/bge-m3` is not preferred for the first minimal test because its 1024-dimensional output would change encoder family **and** Guard input dimension simultaneously.

**Exact Hugging Face revision is not yet frozen.** P3 empirical execution must not start until the resolved model commit/revision and tokenizer/remote-code files are hashed.

### 4.2 Existing pipeline compatibility

The current factorial runner hardcodes the E5 model directory and expects 768-dimensional raw embeddings. It must **not** be edited in place. Because the selected GTE candidate also emits 768 dimensions, a new isolated second-encoder runner can reuse the immutable Guard transform mathematics, D/B factors, exact dot-product ranking, qrels loader and metrics while replacing only the raw embedding source.

Local inventory confirms SciFact raw corpus/query files are available, enabling re-encoding without altering existing E5 arrays.

### 4.3 Tokenization/input-rule gate

The exact historical E5 model revision and preprocessing/prefix/token-length contract are not fully recovered in the public environment record. Therefore cross-encoder comparison must not claim that every preprocessing detail is controlled until that lineage is recovered or explicitly redefined prospectively.

Before embedding:
1. pin GTE model and tokenizer revision;
2. record `transformers`, `torch`, backend and remote-code hashes;
3. freeze query/document text construction and max lengths;
4. record whether model-native query/passage instructions are used;
5. keep BEIR corpus/query IDs and test qrels unchanged.

### 4.4 Minimum P3 pilot

SciFact × seed 7 × four D/B cells. Encode corpus/queries once under the frozen GTE protocol, then apply the same four Guard factor conditions and exact retrieval evaluation.

PASS requires:
- exactly 768 output dimensions, finite embeddings and documented normalization;
- corpus/query IDs aligned to raw SciFact files;
- 300 judged test queries evaluated against the same qrels;
- four D/B Guard outputs finite and normalized;
- no epsilon label assigned to off-diagonals;
- complete model/source/input/output hashes and exact command.

Performance need not exceed E5. The pilot tests pipeline/model compatibility and sensitivity, not superiority.

If PASS, expand to SciFact 3 seeds ×4 =12 cells. Full three-dataset 36-cell second-model expansion is optional and should be justified by the 12-cell result and resource need, not done automatically.

## 5. P1 gate decision

- **Professor PDF:** independently checked.
- **Unresolved tasks:** classified with owner, next action, success and stop rules.
- **P2/P3 feasibility:** sufficient to proceed to isolated code preflights.
- **Exact frozen v18 text:** `SOURCE_NOT_RECOVERED` in this audit. This blocks sentence/line-level manuscript reconciliation and P6 editing, but it does not block P2/P3 read-only/new-path experiments.
- **P1 decision:** `GO_WITH_SOURCE_BLOCKER`, not full PASS.

No frozen manuscript, original Guard source, historical result, or existing 36-cell result was modified by this audit.
