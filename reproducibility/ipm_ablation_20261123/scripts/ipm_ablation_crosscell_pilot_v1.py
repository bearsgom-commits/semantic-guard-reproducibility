#!/usr/bin/env python3
"""Isolated one-cell pilot for IP&M D=128, B=10, SciFact seed=7.

Reads historical research sources and raw embeddings without modifying them.
Writes only to a brand-new output directory outside --root.
Does NOT claim to reproduce a historical run or compute qrels metrics.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import numpy as np

SOURCE_SHA = '8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d'
DS = 'scifact'
SEED = 7
DIM = 128
BITS = 10
TOPK = 100

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    root = args.root.expanduser().resolve(strict=True)
    out = args.out.expanduser().resolve(strict=False)
    if not root.is_dir():
        ap.error('root must be a directory')
    if out == root or root in out.parents or out in root.parents:
        ap.error('out MUST be separate from root and its ancestors')
    if out.exists():
        ap.error('out already exists; refusing overwrite')
    source = root / 'repo/src/guard_repr.py'
    base = root / 'artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared'
    doc_path = base / 'corpus_embeddings_fp32.npy'
    qry_path = base / 'query_embeddings_fp32.npy'
    for p in (source, doc_path, qry_path):
        if not p.is_file() or p.is_symlink():
            ap.error(f'required regular file missing or symlink: {p}')
    if sha(source) != SOURCE_SHA:
        ap.error('guard_repr.py hash mismatch; historical code not as expected')
    docs = np.load(doc_path, mmap_mode='r', allow_pickle=False)
    qrys = np.load(qry_path, mmap_mode='r', allow_pickle=False)
    if docs.shape != (5183, 768) or qrys.shape != (1109, 768):
        ap.error(f'wrong raw shapes: docs={docs.shape}, queries={qrys.shape}')
    if docs.dtype != np.float32 or qrys.dtype != np.float32:
        ap.error('raw dtype must be float32')
    input_hashes = {str(doc_path.relative_to(root)): sha(doc_path),
                    str(qry_path.relative_to(root)): sha(qry_path),
                    str(source.relative_to(root)): sha(source)}
    spec = importlib.util.spec_from_file_location('guard_repr_original_readonly', source)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    assert mod.eps_to_repr_spec(0, 768).proj_dim == 128
    assert mod.eps_to_repr_spec(0, 768).q_bits == 4
    assert mod.eps_to_repr_spec(32, 768).proj_dim == 320
    assert mod.eps_to_repr_spec(32, 768).q_bits == 10

    # Original functions and order unchanged; only D/B are decoupled.
    W = mod.make_projection_matrix(768, DIM, SEED)
    def transform(x):
        normalized = mod.l2_normalize(np.asarray(x, dtype=np.float32))
        projected = normalized @ W
        quantized = mod.uniform_quantize(projected, q_bits=BITS, clip=1.0)
        return mod.l2_normalize(quantized).astype(np.float32)
    d_out = transform(docs)
    q_out = transform(qrys)
    if not np.isfinite(d_out).all() or not np.isfinite(q_out).all():
        ap.error('non-finite embeddings')
    norm_dev = max(float(np.abs(np.linalg.norm(d_out, axis=1)-1).max()),
                   float(np.abs(np.linalg.norm(q_out, axis=1)-1).max()))
    if norm_dev > 2e-5:
        ap.error(f'output norms unexpectedly far from unity: {norm_dev}')

    # Pilot retrieval. Row-index ranking only, not document-ID/qrels evaluation.
    indices = np.empty((len(q_out), TOPK), dtype=np.int32)
    scores = np.empty((len(q_out), TOPK), dtype=np.float32)
    # NumPy exact float32 dot, deterministic tie rule: lower corpus row first.
    for i, q in enumerate(q_out):
        sim = d_out @ q
        top = np.lexsort((np.arange(len(sim)), -sim))[:TOPK]
        indices[i] = top
        scores[i] = sim[top]

    # All checks complete before creating files.
    out.mkdir(parents=True, exist_ok=False)
    paths = {'guard_corpus.npy': d_out, 'guard_queries.npy': q_out,
             'top100_row_indices.npy': indices, 'top100_scores.npy': scores}
    output_hashes = {}
    for filename, arr in paths.items():
        p = out / filename
        with p.open('xb') as f:
            np.save(f, arr, allow_pickle=False)
        output_hashes[filename] = sha(p)
    manifest = {
        'status': 'PILOT_CROSS_CELL_NOT_HISTORICAL_REPRODUCTION',
        'dataset': DS, 'seed': SEED, 'dimension': DIM, 'quantization_bits': BITS,
        'guard_pipeline': 'original l2_normalize -> original Gaussian matrix -> original uniform_quantize(clip=1.0) -> original l2_normalize',
        'input_shapes': {'corpus': list(docs.shape), 'queries': list(qrys.shape)},
        'output_shapes': {'corpus': list(d_out.shape), 'queries': list(q_out.shape)},
        'input_sha256': input_hashes, 'output_sha256': output_hashes,
        'top100': 'Exact float32 dot, deterministic ties by lower corpus row; indexes are rows, NOT document IDs',
        'max_l2_norm_deviation': norm_dev,
        'qrels_evaluated': False,
        'source_preservation': 'All original inputs read-only; immutable SHA checked before and after.',
        'python': sys.version.split()[0], 'numpy': np.__version__,
    }
    with (out / 'pilot_manifest.json').open('x', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    after = {key: sha(root / key) for key in input_hashes}
    if after != input_hashes:
        print('CRITICAL_INPUT_HASH_CHANGED; investigate before continuing')
        return 2
    print('PILOT_STATUS=PASS')
    print('CELL=scifact_seed7_D128_B10')
    print('SHAPES=corpus_5183x128,queries_1109x128,top100_1109x100')
    print(f'MAX_L2_NORM_DEVIATION={norm_dev:.9g}')
    print('INPUT_SHA256_UNCHANGED=YES')
    print('QRELS_METRICS=NOT_YET_COMPUTED')
    print('RANKING_IDS=ROW_INDICES_ONLY')
    print('OUTPUT=', out)
    print('OUTPUT_FILES=', ','.join([*paths.keys(), 'pilot_manifest.json']))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
