#!/usr/bin/env python3
"""Prospective SciFact seed-7 four-cell anchor-assisted ReID experiment.

Attack T1b: attacker knows identified E5 raw candidate vectors and exactly 256
matched raw-Guard anchor pairs, but NOT the true projection matrix. Ridge
aligns raw E5 -> guarded space from anchors only. Target Guard rows are held
out and matched to 4744 independently predicted candidate references.

Read-only inputs; creates a new output directory outside the research tree.
Never modifies the canonical 36-cell experiment, Guard implementation, E5
embeddings or historical attack outputs. Python 3.10 compatible.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

EXPECTED_GUARD="8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d"
EXPECTED_RAW="f332ab059f57d4e274ff5e7b513ee19d27104a3f47c7bb98f0b0f93d643716d4"
MATRIX_SHA={128:"42fea5124bbe699d6dbd610629ee580e79522e740b19d2ac0577df3fe9b5256d",
            320:"3495b4a51026b118d91690fcc78a2ff7720a023aa4fa7411a7fcb70b890ced41"}
ANCHOR_COUNT=256
TARGET_COUNT=256
SELECTION_SEED=20261124
ALPHA=1.0

def filehash(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(4*1024*1024),b""):h.update(block)
    return h.hexdigest()

def bytehash(arr):
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()

def loadjson(path):
    with path.open("r",encoding="utf-8") as f:return json.load(f)

def check(condition,message):
    if not condition:raise ValueError(message)

def normalize(rows):
    x=np.asarray(rows,dtype=np.float32)
    norm=np.linalg.norm(x,axis=1,keepdims=True)
    check(bool(np.isfinite(x).all()) and bool((norm>1e-12).all()),"nonfinite/zero norm encountered")
    return (x/norm).astype(np.float32)

def guard_transform(raw,w,bits):
    # Same transform sequence as original Guard:
    # l2_normalize(raw) @ W -> uniform quantize clip=1 -> l2_normalize.
    x=normalize(raw) @ w
    qlevels=(2**bits)-1
    x=np.clip(x,-1.0,1.0)
    xhat=(np.round((x+1.0)*(qlevels/2.0))*(2.0/qlevels)-1.0).astype(np.float32)
    return normalize(xhat)

def sha_list(indices):
    return bytehash(np.asarray(indices,dtype="<i8"))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True,type=Path)
    ap.add_argument("--pilot",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    root=args.root.expanduser().resolve(strict=True)
    pilot=args.pilot.expanduser().resolve(strict=True)
    out=args.out.expanduser().resolve(strict=False)
    check(not out.exists() and not out.is_symlink(),"output path exists")
    check(out!=root and root not in out.parents and out!=pilot and pilot not in out.parents,
          "output must be new and outside original inputs")
    original_guard=root/"repo/src/guard_repr.py"
    rawpath=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_embeddings_fp32.npy"
    idpath=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_doc_ids.json"
    manifest=loadjson(pilot/"run_manifest.json")
    cohorts=loadjson(pilot/"cohort_indices.json")
    check(filehash(original_guard)==EXPECTED_GUARD,"Guard source changed")
    check(filehash(rawpath)==EXPECTED_RAW,"canonical raw embedding changed")
    check(manifest.get("schema")=="ipm_p2_security_pilot_manifest_v1","unexpected historical pilot schema")
    check(manifest.get("dataset")=="scifact" and manifest.get("seed")==7,
          "pilot dataset/seed mismatch")
    check(manifest.get("shared_cohort_across_cells") is True,"pilot cohorts not shared")
    check(filehash(pilot/"cohort_indices.json")==manifest.get("cohort_indices_sha256"),"cohort SHA mismatch")
    expected_inputs=manifest.get("input_sha256",{})
    for name,p in [("guard_repr.py",original_guard),
                   ("corpus_embeddings_fp32.npy",rawpath),
                   ("corpus_doc_ids.json",idpath)]:
        check(filehash(p)==expected_inputs.get(name),name+" pilot SHA mismatch")
    raw=np.load(rawpath,mmap_mode="r",allow_pickle=False)
    ids=loadjson(idpath)
    check(raw.shape==(5183,768) and raw.dtype==np.float32 and len(ids)==5183,
          "raw/ID shape mismatch")
    check(len(set(str(d) for d in ids))==5183,"duplicate document IDs")
    check(cohorts.get("sampling_seed")==20260822 and
          cohorts.get("sample_size_per_class")==2500,"cohort metadata mismatch")
    m=np.asarray(cohorts["member_row_indices"],dtype=np.int64)
    n=np.asarray(cohorts["nonmember_row_indices"],dtype=np.int64)
    both=np.concatenate((m,n))
    check(len(m)==2500 and len(n)==2500 and
          len(set(int(v) for v in both))==5000 and
          int(both.min())>=0 and int(both.max())<5183,
          "cohort counts/uniqueness/range failed")
    # No membership labels are used in ReID attack, except to select same 5000 rows.
    union=np.sort(both)
    perm=np.random.default_rng(SELECTION_SEED).permutation(union)
    anchors=np.asarray(perm[:ANCHOR_COUNT],dtype=np.int64)
    targets=np.asarray(perm[ANCHOR_COUNT:ANCHOR_COUNT+TARGET_COUNT],dtype=np.int64)
    excluded=set(int(v) for v in anchors)
    candidates=np.asarray([v for v in union if int(v) not in excluded],dtype=np.int64)
    check(len(candidates)==4744 and len(targets)==TARGET_COUNT and
          not (set(int(x) for x in anchors)&set(int(x) for x in targets)) and
          set(int(x) for x in targets)<=set(int(x) for x in candidates),
          "anchor/target/candidate leakage")
    # Train ridge in dual once using only anchor raw vectors; centered on TRAINING only.
    xanchor=np.asarray(raw[anchors],dtype=np.float64)
    xcand=np.asarray(raw[candidates],dtype=np.float64)
    xmu=np.mean(xanchor,axis=0)
    xa=xanchor-xmu
    candcenter=xcand-xmu
    gram=xa@xa.T
    gram.flat[::len(gram)+1]+=ALPHA
    # Cholesky, numerically stable SPD; candidate Gram shared across 4 cells.
    chol=np.linalg.cholesky(gram)
    kc=candcenter@xa.T
    cpos={int(v):i for i,v in enumerate(candidates)}
    target_pos=np.asarray([cpos[int(v)] for v in targets],dtype=np.int64)
    # Exact four input matrices: inspect pilot stored factors + projection SHA
    for dim in (128,320):
        for bits in (4,10):
            name="scifact_s7_D"+str(dim)+"_B"+str(bits)
            s=loadjson(pilot/name/"attack_summary.json")
            check(s.get("dimension")==dim and s.get("quantization_bits")==bits and
                  s.get("seed")==7 and s.get("projection_matrix_sha256")==MATRIX_SHA[dim],
                  "prior pilot factor/projection mismatch "+name)
            check(filehash(pilot/name/"attack_item.csv")==s.get("attack_item_sha256"),
                  "prior pilot attack item changed "+name)
    results=[]
    per_target={}
    for dim in (128,320):
        rng=np.random.default_rng(7)
        w=rng.normal(0.0,1.0,size=(768,dim)).astype(np.float32)
        w/=np.sqrt(float(dim))
        check(bytehash(w)==MATRIX_SHA[dim],"Guard W hash mismatch D="+str(dim))
        for bits in (4,10):
            key="D"+str(dim)+"_B"+str(bits)
            # T1b's attacker does NOT receive the matrix. The evaluator only
            # computes true Guard vectors to present anchor pairs and target rows.
            true_anchor=guard_transform(np.asarray(raw[anchors],dtype=np.float32),w,bits)
            true_targets=guard_transform(np.asarray(raw[targets],dtype=np.float32),w,bits)
            y=np.asarray(true_anchor,dtype=np.float64)
            ym=y.mean(axis=0)
            yc=y-ym
            # Fixed ridge alpha=1, no target tuning or tuning on held-out labels.
            coef=np.linalg.solve(chol.T,np.linalg.solve(chol,yc))
            ypred=kc@coef+ym
            check(bool(np.isfinite(ypred).all()),"nonfinite candidate prediction "+key)
            # Float32 normalized predictions used for cosine ranking.
            pred=normalize(ypred.astype(np.float32))
            sims=np.asarray(true_targets@pred.T,dtype=np.float32)
            check(sims.shape==(TARGET_COUNT,4744) and np.isfinite(sims).all(),"invalid scores "+key)
            # Stable ranking: descending similarity, candidate row ID ascending on ties.
            top5=np.argsort(-sims,axis=1,kind="stable")[:,:5]
            hit1=(top5[:,0]==target_pos).astype(np.int8)
            hit5=np.any(top5==target_pos[:,None],axis=1).astype(np.int8)
            result={"dataset":"scifact","seed":7,"dimension":dim,"bits":bits,
             "attacker":"T1b_256_anchor_unknown_matrix","alpha":ALPHA,
             "anchor_count":256,"target_count":256,"candidate_count":4744,
             "top1_hits":int(hit1.sum()),"top1_rate":float(hit1.mean()),
             "top5_hits":int(hit5.sum()),"top5_rate":float(hit5.mean()),
             "random_top1_reference":1.0/4744,"random_top5_reference":5.0/4744,
             "target_guard_sha256":bytehash(true_targets),
             "anchor_guard_sha256":bytehash(true_anchor),
             "candidate_predictions_sha256":bytehash(pred),
             "matrix_sha256_evaluator_only":bytehash(w)}
            results.append(result)
            per_target[key]={"top1":hit1,"top5":hit5}
            print("REID_CELL "+key+" TOP1="+str(result["top1_hits"])+"/256"+
                  " TOP5="+str(result["top5_hits"])+"/256",flush=True)
    # Verify relevant source inputs did not change during execution.
    check(filehash(original_guard)==EXPECTED_GUARD and filehash(rawpath)==EXPECTED_RAW,
          "input changed during attack")
    check(filehash(pilot/"cohort_indices.json")==manifest["cohort_indices_sha256"],
          "cohort file changed during attack")
    out.mkdir(parents=True,exist_ok=False)
    summarypath=out/"reid_4cell_summary.csv"
    keys=["dataset","seed","dimension","bits","attacker","alpha","anchor_count",
          "target_count","candidate_count","top1_hits","top1_rate","top5_hits","top5_rate",
          "random_top1_reference","random_top5_reference","target_guard_sha256",
          "anchor_guard_sha256","candidate_predictions_sha256","matrix_sha256_evaluator_only"]
    with summarypath.open("x",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(results)
    rowpath=out/"target_hits_PRIVATE.csv"
    with rowpath.open("x",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["target_private_position","D128_B4_top1","D128_B4_top5",
                         "D128_B10_top1","D128_B10_top5","D320_B4_top1",
                         "D320_B4_top5","D320_B10_top1","D320_B10_top5"])
        for j in range(256):
            row=[j]
            for dim in (128,320):
                for bits in (4,10):
                    r=per_target["D"+str(dim)+"_B"+str(bits)]
                    row.extend([int(r["top1"][j]),int(r["top5"][j])])
            writer.writerow(row)
    metapath=out/"reid_manifest.json"
    metadata={
      "schema":"ipm_p2_anchor_assisted_reid_v1",
      "status":"PASS_4_PROSPECTIVE_CELLS",
      "created_at_utc":datetime.now(timezone.utc).isoformat(),
      "attack_knowledge":"256 known raw/Guard anchor pairs, identified raw embeddings of 4744 candidate documents, unknown true matrix",
      "attack_estimator":"dual ridge alpha=1.0, training-only centering, no target supervision",
      "cohort_selection":"rng(20261124) permutation of sorted 5000 prior sampled indices",
      "selection_sha256":{"anchors":sha_list(anchors),"targets":sha_list(targets),
                          "candidates":sha_list(candidates)},
      "dataset":"scifact","seed":7,"anchor_count":256,"target_count":256,
      "candidate_count":4744,"results":results,
      "source_input_sha256":{
       "original_guard":EXPECTED_GUARD,"canonical_raw":EXPECTED_RAW,
       "corpus_doc_ids":filehash(idpath),"original_pilot_manifest":filehash(pilot/"run_manifest.json"),
       "cohort_indices":filehash(pilot/"cohort_indices.json")},
      "output_sha256":{"reid_4cell_summary.csv":filehash(summarypath),
                       "target_hits_PRIVATE.csv":filehash(rowpath)},
      "model_access_caveat":"This is auxiliary-reference document linkage, not plaintext recovery or conventional training-membership inference",
      "reid_executed":True,"retrieval_executed":False,
      "originals_modified":False}
    metapath.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("P2_ANCHOR_REID_4CELL=PASS_4")
    print("RETRIEVAL_EXECUTED=NO")
    print("ORIGINALS_MODIFIED=NO")
    print("PRIVATE_ROW_LEVEL_OUTPUT="+str(rowpath))
    print("OUTPUT="+str(out))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("P2_ANCHOR_REID_FAIL "+type(exc).__name__+": "+str(exc),file=sys.stderr)
        raise SystemExit(2)
