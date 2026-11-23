# IP&M P3 GTE SciFact seed-7 four-cell pilot — author execution report

Date: 2026-11-23 KST. **Status: AUTHOR-REPORTED P3_4CELL_PILOT_PASS; not independent remote rerun.**

## Pinned model and provenance
- Encoder: `Alibaba-NLP/gte-multilingual-base`
- Model commit: `9bbca17d9273fd0d03d5725c7a4b0f6b45142062`.
- Remote code commit: `40ced75c3017eb27626c9d4ea981bde21a2662f4`.
- Dataset: SciFact 5,183 corpus documents, 300 test-qrels judged queries.
- Embeddings: 5,183×768 corpus; 300×768 judged queries; encoder manifest is stored locally.
- P3 pilot runner: `reproducibility/ipm_p3_second_encoder_20261123/scripts/ipm_p3_gte_scifact_factorial_pilot_v1.py` committed at `7d982f6ec60f92157c1b6893649543ebd32b7613`.
- Local output: `~/Downloads/IPM_P3_GTE_SCIFACT_4CELL_20261123`.
- `ORIGINAL_INPUT_HASHES_UNCHANGED=YES`.

## Measured results (user terminal output)
| Seed | D | Bits | Recall@10 | nDCG@10 |
|---:|---:|---:|---:|---:|
| 7 | 128 | 4 | 0.58655556 | 0.44625966 |
| 7 | 128 | 10 | 0.72416667 | 0.58397886 |
| 7 | 320 | 4 | 0.61188889 | 0.49484356 |
| 7 | 320 | 10 | 0.79550000 | 0.65622941 |

## Methodological reading
- At seed 7, nDCG@10 is higher for 10 bits than 4 bits at fixed D, and higher for 320 than 128 at fixed bits. No three-seed statistical inference yet.
- This experiment compares **four Guard representations within the second encoder**, NOT proof of cross-encoder superiority or security. Input preprocessing differs across models unless shown otherwise.
- E5's historically reported SciFact retrieval scores are much lower; that large discrepancy is a **comparability audit trigger**, not an automatic explanation of architecture superiority. Cross-encoder comparison must check query/passage prefixes, tokenization, text construction, model scoring, query cohort and retrieval ranker carefully.
- Numerical console reporting is insufficient for independent audit without output manifests and rankings. These remain local.

## Next bounded run
Re-use the same immutable GTE embeddings and the same source script, with only `--seed 13` and `--seed 42`, writing distinct output folders. The four-cell source supports both seeds. Verify 12 manifests, exact matched 300 qids, ranking hashes and input hashes before factorial contrasts or confidence intervals. Never rerun the original E5 36-condition sweep.

## Scope and exclusions
No P2 exposure measurement, privacy proof, 3-dataset generalization, or externally validated statistical inference is claimed. No frozen manuscript or original historical result modified.
