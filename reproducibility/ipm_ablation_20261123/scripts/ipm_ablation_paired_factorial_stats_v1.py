#!/usr/bin/env python3
"""Read-only paired query-level 2x2 factorial statistics for audited 36-cell IP&M run.

Never writes source, experiment outputs or manuscripts. Optional report directory is
created exclusively outside the research root and outside the results directory.
Fixed seeds 7,13,42; query bootstrap conditions on these seeds, does NOT provide
inference over seeds, encoders, corpora, or datasets. CIs are exploratory.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import numpy as np

DATASETS={'fiqa':648,'scifact':300,'trec-covid':50}
SEEDS=(7,13,42)
FACTORS=((128,4),(128,10),(320,4),(320,10))
METRICS=('recall_at_10','ndcg_at_10')
N_TESTS=len(DATASETS)*len(METRICS)*3


def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def read_cell(results,ds,seed,d,b,verify_hash=True):
    path=results/f'{ds}_s{seed}_D{d}_B{b}'
    if not path.is_dir() or path.is_symlink():
        raise ValueError(f'Invalid cell folder: {path}')
    mp=path/'cell_manifest.json'; rp=path/'test_rankings_top100.jsonl'
    if any(not x.is_file() or x.is_symlink() for x in (mp,rp)):
        raise ValueError(f'Missing or unsafe manifest/ranking: {path}')
    manifest=json.loads(mp.read_text(encoding='utf-8'))
    assert manifest['schema']=='ipm_ablation_factorial_v1'
    assert (manifest['dataset'],manifest['seed'],manifest['dimension'],manifest['quantization_bits'])==(ds,seed,d,b)
    assert manifest['tested_queries']==DATASETS[ds]
    if verify_hash and sha256(rp)!=manifest['output_sha256']['test_rankings_top100.jsonl']:
        raise ValueError(f'Output hash mismatch: {path}')
    rows={}
    with rp.open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            q=str(r['qid'])
            if q in rows: raise ValueError(f'Duplicate qid {q} in {path}')
            vals=np.asarray([float(r[m]) for m in METRICS],dtype=np.float64)
            if not np.all(np.isfinite(vals)) or np.any(vals < -1e-12) or np.any(vals > 1+1e-12):
                raise ValueError(f'Invalid metric values: {path} {q}')
            rows[q]=vals
    if len(rows)!=DATASETS[ds]:
        raise ValueError(f'Query count mismatch: {path} ({len(rows)})')
    means=np.stack(list(rows.values())).mean(axis=0)
    claimed=np.asarray([manifest['mean_recall_at_10'],manifest['mean_ndcg_at_10']])
    if not np.allclose(means,claimed,rtol=0,atol=1e-10):
        raise ValueError(f'Metric averages mismatch: {path}')
    return rows


def make_effects(cells):
    # cells array: [queries, seeds, 4 factor combinations, 2 metrics]
    a,b,c,d=(cells[:,:,j,:] for j in range(4))
    dim=((c-a)+(d-b))/2
    bits=((b-a)+(d-c))/2
    interaction=(d-c)-(b-a)
    return {'dimension_320_minus_128':dim,
            'bits_10_minus_4':bits,
            'interaction_difference_of_differences':interaction}


def bootstrap_fixed_seed_query_effect(effect_qs, rng, samples, alpha, chunk=256):
    # Average the three fixed-seed paired differences within each query,
    # then resample queries (not query-seed rows, which would pseudoreplicate).
    per_query=effect_qs.mean(axis=1)
    n=len(per_query)
    actual=float(per_query.mean())
    boot=np.empty(samples,dtype=np.float64)
    for i in range(0,samples,chunk):
        take=min(chunk,samples-i)
        inds=rng.integers(0,n,size=(take,n))
        boot[i:i+take]=per_query[inds].mean(axis=1)
    lo,hi=np.quantile(boot,[alpha/2,1-alpha/2])
    return actual,float(lo),float(hi)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--results',required=True,type=Path)
    ap.add_argument('--root',required=True,type=Path,help='used ONLY to enforce safe report location')
    ap.add_argument('--bootstrap',type=int,default=5000)
    ap.add_argument('--random-seed',type=int,default=20261123)
    ap.add_argument('--report-dir',type=Path,help='optional NEW output directory outside originals and results')
    args=ap.parse_args()
    if not 1000 <= args.bootstrap <= 200000: ap.error('--bootstrap must be 1000..200000')
    original=args.root.expanduser().resolve(strict=True)
    results=args.results.expanduser().resolve(strict=True)
    if original==results or original in results.parents:
        ap.error('results must be outside the research root')
    report=None
    if args.report_dir:
        report=args.report_dir.expanduser().resolve(strict=False)
        if any(report==p or p in report.parents or report in p.parents for p in (original,results)):
            ap.error('report must be in a separate path from originals/results')
        if report.exists() or report.is_symlink():
            ap.error('report-dir already exists: overwrite prohibited')
    expected={f'{ds}_s{s}_D{d}_B{b}' for ds in DATASETS for s in SEEDS for d,b in FACTORS}
    actual={p.name for p in results.iterdir() if p.is_dir()}
    if actual!=expected:
        raise ValueError(f'Folder set mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}')
    print('METHOD=paired_2x2_query_bootstrap_fixed_seeds')
    print('CONTRAST=dimension_high_minus_low;bits_high_minus_low;interaction_difference_of_differences')
    print(f'BOOTSTRAP_REPS={args.bootstrap} RANDOM_SEED={args.random_seed}')
    print(f'SIMULTANEOUS_FAMILY=18_contrasts BONFERRONI_ALPHA={0.05/N_TESTS:.10f}')
    print('INFERENCE_UNIT=queries;SEEDS=FIXED_7_13_42;NO_SEED_POPULATION_CLAIM')
    rng=np.random.default_rng(args.random_seed)
    records=[]; descriptive=[]
    for ds,n in DATASETS.items():
        per_seed=[]; qids=None
        for s in SEEDS:
            four=[read_cell(results,ds,s,d,b) for d,b in FACTORS]
            ids=set(four[0])
            if any(set(m)!=ids for m in four):
                raise ValueError(f'Factor cohort mismatch: {ds} seed{s}')
            if qids is None:qids=sorted(ids)
            if set(qids)!=ids:
                raise ValueError(f'Seed cohort mismatch: {ds} seed{s}')
            per_seed.append(np.stack([np.stack([m[q] for q in qids]) for m in four],axis=1))
        arr=np.stack(per_seed,axis=1) # q x seed x factor x metric
        assert arr.shape==(n,3,4,2)
        for j,(d,b) in enumerate(FACTORS):
            for metric_i,metric in enumerate(METRICS):
                mean=float(arr[:,:,j,metric_i].mean())
                descriptive.append(dict(dataset=ds,dimension=d,bits=b,metric=metric,mean=mean,queries=n,seeds=3))
            print(f'CELL_MEAN dataset={ds} D={d} B={b} recall10={arr[:,:,j,0].mean():.8f} ndcg10={arr[:,:,j,1].mean():.8f}')
        effects=make_effects(arr)
        for metric_i,metric in enumerate(METRICS):
            for name,mat in effects.items():
                z=mat[:,:,metric_i]
                point,lo95,hi95=bootstrap_fixed_seed_query_effect(z,rng,args.bootstrap,0.05)
                _,lo_sim,hi_sim=bootstrap_fixed_seed_query_effect(z,rng,args.bootstrap,0.05/N_TESTS)
                records.append(dict(dataset=ds,metric=metric,effect=name,estimate=point,
                                    ci95_low=lo95,ci95_high=hi95,
                                    ci_bonferroni_low=lo_sim,ci_bonferroni_high=hi_sim,
                                    query_count=n,seed_count=3,bootstrap_reps=args.bootstrap))
                print(f'EFFECT dataset={ds} metric={metric} name={name} delta={point:+.8f} '
                      f'ci95=[{lo95:+.8f},{hi95:+.8f}] '
                      f'ci_bonf18=[{lo_sim:+.8f},{hi_sim:+.8f}]')
    if report:
        report.mkdir(parents=True,exist_ok=False)
        for name,items in [('cell_means.csv',descriptive),('factorial_effects.csv',records)]:
            with (report/name).open('x',newline='',encoding='utf-8') as f:
                writer=csv.DictWriter(f,fieldnames=list(items[0]));writer.writeheader();writer.writerows(items)
        protocol=dict(description='Fixed-seed within-query paired 2x2 factorial contrasts; percentile query bootstrap',
                      baseline='prospective 36-cell experiment, NOT historical replay',
                      queries_by_dataset=DATASETS, fixed_seeds=SEEDS,factor_order=FACTORS,
                      metrics=METRICS,bootstrap_reps=args.bootstrap,bootstrap_seed=args.random_seed,
                      marginal_dimension='average of (D320-D128) at B4 and B10',
                      marginal_bits='average of (B10-B4) at D128 and D320',
                      interaction='(D320B10-D320B4)-(D128B10-D128B4)',
                      confidence_intervals='percentile bootstrap over judged queries, fixed 3 seeds; 95% nominal and 1-0.05/18 Bonferroni per contrast',
                      caution='Not over seed or dataset sampling; 18 tests family is prespecified for this script only; not DP or security; no causal interpretation outside these factor levels')
        (report/'analysis_protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'NEW_REPORT_DIRECTORY={report}')
    print('EFFECT_RECORDS=18')
    print('STATS_STATUS=PASS_ALL_36')
    print('ORIGINALS_AND_EXPERIMENT_RESULTS_WRITTEN=NO')
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        print(f'STATS_STATUS=FAIL {type(e).__name__}: {e}',file=sys.stderr)
        sys.exit(1)
