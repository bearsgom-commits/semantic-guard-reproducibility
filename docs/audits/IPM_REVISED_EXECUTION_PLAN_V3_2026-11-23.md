# IP&M revised execution process v3 — 2026-11-23 KST

## Objective and hard boundaries

Resolve professor review priorities with executable evidence rather than labeling open issues as limitations. Complete a Korean v19 revision candidate and English IP&M submission package. **Never overwrite frozen v18, main.tex, original Guard source, historic attack results or the 36-cell results.** New work uses separated paths and GitHub commit-SHA tracking. Plan is post-hoc and does not pretend to be preregistered.

## Completed / frozen

- Prospective 2×2 D={128,320}, bits={4,10}, three datasets, seeds={7,13,42}: 36/36.
- Utility paired-query effects 18 contrasts and their Bonferroni-18 uncertainty, stability 45 contrasts and their separate Bonferroni-45 uncertainty.
- GitHub deposited 13 scripts and 5 descriptive/utility aggregate CSVs at `48e4e2808ecf9ae8325f124ea9f776bb00c2891a`, and 45-effect stability CI table/protocol at `af8a53ec3775c2126b22d90197c2e119ba136e9c`.
- 18/18 canonical diagonal representation vector sample identity passed; distinct legacy TREC-COVID MIA/Re-ID 5000-row inputs differ substantially from 171332-row canonical diagonal representation even after matching prefix IDs. Historical security results are **not** direct measurements of the factorial cells.
- Independent end-to-end reproduction and complete environment provenance are still unverified.

## Seven stages / evidence gates

| stage | goal | concrete tasks | acceptance gate | GitHub deliverable |
|---|---|---|---|---|
| P1 | Evidence/problem baseline | Retrieve exact frozen v18 and professor's original 7-page PDF; audit 6 feedback themes, abstract, RQs, claims, security assumptions, results. Map claims to datasets/seed/cohort/method/code hash. Identify minimal necessary additional tests. | Every unresolved professor request has owner, source, decision, trace and stop criterion; unresolved source-text locations flagged explicitly. | `P1_review_evidence_matrix` + hashes |
| P2 | Security comparability | Read-only security code, scorer, attacker-knowledge and member/nonmember sample audit; pre-specify same-cell protocol and cohorts for 2×2 factors, **four-cell single-seed pilot** with previously computed embeddings; reject incomparable inputs. If valid, extend to comparable 36 cells and bootstrap query/document units appropriate for threat model; do not use old TREC legacy vectors as substitutes. | Identical attacker/access assumptions, aligned cohorts and genuine attack scores; methods and uncertainty documented; otherwise redesign or explicit unresolved status. | threat-model addendum, pilot logs and hash, security effects (if valid) |
| P3 | Second encoder | Select independently supported multilingual encoder revision/licensing, query/passage prefix and normalization. Embed separately, run SciFact 4-factor × one-seed pilot, audit dimensions/queries/exact rank. Expand to at least SciFact 3 seeds ×4 =12 comparable cells if pilot valid; optionally expand 3 datasets. | Model configuration frozen, pairwise factor effects, bootstrap with fixed-seed limits; no cross-model population generality overclaimed. | model manifest, pilot/12-cell audit and statistics |
| P4 | Comparator + integrated analysis | Verify BM25/RAW/Gaussian rank outputs on the same held-out qrels IDs and metric definitions. Integrate utility/stability against P2 exposure **only when jointly comparable**. Avoid formal privacy or causal claims unsupported by protocol. | All table columns have common cohort/method where statistical comparisons claimed; unmeasured security remains explicitly unmeasured. | corrected comparator and integration tables |
| P5 | Novelty grounded in sources | Per-cited-paper contribution/comparison and prior-stage distinction; RQ alignment; validate all citations against publication/source (not blanket claims of first). | Each headline novelty has precise testable evidence or prior-work comparator. | literature-to-contribution matrix |
| P6 | Korean v19 isolated revision | Draft new version only after P2–P5 gates; result-first abstract, intro, methods, results, discussion and conclusion, table/figure numbers, statistics, terminology, threat-model boundaries. Compare every numeric claim to frozen artifacts. | Professor six comments addressed or explicitly escalated; numerical exact-match and independent review done; author approves before touching submission main.tex. | standalone candidate, diff and response-to-review |
| P7 | English + release | Translate academically after author approves v19, verify Elsevier IP&M requirements including anonymity, AI disclosure, data availability, bibliography, figures; reproducibility environment and commands, representative clean replay if feasible; freeze GitHub SHA and submission files. | Compiles, format and source checks pass; any not-reproduced gate clearly labeled. | final release manifest and immutable SHA |

## Dependencies and priority

P1 **first**. P2 (security) and P3 (encoder) **parallel only after read-only preflights**; P5 (literature) can proceed in parallel. P4 requires valid P2 security evidence for a *three-way* comparison but retrieval/stability and baseline analysis can proceed independently. P6 integrates P2–P5 validated evidence. P7 after v19 approval. Run **no new 36-cell retrieval sweep** of first encoder.

## Decision and stop rules

- P2 pilot rejects any mismatch in member/nonmember selection, attacker knowledge, embedding generator or evaluation identity; invalid pilot cannot justify full 36-cell security extrapolation.
- P3 pilot rejects input-preprocessing incompatibility or absent model/tokenizer revision; select a different documented encoder if necessary, not ad hoc factor changes.
- If P2 fails, report multi-axis historic findings and prospective 2-axis factorial only. This would **not** satisfy the full three-way trade-off objective; revisit scientific scope explicitly.
- If P3 fails, professor request 4 is still unmet. Do not quietly relabel it an accepted generalization limitation.
- Confidence intervals: 18-contrast and 45-contrast Bonferroni families are separate, not 63-way simultaneous coverage. Stability relevance Hit@10 flip ≠ human operational decision; union-order metric ≠ ordinary Kendall tau-b. Guard epsilon ≠ DP epsilon.

## Every-stage audit contract

At each gate: source SHA + exact run command + output SHA + acceptance/error log; GitHub commit then remote SHA/content check. Publish only license/privacy-permitted non-sensitive aggregates and scripts; large embeddings, source text, qrels or sensitive query rows remain local. Existing v18 and original experiments are immutable without author authorization.

**Immediate next action:** P1 claim/evidence matrix on available working manuscript and known professor audit, then P2/P3 read-only code/data feasibility checks. Never imply original seven-page professor PDF is reliably extractable if fonts are corrupted.
