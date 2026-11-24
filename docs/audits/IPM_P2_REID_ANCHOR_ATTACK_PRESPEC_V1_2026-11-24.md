# IP&M P2 — prospective anchor-assisted ReID prespecification v1
Date: 2026-11-24 KST

## Evidence already obtained (author-reported terminal output, not independent reproduction)
`P2_REID_PREFLIGHT=PASS_4CELL_PREFLIGHT`; SciFact seed7; all four D128/B4, D128/B10, D320/B4, D320/B10 fixed sample 2500 index-member + 2500 nonmember IDs, same sampling seed 20260822, same Guard source/hash and raw E5 inputs. File SHA checks for cohort, manifest, projection matrices and four prior index-membership attack item outputs passed. **This preflight measures no ReID outcome**.

Existing historical ReID uses independent random projection of raw E5 embeddings, a different RNG/seed from canonical Guard, index-based doc identity scoring and no strict original Guard row lineage proof. It is a historically descriptive proxy, not the target security outcome.

## New scientifically distinguishable attacker assumptions

**T0**: stored Guard embeddings/identifiers only, no independently identified reference documents/paired vectors. Identified-document ReID is not identified here, so no valid Top1 ReID outcome. Do not present AUROC from index-membership as T0 ReID.

**T1a**: identified raw E5 embeddings for the candidate set, but no target-Guard/raw paired training observations and no Guard projection matrix. Independent random projection is a weak negative control, not a validated realistic attacker.

**T1b anchor-assisted**: attacker has separately identified raw E5 vectors for candidate documents and exactly **256 disjoint, matched (raw E5, Guard) anchor pairs**. Attacker does not know the actual projection seed/matrix and learns an alignment from anchor pairs using one fixed ridge regression method; predicts Guard-space candidate vectors for nonanchor documents. Targets are disjoint from anchors, labels hidden from predictor, and no exact Guard target used in training. This quantifies leakage under a strong, expressly stated auxiliary-data breach. It does not imply arbitrary attacker capability.

**T2**: attacker knows raw E5 vectors, true Guard projection matrix and quantizer. Exact Guard representation reconstruction is a known-transform oracle positive control: a high Top1 result would be largely mechanical. Run a small bounded control or state analytically; do not sell it as meaningful factorial privacy discrimination.

## Prospectively fixed pilot geometry
- Dataset: SciFact; canonical ordered 5183 rows; seed 7, all 4 D/B settings, model E5 and immutable Guard code.
- Same prior fixed cohort union of 5000 unique row indices (2500 previously sampled members and 2500 sampled nonmembers), **not used as MIA classes in this ReID pilot**. Do not interpret membership labels as ReID outcome.
- Select 256 anchor rows and 256 disjoint target rows via `numpy.random.default_rng(20261124)` on a sorted union of the 5000 prior indices. Freeze selection and publish only counts + SHA of list (actual IDs locally private).
- Candidate pool consists of the 5000 sampled rows **excluding anchors**, hence 4744 identified raw reference candidates, including all 256 targets. Fixed identical candidate set and targets across four cells.
- For each condition, construct canonical Guard vectors using immutable Guard: L2 raw normalize → seed7 768×D Gaussian projection → qbits uniform quantize at clip1 → L2 normalize. Verify SHA of projection matrix matches prior pilot, and no source/original file modification.
- Fit **one fixed closed-form ridge alignment** using 256 paired anchors, centered raw inputs and Guard outputs, with regularization alpha fixed before exposure to test outcomes; avoid per-condition tuning on target accuracy. Suggested primal/dual ridge with `alpha=1.0` and training-only centering (the exact solver and standardization must be frozen in script before pilot). Predict candidate vectors in Guard space, L2 normalize, cosine-rank targets against all 4744 candidate predictions. Under extreme quantization this map approximates a nonlinear transformation; failure may reflect estimator misspecification, not confidentiality.
- Report Top1 and Top5 hit fraction; random-uniform candidate chance Top1=1/4744, Top5=5/4744; **not** equivalence to privacy confidence.
- Use matched target IDs across 4 cells; estimate 2×2 effects only descriptively initially. For uncertainty bootstrap the **256 target IDs as paired units**, conditional on fixed cohort, anchor selection, projection seed, attack estimator and reference candidate set; do not present 3-seed generalizability.
- Nontriviality gate: anchors never overlap targets, candidate prediction never uses target Guard embeddings, no identity label leakage, no selection from test hit outcomes, exact SHA and ID-order provenance; any violation => INVALID pilot.

## Interpretation/stop conditions
1. T1b performance above random reference identifies risk *conditional on the strong 256-anchor + all candidate raw embeddings access*; not information recovery from embeddings alone.
2. If T1b is uninformative across all four cells, do not claim Guard proves privacy; reformulate threat/utility claims rather than automatically expanding to 36.
3. If T1b saturates all cells, no evidence of dimension/bits effect, even though strong reference-based disclosure is possible.
4. Statistical difference across D/B at one seed is exploratory and does not satisfy joint utility/stability/security inferential claim.
5. No reread/rerun of original historical ReID or 36 retrieval conditions. New security attack is prospectively named, not an historical replay.
6. Re-ID candidates are drawn from E5 *training-independent raw corpus embeddings*; no plaintext recovery is measured. Any interpretation of original-text secrecy additionally requires a distinct extraction/inversion threat model and measures.

Current status: **PRE-SPEC_REGISTERED / ATTACK_NOT_EXECUTED / NEED_PROSPECTIVE_IMPLEMENTATION_AND_REVIEW**.
