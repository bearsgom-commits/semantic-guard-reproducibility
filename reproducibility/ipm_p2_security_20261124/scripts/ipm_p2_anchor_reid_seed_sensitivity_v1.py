#!/usr/bin/env python3
"""Read-only, bounded T1b anchor-assisted ReID seed 13/42 sensitivity test.

Reuses SAME SciFact 5000-row cohort, 256 anchors, 256 targets, 4744
candidates and fixed ridge alpha=1 as previously frozen seed-7 experiment.
No retrieval, no historical attack replay, no private row-level export beyond
new local output. Writes one private CSV per seed and aggregate summary.
This tests projection-seed sensitivity ONLY, not independent documents.
Python >=3.10; requires numpy.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

GUARD_SHA="8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d"
RAW_SHA="f332ab059f57d4e274ff5e7b513ee19d27104a3f47c7bb98f0b0f93d643716d4"
ANCHORS=256
TARGETS=256
SELECTION_SEED=20261124
RIDGE_ALPHA=1.0
CELLS=((128,4),(128,10),(320,4),(320,10))
SEEDS=(13,42)
FIELDS=["dataset","seed","dimension","bits","attacker","alpha",
        "anchor_count","target_count","candidate_count","top1_hits",
        "top1_rate","top5_hits","top5_rate","random_top1_reference",
        "random_top5_reference","projection_matrix_sha256_evaluator_only",
        "true_target_guard_sha256","candidate_prediction_sha256"]

def hashfile(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
    return h.hexdigest()

def hasharray(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

def readjson(path):
    with path.open("r",encoding="utf-8") as f:return json.load(f)

def ensure(ok,msg):
    if not ok:raise ValueError(msg)

def norm(a):
    x=np.asarray(a,dtype=np.float32)
    n=np.linalg.norm(x,axis=1,keepdims=True)
    ensure(bool(np.isfinite(x).all()) and bool((n>1e-12).all()),"nonfinite or zero-norm vector")
    return (x/n).astype(np.float32)

def guard(a,w,bits):
    x=norm(a)@w
    levels=(2**bits)-1
    x=np.clip(x,-1.0,1.0)
    q=(np.round((x+1.0)*(levels/2.0))*(2.0/levels)-1.0).astype(np.float32)
    return norm(q)

def index_sha(indices):
    return hasharray(np.asarray(indices,dtype="<i8"))

def load_and_verify(root,pilot,base):
    src=root/"repo/src/guard_repr.py"
    rawfile=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_embeddings_fp32.npy"
    idfile=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_doc_ids.json"
    cohortfile=pilot/"cohort_indices.json"
    runfile=pilot/"run_manifest.json"
    older=base/"reid_manifest.json"
    ensure(hashfile(src)==GUARD_SHA,"source guard hash failed")
    ensure(hashfile(rawfile)==RAW_SHA,"source E5 hash failed")
    rm=readjson(runfile)
    ensure(rm.get("dataset")=="scifact" and rm.get("seed")==7 and
           rm.get("shared_cohort_across_cells") is True and
           rm.get("schema")=="ipm_p2_security_pilot_manifest_v1",
           "original P2 cohort manifest mismatch")
    ensure(hashfile(cohortfile)==rm.get("cohort_indices_sha256"),
           "original cohort SHA mismatch")
    for name,path in (("guard_repr.py",src),
                      ("corpus_embeddings_fp32.npy",rawfile),
                      ("corpus_doc_ids.json",idfile)):
        ensure(hashfile(path)==rm.get("input_sha256",{}).get(name),
               "input changed from prior pilot: "+name)
    old=readjson(older)
    ensure(old.get("status")=="PASS_4_PROSPECTIVE_CELLS" and
           old.get("schema")=="ipm_p2_anchor_assisted_reid_v1" and
           old.get("dataset")=="scifact" and old.get("seed")==7,
           "seed7 reference manifest mismatch")
    ensure(hashfile(base/"reid_4cell_summary.csv")==old.get("output_sha256",{}).get("reid_4cell_summary.csv"),
           "seed7 summary SHA mismatch")
    ensure(hashfile(base/"target_hits_PRIVATE.csv")==old.get("output_sha256",{}).get("target_hits_PRIVATE.csv"),
           "seed7 private target evidence SHA mismatch")
    coh=readjson(cohortfile)
    ensure(coh.get("sample_size_per_class")==2500 and coh.get("sampling_seed")==20260822,
           "cohort sampling configuration changed")
    m=np.asarray(coh["member_row_indices"],dtype=np.int64)
    n=np.asarray(coh["nonmember_row_indices"],dtype=np.int64)
    union=np.sort(np.concatenate((m,n)))
    ensure(len(m)==len(n)==2500 and len(set(union.tolist()))==5000
           and union.min()>=0 and union.max()<5183,"bad cohort")
    perm=np.random.default_rng(SELECTION_SEED).permutation(union)
    anchors=np.asarray(perm[:ANCHORS],dtype=np.int64)
    targets=np.asarray(perm[ANCHORS:ANCHORS+TARGETS],dtype=np.int64)
    anchorset=set(anchors.tolist())
    candidates=np.asarray([i for i in union if int(i) not in anchorset],dtype=np.int64)
    ensure(len(candidates)==4744 and not(anchorset&set(targets.tolist()))
           and set(targets.tolist())<=set(candidates.tolist()),"candidate leakage")
    oldsha=old.get("selection_sha256",{})
    for key,v in (("anchors",anchors),("targets",targets),("candidates",candidates)):
        ensure(index_sha(v)==oldsha.get(key),"selection changed from seed7 "+key)
    raw=np.load(rawfile,mmap_mode="r",allow_pickle=False)
    ids=readjson(idfile)
    ensure(raw.shape==(5183,768) and raw.dtype==np.float32
           and len(ids)==len(set(map(str,ids)))==5183,"raw/IDs shape mismatch")
    return raw,anchors,targets,candidates,{"guard":hashfile(src),
        "raw":hashfile(rawfile),"ids":hashfile(idfile),
        "cohort":hashfile(cohortfile),"seed7_manifest":hashfile(older)},oldsha

def run():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True,type=Path)
    ap.add_argument("--pilot",required=True,type=Path)
    ap.add_argument("--seed7",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args()
    root=a.root.expanduser().resolve(strict=True)
    pilot=a.pilot.expanduser().resolve(strict=True)
    seed7=a.seed7.expanduser().resolve(strict=True)
    out=a.out.expanduser().resolve(strict=False)
    ensure(not out.exists() and not out.is_symlink(),"output already exists")
    ensure(not any(out==p or p in out.parents or out in p.parents for p in (root,pilot,seed7)),
           "output must be new and disjoint from all inputs")
    raw,anchors,targets,candidates,insha,selsha=load_and_verify(root,pilot,seed7)
    # Same math and float types as initial seed7 script.
    xa0=np.asarray(raw[anchors],dtype=np.float64)
    xc0=np.asarray(raw[candidates],dtype=np.float64)
    xmu=xa0.mean(axis=0)
    xa=xa0-xmu
    gram=xa@xa.T
    gram.flat[::len(gram)+1]+=RIDGE_ALPHA
    chol=np.linalg.cholesky(gram)
    kc=(xc0-xmu)@xa.T
    pos={int(v):i for i,v in enumerate(candidates)}
    targets_pos=np.asarray([pos[int(v)] for v in targets],dtype=np.int64)
    results=[]
    private={}
    for seed in SEEDS:
        private[seed]={}
        for dim in (128,320):
            rng=np.random.default_rng(seed)
            w=rng.normal(0.0,1.0,size=(768,dim)).astype(np.float32)
            w/=np.sqrt(float(dim))
            for bits in (4,10):
                key=f"D{dim}_B{bits}"
                ya=guard(np.asarray(raw[anchors],dtype=np.float32),w,bits)
                yt=guard(np.asarray(raw[targets],dtype=np.float32),w,bits)
                y=np.asarray(ya,dtype=np.float64)
                mu=y.mean(axis=0)
                coef=np.linalg.solve(chol.T,np.linalg.solve(chol,y-mu))
                yhat=norm((kc@coef+mu).astype(np.float32))
                sims=np.asarray(yt@yhat.T,dtype=np.float32)
                ensure(sims.shape==(256,4744) and bool(np.isfinite(sims).all()),
                       "unexpected cosine score output")
                hits5=np.argsort(-sims,axis=1,kind="stable")[:,:5]
                h1=(hits5[:,0]==targets_pos).astype(np.int8)
                h5=np.any(hits5==targets_pos[:,None],axis=1).astype(np.int8)
                private[seed][key]=(h1,h5)
                result={
                    "dataset":"scifact","seed":seed,"dimension":dim,"bits":bits,
                    "attacker":"T1b_256_anchor_unknown_matrix","alpha":RIDGE_ALPHA,
                    "anchor_count":ANCHORS,"target_count":TARGETS,"candidate_count":4744,
                    "top1_hits":int(h1.sum()),"top1_rate":float(h1.mean()),
                    "top5_hits":int(h5.sum()),"top5_rate":float(h5.mean()),
                    "random_top1_reference":1/4744,"random_top5_reference":5/4744,
                    "projection_matrix_sha256_evaluator_only":hasharray(w),
                    "true_target_guard_sha256":hasharray(yt),
                    "candidate_prediction_sha256":hasharray(yhat)}
                results.append(result)
                print(f"REID_SEED={seed} CELL={key} TOP1={int(h1.sum())}/256 "
                      f"TOP5={int(h5.sum())}/256",flush=True)
    # Guard source + raw + cohort + reference seed-7 result still intact.
    again,aa,tt,cc,rehashed,_=load_and_verify(root,pilot,seed7)
    ensure(insha==rehashed and np.array_equal(anchors,aa) and
           np.array_equal(targets,tt) and np.array_equal(candidates,cc),
           "source change detected during sensitivity test")
    out.mkdir(parents=True,exist_ok=False)
    summary=out/"reid_seed13_42_8cell_summary.csv"
    with summary.open("x",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(results)
    rowhashes={}
    for seed in SEEDS:
        p=out/f"target_hits_seed{seed}_PRIVATE.csv"
        with p.open("x",encoding="utf-8",newline="") as f:
            w=csv.writer(f)
            w.writerow(["target_private_position"]+
                [f"{key}_{metric}" for key in
                 ("D128_B4","D128_B10","D320_B4","D320_B10")
                 for metric in ("top1","top5")])
            for i in range(TARGETS):
                row=[i]
                for key in ("D128_B4","D128_B10","D320_B4","D320_B10"):
                    h1,h5=private[seed][key]
                    row.extend((int(h1[i]),int(h5[i])))
                w.writerow(row)
        rowhashes[p.name]=hashfile(p)
    manifest={
       "schema":"ipm_p2_anchor_reid_seed_sensitivity_v1",
       "status":"PASS_8_ADDITIONAL_CELLS",
       "created_at_utc":datetime.now(timezone.utc).isoformat(),
       "dataset":"scifact","new_seeds":list(SEEDS),
       "seed7_reference":True,"fixed_anchors_targets_candidates_sha256":selsha,
       "method":"identical to T1b seed7 script: dual ridge alpha=1, 256 paired anchors, 256 disjoint target rows, 4744 raw candidate refs",
       "same_target_ids_across_seeds":True,
       "results":results,"input_sha256":insha,
       "output_sha256":{summary.name:hashfile(summary),**rowhashes},
       "retrieval_executed":False,"historical_attacks_executed":False,
       "originals_modified":False,
       "scope":"projection seed sensitivity only; not dataset generality or independent target resampling"}
    (out/"seed_sensitivity_manifest.json").write_text(
       json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("P2_T1B_SEED_SENSITIVITY=PASS_8")
    print("RETRIEVAL_EXECUTED=NO")
    print("ORIGINALS_MODIFIED=NO")
    print("OUTPUT=",out)

if __name__=="__main__":
    try:run()
    except Exception as e:
        print(f"P2_T1B_SEED_SENSITIVITY_ERROR={type(e).__name__}: {e}",file=sys.stderr)
        sys.exit(2)
