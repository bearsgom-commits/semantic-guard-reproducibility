#!/usr/bin/env python3
"""Validate published derived tables (not an independent MIA rerun).

Run from repository root: python3 scripts/check_published_validation.py
Requires only Python standard library.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "results" / "stage3" / "matched_mia" / "validation"
EPS = [0, 2, 4, 8, 16, 32, 64]
EXPECTED = {0: 0, 2: 3, 4: 8, 8: 8, 16: 9, 32: 9, 64: 0}

def read_csv(name):
    with (DIR / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def main():
    rows = read_csv("matched_vs_old_63_conditions.csv")
    summary = read_csv("verified_epsilon_summary.csv")
    checks = json.loads((DIR / "verified_checks.json").read_text(encoding="utf-8"))
    assert len(rows) == 63, len(rows)
    assert len(summary) == 7, len(summary)
    seen = set()
    counts = {eps: 0 for eps in EPS}
    old = 0
    for row in rows:
        eps = int(row["epsilon"])
        key = (row["dataset"].replace("_", "-"), int(row["seed"]), eps)
        assert key not in seen, key
        seen.add(key)
        assert eps in EXPECTED, eps
        assert int(row["region_flag_matched"]) in (0, 1)
        assert int(row["region_flag_old"]) in (0, 1)
        counts[eps] += int(row["region_flag_matched"])
        old += int(row["region_flag_old"])
    assert counts == EXPECTED, (counts, EXPECTED)
    assert old == 0
    assert sum(counts.values()) == 37
    for row in summary:
        eps = int(row["epsilon"])
        assert int(row["conditions"]) == 9
        assert int(row["old_flags"]) == 0
        assert int(row["matched_flags"]) == counts[eps]
    assert checks["condition_rows"] == 63
    assert checks["matched_region_flags"] == 37
    assert checks["old_region_flags"] == 0
    print("PASS: 63 unique published rows; 7 epsilon aggregates; 37 matched flags")
    print("LIMITATION: no source attacks, embeddings, retrieval, or security formula rerun")

if __name__ == "__main__":
    main()
