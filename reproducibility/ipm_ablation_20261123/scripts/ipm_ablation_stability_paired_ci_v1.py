#!/usr/bin/env python3
"""Read-only paired-query inference for 36-cell stability analysis.

Uses saved stability_query_36.csv (not retrieval rerun). Resamples judged query
IDs, preserves their fixed 3-seed blocks and four matched factor cells.
Reported 45 Bonferroni intervals apply to this 45-contrast family only.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import sys
import numpy as np

DATASETS = {'fiqa':648, 'scifact':300, 'trec-covid':50}
SEEDS = (7,13,42)
FACTORS = ((128,4),(128,10),(320,4),(320,10))
METRICS = ('top1_same','overlap_at_10','kendall_tau_at_50','flip_at_10','stability_score_raw')
EFFECTS = ('dimension_320_minus_128','bits_10_minus_4','interaction_difference_of_differences')
NCONTRASTS = 3*5*3


def within(path, directory):
    return path == directory or directory in path.parents


def read_input(csv_path):
    all_rows={ds:{} for ds in DATASETS}
    with csv_path.open(encoding='utf-8-sig',newline='') as f:
        rdr=csv.DictReader(f)
        required={'dataset','seed','dimension','bits','qid',*METRICS}
        if not required <= set(rdr.fieldnames or []):
            raise ValueError(f'Missing input columns: {sorted(required-set(rdr.fieldnames or []))}')
        num_rows=0
        for r in rdr:
            ds=r['dataset']; seed=int(r['seed']); d=int(r['dimension']); bit=int(r['bits']); qid=str(r['qid'])
            if ds not in DATASETS or seed not in SEEDS or (d,bit) not in FACTORS:
                raise ValueError(f'Unexpected cell at input row {num_rows+2}: {ds} {seed} {d} {bit}')
            key=(seed,d,bit,qid)
            if key in all_rows[ds]:
                raise ValueError(f'Duplicate input record: {ds} {key}')
            v=np.array([float(r[m]) for m in METRICS],dtype=np.float64)
            if not np.all(np.isfinite(v)):
                raise ValueError(f'Non-finite metric: {ds} {key}')
            if np.any(v[[0,1,3,4]] < -1e-10) or np.any(v[[0,1,3,4]] > 1+1e-10) or not -1.0000001 <= v[2] <= 1.0000001:
                raise ValueError(f'Out-of-range metric: {ds} {key}')
            if not np.isclose(v[4],.4*v[0]+.4*v[1]+.2*(1-v[3]),rtol=0,atol=1e-9):
                raise ValueError(f'Stability composite mismatch: {ds} {key}')
            all_rows[ds][key]=v
            num_rows += 1
    if num_rows != 11976: raise ValueError(f'Expected 11976 records; got {num_rows}')
    arrays={}
    for ds,n in DATASETS.items():
        rows=all_rows[ds]
        expected=n*len(SEEDS)*len(FACTORS)
        if len(rows)!=expected: raise ValueError(f'{ds}: expected {expected} records; got {len(rows)}')
        qids_by_cell=[{k[3] for k in rows if k[:3]==(s,d,b)} for s in SEEDS for d,b in FACTORS]
        qids=qids_by_cell[0]
        if len(qids)!=n or any(x!=qids for x in qids_by_cell):
            raise ValueError(f'{ds}: unmatched judged-query cohorts')
        ordered_qids=sorted(qids)
        arr=np.empty((n,3,4,5),dtype=np.float64)
        for si,s in enumerate(SEEDS):
            for ci,(d,b) in enumerate(FACTORS):
                arr[:,si,ci,:]=np.stack([rows[(s,d,b,q)] for q in ordered_qids])
        arrays[ds]=arr
    return arrays


def effects(a):
    x00,x01,x10,x11=(a[:,:,i,:] for i in range(4))
    return (0.5*((x10-x00)+(x11-x01)),
            0.5*((x01-x00)+(x11-x10)),
            (x11-x10)-(x01-x00))


def ci_from_samples(values, rng, repeats, family, chunk=256):
    # average over fixed seeds first, then resample judged query rows
    q=values.mean(axis=1)
    n=len(q)
    point=float(q.mean())
    boot=np.empty(repeats)
    for offset in range(0,repeats,chunk):
        size=min(chunk,repeats-offset)
        index=rng.integers(0,n,size=(size,n))
        boot[offset:offset+size]=q[index].mean(axis=1)
    a,b=np.quantile(boot,[.025,.975])
    c,d=np.quantile(boot,[.025/family,1-.025/family])
    return point,float(a),float(b),float(c),float(d)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,required=True)
    p.add_argument('--root',type=Path,required=True,help='read-only research root, used for safety guard')
    p.add_argument('--results',type=Path,required=True,help='read-only 36-cell results, used for safety guard')
    p.add_argument('--report-dir',type=Path,required=True,help='MUST be new and separate')
    p.add_argument('--bootstrap',type=int,default=5000)
    p.add_argument('--random-seed',type=int,default=20261123)
    args=p.parse_args()
    if not 1000 <= args.bootstrap <= 100000: p.error('--bootstrap must be between 1000 and 100000')
    root=args.root.expanduser().resolve(strict=True)
    results=args.results.expanduser().resolve(strict=True)
    inp=args.input_dir.expanduser().resolve(strict=True)
    output=args.report_dir.expanduser().resolve(strict=False)
    if not inp.is_dir() or not (inp/'stability_query_36.csv').is_file():p.error('Missing stability_query_36.csv')
    if output.exists() or output.is_symlink(): p.error('Output directory already exists (no overwrite allowed)')
    if any(within(output,protected) or within(protected,output) for protected in (root,results,inp)):
        p.error('Report path must be separate from original, experiments and stability inputs')
    arrays=read_input(inp/'stability_query_36.csv')
    rng=np.random.default_rng(args.random_seed)
    records=[]
    for ds,a in arrays.items():
        for metric_i,metric in enumerate(METRICS):
            for name,eff in zip(EFFECTS,effects(a)):
                pt,l,u,bl,bu=ci_from_samples(eff[:,:,metric_i],rng,args.bootstrap,NCONTRASTS)
                records.append(dict(dataset=ds,metric=metric,effect=name,delta=pt,
                                    ci95_low=l,ci95_high=u,ci_bonf45_low=bl,ci_bonf45_high=bu,
                                    bootstrap_reps=args.bootstrap,query_count=DATASETS[ds],fixed_seeds='7,13,42'))
                print(f'EFFECT dataset={ds} metric={metric} name={name} delta={pt:+.8f} '
                      f'ci95=[{l:+.8f},{u:+.8f}] ci_bonf45=[{bl:+.8f},{bu:+.8f}]')
    # cross-check descriptive effects recorded in stability analysis
    descriptor=inp/'stability_factorial_effects_descriptive_15.csv'
    if descriptor.is_file():
        with descriptor.open(encoding='utf-8-sig',newline='') as f:
            stored={(r['dataset'],r['metric'],r['effect']):float(r['delta']) for r in csv.DictReader(f)}
        for r in records:
            k=(r['dataset'],r['metric'],r['effect'])
            if k not in stored or not np.isclose(stored[k],r['delta'],atol=1e-10,rtol=0):
                raise ValueError(f'Previous descriptive effect mismatch: {k}')
        print('DESCRIPTIVE_EFFECT_CROSSCHECK=PASS_45')
    output.mkdir(parents=True,exist_ok=False)
    with (output/'stability_factorial_effects_ci45.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    with (output/'analysis_protocol.json').open('x',encoding='utf-8') as f:
        json.dump({'source':'stability_query_36.csv','family_comparisons':45,'bootstrap_reps':args.bootstrap,
                   'random_seed':args.random_seed,'resampling_unit':'judged qid within dataset',
                   'seeds':'7, 13, 42 fixed and averaged within query',
                   'effect_definitions':{'dimension':'average of D320-D128 at both bit settings',
                                         'bits':'average of B10-B4 at both dimensions',
                                         'interaction':'(D320B10-D320B4)-(D128B10-D128B4)'},
                   'confidence_intervals':'percentile query bootstrap 95% nominal; Bonferroni 45 contrasts',
                   'limitations':['does not sample seeds, datasets, encoders or corpus documents',
                                  'historical RAW ranker and prospective guard run may differ in computational pathway',
                                  'decision flip is hit@10 proxy, not human operational decisions',
                                  'tau_on_union has nonstandard tie treatment',
                                  'no security inference or privacy guarantees',
                                  '45-contrast family does not cover previously reported utility tests']},f,indent=2)
    print(f'EFFECT_RECORDS={len(records)}')
    print('STABILITY_CI_STATUS=PASS_ALL_45')
    print('ORIGINALS_AND_EXPERIMENT_RESULTS_WRITTEN=NO')
    print(f'NEW_REPORT_DIRECTORY={output}')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print(f'STABILITY_CI_STATUS=FAIL {type(e).__name__}: {e}',file=sys.stderr)
        sys.exit(1)
