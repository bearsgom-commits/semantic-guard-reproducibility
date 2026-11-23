#!/usr/bin/env python3
"""Read-only rank-semantics audit for SciFact pilot (original runner vs pilot tie rule).
Does not change historical files, pilot outputs, or research methods.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024), b''): h.update(block)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',required=True,type=Path)
    ap.add_argument('--pilot',required=True,type=Path)
    a=ap.parse_args()
    root=a.root.expanduser().resolve(strict=True)
    pilot=a.pilot.expanduser().resolve(strict=True)
    if root==pilot or root in pilot.parents: ap.error('Pilot must be outside research root')
    files=[pilot/x for x in ('guard_corpus.npy','guard_queries.npy','top100_row_indices.npy','top100_scores.npy','pilot_manifest.json')]
    files += [root/'artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/query_ids.json',root/'private_data/beir/scifact/qrels/test.tsv']
    if any(not f.is_file() or f.is_symlink() for f in files): ap.error('Missing or linked input')
    before={str(f):digest(f) for f in files}
    d=np.load(files[0],mmap_mode='r',allow_pickle=False)
    q=np.load(files[1],mmap_mode='r',allow_pickle=False)
    indices=np.load(files[2],mmap_mode='r',allow_pickle=False)
    scores=np.load(files[3],mmap_mode='r',allow_pickle=False)
    manifest=json.loads(files[4].read_text(encoding='utf-8'))
    qids=json.loads(files[5].read_text(encoding='utf-8'))
    if (d.shape,q.shape,indices.shape,scores.shape)!=((5183,128),(1109,128),(1109,100),(1109,100)):
        ap.error('Unexpected shapes')
    if manifest.get('seed')!=7 or manifest.get('dimension')!=128 or manifest.get('quantization_bits')!=10:
        ap.error('Unexpected manifest condition')
    for filename in ('guard_corpus.npy','guard_queries.npy','top100_row_indices.npy','top100_scores.npy'):
        expected=manifest.get('output_sha256',{}).get(filename)
        if not expected or digest(pilot/filename)!=expected: ap.error('Manifest hash mismatch for '+filename)
    judged=set()
    with files[6].open(encoding='utf-8') as f:
        next(f)
        for line in f:
            parts=line.rstrip('\n').split('\t')
            if len(parts)>=3: judged.add(parts[0])
    if len(qids)!=1109 or len(judged)!=300 or not judged.issubset(set(map(str,qids))):
        ap.error('Test qrels cohort mismatch')
    # Historical source: separately L2-normalize docs/queries, float32 dot, argpartition, argsort.
    def normalize(x):
        n=np.linalg.norm(x,axis=1,keepdims=True)
        return x/np.clip(n,1e-12,None)
    doc=normalize(np.asarray(d,dtype=np.float32))
    qry=normalize(np.asarray(q,dtype=np.float32))
    stats={name:0 for name in ('all_top100_order','all_top100_set','all_top10_order','all_top10_set','judged_top100_order','judged_top100_set','judged_top10_order','judged_top10_set','pilot_score_drift_queries')}
    max_score_drift=0.0
    for i,(qid,vec) in enumerate(zip(qids,qry)):
        sim=doc@vec
        k=100
        top=np.argpartition(-sim,k-1)[:k]
        top=top[np.argsort(-sim[top])]
        p=np.asarray(indices[i],dtype=np.int64)
        judged_q=str(qid) in judged
        for n in (100,10):
            order=np.array_equal(top[:n],p[:n])
            set_equal=set(top[:n].tolist())==set(p[:n].tolist())
            stats[f'all_top{n}_order']+=int(order)
            stats[f'all_top{n}_set']+=int(set_equal)
            if judged_q:
                stats[f'judged_top{n}_order']+=int(order)
                stats[f'judged_top{n}_set']+=int(set_equal)
        drift=float(np.max(np.abs(sim[p]-np.asarray(scores[i]))))
        max_score_drift=max(max_score_drift,drift)
        stats['pilot_score_drift_queries']+=int(drift>1e-6)
    after={str(f):digest(f) for f in files}
    print('ABLATION_PILOT_RANK_COMPAT_V1')
    print('MODE=READ_ONLY_NO_WRITE')
    print('CELL=scifact_seed7_D128_B10')
    print('COMPARISON=HISTORICAL_ARGPARTITION_ARGSORT_VS_PILOT_LEXSORT')
    print('ALL_QUERIES=1109 TEST_JUDGED_QUERIES=300')
    for k,v in stats.items(): print(f'{k.upper()}={v}')
    print(f'MAX_PILOT_SCORE_DRIFT={max_score_drift:.9g}')
    print('INPUT_HASHES_UNCHANGED='+('YES' if before==after else 'NO'))
    print('STATUS='+('PASS_EXACT' if stats['all_top100_order']==1109 and stats['pilot_score_drift_queries']==0 and before==after else 'REVIEW_DIFFERENCES'))

if __name__=='__main__':main()
