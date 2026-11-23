# IP&M P2 attacker knowledge and ReID protocol decision v1 (2026-11-23 KST)

## Existing evidence and limitation
For SciFact seed7 D128/B4 the author-reported index-membership audit returned leave-one-out max-neighbor AUROC=0.494510, versus self-inclusive exact-copy matching AUROC=1.000000. This fork arises because the two setups expose different information. It does not imply either text reconstruction or proof of privacy. This experiment tests **index membership**, not conventional training-set membership inference.

## Candidate attacker classes
| Class | Indexed embeddings | Identified auxiliary candidate corpus | Known projection matrix | Metric that can be justified |
|---|---|---|---|---|
| T0 | Index exposed under stated vector access | None | No | Structural/index-level metrics only; not identified-document ReID |
| T1 | Index exposed | Identified raw texts and independently generated raw E5 embeddings | No | Matrix-free linkage only if a specified workable alignment algorithm is tested; else **not measurable** |
| T2 | Index exposed | Identified raw texts and raw embeddings | Yes, with matching quantizer | Known-matrix candidate linkage/ReID Top1/TopK; explicitly strong attacker |

T2 ReID must compare a matching candidate reference set against stored Guard document embeddings, using strictly identical corpus order and legitimate non-self-disclosure assumptions. An exact copied Guard candidate vector is a separate **equality-oracle positive control**, not a realistic T1 or T0 attack.

## Minimum next gate (NO new full experiment)
1. Recover and inspect original historical ReID script at SHA256 e934489d54acbf83592a7de25ef5bb2a5b72dc57f33853e50ef4ca3363710bca and historical attack cohort/sample generation.
2. Specify allowed reference data and whether an attacker knows projection seed/matrix; if absent, do not silently use it.
3. Define a new separately labeled same-cell SciFact four-cell pilot only after the above protocol is auditable. Predetermine sample size, candidate pool, independent attack scoring, Top1/Top5 accuracy, chance baseline, and uncertainty unit.
4. If all candidates are already indexed and attacker receives exact projected vectors, acknowledge deterministic near-perfect linkage is a strong-knowledge oracle and uninformative about effects of quantization.
5. Do not integrate P2 with utility/stability until experiments share D/B factors, dataset, seed, candidate identities, and reproducible threat assumptions.

Stop rule: Missing historical ReID source means original reproduction remains unverified. New-protocol research is allowed only as a **prospective**, transparently different experiment; no reinterpretation of old ReID results.

Status: ATTACK_MODEL_SPECIFICATION_DRAFT / HISTORICAL_REID_SOURCE_OPEN / SAME_CELL_REID_NOT_RUN.
