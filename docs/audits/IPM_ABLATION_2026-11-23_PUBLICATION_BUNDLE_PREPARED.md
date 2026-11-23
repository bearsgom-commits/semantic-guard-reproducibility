# 2026-11-23 runnable-source publication bundle — prepared, not yet pushed

**Status at this entry: ZIP assembled and local checks performed in ChatGPT's working environment. The ZIP and Mac aggregate outputs are NOT stored as bytes in this GitHub repository yet.** Do not confuse this metadata note with a completed source-code deposit.

Prepared artifact: `IPM_repro_publication_bundle_20261123.zip`
SHA-256: `dcf7f3aca7bfcd0c0464251c4bdba01fd3bac6c1ec14a0051e91d5bbd9f55e86`

Contains 13 actual UTF-8 Python source scripts from generated ChatGPT working copies, their SHA256SUMS.txt, a Mac-side publisher and README. A Python compile check on source scripts and ZIP integrity check passed in the generator environment. The publisher's Bash syntax check passed; its network Git push and any Mac data-path verification have NOT yet been tested.

The publisher, when executed locally:
- Verifies every bundled script against its checksum.
- Compares each available `~/Downloads/<script>.py` copy byte-for-byte with the bundled copy, failing on mismatch.
- Creates a **new** local Git clone of the public reproducibility repository (does not modify the research working tree).
- Stages exact Python sources and a strict allowlist of aggregate statistics CSVs under `reproducibility/ipm_ablation_20261123/`. It excludes query-level outputs, raw embeddings, attack items, qrels, and text.
- Requires at least one matching Mac local script before making a Git commit/push.
- Prints the pushed commit SHA after a successful `git push origin HEAD:main`.
- Does not replace original research code, previous historical results, or v18 manuscript.

**Risk/remaining gate:** Only a remote Git commit with the actual scripts and safe aggregate files completes this phase. Some allowed aggregate CSVs may be unavailable and will be explicitly reported. There is no security guarantee from simply uploading experiment scripts. Anyone claiming complete reproduction must check permissible original BEIR inputs and report provenance, deterministic settings and full data-generation gates.

This note is intentionally separate from prior audit ledgers and represents a proposed publication package, not execution evidence from Mac.