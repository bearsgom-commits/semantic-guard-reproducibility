#!/usr/bin/env python3
"""Prospective IP&M P2 security pilot for the D x B factorial cells.

This script does NOT rerun retrieval. It deterministically regenerates only the
sampled Guard rows needed by the matched index-membership proxy from frozen raw
E5 corpus embeddings, using the immutable Guard source. Historical attack
outputs and the completed 36-cell retrieval/stability results are never edited.

Scientific scope: this is an index-membership proxy, not a conventional
training-data membership-inference attack and not a privacy guarantee.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

GUARD_SHA256 = "8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d"
DATASETS = {
    "fiqa": (57638, "fiqa"),
    "scifact": (5183, "scifact"),
    "trec-covid": (171332, "trec_covid"),
}
CELLS = ((128, 4), (128, 10), (320, 4), (320, 10))
MODEL_DIR = "intfloat_multilingual-e5-base"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"missing/unsafe input: {path}")
    return path


def safe_new_out(root: Path, out: Path) -> Path:
    root = root.resolve(strict=True)
    out = out.expanduser().resolve(strict=False)
    if out == root or root in out.parents or out in root.parents:
        raise ValueError("output must be strictly outside research root")
    if out.exists() or out.is_symlink():
        raise FileExistsError(f"refusing overwrite: {out}")
    return out


def load_guard_module(path: Path):
    if sha256(path) != GUARD_SHA256:
        raise ValueError("immutable Guard SHA-256 mismatch")
    spec = importlib.util.spec_from_file_location("ipm_guard_immutable_p2", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Guard module")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if (mod.eps_to_repr_spec(0, 768).proj_dim, mod.eps_to_repr_spec(0, 768).q_bits) != (128, 4):
        raise ValueError("Guard eps0 reference mapping changed")
    if (mod.eps_to_repr_spec(32, 768).proj_dim, mod.eps_to_repr_spec(32, 768).q_bits) != (320, 10):
        raise ValueError("Guard eps32 reference mapping changed")
    return mod


def normalize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    n = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.clip(n, 1e-12, None)


def guard_transform_rows(raw_rows: np.ndarray, w: np.ndarray, bits: int, mod) -> np.ndarray:
    z = mod.l2_normalize(np.asarray(raw_rows, dtype=np.float32))
    z = z @ w
    z = mod.uniform_quantize(z, q_bits=bits, clip=1.0)
    z = mod.l2_normalize(z)
    if not np.isfinite(z).all():
        raise ValueError("nonfinite Guard output")
    max_dev = float(np.max(np.abs(np.linalg.norm(z, axis=1) - 1.0)))
    if max_dev > 2e-5:
        raise ValueError(f"Guard norm deviation too large: {max_dev}")
    return np.asarray(z, dtype=np.float32)


def feature_rows(candidate: np.ndarray, index: np.ndarray, exclude_self: bool, chunk_size: int):
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
                excluded += 1
        for i in range(end - start):
            row = sims[i]
            k = min(5, len(row))
            ids = np.argpartition(-row, kth=k - 1)[:k]
            vals = np.sort(row[ids])[::-1]
            out.append({
                "max_sim_to_index": float(vals[0]),
                "mean_top5_sim_to_index": float(np.mean(vals)),
                "margin_top1_top2": float(vals[0] - vals[1]) if len(vals) >= 2 else float(vals[0]),
                "self_norm": float(np.linalg.norm(candidate[start + i])),
            })
    return out, excluded


def attack_score(feat: dict) -> float:
    raw = (
        0.5 * feat["max_sim_to_index"]
        + 0.3 * feat["mean_top5_sim_to_index"]
        + 0.2 * feat["margin_top1_top2"]
    )
    return float(1.0 / (1.0 + np.exp(-8.0 * (raw - 0.5))))


def rankdata(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a)
    ranks = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        rank = (i + j + 2) / 2.0
        ranks[order[i:j + 1]] = rank
        i = j + 1
    return ranks


def auroc(y: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y, dtype=int)
    scores = np.asarray(scores, dtype=float)
    n1 = int(np.sum(y == 1))
    n0 = int(np.sum(y == 0))
    if not n1 or not n0:
        raise ValueError("AUROC requires both classes")
    ranks = rankdata(scores)
    return float((np.sum(ranks[y == 1]) - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def write_json(path: Path, obj) -> None:
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--dataset", choices=tuple(DATASETS), default="scifact")
    ap.add_argument("--seed", type=int, choices=(7, 13, 42), default=7)
    ap.add_argument("--sample-size", type=int, default=2500)
    ap.add_argument("--sampling-seed", type=int, default=20260822)
    ap.add_argument("--chunk-size", type=int, default=256)
    a = ap.parse_args()

    root = a.root.expanduser().resolve(strict=True)
    out = safe_new_out(root, a.out)
    n_expected, slug = DATASETS[a.dataset]
    n = a.sample_size
    if n <= 1 or a.chunk_size <= 0:
        raise ValueError("invalid sample/chunk size")
    if n_expected < 2 * n:
        raise ValueError(f"dataset too small for 2N sampling: {n_expected} < {2*n}")

    guard_path = require_file(root / "repo" / "src" / "guard_repr.py")
    raw_path = require_file(root / "artifacts" / slug / MODEL_DIR / "stage3" / "shared" / "corpus_embeddings_fp32.npy")
    ids_path = require_file(root / "artifacts" / slug / MODEL_DIR / "stage3" / "shared" / "corpus_doc_ids.json")

    input_hashes = {
        "guard_repr.py": sha256(guard_path),
        "corpus_embeddings_fp32.npy": sha256(raw_path),
        "corpus_doc_ids.json": sha256(ids_path),
    }
    mod = load_guard_module(guard_path)
    raw = np.load(raw_path, mmap_mode="r", allow_pickle=False)
    if raw.shape != (n_expected, 768) or raw.dtype != np.float32:
        raise ValueError(f"unexpected raw embedding shape/dtype: {raw.shape}/{raw.dtype}")
    ids = json.loads(ids_path.read_text(encoding="utf-8"))
    ids = [str(x) for x in ids]
    if len(ids) != n_expected or len(ids) != len(set(ids)):
        raise ValueError("document-ID alignment/uniqueness failure")

    rng = np.random.default_rng(a.sampling_seed)
    perm = rng.permutation(n_expected)
    member_idx = np.asarray(perm[:n], dtype=np.int64)
    nonmember_idx = np.asarray(perm[n:2*n], dtype=np.int64)
    if np.intersect1d(member_idx, nonmember_idx).size:
        raise RuntimeError("member/nonmember overlap")
    sampled_idx = np.concatenate([member_idx, nonmember_idx])
    sampled_raw = np.asarray(raw[sampled_idx], dtype=np.float32)
    if sampled_raw.shape != (2*n, 768) or not np.isfinite(sampled_raw).all():
        raise ValueError("sampled raw input invalid")

    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "cohort_indices.json", {
        "dataset": a.dataset,
        "sampling_seed": a.sampling_seed,
        "sample_size_per_class": n,
        "member_row_indices": [int(x) for x in member_idx],
        "nonmember_row_indices": [int(x) for x in nonmember_idx],
        "note": "local audit evidence; do not publish row-level cohort unless disclosure is approved",
    })

    summary_rows = []
    cell_hashes = {}
    for dim, bits in CELLS:
        proj = mod.make_projection_matrix(768, dim, a.seed)
        guarded = guard_transform_rows(sampled_raw, proj, bits, mod)
        member = guarded[:n]
        nonmember = guarded[n:]
        index = member.copy()
        mf, excluded = feature_rows(member, index, True, a.chunk_size)
        nf, _ = feature_rows(nonmember, index, False, a.chunk_size)
        if excluded != n:
            raise RuntimeError(f"self exclusion mismatch in D{dim} B{bits}: {excluded} != {n}")

        rows = []
        for label, feats, idxs in ((1, mf, member_idx), (0, nf, nonmember_idx)):
            for i, feat in enumerate(feats):
                rows.append({
                    "dataset": a.dataset,
                    "seed": a.seed,
                    "dimension": dim,
                    "quantization_bits": bits,
                    "attack_name": "index_membership_proxy_matched",
                    "corpus_row_index": int(idxs[i]),
                    "label_member": label,
                    **feat,
                    "pred_member_prob": attack_score(feat),
                })
        scores = np.asarray([r["pred_member_prob"] for r in rows], dtype=float)
        labels = np.asarray([r["label_member"] for r in rows], dtype=int)
        if not np.isfinite(scores).all() or float(np.max(scores) - np.min(scores)) <= 1e-12:
            raise ValueError(f"degenerate/nonfinite attack scores in D{dim} B{bits}")
        auc = auroc(labels, scores)
        if not np.isfinite(auc):
            raise ValueError(f"nonfinite AUROC in D{dim} B{bits}")

        cell_dir = out / f"{a.dataset}_s{a.seed}_D{dim}_B{bits}"
        cell_dir.mkdir()
        item_path = cell_dir / "attack_item.csv"
        fields = list(rows[0].keys())
        with item_path.open("x", encoding="utf-8", newline="") as f:
            wcsv = csv.DictWriter(f, fieldnames=fields)
            wcsv.writeheader()
            wcsv.writerows(rows)
        summary = {
            "schema": "ipm_p2_index_membership_proxy_v1",
            "created_at_utc": now_iso(),
            "dataset": a.dataset,
            "seed": a.seed,
            "dimension": dim,
            "quantization_bits": bits,
            "epsilon_label": "NONE_OFF_DIAGONAL" if (dim, bits) not in ((128, 4), (320, 10)) else "REFERENCE_CONFIGURATION_ONLY",
            "attack_name": "index_membership_proxy_matched",
            "interpretation": "sampled comparison-index membership proxy; not training-data MIA and not a privacy guarantee",
            "sample_size_per_class": n,
            "sampling_seed": a.sampling_seed,
            "self_exclusion_count": excluded,
            "index_membership_proxy_auroc": auc,
            "score_min": float(np.min(scores)),
            "score_max": float(np.max(scores)),
            "member_score_mean": float(np.mean(scores[labels == 1])),
            "nonmember_score_mean": float(np.mean(scores[labels == 0])),
            "projection_matrix_sha256": hashlib.sha256(np.asarray(proj, dtype=np.float32).tobytes()).hexdigest(),
            "sampled_guard_sha256": hashlib.sha256(guarded.tobytes()).hexdigest(),
            "attack_item_sha256": sha256(item_path),
        }
        write_json(cell_dir / "attack_summary.json", summary)
        summary_rows.append(summary)
        cell_hashes[f"D{dim}_B{bits}"] = {
            "summary_sha256": sha256(cell_dir / "attack_summary.json"),
            "item_sha256": sha256(item_path),
        }

    summary_csv = out / "pilot_summary_4cells.csv"
    fields = [
        "dataset", "seed", "dimension", "quantization_bits", "attack_name",
        "sample_size_per_class", "sampling_seed", "self_exclusion_count",
        "index_membership_proxy_auroc", "score_min", "score_max",
        "member_score_mean", "nonmember_score_mean", "projection_matrix_sha256",
        "sampled_guard_sha256",
    ]
    with summary_csv.open("x", encoding="utf-8", newline="") as f:
        wcsv = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        wcsv.writeheader()
        wcsv.writerows(summary_rows)

    manifest = {
        "schema": "ipm_p2_security_pilot_manifest_v1",
        "created_at_utc": now_iso(),
        "status": "PROSPECTIVE_SECURITY_PILOT_NOT_HISTORICAL_REPLAY",
        "dataset": a.dataset,
        "seed": a.seed,
        "cells": [{"dimension": d, "quantization_bits": b} for d, b in CELLS],
        "retrieval_executed": False,
        "guard_rows_regenerated": 2 * n,
        "shared_cohort_across_cells": True,
        "input_sha256": input_hashes,
        "cohort_indices_sha256": sha256(out / "cohort_indices.json"),
        "pilot_summary_sha256": sha256(summary_csv),
        "cell_output_sha256": cell_hashes,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "historical_originals_modified": False,
    }
    write_json(out / "run_manifest.json", manifest)

    if sha256(guard_path) != input_hashes["guard_repr.py"] or sha256(raw_path) != input_hashes["corpus_embeddings_fp32.npy"] or sha256(ids_path) != input_hashes["corpus_doc_ids.json"]:
        raise RuntimeError("CRITICAL: frozen input changed during pilot")

    print(f"P2_PILOT_PASS dataset={a.dataset} seed={a.seed} cells=4 sample_per_class={n}")
    for r in summary_rows:
        print(f"CELL D={r['dimension']} B={r['quantization_bits']} AUROC={r['index_membership_proxy_auroc']:.6f}")
    print("RETRIEVAL_EXECUTED=NO")
    print("ORIGINAL_INPUT_HASHES_UNCHANGED=YES")
    print(f"OUTPUT={out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P2_PILOT_FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
