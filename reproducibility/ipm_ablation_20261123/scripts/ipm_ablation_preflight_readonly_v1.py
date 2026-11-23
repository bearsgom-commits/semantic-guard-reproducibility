#!/usr/bin/env python3
"""IP&M ablation preflight. Reads existing project only; emits a concise stdout report.
No source/result modifications, network access, or experiment execution.
"""
import argparse
import ast
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

SKIP = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.cache', 'site-packages', 'manuscript_review'}
RELEVANT_NAMES = {'guard_repr.py', 'run_dense_retrieval.py', 'compute_stability.py', 'config_resolved.json',
                  'rankings_top100.jsonl', 'metrics_query.csv', 'queries_ids.json', 'query_ids.json',
                  'doc_ids.json', 'qrels.tsv', 'qrels.csv', 'main.tex'}
RELEVANT_EXT = {'.npy', '.npz'}
DATASET_WORDS = {'fiqa': 'fiqa', 'scifact': 'scifact', 'trec-covid': 'trec-covid', 'trec_covid': 'trec-covid', 'treccovid': 'trec-covid'}

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def detected_ds(path):
    p = str(path).lower()
    for k, v in DATASET_WORDS.items():
        if k in p: return v
    return '?'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--max-files', type=int, default=300000)
    args = ap.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir(): ap.error('root directory not found')
    candidates, configs, errors = [], [], []
    file_count = 0
    for folder, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP and not (Path(folder)/d).is_symlink()]
        for name in names:
            file_count += 1
            if file_count > args.max_files:
                errors.append('SCAN_LIMIT_REACHED'); break
            p = Path(folder) / name
            if p.is_symlink() or not p.is_file(): continue
            if name in RELEVANT_NAMES or (p.suffix.lower() in RELEVANT_EXT and any(w in name.lower() for w in ('embed','corpus','query','guard','raw'))):
                rel = str(p.relative_to(root))
                candidates.append((name, rel, detected_ds(rel)))
                if name == 'config_resolved.json':
                    try:
                        c = json.loads(p.read_text(encoding='utf-8'))
                        configs.append((rel, c))
                    except (OSError, UnicodeError, ValueError) as e: errors.append('CONFIG_READ_ERROR '+rel+' '+type(e).__name__)
        if file_count > args.max_files: break
    print('IPM_ABLATION_PREFLIGHT_READ_ONLY_V1')
    print('ROOT_EXISTS=YES')
    print('FILES_SCANNED='+str(file_count))
    print('CANDIDATES='+str(len(candidates)))
    print('CONFIGS_PARSED='+str(len(configs)))
    print('NAME_COUNTS='+json.dumps(dict(sorted(Counter(n for n,_,_ in candidates).items())),ensure_ascii=False))
    for ds in ['fiqa','scifact','trec-covid']:
        print('DATASET_'+ds.upper().replace('-','_')+'_CANDIDATES='+str(sum(k==ds for _,_,k in candidates)))
    for n in ('guard_repr.py','run_dense_retrieval.py','compute_stability.py'):
        paths = [(rel, root/rel) for nn,rel,_ in candidates if nn==n]
        print('SOURCE_'+n+'='+('NOT_FOUND' if not paths else str(len(paths))+'_FOUND'))
        for rel,p in paths[:3]:
            print('  SOURCE_PATH='+rel+' SHA256='+sha256(p))
    # Identify presence of historical diagonal conditions without assuming config schema.
    diag = {'128x4':0,'320x10':0}
    not_inspected=0
    for rel,c in configs:
        raw = json.dumps(c,ensure_ascii=False).lower()
        # Schemas differ; intentionally do not certify equivalence from textual JSON matches.
        if '128' in raw and ('"4"' in raw or 'q_bits' in raw or 'quantization_bits' in raw): diag['128x4']+=1
        if '320' in raw and ('"10"' in raw or 'q_bits' in raw or 'quantization_bits' in raw): diag['320x10']+=1
    print('DIAGONAL_REUSE_CERTIFIED=NO (requires artifact/embedding IDs, projection and scoring equivalence)')
    print('EXISTING_DIAGONAL_MAPPING=eps0:128x4,eps32:320x10 (historical mapping; not revalidated here)')
    print('NEW_CROSS_CELLS=128x10,320x4 (each 3 datasets x 3 seeds)')
    print('RECOMMENDED_NEXT_GATE=inspect local config/schema and saved embedding provenance; no experiment run')
    print('ERROR_COUNT='+str(len(errors)))
    for err in errors[:10]: print('ERROR='+err)
    print('EXISTING_FILES_MODIFIED=NO_BY_THIS_SCRIPT')

if __name__=='__main__': main()
