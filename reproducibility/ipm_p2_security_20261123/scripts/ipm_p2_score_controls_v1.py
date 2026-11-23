#!/usr/bin/env python3
"""Independent numerical audit of four saved P2 cells. Does not rerun attacks.

Oracle and shuffled controls validate AUROC arithmetic, NOT attacker power.
Input order and common cohort are checked exactly. Output is new-path only.
"""
import argparse, csv, hashlib, json, math
from pathlib import Path
import numpy as np

CELLS=((128,4),(128,10),(320,4),(320,10))

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()

def auc(y,s):
    # Independent pair-ranking calculation; average ranks for exact ties.
    order=np.argsort(s,kind="stable")
    rank=np.empty(len(s),dtype=np.float64)
    i=0
    while i<len(s):
        j=i+1
        while j<len(s) and s[order[j]]==s[order[i]]:
            j+=1
        rank[order[i:j]]=(i+1+j)/2.0
        i=j
    n1=int(y.sum()); n0=len(y)-n1
    return float((rank[y==1].sum()-n1*(n1+1)/2)/(n1*n0))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    root=a.input.expanduser().resolve(strict=True)
    out=a.out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink() or out==root or root in out.parents or out in root.parents:
        raise ValueError("output must be a NEW separate directory")
    manifest=json.loads((root/"run_manifest.json").read_text())
    assert manifest["dataset"]=="scifact" and manifest["seed"]==7
    assert manifest["retrieval_executed"] is False
    n=2500
    cohort=json.loads((root/"cohort_indices.json").read_text())
    assert sha(root/"cohort_indices.json")==manifest["cohort_indices_sha256"]
    expected=list(map(int,cohort["member_row_indices"]))+list(map(int,cohort["nonmember_row_indices"]))
    assert len(expected)==2*n and len(set(expected))==2*n
    report=[]
    first_labels=None
    for d,b in CELLS:
        folder=root/f"scifact_s7_D{d}_B{b}"
        src=folder/"attack_item.csv"
        summ=json.loads((folder/"attack_summary.json").read_text())
        assert sha(src)==summ["attack_item_sha256"]
        assert sha(src)==manifest["cell_output_sha256"][f"D{d}_B{b}"]["item_sha256"]
        with src.open(newline="") as f: rows=list(csv.DictReader(f))
        y=np.array([int(r["label_member"]) for r in rows],dtype=int)
        scores=np.array([float(r["pred_member_prob"]) for r in rows],dtype=float)
        ids=[int(r["corpus_row_index"]) for r in rows]
        assert len(rows)==2*n and y.sum()==n and ids==expected
        assert np.array_equal(y,np.r_[np.ones(n,dtype=int),np.zeros(n,dtype=int)])
        if first_labels is None: first_labels=y.copy()
        assert np.array_equal(first_labels,y)
        assert np.isfinite(scores).all()
        # Independently reconstruct score for every row from stored features.
        raw=np.array([
            .5*float(r["max_sim_to_index"])
            +.3*float(r["mean_top5_sim_to_index"])
            +.2*float(r["margin_top1_top2"])
            for r in rows
        ])
        rebuilt=1/(1+np.exp(-8*(raw-.5)))
        assert np.max(np.abs(rebuilt-scores))<1e-12
        observed=auc(y,scores)
        assert abs(observed-float(summ["index_membership_proxy_auroc"]))<1e-12
        # Controls: perfect oracle, score-label reversal, random permutation.
        assert auc(y,y.astype(float))==1.
        assert abs(auc(y,1-y.astype(float)))<1e-12
        rng=np.random.default_rng(20261123+d*100+b)
        null_scores=scores[rng.permutation(len(scores))]
        shuffled=auc(y,null_scores)
        report.append({
            "D":d,"B":b,"observed_auroc":observed,
            "label_shuffled_control_auroc":shuffled,
            "oracle_control_auroc":1.0,
            "reversed_oracle_control_auroc":0.0,
            "score_range":float(np.ptp(scores)),
            "cohort_exact_match":True,
            "score_formula_exact_match":True,
            "attack_item_sha256":sha(src),
        })
        print(f"D={d} B={b} SCORE_AUDIT=PASS AUROC={observed:.6f} SHUFFLED={shuffled:.6f}")
    out.mkdir(parents=True,exist_ok=False)
    result={"schema":"ipm_p2_score_controls_v1",
      "interpretation":"Arithmetic/integrity controls only; cannot establish physical attacker sensitivity or confidentiality",
      "source_run_manifest_sha256":sha(root/"run_manifest.json"),
      "source_cohort_sha256":sha(root/"cohort_indices.json"),
      "cells":report}
    (out/"score_controls.json").write_text(json.dumps(result,indent=2)+"\n")
    print("P2_SCORE_CONTROLS=PASS_4")
    print("ATTACK_POSITIVE_SENSITIVITY=NOT_TESTED")
    print(f"OUTPUT={out}")

if __name__=="__main__":
    main()
