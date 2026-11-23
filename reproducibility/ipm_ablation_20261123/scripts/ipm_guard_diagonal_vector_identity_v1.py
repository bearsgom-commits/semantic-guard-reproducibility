#!/usr/bin/env python3
"""Read-only sampled vector concordance: historical Guard against prospective 2x2 diagonal.
This checks *corpus vectors*, not attack validity or historical ranking equivalence.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys
import numpy as np

DATASETS={'fiqa':(57638,'fiqa'),'scifact':(5183,'scifact'),'trec-covid':(171332,'trec_covid')}
SEEDS=(7,13,42)
CONDITIONS=((0,128,4),(32,320,10))

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def import_module(path):
    s=importlib.util.spec_from_file_location('immutable_guard_for_sample_audit',path)
    m=importlib.util.module_from_spec(s)
    sys.modules[s.name]=m
    s.loader.exec_module(m)
    return m

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',required=True,type=Path)
    ap.add_argument('--results',required=True,type=Path)
    ap.add_argument('--sample-size',type=int,default=64)
    args=ap.parse_args()
    root=args.root.expanduser().resolve(strict=True)
    results=args.results.expanduser().resolve(strict=True)
    if args.sample_size<2:ap.error('sample-size must be >= 2')
    source=root/'repo/src/guard_repr.py'
    if not source.is_file() or source.is_symlink():raise ValueError('Guard source missing/unsafe')
    mod=import_module(source)
    assert (mod.eps_to_repr_spec(0,768).proj_dim,mod.eps_to_repr_spec(0,768).q_bits)==(128,4)
    assert (mod.eps_to_repr_spec(32,768).proj_dim,mod.eps_to_repr_spec(32,768).q_bits)==(320,10)
    failures=[]; count=0
    source_hash=sha(source)
    for dataset,(n_docs,slug) in DATASETS.items():
        raw_path=root/'artifacts'/slug/'intfloat_multilingual-e5-base/stage3/shared/corpus_embeddings_fp32.npy'
        if not raw_path.is_file() or raw_path.is_symlink():raise ValueError(f'Raw absent/unsafe: {raw_path}')
        raw_hash=sha(raw_path)
        raw=np.load(raw_path,mmap_mode='r',allow_pickle=False)
        if raw.shape!=(n_docs,768) or raw.dtype!=np.float32:raise ValueError(f'Raw shape/dtype: {raw_path}')
        indices=np.unique(np.r_[0,n_docs-1,np.random.default_rng(20261123).choice(n_docs,min(args.sample_size,n_docs),replace=False)])
        # Reconstruct with the EXACT same stages used by the prospective runner.
        x=mod.l2_normalize(np.array(raw[indices],dtype=np.float32))
        for seed in SEEDS:
            for eps,dim,bits in CONDITIONS:
                cell=results/f'{dataset}_s{seed}_D{dim}_B{bits}'
                manifest_path=cell/'cell_manifest.json'
                if not manifest_path.is_file():raise ValueError(f'Missing manifest: {manifest_path}')
                m=json.loads(manifest_path.read_text())
                if (m['dataset'],m['seed'],m['dimension'],m['quantization_bits'])!=(dataset,seed,dim,bits):
                    raise ValueError(f'Wrong manifest condition: {cell}')
                if m['input_sha256'][str(source.relative_to(root))]!=source_hash:
                    raise ValueError('Original Guard source hash mismatch')
                if m['input_sha256'][str(raw_path.relative_to(root))]!=raw_hash:
                    raise ValueError(f'Original raw data hash mismatch: {raw_path}')
                w=mod.make_projection_matrix(768,dim,seed)
                matrix_hash=hashlib.sha256(w.tobytes()).hexdigest()
                if m['matrix_sha256']!=matrix_hash:raise ValueError(f'New matrix manifest mismatch: {cell}')
                new=mod.l2_normalize(mod.uniform_quantize(x@w,q_bits=bits,clip=1.0))
                old_path=root/'artifacts'/slug/'intfloat_multilingual-e5-base/stage3'/f'seed{seed}'/f'eps_{eps:02d}'/'guard_embeddings.npy'
                if not old_path.is_file() or old_path.is_symlink():raise ValueError(f'Missing old guard: {old_path}')
                old=np.load(old_path,mmap_mode='r',allow_pickle=False)
                if old.shape!=(n_docs,dim):raise ValueError(f'Old shape mismatch: {old_path}')
                compared=np.array(old[indices],dtype=np.float32)
                if not np.isfinite(compared).all() or not np.isfinite(new).all():raise ValueError('Nonfinite vector')
                diff=np.abs(compared-new)
                max_abs=float(np.max(diff))
                equal=bool(np.array_equal(compared,new))
                allclose=bool(np.allclose(compared,new,atol=1e-6,rtol=1e-6))
                count+=1
                if not allclose:failures.append((dataset,seed,eps))
                print(f'CELL dataset={dataset} seed={seed} eps={eps} dim={dim} bits={bits} sampled={len(indices)} max_abs={max_abs:.9g} exact={int(equal)} close_1e-6={int(allclose)} status={"PASS" if allclose else "MISMATCH"}',flush=True)
    print(f'SAMPLED_VECTOR_CHECK completed={count}/18 mismatches={len(failures)}')
    print('HISTORICAL_AND_ABLATION_FILES_WRITTEN=NO_BY_THIS_SCRIPT')
    print('VECTOR_IDENTITY_STATUS='+('PASS_SAMPLED_18' if not failures else 'REVIEW_MISMATCH'))
    print('LIMITATION=SAMPLED_CORPUS_VECTORS_ONLY_NOT_FULL_IDENTITY_OR_SECURITY_EQUIVALENCE')
    return 0 if not failures else 2

if __name__=='__main__':sys.exit(main())
