#!/usr/bin/env python3
"""Read-only audit of the 36-cell IP&M prospective factorial run.

Does not mutate experiment inputs/outputs. Optionally checks original input hashes.
Writes a new CSV summary only when --report is supplied (must not exist).
"""
import argparse, csv, hashlib, json, math, re, statistics, sys
from collections import defaultdict
from pathlib import Path

EXPECTED = {'fiqa':648, 'scifact':300, 'trec-covid':50}
SEEDS = (7,13,42)
DIMS = (128,320)
BITS = (4,10)
CELL_RE = re.compile(r'^(fiqa|scifact|trec-covid)_s(7|13|42)_D(128|320)_B(4|10)$')

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def qrels_load(path):
    out=defaultdict(dict)
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f,delimiter='\t')
        if not {'query-id','corpus-id','score'} <= set(reader.fieldnames or []):
            raise ValueError(f'qrels header: {path}')
        for row in reader:
            out[str(row['query-id'])][str(row['corpus-id'])]=int(float(row['score']))
    return out

def recall_ndcg(ids, relmap, k=10):
    relevant={d for d,v in relmap.items() if v>0}
    r=(len(set(ids[:k])&relevant)/len(relevant)) if relevant else 0.0
    def dcg(rels):return sum((2**rel-1)/math.log2(i+2) for i,rel in enumerate(rels[:k]))
    actual=dcg([relmap.get(d,0) for d in ids[:k]])
    ideal=dcg(sorted(relmap.values(), reverse=True))
    return r, actual/ideal if ideal else 0.0

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True,help='original semantic-guard root')
    p.add_argument('--results',type=Path,required=True,help='36-cell output directory')
    p.add_argument('--check-input-hashes',action='store_true',help='also hash original input files; could take time')
    p.add_argument('--report',type=Path,help='optional new CSV output; path must not already exist')
    a=p.parse_args()
    if a.report and a.report.exists(): p.error('--report already exists; refusing overwrite')
    results=a.results.expanduser().resolve(strict=True)
    root=a.root.expanduser().resolve(strict=True)
    errors=[]; records=[]; input_claims={}; matrix_claims={}; qrels_cache={}
    dirs={x.name:x for x in results.iterdir() if x.is_dir()}
    expected_names={f'{ds}_s{s}_D{d}_B{b}' for ds in EXPECTED for s in SEEDS for d in DIMS for b in BITS}
    if set(dirs)!=expected_names:
        errors.append(f'cell_folders: missing={sorted(expected_names-set(dirs))} extra={sorted(set(dirs)-expected_names)}')
    for name in sorted(expected_names):
        path=dirs.get(name)
        if not path:continue
        try:
            m=CELL_RE.fullmatch(name)
            ds,s,d,b=m.group(1),int(m.group(2)),int(m.group(3)),int(m.group(4))
            mp=path/'cell_manifest.json'; rp=path/'test_rankings_top100.jsonl'
            manifest=json.loads(mp.read_text(encoding='utf-8'))
            assert manifest['schema']=='ipm_ablation_factorial_v1','schema mismatch'
            assert manifest['status']=='NEW_PROSPECTIVE_EXPERIMENT_NOT_HISTORICAL_REPLAY','status mismatch'
            assert (manifest['dataset'],manifest['seed'],manifest['dimension'],manifest['quantization_bits'])==(ds,s,d,b),'factors mismatch'
            assert manifest['tested_queries']==EXPECTED[ds],'query count mismatch'
            assert manifest['historical_originals_modified'] is False,'original modified claim'
            assert manifest['output_sha256']['test_rankings_top100.jsonl']==sha256(rp),'output hash mismatch'
            matrix_key=(s,d)
            old=matrix_claims.setdefault(matrix_key,manifest['matrix_sha256'])
            assert old==manifest['matrix_sha256'],'projection matrix hash mismatch within seed/dimension'
            for rel,h in manifest['input_sha256'].items():
                assert not Path(rel).is_absolute() and '..' not in Path(rel).parts,'unsafe input path'
                old=input_claims.setdefault(rel,h)
                assert old==h,'input hash inconsistent across manifests'
            qrelrel=f'private_data/beir/{ds}/qrels/test.tsv'
            if ds=='trec-covid': qrelrel='private_data/beir/trec-covid/qrels/test.tsv'
            assert qrelrel in manifest['input_sha256'],'qrels input hash missing'
            if ds not in qrels_cache:qrels_cache[ds]=qrels_load(root/qrelrel)
            qrels=qrels_cache[ds]
            assert len(qrels)==EXPECTED[ds],f'qrels cohort count {len(qrels)}'
            qids=set(); rr=[]; nn=[]; nrows=0
            with rp.open('r',encoding='utf-8') as f:
                for line in f:
                    row=json.loads(line);nrows+=1
                    qid=str(row['qid'])
                    assert qid in qrels,'unknown test query'
                    assert qid not in qids,'duplicate qid'
                    qids.add(qid)
                    ids=row['top_doc_ids']; scores=row['top_scores']
                    assert len(ids)==len(scores)==100,'top100 length'
                    assert len(set(ids))==100,'duplicate rank ids'
                    assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in scores),'nonfinite score'
                    assert all(scores[i]>=scores[i+1]-1e-7 for i in range(99)),'score order'
                    r,n=recall_ndcg(ids,qrels[qid])
                    assert math.isclose(float(row['recall_at_10']),r,abs_tol=1e-9),'recall mismatch'
                    assert math.isclose(float(row['ndcg_at_10']),n,abs_tol=1e-9),'ndcg mismatch'
                    assert int(row['hit_at_10'])==int(any(qrels[qid].get(j,0)>0 for j in ids[:10])),'hit mismatch'
                    assert int(row['top1_rel'])==int(qrels[qid].get(ids[0],0)>0),'top1_rel mismatch'
                    rr.append(r);nn.append(n)
            assert nrows==EXPECTED[ds] and qids==set(qrels),'test cohort incomplete'
            meanr=statistics.mean(rr); meann=statistics.mean(nn)
            assert math.isclose(meanr,manifest['mean_recall_at_10'],abs_tol=1e-10),'recall mean mismatch'
            assert math.isclose(meann,manifest['mean_ndcg_at_10'],abs_tol=1e-10),'ndcg mean mismatch'
            records.append({'dataset':ds,'seed':s,'dimension':d,'bits':b,'test_queries':nrows,'recall10':meanr,'ndcg10':meann})
            print(f'CELL_AUDIT_PASS {name} rows={nrows} recall10={meanr:.8f} ndcg10={meann:.8f}')
        except Exception as e:
            errors.append(f'{name}: {type(e).__name__}: {e}')
            print(f'CELL_AUDIT_FAIL {name}: {type(e).__name__}: {e}')
    if a.check_input_hashes:
        for rel,h in sorted(input_claims.items()):
            f=root/rel
            try:
                assert f.is_file(),'input missing'
                assert sha256(f)==h,'input hash mismatch'
                print(f'ORIGINAL_INPUT_PASS {rel}')
            except Exception as e:
                errors.append(f'input {rel}: {e}')
                print(f'ORIGINAL_INPUT_FAIL {rel}: {e}')
    print(f'CELL_AUDIT_RESULT passed={len(records)}/36 failures={len(errors)} input_claims={len(input_claims)}')
    if errors:
        for e in errors:print('AUDIT_ERROR',e)
        print('AUDIT_STATUS=FAIL')
        return 1
    lookup={(r['dataset'],r['seed'],r['dimension'],r['bits']):r for r in records}
    print('FACTORIAL_DESCRIPTIVE_RESULTS (seed means; not inferential claims)')
    for ds in EXPECTED:
        print(f'DATASET={ds}')
        for d in DIMS:
            for b in BITS:
                z=[lookup[(ds,s,d,b)] for s in SEEDS]
                print(f' CELL D={d} B={b} recall10={statistics.mean(r["recall10"] for r in z):.8f} ndcg10={statistics.mean(r["ndcg10"] for r in z):.8f}')
        for metric in ['recall10','ndcg10']:
            diffs_dim=[];diffs_bits=[];inter=[]
            for s in SEEDS:
                V=lambda d,b:lookup[(ds,s,d,b)][metric]
                diffs_dim.append(((V(320,4)-V(128,4))+(V(320,10)-V(128,10)))/2)
                diffs_bits.append(((V(128,10)-V(128,4))+(V(320,10)-V(320,4)))/2)
                inter.append((V(320,10)-V(320,4))-(V(128,10)-V(128,4)))
            print(f' {metric} dimension_delta={statistics.mean(diffs_dim):+.8f} bit_delta={statistics.mean(diffs_bits):+.8f} interaction_difference_of_differences={statistics.mean(inter):+.8f} seeds=3')
    if a.report:
        # Output creation is opt-in and separate from originals and input results.
        with a.report.open('x',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
        print(f'NEW_REPORT={a.report}')
    print('AUDIT_STATUS=PASS_ALL_36')
    print('ORIGINALS_AND_EXPERIMENT_RESULTS_WRITTEN=NO')
    return 0
if __name__=='__main__':sys.exit(main())
