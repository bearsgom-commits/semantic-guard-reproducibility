#!/usr/bin/env python3
"""Read-only discovery of local IP&M experiment materials.

Usage:
  python3 scripts/inventory_local_ipm_inputs.py --root "$HOME/Downloads/research" \
    --output "$HOME/Downloads/ipm_inputs_inventory.json"

Searches only the supplied root. No copying, downloading, upload, model execution,
content dumping, recursive symlink following, or deletion. Output may reveal local
relative paths: inspect JSON before sharing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".cache",
             ".tox", ".mypy_cache", ".pytest_cache", "site-packages"}
FILE_NAMES = {
    "guard_embeddings.npy": "guard_embedding",
    "raw_embeddings.npy": "raw_embedding",
    "corpus_embeddings.npy": "corpus_embedding",
    "query_embeddings.npy": "query_embedding",
    "retrieval_all.csv": "retrieval_summary",
    "stability_all.csv": "stability_summary",
    "joined_stage3_ext.csv": "joined_results",
    "attack_summary.json": "attack_summary",
    "run_meta.json": "run_metadata",
    "sampling_indices.json": "sampling_indices",
    "references.bib": "references",
    "reference.bib": "references",
    "qrels.tsv": "qrels",
    "qrels.csv": "qrels",
    "queries.jsonl": "queries",
    "corpus.jsonl": "corpus",
    "requirements.txt": "environment",
    "poetry.lock": "environment",
    "conda-lock.yml": "environment",
    "environment.yml": "environment",
}
KEYWORDS = ("guard", "embedding", "retrieval", "stability", "qrel",
            "beir", "fiqa", "scifact", "trec", "stage3", "runner", "manifest",
            "replay", "requirements", "figure", "fig_", "plot", "reference")
EXTS = {".py", ".json", ".jsonl", ".npy", ".npz", ".csv", ".tsv",
        ".yaml", ".yml", ".toml", ".lock", ".bib", ".png", ".pdf", ".sh"}
ALLOWED_HASH_EXTS = {".py", ".json", ".yaml", ".yml", ".toml", ".lock",
                     ".bib", ".sh", ".txt"}
HASH_LIMIT = 4 * 1024 * 1024

def sha_small(path, size):
    if size > HASH_LIMIT or path.suffix.lower() not in ALLOWED_HASH_EXTS:
        return None
    dig = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            dig.update(chunk)
    return dig.hexdigest()

def classify(path):
    name = path.name.lower()
    if name in FILE_NAMES:
        return FILE_NAMES[name]
    if path.suffix.lower() not in EXTS:
        return None
    if not any(word in name for word in KEYWORDS):
        return None
    if path.suffix.lower() in {".png", ".pdf"}:
        return "figure_or_pdf"
    if path.suffix.lower() in {".py", ".sh"}:
        return "candidate_runner_or_script"
    if path.suffix.lower() in {".npy", ".npz"}:
        return "candidate_embedding"
    return "candidate_evidence"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True,
                        help="Local experiment project directory or common parent")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-files", type=int, default=300000)
    parser.add_argument("--max-matches", type=int, default=10000)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not root.is_dir():
        parser.error("Root is not an existing directory")
    if output == root or root in output.parents:
        parser.error("Put the inventory output OUTSIDE the scanned root")
    if args.max_files < 1 or args.max_matches < 1:
        parser.error("Limits must be positive")
    matches, count, errors = [], 0, []
    truncated = False
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and
                         not (Path(base) / d).is_symlink())
        for name in sorted(files):
            count += 1
            if count > args.max_files or len(matches) >= args.max_matches:
                truncated = True
                break
            path = Path(base) / name
            if path.is_symlink():
                continue
            kind = classify(path)
            if kind is None:
                continue
            try:
                st = path.stat()
                entry = {
                    "type": kind,
                    "relative_path": str(path.relative_to(root)),
                    "size_bytes": st.st_size,
                    "sha256_if_small_text": sha_small(path, st.st_size),
                }
                matches.append(entry)
            except (OSError, ValueError) as exc:
                errors.append({"relative_path": str(path.relative_to(root)),
                               "error_type": type(exc).__name__})
        if truncated:
            break
    summary = dict(sorted(Counter(m["type"] for m in matches).items()))
    report = {
        "schema": "ipm_local_input_inventory_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "local_read_only_search_no_file_content_or_upload",
        "searched_file_count": count,
        "matched_file_count": len(matches),
        "truncated": truncated,
        "counts_by_type": summary,
        "notes": [
            "relative_path is relative to the caller-provided root; absolute root omitted",
            "hashes are computed only on small text files, never on large embeddings",
            "unmatched filenames may still contain useful materials",
            "inspect the JSON for sensitive names before sharing",
        ],
        "matches": matches,
        "errors": errors[:100],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        parser.error("Output exists: choose a new output path; no overwrite")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("SCAN_COMPLETE")
    print("files_scanned:", count)
    print("candidates:", len(matches))
    print("truncated:", truncated)
    print("counts_by_type:", json.dumps(summary, ensure_ascii=False))
    print("inventory_saved:", output)
    print("Review the file before sharing. No experiment was run or data uploaded.")

if __name__ == "__main__":
    main()
