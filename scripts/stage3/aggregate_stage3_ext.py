#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def first_nonnull(series: pd.Series):
    for v in series:
        if pd.notna(v):
            return v
    return np.nan


def ensure_numeric(df: pd.DataFrame, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def norm01(s: pd.Series) -> pd.Series:
    """Apply global min-max normalization over non-missing values."""
    s = pd.to_numeric(s, errors="coerce")
    valid = s.dropna()

    if valid.empty:
        return pd.Series(
            np.nan,
            index=s.index,
            dtype=float,
        )

    lo = valid.min()
    hi = valid.max()

    if hi <= lo:
        return pd.Series(
            0.5,
            index=s.index,
            dtype=float,
        )

    return (s - lo) / (hi - lo)


def collect_bm25(runs_root: Path) -> pd.DataFrame:
    rows = []
    for p in sorted(runs_root.rglob("retrieval/stage3/bm25/eps_00/metrics_summary.json")):
        obj = load_json(p)
        rows.append({
            "dataset": obj.get("dataset"),
            "seed": obj.get("seed"),
            "epsilon": int(obj.get("epsilon", 0)),
            "method_family": obj.get("method_family", "bm25"),
            "target_mode": obj.get("target_mode", "bm25"),
            "n_queries": obj.get("n_queries"),
            "recall_at_10_mean": obj.get("recall_at_10_mean"),
            "recall_at_100_mean": obj.get("recall_at_100_mean"),
            "ndcg_at_10_mean": obj.get("ndcg_at_10_mean"),
            "mrr_at_10_mean": obj.get("mrr_at_10_mean"),
            "source_path": str(p),
        })
    df = pd.DataFrame(rows)
    return ensure_numeric(df, [
        "seed", "epsilon", "n_queries",
        "recall_at_10_mean", "recall_at_100_mean", "ndcg_at_10_mean", "mrr_at_10_mean"
    ])


def collect_attacks(runs_root: Path) -> pd.DataFrame:
    rows = []
    for p in sorted(runs_root.rglob("attacks/stage3/*/attack_summary.json")):
        obj = load_json(p)
        rows.append({
            "dataset": obj.get("dataset"),
            "seed": obj.get("seed"),
            "epsilon": obj.get("epsilon"),
            "attack_name": obj.get("attack_name"),
            "reidentification_accuracy": obj.get("reidentification_accuracy"),
            "top1_leakage_rate": obj.get("top1_leakage_rate"),
            "top5_leakage_rate": obj.get("top5_leakage_rate"),
            "top10_leakage_rate": obj.get("top10_leakage_rate"),
            "mean_true_raw_rank": obj.get("mean_true_raw_rank"),
            "membership_inference_auroc": obj.get("membership_inference_auroc"),
            "membership_attack_acc_at_0_5": obj.get("membership_attack_acc_at_0_5"),
            "member_score_mean": obj.get("member_score_mean"),
            "nonmember_score_mean": obj.get("nonmember_score_mean"),
            "n_items": obj.get("n_items"),
            "n_aligned_items": obj.get("n_aligned_items"),
            "target_dim": obj.get("target_dim"),
            "membership_mode": obj.get("membership_mode"),
            "projection_method": obj.get("projection_method"),
            "source_path": str(p),
        })
    df = pd.DataFrame(rows)
    return ensure_numeric(df, [
        "seed", "epsilon",
        "reidentification_accuracy", "top1_leakage_rate", "top5_leakage_rate",
        "top10_leakage_rate", "mean_true_raw_rank",
        "membership_inference_auroc", "membership_attack_acc_at_0_5",
        "member_score_mean", "nonmember_score_mean",
        "n_items", "n_aligned_items", "target_dim"
    ])


def build_attack_wide(attacks_long: pd.DataFrame) -> pd.DataFrame:
    if attacks_long.empty:
        return pd.DataFrame(columns=["dataset", "seed", "epsilon"])

    numeric_cols = [
        "reidentification_accuracy", "top1_leakage_rate", "top5_leakage_rate",
        "top10_leakage_rate", "mean_true_raw_rank",
        "membership_inference_auroc", "membership_attack_acc_at_0_5",
        "member_score_mean", "nonmember_score_mean",
        "n_items", "n_aligned_items", "target_dim"
    ]
    text_cols = [
        "attack_name", "membership_mode", "projection_method", "source_path"
    ]
    agg_map = {c: "max" for c in numeric_cols if c in attacks_long.columns}
    agg_map.update({c: first_nonnull for c in text_cols if c in attacks_long.columns})

    return (
        attacks_long
        .sort_values(["dataset", "seed", "epsilon", "attack_name"])
        .groupby(["dataset", "seed", "epsilon"], as_index=False)
        .agg(agg_map)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary_root", type=str, required=True)
    parser.add_argument("--runs_root", type=str, required=True)
    args = parser.parse_args()

    summary_root = Path(args.summary_root).resolve()
    runs_root = Path(args.runs_root).resolve()
    summary_root.mkdir(parents=True, exist_ok=True)

    retrieval_path = summary_root / "retrieval_all.csv"
    stability_path = summary_root / "stability_all.csv"

    if not retrieval_path.exists():
        raise FileNotFoundError(f"[ERROR] missing retrieval_all.csv: {retrieval_path}")
    if not stability_path.exists():
        raise FileNotFoundError(f"[ERROR] missing stability_all.csv: {stability_path}")

    retrieval = pd.read_csv(retrieval_path)
    stability = pd.read_csv(stability_path)

    # normalize dataset labels
    for df in [retrieval, stability]:
        if "dataset" in df.columns:
            df["dataset"] = (
                df["dataset"]
                .astype(str)
                .str.replace("-", "_", regex=False)
                .str.strip()
            )

    retrieval = ensure_numeric(retrieval, [
        "seed", "epsilon", "embedding_dim", "n_queries",
        "recall_at_10", "ndcg_at_10"
    ])
    stability = ensure_numeric(stability, [
        "seed", "ref_epsilon", "target_epsilon",
        "ref_embedding_dim", "target_embedding_dim", "n_queries",
        "mean_top1_stability", "mean_top10_overlap",
        "mean_kendall_tau50", "decision_flip_probability_at10"
    ])

    bm25 = collect_bm25(runs_root)
    attacks_long = collect_attacks(runs_root)

    for df in [bm25, attacks_long]:
        if not df.empty and "dataset" in df.columns:
            df["dataset"] = (
                df["dataset"]
                .astype(str)
                .str.replace("-", "_", regex=False)
                .str.strip()
            )

    attack_wide = build_attack_wide(attacks_long)

    bm25.to_csv(summary_root / "bm25_all.csv", index=False)
    attacks_long.to_csv(summary_root / "attack_all.csv", index=False)

    # 1) raw baseline table: baseline compare only
    raw_base = retrieval.copy()
    raw_base = raw_base[(raw_base["mode"] == "raw") & (raw_base["epsilon"] == 0)].copy()
    raw_base["utility_score_mean"] = (raw_base["recall_at_10"] + raw_base["ndcg_at_10"]) / 2.0

    # 2) guard retrieval rows: main utility/security/stability analysis
    guard_ret = retrieval.copy()
    guard_ret = guard_ret[guard_ret["mode"] == "guard"].copy()
    guard_ret["utility_score_mean"] = (guard_ret["recall_at_10"] + guard_ret["ndcg_at_10"]) / 2.0

    # 3) raw-reference stability only
    rawref_stab = stability.copy()
    rawref_stab = rawref_stab[
        (rawref_stab["ref_mode"] == "raw") &
        (rawref_stab["ref_epsilon"] == 0) &
        (rawref_stab["target_mode"] == "guard")
    ].copy()

    # 4) join guard retrieval with raw-reference stability on target epsilon
    joined = guard_ret.merge(
        rawref_stab,
        left_on=["dataset", "seed", "epsilon"],
        right_on=["dataset", "seed", "target_epsilon"],
        how="left",
        suffixes=("_retrieval", "_stability")
    )

    # 5) join attacks on guard epsilon
    joined = joined.merge(
        attack_wide,
        on=["dataset", "seed", "epsilon"],
        how="left"
    )

    # 6) direction-aligned security proxy score
    reid = pd.to_numeric(
        joined["reidentification_accuracy"], errors="coerce"
    )
    leakage = pd.to_numeric(
        joined["top10_leakage_rate"], errors="coerce"
    )
    mia = pd.to_numeric(
        joined["membership_inference_auroc"], errors="coerce"
    )

    for name, values in {
        "reidentification_accuracy": reid,
        "top10_leakage_rate": leakage,
        "membership_inference_auroc": mia,
    }.items():
        invalid = values.notna() & ~values.between(0.0, 1.0)
        if invalid.any():
            raise ValueError(
                f"[ERROR] {name} contains values outside [0, 1]"
            )

    # Global min-max normalization of all three security components.
    # This restores the source-level implementation used to create
    # the official Stage 3 security_score_mean outputs.
    joined["security_score_mean"] = (
        (1.0 - norm01(reid))
        + (1.0 - norm01(leakage))
        + (1.0 - norm01(mia))
    ) / 3.0

    # Preserve the legacy Stage 3 ESR output structure.
    # The rule is retained for reproducibility of the official outputs.
    joined["region_flag_v3"] = (
        (
            pd.to_numeric(
                joined["utility_score_mean"],
                errors="coerce",
            ) < 0.98
        )
        & (
            pd.to_numeric(
                joined["mean_top1_stability"],
                errors="coerce",
            ) >= 0.20
        )
        & (
            pd.to_numeric(
                joined["decision_flip_probability_at10"],
                errors="coerce",
            ) <= 0.30
        )
        & (
            pd.to_numeric(
                joined["reidentification_accuracy"],
                errors="coerce",
            ) <= 0.20
        )
        & (
            pd.to_numeric(
                joined["membership_inference_auroc"],
                errors="coerce",
            ) <= 0.60
        )
    ).astype("Int64")

    joined.to_csv(summary_root / "joined_stage3_ext.csv", index=False)

    # 7) baseline compare
    utility_compare_guard = joined[[
        "dataset", "seed", "epsilon", "mode", "target_mode",
        "recall_at_10", "ndcg_at_10", "utility_score_mean"
    ]].copy()
    utility_compare_guard["method_family"] = "dense_guard"

    utility_compare_raw = raw_base[[
        "dataset", "seed", "epsilon", "mode",
        "recall_at_10", "ndcg_at_10", "utility_score_mean"
    ]].copy()
    utility_compare_raw["target_mode"] = "raw"
    utility_compare_raw["method_family"] = "dense_raw"

    if not bm25.empty:
        bm25["utility_score_mean"] = (
            pd.to_numeric(bm25["recall_at_10_mean"], errors="coerce") +
            pd.to_numeric(bm25["ndcg_at_10_mean"], errors="coerce")
        ) / 2.0
        bm25_compare = bm25[[
            "dataset", "seed", "epsilon", "target_mode",
            "recall_at_10_mean", "ndcg_at_10_mean", "utility_score_mean", "method_family"
        ]].copy()
        bm25_compare = bm25_compare.rename(columns={
            "recall_at_10_mean": "recall_at_10",
            "ndcg_at_10_mean": "ndcg_at_10"
        })
        bm25_compare["mode"] = "bm25"
    else:
        bm25_compare = pd.DataFrame()

    utility_compare = pd.concat(
        [utility_compare_guard, utility_compare_raw, bm25_compare],
        ignore_index=True,
        sort=False
    )
    utility_compare.to_csv(summary_root / "utility_baseline_compare.csv", index=False)

    # 8) security curve input
    security_curve = joined[[
        "dataset", "seed", "epsilon",
        "reidentification_accuracy", "top1_leakage_rate", "top5_leakage_rate",
        "top10_leakage_rate", "membership_inference_auroc",
        "membership_attack_acc_at_0_5", "security_score_mean"
    ]].copy()
    security_curve.to_csv(summary_root / "security_curve_input.csv", index=False)

    # 9) phase diagram input v2
    phase_v2 = joined[[
        "dataset", "seed", "epsilon",
        "utility_score_mean", "security_score_mean",
        "mean_top1_stability", "decision_flip_probability_at10",
        "reidentification_accuracy", "membership_inference_auroc",
        "region_flag_v3"
    ]].copy()
    phase_v2.to_csv(summary_root / "phase_diagram_input_v2.csv", index=False)

    # 10) dataset–epsilon summary with the legacy ESR flag
    table_region = (
        joined
        .groupby(
            ["dataset", "epsilon"],
            dropna=False,
        )
        .agg({
            "utility_score_mean": "mean",
            "mean_top1_stability": "mean",
            "decision_flip_probability_at10": "mean",
            "reidentification_accuracy": "mean",
            "top10_leakage_rate": "mean",
            "membership_inference_auroc": "mean",
            "security_score_mean": "mean",
            "region_flag_v3": "mean",
        })
        .reset_index()
    )

    table_region.to_csv(
        summary_root / "table_region_v3_summary.csv",
        index=False,
    )

    print(f"[OK] wrote: {summary_root / 'bm25_all.csv'}")
    print(f"[OK] wrote: {summary_root / 'attack_all.csv'}")
    print(f"[OK] wrote: {summary_root / 'joined_stage3_ext.csv'}")
    print(f"[OK] wrote: {summary_root / 'utility_baseline_compare.csv'}")
    print(f"[OK] wrote: {summary_root / 'security_curve_input.csv'}")
    print(f"[OK] wrote: {summary_root / 'phase_diagram_input_v2.csv'}")
    print(f"[OK] wrote: {summary_root / 'table_region_v3_summary.csv'}")

    print("[DONE] aggregate_stage3_ext finished.")


if __name__ == "__main__":
    main()
