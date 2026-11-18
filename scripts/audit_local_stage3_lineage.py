#!/usr/bin/env python3
"""Read-only, derived-output-only IP&M Stage3 lineage comparison.

Run:
 python3 audit_local_stage3_lineage.py \
   --inventory ~/Downloads/ipm_inputs_inventory.json \
   --root ~/Downloads/research

Prints one compact summary per located joined_stage3_ext.csv. Reads CSV only,
does not write, upload, re-run experiments, modify local data or infer canonical
status from a directory name. Absolute paths are never printed.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

EPS = (0, 2, 4, 8, 16, 32, 64)
SCORE = "security_score_mean"

def asnum(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return None

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inventory", required=True, type=Path)
    p.add_argument("--root", required=True, type=Path)
    args = p.parse_args()
    inventory = json.loads(args.inventory.expanduser().read_text(encoding="utf-8"))
    root = args.root.expanduser().resolve()
    candidates = [r for r in inventory.get("matches", [])
                  if r.get("type") == "joined_results"
                  and r.get("relative_path", "").startswith("semantic-guard/")]
    if not candidates:
        print("NO_JOINED_CANDIDATES_IN_INVENTORY")
        return
    for item in candidates:
        rel = item["relative_path"]
        file = (root / rel).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            print("NOT_FOUND", rel)
            continue
        hashobj = hashlib.sha256()
        with file.open("rb") as raw:
            for chunk in iter(lambda: raw.read(1024 * 1024), b""):
                hashobj.update(chunk)
        try:
            with file.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                columns = reader.fieldnames or []
                rows = list(reader)
        except (UnicodeDecodeError, csv.Error) as exc:
            print("CSV_READ_ERROR", rel, type(exc).__name__)
            continue
        by_eps = defaultdict(list)
        unique = set()
        duplicates = 0
        flags = Counter()
        for row in rows:
            try:
                eps = int(float(row.get("epsilon", "")))
            except ValueError:
                continue
            ds = (row.get("dataset", "") or "").replace("-", "_").lower().strip()
            seed = row.get("seed", "")
            key = (ds, str(seed), eps)
            if key in unique:
                duplicates += 1
            unique.add(key)
            value = asnum(row.get(SCORE))
            if value is not None:
                by_eps[eps].append(value)
            flag = asnum(row.get("region_flag_v3"))
            if flag is not None:
                flags[int(flag)] += 1
        averages = {str(e): round(mean(by_eps[e]), 7) if by_eps[e] else None
                    for e in EPS}
        missing = [e for e in EPS if not by_eps[e]]
        print("---")
        print("path:", rel)
        print("sha256:", hashobj.hexdigest())
        print("rows:", len(rows), "unique_keys:", len(unique), "duplicates:", duplicates)
        print("score_field:", SCORE in columns, "region_field:", "region_flag_v3" in columns)
        print("region_positive:", flags[1], "region_observed:", sum(flags.values()))
        print("security_mean_by_epsilon:", json.dumps(averages, sort_keys=True))
        print("missing_eps:", missing)
    print("NOTE: Matching historical manuscript numbers does NOT establish execution provenance.")

if __name__ == "__main__":
    main()
