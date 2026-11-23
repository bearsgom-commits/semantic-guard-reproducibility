#!/usr/bin/env python3
"""IP&M existing diagonal reuse: READ-ONLY local evidence inventory.

Does NOT modify originals, generate embeddings, certify matching computations,
or print vectors/IDs. Prints counts and selected metadata for manual evidence review.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys
from collections import Counter, defaultdict
from pathlib import Path

SKIP={'.git','.venv','venv','node_modules','__pycache__','.cache','site-packages','manuscript_review'}
NAMES={'config_resolved.json','guard_embeddings.npy','guard_queries.npy','corpus_embeddings_fp32.npy','query_embeddings_fp32.npy','query_ids.json','doc_ids.json','rankings_top100.jsonl','metrics_query.csv','guard_repr.py','run_dense_retrieval.py','compute_stability.py'}
DATASETS={'fiqa':('fiqa',),'scifact':('scifact',),'trec-covid':('trec-covid','trec_covid','treccovid')}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def dataset(s):
    s=s.lower()
    for d,names in DATASETS.items():
        if any(n in s for n in names):return d
    return None

def nested(obj,prefix='',depth=0):
    if depth>9:return
    if isinstance(obj,dict):
        for k,v in obj.items():yield from nested(v,prefix+'.'+str(k) if prefix else str(k),depth+1)
    elif isinstance(obj,(int,float,str,bool)) and not isinstance(obj,bool):
        yield prefix,obj

def field(flat,words):
    matches=[(k,v) for k,v in flat if any(k.lower().endswith(w) for w in words)]
    vals=list(dict.fromkeys(str(v) for _,v in matches))
    return ','.join(vals[:4]) if vals else '?'

def parse_int(s):
    try:return int(float(s))
    except (ValueError,TypeError):return None

def path_int(rel,kind):
    regexes={'epsilon':[r'(?:^|[/_\-])eps(?:ilon)?[_=\-]?(\d+)(?:$|[/_\-])'],
             'seed':[r'(?:^|[/_\-])seed[_=\-]?(\d+)(?:$|[/_\-])']}
    for rg in regexes[kind]:
        m=re.search(rg,rel.lower())
        if m:return int(m.group(1))
    return None

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',required=True)
    ap.add_argument('--max-files',type=int,default=100000)
    args=ap.parse_args()
    root=Path(args.root).expanduser().resolve()
    if not root.is_dir():ap.error('root not found')
    files=[];scanned=0;errors=[]
    for base,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink())
        for nm in names:
            scanned+=1
            if scanned>args.max_files:errors.append('SCAN_TRUNCATED');break
            p=Path(base)/nm
            if nm not in NAMES or p.is_symlink() or not p.is_file():continue
            files.append((p, str(p.relative_to(root))))
        if scanned>args.max_files:break
    counts=Counter(p.name for p,_ in files)
    rows=[]
    for p,rel in files:
        if p.name!='config_resolved.json':continue
        try:cfg=json.loads(p.read_text(encoding='utf8'))
        except (OSError,UnicodeError,ValueError) as e:
            errors.append('CONFIG_PARSE_'+type(e).__name__);continue
        flat=list(nested(cfg))
        ds=dataset(rel) or dataset(' '.join(str(v) for k,v in flat if 'dataset' in k.lower()))
        e=parse_int(field(flat,['epsilon','eps']))
        s=parse_int(field(flat,['seed','random_seed']))
        if e is None:e=path_int(rel,'epsilon')
        if s is None:s=path_int(rel,'seed')
        dim=field(flat,['proj_dim','projection_dim','dimension','dim'])
        bits=field(flat,['q_bits','quantization_bits','bits'])
        if ds and e in (0,32) and s in (7,13,42):
            # No raw identifiers/embeddings ever read or printed.
            rows.append({'dataset':ds,'seed':s,'epsilon':e,'dim':dim,'bits':bits,
                         'path':rel,'config_sha256':sha(p),'keys':sorted(k for k,_ in flat)})
    print('IPM_ABLATION_DIAGONAL_REUSE_GATE_V2')
    print('MODE=READ_ONLY_NO_WRITE_NO_EXPERIMENT')
    print('SCANNED='+str(scanned))
    print('FILES='+json.dumps(dict(sorted(counts.items()))))
    print('DIAGONAL_CONFIG_MATCHES='+str(len(rows)))
    groups=defaultdict(list)
    for r in rows:groups[(r['dataset'],r['seed'],r['epsilon'])].append(r)
    print('DIAGONAL_UNIQUE_DATASET_SEED_EPS='+str(len(groups))+'/18')
    for ds in DATASETS:
        for seed in (7,13,42):
            for eps in (0,32):
                rr=groups.get((ds,seed,eps),[])
                print('CELL dataset='+ds+' seed='+str(seed)+' eps='+str(eps)+
                      ' configs='+str(len(rr))+' dim='+','.join(sorted({r['dim'] for r in rr}))+ 
                      ' bits='+','.join(sorted({r['bits'] for r in rr})))
    # Describe but never read the possibly massive arrays.
    for ds in DATASETS:
        for name in ('corpus_embeddings_fp32.npy','query_embeddings_fp32.npy','guard_embeddings.npy','guard_queries.npy','query_ids.json','rankings_top100.jsonl','metrics_query.csv'):
            matches=[(p,rel) for p,rel in files if p.name==name and dataset(rel)==ds]
            print('ARTIFACT dataset='+ds+' name='+name+' count='+str(len(matches)))
    # Small source provenance checks.
    for name in ('guard_repr.py','run_dense_retrieval.py','compute_stability.py'):
        matches=[(p,rel) for p,rel in files if p.name==name]
        print('SOURCE '+name+' copies='+str(len(matches))+' unique_sha256='+str(len({sha(p) for p,_ in matches})))
    if rows:
        first=sorted(rows,key=lambda r:(r['dataset'],r['seed'],r['epsilon'],r['path']))[0]
        print('CONFIG_SAMPLE_KEYS='+json.dumps(first['keys'][:70],ensure_ascii=False))
        print('CONFIG_SAMPLE_RELATIVE_PATH='+first['path'])
        print('CONFIG_SAMPLE_SHA256='+first['config_sha256'])
    print('ERROR_COUNT='+str(len(errors)))
    print('ERROR_TYPES='+json.dumps(dict(Counter(errors))))
    print('DIAGONAL_REUSE_CERTIFIED=NO')
    print('REASON=Requires source raw inputs, exact projection/quantization output equivalence and identical judged-query scoring; config inventory alone is insufficient')
    print('ORIGINALS_MODIFIED=NO_BY_THIS_SCRIPT')

if __name__=='__main__':main()
