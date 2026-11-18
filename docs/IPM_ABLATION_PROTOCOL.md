# IP&M Guard dimension × quantization ablation — preregistration draft

**Status:** DESIGN ONLY / NOT EXECUTED. Date: 2026-11-19 (KST).

This specifies a confirmatory supplemental experiment proposed in response to the manuscript review. No new empirical outcomes, positive findings, execution logs or reproduction claims are asserted here.

## Research questions
- Factor D: Does projection dimension affect retrieval utility and stability when quantization precision is held constant?
- Factor B: Does quantization precision affect retrieval utility and stability when projected dimension is held constant?
- Interaction D × B: Do these differences depend on each other?
- Secondary: Do individually measured exposure proxies change in the same directions as retrieval utility/stability?

## Crossed design
| Dimension D | 4-bit | 10-bit |
|---:|---|---|
| 128 | existing epsilon=0 configuration to be **re-executed** | new cross cell |
| 320 | new cross cell | existing epsilon=32 configuration to be **re-executed** |

The existing epsilon labels are mappings for the two diagonal reference cells only. The off-diagonal cells **must not** be invented as new epsilon levels or interpreted as an independent epsilon causal effect.

## Experimental controls
- Dataset/corpus/query and BEIR qrels: FiQA, SciFact, TREC-COVID, same frozen splits and preprocessing for every cell.
- Encoder: `intfloat/multilingual-e5-base`, frozen model revision/tokenization/instruction prefixes and numerical environment.
- Seeds: 7, 13 and 42; document IDs and queries aligned within each seed over all four cells.
- Transformation pipeline: input L2 normalization; seeded Gaussian random projection to D; quantization at B bits with a fully specified fixed clipping range and rounding rule; final L2 normalization.
- Do **not** infer or reconstruct the historical projection matrix from a public config. Identify the original generator/version and seed convention; record exact matrix/checksum or reproducible generation parameters for all cells.
- Retrieval: predeclared exact inner-product on L2 normalized vectors, Top-100 candidates and consistent tie handling. Do not switch between ANN and exact ranking within cells.
- Threat model: specify matching index/member and nonmember representation; sample 2,500 each if corpus permits. For TREC-COVID state whether 5,000-document subset or full corpus is used. Cross-cell security comparisons must use the same authorized set, row IDs and sample seed 20260822.
- Baselines: raw dense and BM25 as reference; keep them constant, do not claim equal privacy budgets. Norm-matched Gaussian comparison is separate and is not a dimension/bit-factor level.

## Minimum execution and preserved artifacts
1. Fix dataset release, qrels, encoder revision, Guard implementation commit and full commands/environment manifest.
2. Re-execute **all** four cells for each of 3 datasets × 3 seeds: **36 cell runs**, not 18 unverified carryovers. Preserve input and output file SHA-256 for each.
3. Measure Recall@10, nDCG@10, Top-1 stability, Top-10 overlap, Kendall-based stability, Decision Flip@10 against a common raw baseline. Report separate per-cell security components where reproducibly available, rather than only a composite.
4. Produce one machine-readable per-cell results table including dataset, seed, dimension, bits, run SHA, corpus/query/qrels identity and all outcomes; keep commands, software versions and deterministic settings.
5. Check score/value and retrieval ID alignment before statistical analysis; replicate previously reported diagonal outcomes **only if** input and code equivalence are established. Otherwise report new outcomes separately, without replacing prior paper data silently.

## Analysis and decision gate
For each metric `Y` within a dataset/seed block, compute:
- Dimension simple effects: `Y(320,4)-Y(128,4)`, `Y(320,10)-Y(128,10)`.
- Bit simple effects: `Y(128,10)-Y(128,4)`, `Y(320,10)-Y(320,4)`.
- Interaction contrast: `[Y(320,10)-Y(128,10)]-[Y(320,4)-Y(128,4)]`.
Aggregate paired contrasts across matched evaluation blocks and report magnitudes plus uncertainty; do not treat three seeds alone as enough for strong population generalization. Query-level uncertainty must preserve query pairing and clarify seed averaging. Correct multiplicity for confirmatory endpoints, or label analyses exploratory.

**Acceptance of a stronger causal statement is conditional on completed off-diagonal runs and stable controls.** With the existing seven joint epsilon configurations alone, only joint-condition association is identified, not independent effects. If the resources/sources cannot support controlled reruns, retain the current manuscript's explicit joint-configuration-only claim; do not upgrade the claim based on this protocol.

## Data and license constraints
Do not publish protected text, user data, or unauthorized embeddings. The GitHub package should provide code/configuration and safe hashes or generated public BEIR inputs, making disclosure restrictions explicit. A successful audit requires an independent permitted reader to rerun the specified experiments and regenerate tables, not merely verify this design document.
