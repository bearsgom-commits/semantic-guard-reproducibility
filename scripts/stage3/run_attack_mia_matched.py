#!/usr/bin/env python3

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

MODEL = "intfloat_multilingual-e5-base"


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat()


def normalize(x):
    x = x.astype(np.float32)
    n = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.clip(n, 1e-12, None)


def find_guard(root, dataset, seed, eps):
    variants = {
        dataset,
        dataset.replace("-", "_"),
        dataset.replace("_", "-"),
    }

    for ds in variants:
        p = (
            root / "artifacts" / ds / MODEL / "stage3"
            / f"seed{seed}" / f"eps_{eps:02d}"
            / "guard_embeddings.npy"
        )
        if p.exists():
            return p

    hits = []
    for ds in variants:
        base = root / "artifacts" / ds
        if not base.exists():
            continue
        for p in base.rglob("guard_embeddings.npy"):
            s = str(p)
            if f"seed{seed}" not in s:
                continue
            if (
                f"eps_{eps:02d}" in s
                or f"eps_{eps}" in s
                or f"eps{eps}" in s
            ):
                hits.append(p)

    if not hits:
        raise FileNotFoundError(
            f"guard not found: {dataset} seed={seed} eps={eps}"
        )

    return sorted(hits)[0]


def features(candidate, index, chunk_size, exclude_self):
    candidate = normalize(candidate)
    index = normalize(index)

    out = []
    excluded = 0

    for start in range(0, len(candidate), chunk_size):
        end = min(start + chunk_size, len(candidate))
        sims = candidate[start:end] @ index.T

        if exclude_self:
            for local_i in range(end - start):
                global_i = start + local_i
                sims[local_i, global_i] = -1.0
                if sims[local_i, global_i] != -1.0:
                    raise RuntimeError("self exclusion failed")
                excluded += 1

        for i in range(end - start):
            row = sims[i]
            k = min(5, len(row))
            ids = np.argpartition(-row, kth=k - 1)[:k]
            vals = np.sort(row[ids])[::-1]

            out.append({
                "max_sim_to_index": float(vals[0]),
                "mean_top5_sim_to_index": float(np.mean(vals)),
                "margin_top1_top2":
                    float(vals[0] - vals[1]) if len(vals) >= 2
                    else float(vals[0]),
                "self_norm":
                    float(np.linalg.norm(candidate[start + i])),
            })

    return out, excluded


def score(feat):
    raw = (
        0.5 * feat["max_sim_to_index"]
        + 0.3 * feat["mean_top5_sim_to_index"]
        + 0.2 * feat["margin_top1_top2"]
    )
    return float(1.0 / (1.0 + np.exp(-8.0 * (raw - 0.5))))


def rankdata(a):
    order = np.argsort(a)
    ranks = np.empty(len(a), dtype=float)
    i = 0

    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1

        r = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1

    return ranks


def auroc(y, s):
    y = np.asarray(y, dtype=int)
    s = np.asarray(s, dtype=float)
    n1 = int(np.sum(y == 1))
    n0 = int(np.sum(y == 0))
    r = rankdata(s)
    return float(
        (np.sum(r[y == 1]) - n1 * (n1 + 1) / 2)
        / (n1 * n0)
    )


def write_json(path, obj):
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project_root", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--epsilon", type=int, required=True)
    ap.add_argument("--sample_size", type=int, default=2500)
    ap.add_argument("--sampling_seed", type=int, default=20260822)
    ap.add_argument("--chunk_size", type=int, default=256)
    ap.add_argument("--output_dir", required=True)
    a = ap.parse_args()

    root = Path(a.project_root).resolve()
    out_dir = Path(a.output_dir).resolve()

    if out_dir.exists():
        raise FileExistsError(f"refusing overwrite: {out_dir}")

    guard_path = find_guard(root, a.dataset, a.seed, a.epsilon)
    guard = np.load(guard_path, mmap_mode="r")

    if guard.ndim != 2:
        raise ValueError("guard must be 2D")

    n_total, dim = guard.shape
    N = a.sample_size

    if n_total < 2 * N:
        raise ValueError(
            f"insufficient corpus: total={n_total}, required={2*N}"
        )

    rng = np.random.default_rng(a.sampling_seed)
    perm = rng.permutation(n_total)

    member_idx = perm[:N]
    nonmember_idx = perm[N:2 * N]
    index_idx = member_idx.copy()

    if not np.array_equal(index_idx, member_idx):
        raise RuntimeError("member/index alignment failure")

    if np.intersect1d(member_idx, nonmember_idx).size:
        raise RuntimeError("member/nonmember overlap")

    index = np.asarray(guard[index_idx], dtype=np.float32)
    member = np.asarray(guard[member_idx], dtype=np.float32)
    nonmember = np.asarray(guard[nonmember_idx], dtype=np.float32)

    mf, excluded = features(
        member, index, a.chunk_size, exclude_self=True
    )
    nf, _ = features(
        nonmember, index, a.chunk_size, exclude_self=False
    )

    if excluded != N:
        raise RuntimeError(
            f"self exclusion count mismatch: {excluded} != {N}"
        )

    rows = []

    for i, f in enumerate(mf):
        rows.append({
            "dataset": a.dataset,
            "seed": a.seed,
            "epsilon": a.epsilon,
            "attack_name": "mia_proxy_matched_index",
            "item_id": f"member_{i}",
            "corpus_row_index": int(member_idx[i]),
            "label_member": 1,
            **f,
            "pred_member_prob": score(f),
        })

    for i, f in enumerate(nf):
        rows.append({
            "dataset": a.dataset,
            "seed": a.seed,
            "epsilon": a.epsilon,
            "attack_name": "mia_proxy_matched_index",
            "item_id": f"nonmember_{i}",
            "corpus_row_index": int(nonmember_idx[i]),
            "label_member": 0,
            **f,
            "pred_member_prob": score(f),
        })

    y = np.array([r["label_member"] for r in rows])
    s = np.array([r["pred_member_prob"] for r in rows])

    auc = auroc(y, s)
    acc = float(np.mean((s >= 0.5).astype(int) == y))

    member_scores = s[y == 1]
    nonmember_scores = s[y == 0]

    summary = {
        "created_at": now_iso(),
        "dataset": a.dataset,
        "seed": a.seed,
        "epsilon": a.epsilon,
        "attack_name": "mia_proxy_matched_index",
        "membership_mode":
            "matched_guard_index_membership_with_self_exclusion",
        "representation_family": "guard",
        "target_dim": int(dim),
        "sample_size": N,
        "sampling_seed": a.sampling_seed,
        "n_items": 2 * N,
        "n_index": N,
        "n_member": N,
        "n_nonmember": N,
        "membership_inference_auroc": auc,
        "membership_attack_acc_at_0_5": acc,
        "member_score_mean": float(np.mean(member_scores)),
        "nonmember_score_mean": float(np.mean(nonmember_scores)),
    }

    meta = {
        "created_at": now_iso(),
        "dataset": a.dataset,
        "seed": a.seed,
        "epsilon": a.epsilon,
        "guard_embedding_path": str(guard_path.resolve()),
        "guard_shape": [int(n_total), int(dim)],
        "guard_dtype": str(guard.dtype),
        "sampling_seed": a.sampling_seed,
        "sample_size": N,
        "index_rule":
            "deterministic sampled Guard rows; identical member candidates",
        "member_rule":
            "same sampled Guard rows as index with self exclusion",
        "nonmember_rule":
            "disjoint sampled Guard rows from same epsilon/seed representation",
        "self_exclusion": True,
        "self_exclusion_count": excluded,
        "score_formula":
            "sigmoid(8*(0.5*max_sim+0.3*mean_top5+0.2*margin-0.5))",
    }

    sampling = {
        "dataset": a.dataset,
        "sampling_seed": a.sampling_seed,
        "sample_size": N,
        "index_row_indices": [int(x) for x in index_idx],
        "member_row_indices": [int(x) for x in member_idx],
        "nonmember_row_indices": [int(x) for x in nonmember_idx],
    }

    out_dir.mkdir(parents=True)

    fields = [
        "dataset", "seed", "epsilon", "attack_name",
        "item_id", "corpus_row_index", "label_member",
        "max_sim_to_index", "mean_top5_sim_to_index",
        "margin_top1_top2", "self_norm", "pred_member_prob",
    ]

    with (out_dir / "attack_item.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    write_json(out_dir / "attack_summary.json", summary)
    write_json(out_dir / "run_meta.json", meta)
    write_json(out_dir / "sampling_indices.json", sampling)

    print(
        f"RESULT dataset={a.dataset} seed={a.seed} eps={a.epsilon} "
        f"N={N} dim={dim} AUROC={auc:.6f} ACC={acc:.6f} "
        f"M={np.mean(member_scores):.6f} "
        f"NM={np.mean(nonmember_scores):.6f}"
    )
    print(f"SELF_EXCLUSION={'PASS' if excluded == N else 'FAIL'}")
    print("WRITE=NEW_OUTPUT_ONLY")


if __name__ == "__main__":
    main()
