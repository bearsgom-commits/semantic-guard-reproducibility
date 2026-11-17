#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

MODEL_DIRNAME = "intfloat_multilingual-e5-base"
PROJ_SEED = 20260401


def now_iso_kst():
    return datetime.now(timezone.utc).astimezone().isoformat()


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_csv(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def l2_normalize(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return x / norms


def discover_raw_path(project_root: Path, dataset: str) -> Path:
    dataset_variants = {
        dataset,
        dataset.replace("-", "_"),
        dataset.replace("_", "-"),
        dataset.replace("-", ""),
        dataset.replace("_", ""),
    }

    direct_candidates = []
    for ds in dataset_variants:
        direct_candidates.extend([
            project_root / "artifacts" / ds / MODEL_DIRNAME / "stage3" / "shared" / "corpus_embeddings_fp32.npy",
            project_root / "artifacts" / ds / MODEL_DIRNAME / "stage3" / "shared" / "corpus_embeddings.npy",
            project_root / "artifacts" / ds / MODEL_DIRNAME / "stage3" / "shared" / "embeddings.npy",
        ])

    for p in direct_candidates:
        if p.exists():
            return p

    all_npy = sorted((project_root / "artifacts").rglob("*.npy"))

    strong_hits = []
    weak_hits = []
    for p in all_npy:
        s = str(p).lower()
        if MODEL_DIRNAME.lower() not in s:
            continue
        if "stage3" not in s:
            continue
        if not any(ds.lower() in s for ds in dataset_variants):
            continue

        name = p.name.lower()
        if name in {"corpus_embeddings_fp32.npy", "corpus_embeddings.npy"}:
            strong_hits.append(p)
        elif name == "embeddings.npy" and "guard" not in s and "queries" not in s and "query" not in s:
            weak_hits.append(p)

    if strong_hits:
        return strong_hits[0]
    if weak_hits:
        return weak_hits[0]

    raise FileNotFoundError(f"[ERROR] raw corpus embedding file not found for dataset={dataset}")


def discover_guard_path(project_root: Path, dataset: str, seed: int, epsilon: int) -> Path:
    stage3_path = (
        project_root / "artifacts" / dataset / MODEL_DIRNAME / "stage3" /
        f"seed{seed}" / f"eps_{epsilon:02d}" / "guard_embeddings.npy"
    )
    if stage3_path.exists():
        return stage3_path

    legacy1 = (
        project_root / "artifacts" / dataset / MODEL_DIRNAME /
        f"seed{seed}" / f"L3_a0.2_eps{epsilon}" / "guard_embeddings.npy"
    )
    if legacy1.exists():
        return legacy1

    legacy2 = (
        project_root / "artifacts" / dataset / MODEL_DIRNAME /
        f"seed{seed}" / f"L3_a0.2_eps{epsilon:02d}" / "guard_embeddings.npy"
    )
    if legacy2.exists():
        return legacy2

    dataset_variants = {
        dataset,
        dataset.replace("-", "_"),
        dataset.replace("_", "-"),
        dataset.replace("-", ""),
        dataset.replace("_", ""),
    }
    fallback = sorted((project_root / "artifacts").rglob("guard_embeddings.npy"))
    for p in fallback:
        s = str(p).lower()
        if not any(ds.lower() in s for ds in dataset_variants):
            continue
        if f"seed{seed}" not in s:
            continue
        if f"eps_{epsilon:02d}" in s or f"eps{epsilon}" in s or f"eps_{epsilon}" in s:
            return p

    raise FileNotFoundError(
        f"[ERROR] guard embedding file not found for dataset={dataset}, seed={seed}, eps={epsilon}"
    )


def load_embeddings(path: Path) -> np.ndarray:
    arr = np.load(path)
    if arr.ndim != 2:
        raise ValueError(f"[ERROR] expected 2D embedding array, got shape={arr.shape} at {path}")
    return arr.astype(np.float32)


def project_raw_to_guard_dim(raw_emb: np.ndarray, target_dim: int, proj_seed: int = PROJ_SEED) -> np.ndarray:
    raw_dim = raw_emb.shape[1]

    if raw_dim == target_dim:
        return raw_emb.astype(np.float32)

    if raw_dim < target_dim:
        pad = np.zeros((raw_emb.shape[0], target_dim - raw_dim), dtype=np.float32)
        return np.concatenate([raw_emb.astype(np.float32), pad], axis=1)

    rng = np.random.default_rng(proj_seed + target_dim)
    proj = rng.standard_normal((raw_dim, target_dim), dtype=np.float32) / np.sqrt(target_dim)
    return (raw_emb @ proj).astype(np.float32)


def compute_features_against_index(candidate_emb: np.ndarray, index_emb: np.ndarray, chunk_size: int = 256, exclude_self: bool = False):
    candidate_emb = l2_normalize(candidate_emb.astype(np.float32))
    index_emb = l2_normalize(index_emb.astype(np.float32))

    rows = []
    base_offset = 0

    for start in range(0, candidate_emb.shape[0], chunk_size):
        end = min(start + chunk_size, candidate_emb.shape[0])
        sims = candidate_emb[start:end] @ index_emb.T

        if exclude_self:
            for local_i in range(end - start):
                global_i = start + local_i
                if global_i < index_emb.shape[0]:
                    sims[local_i, global_i] = -1.0

        for i in range(end - start):
            row = sims[i]
            topk = min(5, len(row))
            top_idx = np.argpartition(-row, kth=topk - 1)[:topk]
            top_vals = np.sort(row[top_idx])[::-1]

            max_sim = float(top_vals[0])
            mean_top5 = float(np.mean(top_vals))
            margin = float(top_vals[0] - top_vals[1]) if len(top_vals) >= 2 else float(top_vals[0])
            self_norm = float(np.linalg.norm(candidate_emb[start + i]))

            rows.append({
                "max_sim_to_index": max_sim,
                "mean_top5_sim_to_index": mean_top5,
                "margin_top1_top2": margin,
                "self_norm": self_norm,
            })
        base_offset += (end - start)

    return rows


def rankdata_average(a):
    order = np.argsort(a)
    ranks = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def binary_auroc(y_true, scores):
    y_true = np.asarray(y_true, dtype=int)
    scores = np.asarray(scores, dtype=float)

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))
    if n_pos == 0 or n_neg == 0:
        return float("nan")

    ranks = rankdata_average(scores)
    sum_pos = float(np.sum(ranks[y_true == 1]))
    auc = (sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return auc


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_root", type=str, required=True)
    parser.add_argument("--runs_root", type=str, required=False, default="")
    parser.add_argument("--datasets", nargs="+", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[7, 13, 42])
    parser.add_argument("--epsilons", nargs="+", type=int, default=[0, 8, 16, 32, 64])
    parser.add_argument("--chunk_size", type=int, default=256)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    runs_root = Path(args.runs_root).resolve() if args.runs_root else (project_root / "runs")

    for dataset in args.datasets:
        raw_path = discover_raw_path(project_root, dataset)
        raw_emb = load_embeddings(raw_path)
        print(f"[INFO] dataset={dataset} raw_path={raw_path} raw_shape={tuple(raw_emb.shape)}")

        for seed in args.seeds:
            for epsilon in args.epsilons:
                guard_path = discover_guard_path(project_root, dataset, seed, epsilon)
                guard_emb = load_embeddings(guard_path)

                n_guard = guard_emb.shape[0]
                target_dim = guard_emb.shape[1]
                raw_proj = project_raw_to_guard_dim(raw_emb, target_dim)

                n_index = n_guard // 2
                if n_index < 100:
                    raise ValueError(f"[ERROR] n_index too small for dataset={dataset}, seed={seed}, eps={epsilon}")

                if raw_proj.shape[0] < n_index * 2:
                    raise ValueError(
                        f"[ERROR] raw corpus too small for split-based MIA: raw={raw_proj.shape[0]}, need>={n_index*2}"
                    )

                index_emb = guard_emb[:n_index]
                member_candidate_emb = guard_emb[:n_index]
                nonmember_emb = raw_proj[n_index:n_index + n_index]

                print(
                    f"[INFO] dataset={dataset} seed={seed} eps={epsilon} "
                    f"guard_path={guard_path} guard_shape={tuple(guard_emb.shape)} "
                    f"n_index={n_index} n_member={member_candidate_emb.shape[0]} "
                    f"n_nonmember={nonmember_emb.shape[0]} target_dim={target_dim}"
                )

                member_feats = compute_features_against_index(
                    candidate_emb=member_candidate_emb,
                    index_emb=index_emb,
                    chunk_size=args.chunk_size,
                    exclude_self=True,
                )
                nonmember_feats = compute_features_against_index(
                    candidate_emb=nonmember_emb,
                    index_emb=index_emb,
                    chunk_size=args.chunk_size,
                    exclude_self=False,
                )

                rows = []
                for i, feat in enumerate(member_feats):
                    score = (
                        0.5 * feat["max_sim_to_index"] +
                        0.3 * feat["mean_top5_sim_to_index"] +
                        0.2 * feat["margin_top1_top2"]
                    )
                    pred_prob = float(sigmoid(8.0 * (score - 0.5)))
                    rows.append({
                        "dataset": dataset,
                        "seed": seed,
                        "epsilon": epsilon,
                        "attack_name": "mia_proxy_subindex_split",
                        "item_id": f"member_{i}",
                        "label_member": 1,
                        **feat,
                        "pred_member_prob": pred_prob,
                    })

                for i, feat in enumerate(nonmember_feats):
                    score = (
                        0.5 * feat["max_sim_to_index"] +
                        0.3 * feat["mean_top5_sim_to_index"] +
                        0.2 * feat["margin_top1_top2"]
                    )
                    pred_prob = float(sigmoid(8.0 * (score - 0.5)))
                    rows.append({
                        "dataset": dataset,
                        "seed": seed,
                        "epsilon": epsilon,
                        "attack_name": "mia_proxy_subindex_split",
                        "item_id": f"nonmember_{i}",
                        "label_member": 0,
                        **feat,
                        "pred_member_prob": pred_prob,
                    })

                y_true = [r["label_member"] for r in rows]
                y_score = [r["pred_member_prob"] for r in rows]
                auc = float(binary_auroc(y_true, y_score))
                acc = float(np.mean([(1 if s >= 0.5 else 0) == y for s, y in zip(y_score, y_true)]))

                member_scores = [r["pred_member_prob"] for r in rows if r["label_member"] == 1]
                nonmember_scores = [r["pred_member_prob"] for r in rows if r["label_member"] == 0]

                summary = {
                    "created_at": now_iso_kst(),
                    "dataset": dataset,
                    "seed": seed,
                    "epsilon": epsilon,
                    "attack_name": "mia_proxy_subindex_split",
                    "projection_method": "gaussian_random_projection_raw_to_guard_dim",
                    "projection_seed": PROJ_SEED,
                    "target_dim": target_dim,
                    "membership_mode": "subindex_split_with_self_exclusion",
                    "n_items": len(rows),
                    "n_index": n_index,
                    "n_member": len(member_feats),
                    "n_nonmember": len(nonmember_feats),
                    "membership_inference_auroc": auc,
                    "membership_attack_acc_at_0_5": acc,
                    "member_score_mean": float(np.mean(member_scores)),
                    "nonmember_score_mean": float(np.mean(nonmember_scores)),
                }

                run_meta = {
                    "created_at": now_iso_kst(),
                    "dataset": dataset,
                    "seed": seed,
                    "epsilon": epsilon,
                    "attack_name": "mia_proxy_subindex_split",
                    "raw_embedding_path": str(raw_path),
                    "guard_embedding_path": str(guard_path),
                    "membership_mode": "subindex_split_with_self_exclusion",
                    "nonmember_rule": "projected_raw_second_half",
                    "member_rule": "guard_first_half_as_index_and_candidate",
                    "projection_method": "gaussian_random_projection_raw_to_guard_dim",
                    "projection_seed": PROJ_SEED,
                    "target_dim": target_dim,
                }

                out_dir = runs_root / dataset / f"seed{seed}" / "attacks" / "stage3" / f"mia_eps_{epsilon:02d}"
                out_dir.mkdir(parents=True, exist_ok=True)

                fieldnames = [
                    "dataset", "seed", "epsilon", "attack_name", "item_id", "label_member",
                    "max_sim_to_index", "mean_top5_sim_to_index", "margin_top1_top2",
                    "self_norm", "pred_member_prob"
                ]

                write_csv(out_dir / "attack_item.csv", rows, fieldnames)
                write_json(out_dir / "attack_summary.json", summary)
                write_json(out_dir / "run_meta.json", run_meta)

                print(f"[OK] wrote: {out_dir}")

    print("[DONE] membership inference proxy finished.")


if __name__ == "__main__":
    main()
