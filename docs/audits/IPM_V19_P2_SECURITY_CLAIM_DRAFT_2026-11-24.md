# IP&M v19 P2 security claim integration draft — 2026-11-24 KST

This is a **replacement-language drafting aid**, not an edit of frozen v18 LaTeX and not a statement that its original exact wording was inspected. Before adding to v19, check each target location against the actual v18 source.

## Confirmed source-bounded method statement (English draft)
"We evaluated auxiliary-reference document re-identification under a specified attacker model. The attacker was given raw E5 embeddings for a candidate pool and 256 paired raw/Guard anchor representations, but not the Guard projection matrix. Using a fixed ridge-regression alignment learned from anchor pairs, the attacker ranked 4,744 identified raw-reference candidates for 256 disjoint target Guard representations. We evaluated the 2×2 configurations D∈{128,320} and b∈{4,10}, initially with a single fixed projection seed."

## Observed single-seed7 outcome (English draft)
"For SciFact at projection seed 7, Top-1 re-identification was 210/256 (82.03%), 256/256 (100%), 249/256 (97.27%), and 256/256 (100%) for (128,4), (128,10), (320,4), and (320,10), respectively. These data indicate substantial document-linkage exposure under the assumed auxiliary-reference access, including the most constrained tested representation. They do not measure original-text reconstruction or training-data membership."

## Conditional statistical interpretation (English draft)
"Matched-target bootstrap analysis (20,000 resamples; separate Bonferroni-3 familywise 95% intervals within Top-1 and Top-5 endpoints) for seed 7 yielded positive marginal dimension (+0.07617, [0.04688,0.10742]) and bit-depth (+0.10352, [0.07227,0.13672]) effects on Top-1 re-identification, with a negative interaction (−0.15234, [−0.21484,−0.09375]). The observed interaction partly reflects saturation of the 10-bit configurations. These intervals condition on one dataset, fixed seed, fixed anchors, candidate references and target sample; they do not describe across-seed, across-corpus or attacker-access uncertainty."

## ReID historical terminology correction
- Historical `reid_proxy_projected_raw` uses an independently sampled Gaussian raw-reference projection. DO NOT describe its values as a known-Guard-matrix attacker, plaintext inversion, unconditional leakage, or a directly comparable member/nonmember attack.
- New `T1b_256_anchor_unknown_matrix` is prospective, has different knowledge assumptions, and should be a separate experiment and evidence row. Earlier index-membership proxy AUROC≈0.5 is a different endpoint.
- Storage: 'nonpersistent original plaintext' is a **system architecture property**, not equivalent to cryptographic privacy, anonymity or re-identification resistance.
- `epsilon` denotes a custom structural-strength index, **not a differential-privacy epsilon**.
- SciFact historical ranking denominator issue: judged-qid evaluation uses 300 judged queries, not all 1109 corpus query rows. Keep revised retrieval evaluation denominators distinct from 256 ReID target count.
- 36-cell E5 retrieval and 4-cell ReID pilot are not a completely matched 3-axis factorial study across all datasets and seeds.

## Gate before manuscript freeze
- Obtain author-reported seed13/42 sensitivity outputs, then decide if seed7 paragraph can be expanded to the same 3-seed fixed-target protocol.
- Confirm actual v18 wording, tables, graphs, references, and crosslinks in private v18 ZIP; do not silently replace or publish private draft.
- All strong-claim wording requires explicit threat model, auxiliary information and scope; do not claim 'Guard protects raw text' from MIA chance or 'Guard fails to preserve plaintext' from ReID.
- Report use of paired target IDs (not independent 3×256 observations).

Sources: author-reported fixed four-cell T1b success counts, `docs/audits/IPM_P2_ANCHOR_REID_4CELL_PILOT_RESULT_2026-11-24.md`, `docs/audits/IPM_P2_ANCHOR_REID_PAIRED_CI_RESULT_2026-11-24.md` and code commits `f0d2420e764bac5d096d453555fd501ae8282537`, `49eedd0b6790eff19b308966d2f8af42b6eb9183`.
