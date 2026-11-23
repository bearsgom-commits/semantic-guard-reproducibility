# IP&M professor open-items resolution plan — action gates, not limitation-only (2026-11-23 KST)

**Purpose:** replace the previous passive “mark as limitation” treatment with a concrete solution workflow. This is a post-hoc research-extension plan, not preregistration, and not an executed experiment. Frozen v18 manuscript, Guard source, historical records and prospective 36 retrieval/stability runs are protected.

## Current hard evidence
- Prospective 2x2 dimension×quantization factorial 36/36 retrieval cells across FiQA/SciFact/TREC-COVID × seeds 7/13/42 already audited.
- Utility 18 and stability 45 effects with **separate** family-wise Bonferroni percentile query-bootstrap intervals are committed on public GitHub.
- Old TREC-COVID MIA/Re-ID: 5000-row legacy L3 representations differ materially from canonical 171332-row stage3 2x2 diagonals. Do not claim these measure prospective factorial exposure.
- All prospective runs are based on **one encoder**, `intfloat/multilingual-e5-base`.
- Review requirements were read from `IPM_PROFESSOR_FEEDBACK_ALIGNMENT_AUDIT_20261120.md` (source review 2026-11-18, 7 pages); direct PDF extraction contains font-encoding corruption, so quote-level verification against original PDF is a separate gate.
- Editable working manuscript `IPM_main_revision_working_20261118.tex` shows abstract/intro discussing matching four axes “at the same ε grid”; this is valid **only for historical source-aligned comparisons that satisfy their own protocol**, not a reason to represent all prospective 2x2 cells as having measured security.

## Resolve each unfinished item

| Priority | Issue | Proposed implementable solution | Minimal validation / success criterion | Decision if it fails |
|---:|---|---|---|---|
| P0 | Manuscript overstates same-cell security and decision stability | Build a claim-to-evidence matrix for abstract, RQ3/RQ4, methods, results and conclusion; distinguish legacy ε multi-axis analysis from prospective D×B retrieval/stability; rename Flip@10 to *relevance-hit flip proxy*; custom Top50 union score explicitly nonstandard | No unsupported shared-cohort causal/security claim, each numerical claim tied to fixed dataset/seed/cohort/result file, scan for obsolete values (e.g. historic non-test qrels) | Quarantine unsupported sentence, never invent data |
| P1 | Factorial exposure missing | First inspect existing Matched-MIA/ReID attack code and data/seed/query/attacker knowledge and input provenance; design fixed same-cell adversary protocol with all 4 D/B cells per seed/data set, plus score direction, balanced member/nonmember sampling, split and repeat rules pre-specified *before* running | Read-only compatibility/preflight + **one 4-cell×1 seed pilot**, verify identical attack cohorts and adversarial access; if successful, extend to 36-cell attacks (not 36 retrieval reruns); generate effect CIs and baseline alongside utility/stability; report exact threat assumptions | If attacker/cohort cannot be fixed within resources, omit prospective 3-way trade-off and make clear what was measured; preserve independently valid historical attack observations |
| P1 | Encoder generalization requested | Choose one feasible independent multilingual sentence embedding model with usable license and fixed exact revision; pin tokenizer/weights, normalization and instruction prefixes. Build new embeddings separately; apply unchanged Guard factor settings. Pilot **SciFact × seed7 × 4 factors**, check dimensions/finite values/search parity; then **SciFact ×3 seeds ×4 factors=12** as minimum external-model sensitivity check. If resources permit, expand all 3 datasets to **36 new cells**. Encoder effect is conditional on chosen model; do not claim all-model generality | Pilot input/feature consistency PASS, paired per-query effects and interaction computed; same-corpus model comparison with explicit protocol. Do not silently compare different qrels subsets or different query/document prompts | If pilot fails, record code/data compatibility reason; manuscript must explicitly retain single-encoder conclusion, and professor's requested validation remains unmet |
| P2 | Comparator baseline BM25/Gaussian/Raw coherence | Re-score saved rankings on exact same qrels test IDs, identical Recall@10 and nDCG@10 implementations; audit corpus, index strategy and ranking source first | Baseline cohort/hash and score agreement demonstrated without re-running 36 cells | Present comparator as nonmatched illustrative reference only |
| P2 | Novelty not sharp | Extract table of named prior research vs *independent measurable contributions*: (a) fixed-qrels matched utility/stability, (b) 2x2 factor interactions, (c) attack protocol sensitivity and lineage, (d) limits of nonpersistent text representation | Each novelty statement cites a paper or auditable own experiment; no blanket claims “first” or privacy proof | Narrow claims |
| P2 | Environment/command reproducibility | Collect package/version metadata (python, numpy, transformers, faiss, torch), model revision, GPU/CPU and index/score operation, full command line, source SHA, output SHA into distinct supplementary manifest; static code+aggregates are already remote | Third-party with legally available inputs can follow exact instructions and reproduce a **representative cell + aggregate**; record whether this replay was actually run | Publish evidence-verification package as such; do not claim independent rerun |

## Minimum sequential workflow / stop rules
1. **Immediately** conduct claim matrix on accessible working manuscript; no research-file edits.
2. Run **read-only attack and encoder feasibility preflights**, bounded to actual code/data, not speculative experiments. Prepare public prospective addendum before any new attack data are generated.
3. If preflight PASS, execute a single low-cost factorial security pilot (4 cells × 1 seed) and second-model SciFact pilot (4 cells × 1 seed), no overwrite. Make GO/NO-GO decisions based on scientific validity and feasible computation.
4. Extend the *necessary* successful branch to full comparable scope: preferably prospective 36-cell attack evaluation and 12-cell minimum second-model check; perform multi-model 36-cell only when feasible. Report partial-scope conclusions honestly.
5. Paired statistics: preserve judged query blocks and fixed seeds; pre-specify family/test count per new analysis; distinguish inference on queries from encoders/seeds. Security attacker cohorts must be paired and attack definitions unchanged.
6. Draft **isolated v19** manuscript revision with author-facing diff and response matrix, no overwrite. Verify against original professor PDF typography manually because machine-extracted text is corrupted.
7. Final reproducibility freeze, independent replay if feasible, English translation and submission checks.

## Hypotheses to falsify, not assumptions
- Dimensionality and bit precision may show interactions for retrieval/stability; a different encoder can reverse effect sizes.
- Higher retrieval utility does not mechanically imply higher/lower leakage. No exposure trade-off is established unless comparable same-representation attacks are actually performed.
- Existing security proxy protocols may be unsuitable for proposed attacks; feasibility must be checked before committing to a numeric security goal.

## Research integrity
No modifications to frozen v18, Guard original, historical artifacts, 36-cell outputs or GitHub history. New work in isolated named prospective paths, hashes+logs+GitHub commit for each completed gate; use no false PASS; avoid exposing protected corpus text, query-level records and raw embeddings without explicit license/safety review.

**Status:** `SOLUTION_PLAN_PUBLISHED_ONLY`; experiments/P0 claim audit NOT completed by this file.