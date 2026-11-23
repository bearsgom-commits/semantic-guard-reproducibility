#!/usr/bin/env python3
"""One-cell self-match threat-model falsification gate. No retrieval rerun.

Compares saved SciFact S7 D128 B4 leave-one-out index-membership proxy against
the identical cohort where an index observer may retain member self matches.
This is a positive-control attack, NOT a general security/privacy guarantee.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np

D=128
BITS=4
N=2500
EXPECTED_GUARD_SHA="8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def independent_auc(y,s):
    # Pair-ranking formula with average rank for ties
    order=np.argsort(s,kind="stable")
    ranks=np.empty(len(s),dtype=float)
    k=0
    while k<len(s):
        j=k+1
        while j<len(s) and s[order[j]]==s[order[k]]:
            j+=1
        ranks[order[k:j]]=(k+1+j)/2
        k=j
    n1=int(y.sum())
    n0=len(y)-n1
    return float((ranks[y==1].sum()-n1*(n1+1)/2)/(n1*n0))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--pilot",required=True,type=Path)
    p.add_argument("--pilot-script",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    root=a.root.expanduser().resolve(strict=True)
    pilot=a.pilot.expanduser().resolve(strict=True)
    out=a.out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink() or root==out or root in out.parents or out in root.parents:
        raise ValueError("new output required outside research root")
    guard_path=root/"repo/src/guard_repr.py"
    raw_path=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_embeddings_fp32.npy"
    ids_path=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_doc_ids.json"
    src_path=a.pilot_script.expanduser().resolve(strict=True)
    assert sha(guard_path)==EXPECTED_GUARD_SHA
    manifest=json.loads((pilot/"run_manifest.json").read_text())
    assert manifest["dataset"]=="scifact" and manifest["seed"]==7
    assert manifest["input_sha256"]["guard_repr.py"]==sha(guard_path)
    assert manifest["input_sha256"]["corpus_embeddings_fp32.npy"]==sha(raw_path)
    assert manifest["input_sha256"]["corpus_doc_ids.json"]==sha(ids_path)
    cohort_path=pilot/"cohort_indices.json"
    assert sha(cohort_path)==manifest["cohort_indices_sha256"]
    cohort=json.loads(cohort_path.read_text())
    m=np.asarray(cohort["member_row_indices"],dtype=int)
    n=np.asarray(cohort["nonmember_row_indices"],dtype=int)
    assert len(m)==len(n)==N and len(set(m.tolist()+n.tolist()))==2*N
    raw=np.load(raw_path,mmap_mode="r",allow_pickle=False)
    assert raw.shape==(5183,768) and raw.dtype==np.float32
    ids=json.loads(ids_path.read_text())
    assert len(ids)==len(set(ids))==5183
    script=load_module(src_path,"frozen_p2_pilot_module")
    guard=load_module(guard_path,"immutable_p2_guard_module")
    w=guard.make_projection_matrix(768,D,7)
    sampled=script.guard_transform_rows(np.asarray(raw[np.r_[m,n]],dtype=np.float32),w,BITS,guard)
    members=sampled[:N]
    nonmembers=sampled[N:]
    saved_path=pilot/"scifact_s7_D128_B4/attack_item.csv"
    saved_summary_path=pilot/"scifact_s7_D128_B4/attack_summary.json"
    summary=json.loads(saved_summary_path.read_text())
    assert sha(saved_path)==summary["attack_item_sha256"]
    with saved_path.open(newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==2*N
    assert [int(x["corpus_row_index"]) for x in rows]==m.tolist()+n.tolist()
    scores=np.asarray([float(x["pred_member_prob"]) for x in rows],dtype=float)
    y=np.r_[np.ones(N,dtype=int),np.zeros(N,dtype=int)]
    assert [int(x["label_member"]) for x in rows]==y.tolist()
    # Sampled regeneration checks full saved Guard matrix digest, not just dimensions.
    assert hashlib.sha256(sampled.tobytes()).hexdigest()==summary["sampled_guard_sha256"]
    assert hashlib.sha256(np.asarray(w,dtype=np.float32).tobytes()).hexdigest()==summary["projection_matrix_sha256"]
    # Independently recalculate original stored leave-one-out AUROC.
    loo_auc=independent_auc(y,scores)
    assert abs(loo_auc-summary["index_membership_proxy_auroc"])<1e-12
    # Positive control: identical index-members are allowed to match themselves.
    inclusive_features,excluded=script.feature_rows(members,members,False,256)
    assert excluded==0
    inclusive_scores=np.r_[np.asarray([script.attack_score(f) for f in inclusive_features]),scores[N:]]
    inclusive_max=np.r_[np.asarray([f["max_sim_to_index"] for f in inclusive_features]),
                       np.asarray([float(x["max_sim_to_index"]) for x in rows[N:]])]
    auc_weighted=independent_auc(y,inclusive_scores)
    auc_max=independent_auc(y,inclusive_max)
    identity_dot=np.sum(members*members,axis=1)
    assert np.min(identity_dot)>0.99998
    # Positive control must reveal identity exposure when exact index vectors are accessible.
    if auc_max<0.99:
        raise RuntimeError("self-match positive control failed: inspect ranking and normalization before expansion")
    output={
      "schema":"ipm_p2_self_match_gate_v1",
      "dataset":"scifact","seed":7,"dimension":D,"quantization_bits":BITS,
      "sample_size_per_class":N,
      "saved_leave_one_out_auroc":loo_auc,
      "self_inclusive_weighted_score_auroc":auc_weighted,
      "self_inclusive_max_similarity_auroc":auc_max,
      "minimum_identity_self_dot":float(np.min(identity_dot)),
      "guard_vector_digest_matches_saved":True,
      "threat_model_conclusion":"Self-exclusion hides exact index identity signal; self-inclusive and leave-one-out outcomes are distinct attack protocols. Neither establishes general privacy.",
      "retrieval_executed":False,
      "input_sha256":{"raw":sha(raw_path),"ids":sha(ids_path),"guard":sha(guard_path),
                      "saved_items":sha(saved_path),"cohort":sha(cohort_path),"pilot_script":sha(src_path)}
    }
    # Check originals before output writes.
    assert sha(raw_path)==output["input_sha256"]["raw"]
    assert sha(guard_path)==output["input_sha256"]["guard"]
    out.mkdir(parents=True,exist_ok=False)
    (out/"self_match_gate.json").write_text(json.dumps(output,indent=2)+"\n")
    print("P2_SELF_MATCH_GATE=PASS")
    print(f"LEAVE_ONE_OUT_AUROC={loo_auc:.6f}")
    print(f"SELF_INCLUDED_WEIGHTED_AUROC={auc_weighted:.6f}")
    print(f"SELF_INCLUDED_MAX_AUROC={auc_max:.6f}")
    print("GUARD_DIGEST_REPLAY=PASS")
    print("RETRIEVAL_EXECUTED=NO")
    print(f"OUTPUT={out}")

if __name__=="__main__":
    try: main()
    except Exception as e:
        print(f"P2_SELF_MATCH_GATE=FAIL {type(e).__name__}: {e}",file=sys.stderr)
        raise SystemExit(2)
