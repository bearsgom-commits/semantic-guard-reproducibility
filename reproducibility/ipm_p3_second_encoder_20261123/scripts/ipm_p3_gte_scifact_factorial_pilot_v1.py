#!/usr/bin/env python3
"""IP&M P3 SciFact GTE second-encoder 2x2 seed-7 retrieval pilot.

Read-only original data/Guard/retrieval; consume separately generated frozen GTE
vectors. Produces NEW, isolated 4-cell ranking/metric outputs only. Scores use
the same Guard factor transform and evaluated metrics as the E5 factorial
runner. This is a prospective second-encoder experiment, not historical replay.
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

CELLS = ((128, 4), (128, 10), (320, 4), (320, 10))
GUARD_SHA = "8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d"
RETRIEVAL_SHA = "09ecb4d855417189f9dca36dcf67913ac1b08cb2051f7a09bbfb8b7f5f16a3a5"
TOPK = 100

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def new_output(root: Path, out: Path, extra: Path) -> Path:
    root = root.resolve(strict=True)
    extra = extra.resolve(strict=True)
    out = out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink():
        raise ValueError("output already exists; refusing overwrite")
    for protected in (root, extra):
        if out == protected or protected in out.parents or out in protected.parents:
            raise ValueError("output must be separate from all inputs")
    return out

def load_guard(path: Path):
    spec = importlib.util.spec_from_file_location("immutable_p3_guard", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Guard import failed")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    assert (mod.eps_to_repr_spec(0, 768).proj_dim,
            mod.eps_to_repr_spec(0, 768).q_bits) == (128, 4)
    assert (mod.eps_to_repr_spec(32, 768).proj_dim,
            mod.eps_to_repr_spec(32, 768).q_bits) == (320, 10)
    return mod

def transform(x, w, bits, mod, block=8192):
    output = np.empty((len(x), w.shape[1]), dtype=np.float32)
    for begin in range(0, len(x), block):
        z = mod.l2_normalize(np.asarray(x[begin:begin+block], dtype=np.float32))
        z = z @ w
        z = mod.uniform_quantize(z, q_bits=bits, clip=1.0)
        output[begin:begin+len(z)] = mod.l2_normalize(z)
    return output

def load_ids(p):
    ids = [str(v) for v in json.loads(p.read_text(encoding="utf-8"))]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate IDs")
    return ids

def load_qrels(p):
    qrels = {}
    with p.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not {"query-id", "corpus-id", "score"} <= set(reader.fieldnames or []):
            raise ValueError("bad qrels headers")
        for row in reader:
            q, d = str(row["query-id"]), str(row["corpus-id"])
            relevance = int(float(row["score"]))
            if d in qrels.setdefault(q, {}):
                raise ValueError("duplicate qrel pair")
            qrels[q][d] = relevance
    return qrels

def dcg(rels, k=10):
    return sum((2**r - 1) / np.log2(i+2) for i, r in enumerate(rels[:k]))

def metrics(pred, rels):
    relevant = {d for d, v in rels.items() if v > 0}
    recall = len(set(pred[:10]) & relevant) / len(relevant) if relevant else 0.0
    ideal = dcg(sorted(rels.values(), reverse=True), 10)
    ndcg = dcg([rels.get(d, 0) for d in pred[:10]], 10) / ideal if ideal else 0.0
    return float(recall), float(ndcg)

def write_json(path, value):
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--encoded", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seed", type=int, choices=(7, 13, 42), default=7)
    a = p.parse_args()
    root = a.root.expanduser().resolve(strict=True)
    enc = a.encoded.expanduser().resolve(strict=True)
    out = new_output(root, a.out, enc)
    guard_path = root/"repo/src/guard_repr.py"
    ranker_path = root/"repo/src/stage3/run_dense_retrieval.py"
    qrels_path = root/"private_data/beir/scifact/qrels/test.tsv"
    manifest_path = enc/"encoding_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "PASS" or manifest.get("doc_count") != 5183 or manifest.get("test_qids") != 300:
        raise ValueError("GTE encoding manifest not PASS or unexpected counts")
    if manifest.get("encoder", {}).get("resolved_revision") != "9bbca17d9273fd0d03d5725c7a4b0f6b45142062":
        raise ValueError("unexpected GTE revision")
    if manifest["encoder"].get("resolved_code_revision") != "40ced75c3017eb27626c9d4ea981bde21a2662f4":
        raise ValueError("unexpected remote code revision")
    if sha(guard_path) != GUARD_SHA or sha(ranker_path) != RETRIEVAL_SHA:
        raise ValueError("original Guard/ranker source changed")
    if sha(qrels_path) != manifest["dataset_input_sha256"]["qrels/test.tsv"]:
        raise ValueError("original test qrels changed")
    for name, expected in manifest["outputs_sha256"].items():
        if sha(enc/name) != expected:
            raise ValueError("encoded file digest mismatch: " + name)
    doc_path = enc/"corpus_embeddings_fp32.npy"
    query_path = enc/"judged_query_embeddings_fp32.npy"
    id_path = enc/"corpus_doc_ids.json"
    qid_path = enc/"judged_query_ids.json"
    docs = np.load(doc_path, mmap_mode="r", allow_pickle=False)
    queries = np.load(query_path, mmap_mode="r", allow_pickle=False)
    dids, qids = load_ids(id_path), load_ids(qid_path)
    if docs.shape != (5183, 768) or queries.shape != (300, 768):
        raise ValueError(f"invalid shape {docs.shape}/{queries.shape}")
    if docs.dtype != np.float32 or queries.dtype != np.float32:
        raise ValueError("embedding dtype must be float32")
    if len(dids) != 5183 or len(qids) != 300:
        raise ValueError("ID/vector alignment failure")
    if not np.isfinite(docs).all() or not np.isfinite(queries).all():
        raise ValueError("nonfinite source embeddings")
    qrels = load_qrels(qrels_path)
    if len(qrels) != 300 or set(qrels) != set(qids):
        raise ValueError("judged query set mismatch")
    if not {d for row in qrels.values() for d in row}.issubset(dids):
        raise ValueError("unknown judged document")
    # Exact qid evaluation order and metric implementation match the original E5
    # factorial code. The only changed source is the encoder representation.
    norm0 = max(float(np.max(np.abs(np.linalg.norm(docs, axis=1)-1))),
                float(np.max(np.abs(np.linalg.norm(queries, axis=1)-1))))
    if norm0 > 2e-5:
        raise ValueError(f"input vectors are not unit-normalized: {norm0}")
    mod = load_guard(guard_path)
    input_hashes = {
        "guard_repr.py": sha(guard_path),
        "run_dense_retrieval.py": sha(ranker_path),
        "qrels/test.tsv": sha(qrels_path),
        "encoding_manifest.json": sha(manifest_path),
        **{f"encoded/{name}": digest for name, digest in manifest["outputs_sha256"].items()},
    }
    results = []
    cell_payloads = []
    for dim, bits in CELLS:
        w = mod.make_projection_matrix(768, dim, a.seed)
        guarded_docs = transform(docs, w, bits, mod)
        guarded_queries = transform(queries, w, bits, mod)
        if not np.isfinite(guarded_docs).all() or not np.isfinite(guarded_queries).all():
            raise ValueError(f"nonfinite Guard outputs D{dim} B{bits}")
        norm_dev = max(float(np.max(np.abs(np.linalg.norm(guarded_docs,axis=1)-1))),
                       float(np.max(np.abs(np.linalg.norm(guarded_queries,axis=1)-1))))
        if norm_dev > 2e-5:
            raise ValueError(f"Guard norm drift D{dim} B{bits}: {norm_dev}")
        rows = []
        for i, qid in enumerate(qids):
            sims = guarded_docs @ guarded_queries[i]
            k = min(TOPK, len(sims))
            top = np.argpartition(-sims, k-1)[:k]
            top = top[np.argsort(-sims[top])]
            predicted = [dids[int(j)] for j in top]
            recall, ndcg = metrics(predicted, qrels[qid])
            rows.append({
                "qid": qid,
                "top_doc_ids": predicted,
                "top_scores": [float(sims[j]) for j in top],
                "recall_at_10": recall,
                "ndcg_at_10": ndcg,
                "hit_at_10": int(any(qrels[qid].get(d,0)>0 for d in predicted[:10])),
                "top1_rel": int(qrels[qid].get(predicted[0],0)>0),
            })
        result = {
            "dataset": "scifact",
            "model": "Alibaba-NLP/gte-multilingual-base",
            "seed": a.seed,
            "dimension": dim,
            "quantization_bits": bits,
            "epsilon_label": "NONE_OFF_DIAGONAL" if (dim,bits) not in ((128,4),(320,10)) else "REFERENCE_CONFIGURATION_ONLY",
            "tested_queries": 300,
            "mean_recall_at_10": float(np.mean([r["recall_at_10"] for r in rows])),
            "mean_ndcg_at_10": float(np.mean([r["ndcg_at_10"] for r in rows])),
            "mean_hit_at_10": float(np.mean([r["hit_at_10"] for r in rows])),
            "max_l2_norm_deviation": norm_dev,
            "projection_matrix_sha256": hashlib.sha256(w.tobytes()).hexdigest(),
        }
        cell_payloads.append((dim,bits,rows,result))
        print(f"P3_COMPUTED D={dim} B={bits} nDCG@10={result['mean_ndcg_at_10']:.8f}", flush=True)
    # Fail closed before creating an output: no frozen input may change.
    if sha(guard_path)!=input_hashes["guard_repr.py"] or sha(qrels_path)!=input_hashes["qrels/test.tsv"] or sha(doc_path)!=input_hashes["encoded/corpus_embeddings_fp32.npy"] or sha(query_path)!=input_hashes["encoded/judged_query_embeddings_fp32.npy"]:
        raise RuntimeError("input mutated during experiment")
    out.mkdir(parents=True, exist_ok=False)
    for dim,bits,rows,result in cell_payloads:
        dest=out/f"scifact_s{a.seed}_D{dim}_B{bits}"
        dest.mkdir()
        ranked=dest/"test_rankings_top100.jsonl"
        with ranked.open("x",encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False, allow_nan=False)+"\n")
        result["rankings_sha256"]=sha(ranked)
        write_json(dest/"cell_manifest.json",result)
        results.append(result)
    with (out/"pilot_summary_4cells.csv").open("x",newline="",encoding="utf-8") as f:
        fields=["dataset","model","seed","dimension","quantization_bits","epsilon_label",
                "tested_queries","mean_recall_at_10","mean_ndcg_at_10","mean_hit_at_10",
                "max_l2_norm_deviation","projection_matrix_sha256","rankings_sha256"]
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    write_json(out/"pilot_manifest.json",{
        "schema":"ipm_p3_gte_scifact_factorial_v1",
        "status":"PASS_PROSPECTIVE_SECOND_ENCODER_PILOT",
        "created_at_utc":datetime.now(timezone.utc).isoformat(),
        "seed":a.seed,
        "cell_count":len(results),
        "cohort":"BEIR SciFact test qrels judged queries, 300 fixed IDs",
        "metric_contract":"E5 factorial DCG 2^rel-1, nDCG@10, recall@10",
        "ranking_contract":"float32 dot, np.argpartition followed by argsort; tie order not fixed",
        "originals_modified":False,
        "input_sha256":input_hashes,
        "output_sha256":{
           "pilot_summary_4cells.csv":sha(out/"pilot_summary_4cells.csv"),
           **{f"scifact_s{a.seed}_D{r['dimension']}_B{r['quantization_bits']}/test_rankings_top100.jsonl":r["rankings_sha256"] for r in results}
        },
        "limitations":["Prospective second model, not historical E5 replay",
                       "No off-diagonal epsilon definition",
                       "Cross-encoder claims require preprocessing/protocol audit",
                       "No three-seed stability inference until expansion"],
    })
    print("P3_4CELL_PILOT_PASS")
    for r in results:
        print(f"CELL D={r['dimension']} B={r['quantization_bits']} RECALL10={r['mean_recall_at_10']:.8f} NDCG10={r['mean_ndcg_at_10']:.8f}")
    print("ORIGINAL_INPUT_HASHES_UNCHANGED=YES")
    print(f"OUTPUT={out}")

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print(f"P3_4CELL_PILOT_FAIL {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(2)
