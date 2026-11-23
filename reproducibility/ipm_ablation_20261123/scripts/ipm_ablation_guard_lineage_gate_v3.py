#!/usr/bin/env python3
"""Read-only selection of existing Guard diagonal evidence; NO inference of reuse certification.
Does not write, alter, hash large files, or expose embedding values/document/query IDs.
"""
from __future__ import annotations
import argparse, json, os, re
from pathlib import Path
from collections import defaultdict, Counter

DATASETS=('fiqa','scifact','trec-covid')
SEEDS=(7,13,42)
EPS=(0,32)
NAMES={'config_resolved.json','guard_embeddings.npy','guard_queries.npy','rankings_top100.jsonl','metrics_query.csv','corpus_embeddings_fp32.npy','query_embeddings_fp32.npy'}
SKIP={'.git','.venv','venv','__pycache__','node_modules','.cache','site-packages','manuscript_review'}

def dataset(rel):
    parts=rel.lower().replace('_','-').split('/')
    for d in DATASETS:
        if d in parts: return d
    return None

def seed_ep(rel):
    sl=re.search(r'(?<!\w)seed[_-]?(7|13|42)(?!\d)',rel.lower())
    el=re.search(r'(?<!\w)eps[_-]?0*(0|32)(?!\d)',rel.lower())
    return (int(sl.group(1)) if sl else None,int(el.group(1)) if el else None)

def spec(rel):
    parts=rel.lower().split('/')
    if 'gaussian' in parts or 'raw' in parts or 'baseline' in parts:return None
    if 'guard' not in parts:return None
    ds=dataset(rel)
    seed,eps=seed_ep(rel)
    return (ds,seed,eps) if ds and seed in SEEDS and eps in EPS else None

def npy_shape(path):
    # Numpy mmap reads array header, not full vector contents.
    try:
        import numpy as np
        a=np.load(path,mmap_mode='r',allow_pickle=False)
        return str(tuple(int(i) for i in a.shape))+':'+str(a.dtype)
    except Exception as exc:
        return 'UNREADABLE_'+type(exc).__name__

def config_info(path):
    try:
        x=json.loads(path.read_text(encoding='utf-8'))
        args=x.get('args',{}) if isinstance(x,dict) else {}
        common=x.get('common',{}) if isinstance(x,dict) else {}
        conf=args.get('common',{}) if isinstance(args.get('common',{}),dict) else {}
        mode=args.get('mode','?')
        index=common.get('index',{}) if isinstance(common.get('index',{}),dict) else {}
        return f'mode={mode} index_declared={index.get("type", "?")}'
    except Exception as exc:return 'UNREADABLE_'+type(exc).__name__

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True)
    args=p.parse_args()
    root=Path(args.root).expanduser().resolve()
    if not root.is_dir():p.error('root not found')
    groups=defaultdict(lambda:defaultdict(list)); raw=Counter(); scanned=0; skipped=0
    for base,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink())
        for name in names:
            scanned+=1
            if name not in NAMES:continue
            path=Path(base)/name
            if path.is_symlink() or not path.is_file():continue
            rel=path.relative_to(root).as_posix()
            key=spec(rel)
            if key:groups[key][name].append((path,rel))
            elif name in ('corpus_embeddings_fp32.npy','query_embeddings_fp32.npy') and dataset(rel):raw[(dataset(rel),name)]+=1
            else:skipped+=1
    print('IPM_ABLATION_GUARD_LINEAGE_GATE_V3')
    print('MODE=READ_ONLY_METADATA_ONLY_NO_WRITE_NO_EXPERIMENT')
    print('FILES_SCANNED='+str(scanned))
    print('FILTER=guard stage3 paths only; excludes gaussian/raw/baseline')
    print('NOTE=PATH_FILTER_IS_NOT_EXECUTION_PROVENANCE')
    complete=0; cells_with_duplicates=0
    for ds in DATASETS:
        for seed in SEEDS:
            for ep in EPS:
                key=(ds,seed,ep);g=groups[key]
                cfg=g.get('config_resolved.json',[])
                docs=g.get('guard_embeddings.npy',[])
                queries=g.get('guard_queries.npy',[])
                ranks=g.get('rankings_top100.jsonl',[])
                metrics=g.get('metrics_query.csv',[])
                ok=bool(cfg and docs and queries and ranks and metrics)
                complete+=ok
                duplicates=any(len(g.get(n,[]))>1 for n in ('config_resolved.json','guard_embeddings.npy','guard_queries.npy'))
                cells_with_duplicates+=duplicates
                expected=128 if ep==0 else 320
                shapes_docs=sorted({npy_shape(path) for path,_ in docs})
                shapes_queries=sorted({npy_shape(path) for path,_ in queries})
                print(f'CELL ds={ds} seed={seed} eps={ep} expected_guard_dim={expected} '
                      f'config={len(cfg)} docs={len(docs)} queries={len(queries)} rank={len(ranks)} metric={len(metrics)}')
                print('  DOC_ARRAYS='+json.dumps(shapes_docs))
                print('  QUERY_ARRAYS='+json.dumps(shapes_queries))
                print('  CONFIG_KINDS='+json.dumps(sorted({config_info(path) for path,_ in cfg})))
                # Paths shown for disambiguating original vs cleanroom, not raw IDs/contents.
                for tag,items in (('CONFIG',cfg),('GUARD_DOC',docs),('GUARD_QUERY',queries)):
                    for path,rel in sorted(items,key=lambda z:z[1])[:3]:
                        print('  '+tag+'_PATH='+rel)
                    if len(items)>3:print('  '+tag+'_MORE='+str(len(items)-3))
    print('RAW_INPUT_FILES_BY_DATASET='+json.dumps({d:{'corpus':raw[(d,'corpus_embeddings_fp32.npy')], 'queries':raw[(d,'query_embeddings_fp32.npy')]} for d in DATASETS},sort_keys=True))
    print('CELLS_WITH_ALL_FIVE_ARTIFACT_TYPES='+str(complete)+'/18')
    print('CELLS_WITH_MULTIPLE_PATH_CANDIDATES='+str(cells_with_duplicates)+'/18')
    print('REUSE_CERTIFIED=NO (requires canonical source linkage, identical matrices/input IDs and score cohort)')
    print('ORIGINAL_FILES_MODIFIED=NO_BY_THIS_SCRIPT')

if __name__=='__main__': main()
