#!/usr/bin/env python3
"""Post-hoc AUROC orientation sensitivity based on published derived rows only.

Does not rerun the attack or independently reproduce source experiments.
Usage (from repo checkout): python scripts/check_auc_orientation_sensitivity.py
"""
import csv
import json
import math
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "results/stage3/matched_mia/validation/matched_vs_old_63_conditions.csv"


def norm01(xs):
    lo, hi = min(xs), max(xs)
    return [(x - lo) / (hi - lo) if hi > lo else 0.5 for x in xs]


def ranks(xs):
    order = sorted(range(len(xs)), key=xs.__getitem__)
    result = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        rank = (i + j + 2.0) / 2.0
        for k in range(i, j + 1):
            result[order[k]] = rank
        i = j + 1
    return result


def correlation(a, b):
    ma, mb = mean(a), mean(b)
    numerator = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    denominator = math.sqrt(
        sum((x - ma)**2 for x in a) * sum((y - mb)**2 for y in b)
    )
    return numerator / denominator


def main():
    with SOURCE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    keys = [(r["dataset"], r["seed"], r["epsilon"]) for r in rows]
    if len(rows) != 63 or len(set(keys)) != 63:
        raise ValueError("Expected 63 unique dataset/seed/epsilon rows")

    auc = [float(r["membership_inference_auroc_matched"]) for r in rows]
    old = [float(r["security_score_matched"]) for r in rows]
    dev = [abs(a - 0.5) for a in auc]
    old_part = [1 - x for x in norm01(auc)]
    new_part = [1 - x for x in norm01(dev)]
    new = [s + (alt - orig)/3 for s, alt, orig in zip(old, new_part, old_part)]
    change = [abs(a-b) for a,b in zip(old,new)]
    eps = sorted({int(r["epsilon"]) for r in rows})

    out = {
        "status": "post_hoc_derived_data_only_not_independent_reproduction",
        "source": str(SOURCE.relative_to(ROOT)),
        "conditions": len(rows),
        "membership_gate_pass": sum(a <= 0.60 for a in auc),
        "matched_region_flags": sum(int(r["region_flag_matched"]) for r in rows),
        "matched_auc_range": [min(auc), max(auc)],
        "spearman_rho": correlation(ranks(old), ranks(new)),
        "mean_absolute_score_change": mean(change),
        "max_absolute_score_change": max(change),
        "epsilon_means": {
            str(e): {
                "published": mean(old[i] for i,r in enumerate(rows) if int(r["epsilon"]) == e),
                "orientation_invariant": mean(new[i] for i,r in enumerate(rows) if int(r["epsilon"]) == e),
            } for e in eps
        },
        "definition": "new=published+(1-minmax(abs(AUC-0.5))-(1-minmax(AUC)))/3",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
