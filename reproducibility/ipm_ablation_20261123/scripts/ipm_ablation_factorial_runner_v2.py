#!/usr/bin/env python3
"""IP&M prospective 2x2 Guard ablation: isolated, fail-closed runner.

NO modification of historical source, data, results, or manuscripts.
Use --dataset scifact --seed 7 --dimension 128 --bits 10 for one-cell validation.
Only after reviewing results, use --all for the 36 condition batch.
Every cell writes to an exclusive new directory OUTSIDE the research root.

This is NOT a historical execution replay, and does not infer a new epsilon.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import traceback
from datetime import datetime, timezone
import numpy as np

GUARD_SHA = '8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d'
RETRIEVAL_SHA = '09ecb4d855417189f9dca36dcf67913ac1b08cb2051f7a09bbfb8b7f5f16a3a5'
DATASETS = {'fiqa': (57638,6648,648,'fiqa'), 'scifact': (5183,1109,300,'scifact'),
            'trec-covid': (171332,50,50,'trec_covid')}
SEEDS=(7,13,42)
DIMS=(128,320)
BITS=(4,10)
TOPK=100

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()

def check_path(p):
    if not p.is_file() or p.is_symlink(): raise ValueError(f'missing/unsafe input file: {p}')
    return p

def read_ids(p):
    x=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(x,list): raise ValueError(f'Expected ordered ID list: {p}')
    x=[str(v) for v in x]
    if len(x)!=len(set(x)): raise ValueError(f'Duplicate IDs: {p}')
    return x

def load_qrels(p):
    data={}
    with p.open(encoding='utf-8', newline='') as f:
        r=csv.DictReader(f,delimiter='\t')
        if not {'query-id','corpus-id','score'}<=set(r.fieldnames or []):
            raise ValueError('Unexpected qrels headers')
        for x in r:
            q,d=str(x['query-id']),str(x['corpus-id'])
            rel=int(float(x['score']))
            if d in data.setdefault(q,{}): raise ValueError('Duplicate qrel pair')
            data[q][d]=rel
    return data

def dcg(rels,k=10):
    return sum((2**r-1)/np.log2(i+2) for i,r in enumerate(rels[:k]))

def metrics(pred, rels):
    relevant={d for d,v in rels.items() if v>0}
    recall=len(set(pred[:10])&relevant)/len(relevant) if relevant else 0.0
    ideal=dcg(sorted(rels.values(),reverse=True),10)
    ndcg=dcg([rels.get(d,0) for d in pred[:10]],10)/ideal if ideal else 0.0
    return float(recall),float(ndcg)

def load_original_guard(source):
    spec=importlib.util.spec_from_file_location('original_guard_immutable',source)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    if (mod.eps_to_repr_spec(0,768).proj_dim, mod.eps_to_repr_spec(0,768).q_bits)!=(128,4):
        raise ValueError('Original Guard eps0 mapping changed')
    if (mod.eps_to_repr_spec(32,768).proj_dim, mod.eps_to_repr_spec(32,768).q_bits)!=(320,10):
        raise ValueError('Original Guard eps32 mapping changed')
    return mod

def transform(x, w, bits, mod, block=8192):
    out=np.empty((x.shape[0],w.shape[1]),dtype=np.float32)
    for start in range(0,len(x),block):
        z=mod.l2_normalize(np.asarray(x[start:start+block],dtype=np.float32))
        z=z@w
        z=mod.uniform_quantize(z,q_bits=bits,clip=1.0)
        out[start:start+len(z)]=mod.l2_normalize(z)
    return out

def safe_out(root,out):
    r=root.resolve(strict=True)
    p=out.expanduser().resolve(strict=False)
    if p==r or r in p.parents or p in r.parents:
        raise ValueError('Output MUST be strictly outside research root')
    if p.exists() or p.is_symlink(): raise ValueError(f'Output already exists: {p}')
    return p

def run_cell(root,out,ds,seed,dim,bits):
    n_docs,n_queries,n_test,slug=DATASETS[ds]
    source=check_path(root/'repo/src/guard_repr.py')
    retrieval=check_path(root/'repo/src/stage3/run_dense_retrieval.py')
    base=root/'artifacts'/slug/'intfloat_multilingual-e5-base/stage3/shared'
    doc_p=check_path(base/'corpus_embeddings_fp32.npy')
    qry_p=check_path(base/'query_embeddings_fp32.npy')
    did_p=check_path(base/'corpus_doc_ids.json')
    qid_p=check_path(base/'query_ids.json')
    qrel_slug = 'trec-covid' if ds == 'trec-covid' else slug
    qrel_p=check_path(root/'private_data/beir'/qrel_slug/'qrels/test.tsv')
    inputs=[source,retrieval,doc_p,qry_p,did_p,qid_p,qrel_p]
    hashes={str(p.relative_to(root)):sha(p) for p in inputs}
    if hashes[str(source.relative_to(root))]!=GUARD_SHA: raise ValueError('Original Guard SHA mismatch')
    if hashes[str(retrieval.relative_to(root))]!=RETRIEVAL_SHA: raise ValueError('Original retrieval SHA mismatch')
    docs=np.load(doc_p,mmap_mode='r',allow_pickle=False)
    queries=np.load(qry_p,mmap_mode='r',allow_pickle=False)
    if docs.shape!=(n_docs,768) or queries.shape!=(n_queries,768):
        raise ValueError(f'Unexpected raw input shapes {docs.shape}/{queries.shape}')
    if docs.dtype!=np.float32 or queries.dtype!=np.float32: raise ValueError('Raw dtype mismatch')
    dids=read_ids(did_p); qids=read_ids(qid_p)
    if len(dids)!=n_docs or len(qids)!=n_queries: raise ValueError('ID/vector length mismatch')
    qrels=load_qrels(qrel_p)
    if len(qrels)!=n_test or not set(qrels)<=set(qids): raise ValueError('Unexpected test qrels qids')
    if not {d for rr in qrels.values() for d in rr}<=set(dids): raise ValueError('Unknown qrels doc ID')
    mod=load_original_guard(source)
    w=mod.make_projection_matrix(768,dim,seed)
    # Identical Guard transform functions & per-dimension seeded projection generator;
    # D and bits are explicitly crossed; no modifications to historical epsilon mapping.
    guarded_docs=transform(docs,w,bits,mod)
    # Only judged test queries are ranked/evaluated. Historical method's vector math and
    # argpartition->argsort are unchanged; no fabricated epsilon labels.
    qi_by_id={qid:i for i,qid in enumerate(qids)}
    judged_qids=[qid for qid in qids if qid in qrels]
    selected=np.array([qi_by_id[q] for q in judged_qids],dtype=np.int64)
    guarded_queries=transform(queries[selected],w,bits,mod)
    norm_dev=max(float(np.max(np.abs(np.linalg.norm(guarded_docs,axis=1)-1))),
                 float(np.max(np.abs(np.linalg.norm(guarded_queries,axis=1)-1))))
    if not np.isfinite(guarded_docs).all() or not np.isfinite(guarded_queries).all() or norm_dev>2e-5:
        raise ValueError('Invalid Guard output/norm')
    rows=[]
    for qi,qid in enumerate(judged_qids):
        sims=guarded_docs @ guarded_queries[qi]
        k=min(TOPK,len(sims))
        top=np.argpartition(-sims,k-1)[:k]
        top=top[np.argsort(-sims[top])]
        pred=[dids[int(j)] for j in top]
        recall,ndcg=metrics(pred,qrels[qid])
        if not (0<=recall<=1 and 0<=ndcg<=1.0000001):
            raise ValueError('Invalid retrieval metric')
        rows.append({'qid':qid,'top_doc_ids':pred,'top_scores':[float(sims[j]) for j in top],
                     'recall_at_10':recall,'ndcg_at_10':ndcg,
                     'hit_at_10':int(any(qrels[qid].get(d,0)>0 for d in pred[:10])),
                     'top1_rel':int(qrels[qid].get(pred[0],0)>0)})
    if len(rows)!=n_test:raise ValueError('Test query count mismatch')
    # Verify originals before making any output directory.
    if any(sha(root/k)!=v for k,v in hashes.items()): raise RuntimeError('Input SHA changed during run')
    out.mkdir(parents=True,exist_ok=False)
    try:
        ranked=out/'test_rankings_top100.jsonl'
        with ranked.open('x',encoding='utf-8') as f:
            for row in rows: f.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n')
        report={
            'schema':'ipm_ablation_factorial_v1',
            'status':'NEW_PROSPECTIVE_EXPERIMENT_NOT_HISTORICAL_REPLAY',
            'dataset':ds,'seed':seed,'dimension':dim,'quantization_bits':bits,
            'epsilon_label':'NONE_OFF_DIAGONAL' if (dim,bits) not in ((128,4),(320,10)) else 'REFERENCE_CONFIGURATION_ONLY',
            'cohort':'BEIR test qrels judged queries only',
            'tested_queries':len(rows),'corpus_documents':len(dids),
            'mean_recall_at_10':float(np.mean([x['recall_at_10'] for x in rows])),
            'mean_ndcg_at_10':float(np.mean([x['ndcg_at_10'] for x in rows])),
            'max_l2_norm_deviation':norm_dev,
            'scoring':'existing recall@10 / DCG 2^rel-1 / nDCG@10; test-only mean',
            'ranking':'existing source argpartition(-sims,k-1) then argsort(-sims[top]); float32 dot',
            'guard':'existing seeded Gaussian projection, L2-normalize, uniform quantization clip=1.0, L2-normalize',
            'matrix_sha256':hashlib.sha256(w.tobytes()).hexdigest(),
            'input_sha256':hashes,'output_sha256':{'test_rankings_top100.jsonl':sha(ranked)},
            'python':sys.version.split()[0],'numpy':np.__version__,
            'generated_at_utc':datetime.now(timezone.utc).isoformat(),
            'historical_originals_modified':False,
            'limitations':['Not a security evaluation','Stability/flip against raw baseline not computed here',
                           'No benchmark performance conclusion before all cells and paired analysis',
                           'Original source ranker did not specify a deterministic tie-break']
        }
        with (out/'cell_manifest.json').open('x',encoding='utf-8') as f:
            json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
        if any(sha(root/k)!=v for k,v in hashes.items()):raise RuntimeError('CRITICAL: input changed after run')
    except Exception:
        # Do not delete or overwrite even partial outputs; preserve for audit.
        print(f'CELL_PARTIAL_OUTPUT_PRESERVED={out}',file=sys.stderr)
        raise
    print(f'CELL_PASS dataset={ds} seed={seed} D={dim} B={bits} test_queries={n_test} '
          f'recall10={report["mean_recall_at_10"]:.8f} ndcg10={report["mean_ndcg_at_10"]:.8f}')
    print('ORIGINAL_INPUT_HASHES_UNCHANGED=YES')
    print(f'OUTPUT={out}')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--one',action='store_true',help='One specified cell, safe first test')
    mode.add_argument('--all',action='store_true',help='All 36 cells, NOT intended before --one review')
    mode.add_argument('--resume',action='store_true',help='Validate 24 existing cells, then run only missing cells in existing batch')
    p.add_argument('--dataset',choices=list(DATASETS),default='scifact')
    p.add_argument('--seed',choices=SEEDS,type=int,default=7)
    p.add_argument('--dimension',choices=DIMS,type=int,default=128)
    p.add_argument('--bits',choices=BITS,type=int,default=10)
    a=p.parse_args()
    root=a.root.expanduser().resolve(strict=True)
    out=(a.out.expanduser().resolve(strict=True) if a.resume else safe_out(root,a.out))
    if a.resume and (not out.is_dir() or out.is_symlink() or out == root or root in out.parents or out in root.parents):
        p.error('Resume requires an existing safe directory outside research root')
    if not root.is_dir(): p.error('root is not a directory')
    cells=([(a.dataset,a.seed,a.dimension,a.bits)] if a.one else
           [(ds,seed,dim,bits) for ds in DATASETS for seed in SEEDS for dim in DIMS for bits in BITS])
    if a.one:
        run_cell(root,out,*cells[0]); print('RUN_STATUS=PASS_ONE_CELL')
    elif a.resume:
        expected={(ds,seed,dim,bits) for ds in DATASETS for seed in SEEDS for dim in DIMS for bits in BITS}
        completed=set()
        for child in out.iterdir():
            if not child.is_dir():
                continue
            m=child/'cell_manifest.json'
            if not m.is_file() or m.is_symlink():
                raise ValueError(f'Existing cell without safe manifest: {child}')
            report=json.loads(m.read_text(encoding='utf-8'))
            key=(report.get('dataset'),report.get('seed'),report.get('dimension'),report.get('quantization_bits'))
            if key not in expected or child.name!=f'{key[0]}_s{key[1]}_D{key[2]}_B{key[3]}':
                raise ValueError(f'Unexpected existing cell: {child}')
            if key in completed:raise ValueError(f'Duplicate existing cell: {child}')
            if report.get('schema')!='ipm_ablation_factorial_v1' or report.get('tested_queries')!=DATASETS[key[0]][2]:
                raise ValueError(f'Invalid manifest: {m}')
            ranked=child/'test_rankings_top100.jsonl'
            if not ranked.is_file() or ranked.is_symlink() or sha(ranked)!=report.get('output_sha256',{}).get('test_rankings_top100.jsonl'):
                raise ValueError(f'Ranking hash mismatch: {child}')
            # Validate original input hashes against the manifest recorded for this cell.
            for rel,h in report.get('input_sha256',{}).items():
                f=root/rel
                if not f.is_file() or f.is_symlink() or sha(f)!=h:raise ValueError(f'Original input hash mismatch: {f}')
            completed.add(key)
        print(f'RESUME_VALIDATED_EXISTING={len(completed)}/36',flush=True)
        if len(completed)!=24 or {key[0] for key in completed}!={'fiqa','scifact'}:
            raise ValueError('Expected exactly 24 completed FiQA/SciFact cells; refusing ambiguous resume')
        pending=[key for key in [(ds,seed,dim,bits) for ds in DATASETS for seed in SEEDS for dim in DIMS for bits in BITS] if key not in completed]
        print(f'RESUME_PENDING={len(pending)}',flush=True)
        failures=[]
        for i,(ds,seed,dim,bits) in enumerate(pending,1):
            cell_out=out/f'{ds}_s{seed}_D{dim}_B{bits}'
            print(f'RESUME_CELL={i}/{len(pending)} {ds} s{seed} D{dim} B{bits}',flush=True)
            try:run_cell(root,cell_out,ds,seed,dim,bits)
            except Exception as e:
                failures.append(f'{ds}_s{seed}_D{dim}_B{bits}:{type(e).__name__}:{e}')
                print(f'CELL_FAILED={failures[-1]}',flush=True)
                break
        total=len([x for x in out.iterdir() if x.is_dir() and (x/'cell_manifest.json').exists()])
        print(f'BATCH_RESULT completed={total}/36 failures={len(failures)}')
        if failures:return 2
        if total!=36:raise ValueError('Not all 36 cells present')
        print('BATCH_STATUS=PASS_ALL_36')
    else:
        # Out is a brand-new batch directory. Do not replace an existing batch.
        out.mkdir(parents=True,exist_ok=False)
        print(f'BATCH_START=36 output={out}',flush=True)
        failures=[]
        for i,(ds,seed,dim,bits) in enumerate(cells,1):
            cell_out=out/f'{ds}_s{seed}_D{dim}_B{bits}'
            print(f'BATCH_CELL={i}/36 {ds} s{seed} D{dim} B{bits}',flush=True)
            try: run_cell(root,cell_out,ds,seed,dim,bits)
            except Exception as e:
                failures.append(f'{ds}_s{seed}_D{dim}_B{bits}:{type(e).__name__}:{str(e)}')
                print(f'CELL_FAILED={failures[-1]}',flush=True)
                # Fail closed: no skip and no success claim for incomplete batch.
                break
        print(f'BATCH_RESULT completed={len([x for x in out.iterdir() if (x/"cell_manifest.json").exists()])}/36 failures={len(failures)}')
        if failures: return 2
        print('BATCH_STATUS=PASS_ALL_36')
    return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e:
        print(f'RUN_STATUS=FAIL ERROR={type(e).__name__}: {e}',file=sys.stderr)
        raise SystemExit(2)
