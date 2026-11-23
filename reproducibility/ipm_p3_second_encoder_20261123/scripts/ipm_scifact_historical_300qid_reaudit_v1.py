#!/usr/bin/env python3
"""Read-only audit of historical SciFact 1109-query rankings on 300 judged qids.

Recompute both 1109- and qrels-300-denominator mean metrics from existing
Top100 JSONL; check saved aggregate against recomputed 1109 means.
NEVER rerun retrieval, Guard or embeddings. Save only aggregate evidence in
new directory OUTSIDE the frozen research tree.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from pathlib import Path
import numpy as np

SEEDS=(7,13,42)
MODES=(("raw",0),("guard",0),("guard",32),("guard",64))
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(4<<20),b""):h.update(b)
    return h.hexdigest()
def load_qrels(path):
    data={}
    with path.open(encoding="utf-8",newline="") as f:
        rows=csv.DictReader(f,delimiter="\t")
        if not {"query-id","corpus-id","score"}<=set(rows.fieldnames or []):
            raise ValueError("qrels header mismatch")
        for r in rows:
            q,d=str(r["query-id"]),str(r["corpus-id"])
            grade=int(float(r["score"]))
            if d in data.setdefault(q,{}):raise ValueError("duplicate qrel")
            data[q][d]=grade
    if len(data)!=300:raise ValueError(f"expected 300 judged SciFact qids; got {len(data)}")
    return data
def dcg(rels):
    return sum((2**v-1)/np.log2(i+2) for i,v in enumerate(rels[:10]))
def metric(ids, rels):
    if not rels:return 0.,0.
    relevant={d for d,v in rels.items() if v>0}
    rec=len(set(ids[:10])&relevant)/len(relevant) if relevant else 0.
    ideal=dcg(sorted(rels.values(),reverse=True))
    ndcg=dcg([rels.get(d,0) for d in ids[:10]])/ideal if ideal else 0.
    return float(rec),float(ndcg)
def load_hist_aggregate(path):
    d={}
    with path.open(encoding="utf-8",newline="") as f:
        rows=csv.DictReader(f)
        needed={"dataset","seed","mode","epsilon","n_queries","recall_at_10","ndcg_at_10"}
        if not needed<=set(rows.fieldnames or []):raise ValueError("unexpected summary CSV columns")
        for r in rows:
            if str(r["dataset"]).lower()!="scifact":continue
            key=(int(r["seed"]),str(r["mode"]).lower(),int(r["epsilon"]))
            if key in d:raise ValueError(f"duplicate summary key: {key}")
            d[key]=r
    return d
def audit_ranks(path,qrels):
    count=0;judged=0
    all_rec=0.;all_ndcg=0.;j_rec=0.;j_ndcg=0.
    qids=set(); judged_ids=set(); bad_qids=[]
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():continue
            r=json.loads(line)
            q=str(r["qid"])
            if q in qids:raise ValueError(f"duplicate qid {q} in {path}")
            qids.add(q)
            ids=[str(x) for x in r["top_doc_ids"]]
            if len(ids)!=100 or len(set(ids))!=100:raise ValueError(f"invalid top100 {q}")
            count+=1
            rec,ndcg=metric(ids,qrels.get(q,{}))
            all_rec+=rec;all_ndcg+=ndcg
            if q in qrels:
                judged+=1;judged_ids.add(q)
                j_rec+=rec;j_ndcg+=ndcg
    if count!=1109 or judged!=300 or judged_ids!=set(qrels):
        raise ValueError(f"bad SciFact qid count/coverage n={count}, judged={judged}")
    return {"n_all":count,"n_judged":judged,"n_unjudged":count-judged,
       "all_mean_recall_at_10":all_rec/count,
       "all_mean_ndcg_at_10":all_ndcg/count,
       "judged_mean_recall_at_10":j_rec/judged,
       "judged_mean_ndcg_at_10":j_ndcg/judged,
       "ranking_sha256":sha(path)}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--summary",type=Path,default=None)
    args=ap.parse_args()
    root=args.root.expanduser().resolve(strict=True)
    out=args.out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink() or out==root or root in out.parents or out in root.parents:
        raise ValueError("output must be new and outside research root")
    qpath=root/"private_data/beir/scifact/qrels/test.tsv"
    summary=(args.summary or root/"runs/_summary/stage3_all3/retrieval_all.csv").expanduser().resolve(strict=True)
    if not summary.is_file() or not qpath.is_file():raise ValueError("missing qrels/summary")
    qrels=load_qrels(qpath)
    aggregates=load_hist_aggregate(summary)
    results=[]
    for seed in SEEDS:
        for mode,eps in MODES:
            p=root/f"runs/scifact/seed{seed}/retrieval/stage3/{mode}/eps_{eps:02d}/rankings_top100.jsonl"
            if not p.is_file() or p.is_symlink():raise ValueError(f"missing/unsafe ranking {p}")
            row=audit_ranks(p,qrels)
            key=(seed,mode,eps)
            if key not in aggregates:raise ValueError(f"missing summary key {key}")
            hist=aggregates[key]
            if int(hist["n_queries"])!=1109:
                raise ValueError(f"summary did not contain 1109 for {key}")
            row.update({"seed":seed,"mode":mode,"epsilon":eps})
            row["historical_mean_recall_at_10"]=float(hist["recall_at_10"])
            row["historical_mean_ndcg_at_10"]=float(hist["ndcg_at_10"])
            # Strict check establishes whether 809 unjudged qids were averaged as zero.
            row["summary_1109_matches_recomputed"]=(abs(row["all_mean_recall_at_10"]-row["historical_mean_recall_at_10"])<=2e-7 and
                  abs(row["all_mean_ndcg_at_10"]-row["historical_mean_ndcg_at_10"])<=2e-7)
            row["reported_to_300_multiplier"]=row["judged_mean_ndcg_at_10"]/row["historical_mean_ndcg_at_10"] if row["historical_mean_ndcg_at_10"] else None
            results.append(row)
            print(f"CHECK seed={seed} {mode} eps={eps} 1109_nDCG={row['all_mean_ndcg_at_10']:.8f} 300_nDCG={row['judged_mean_ndcg_at_10']:.8f} SUMMARY_MATCH={str(row['summary_1109_matches_recomputed']).upper()}",flush=True)
    if any(not x["summary_1109_matches_recomputed"] for x in results):
        raise RuntimeError("Historical summary does not match all-1109 recalculation; STOP, inspect evaluation contract")
    if any(sha(root/f"runs/scifact/seed{x['seed']}/retrieval/stage3/{x['mode']}/eps_{x['epsilon']:02d}/rankings_top100.jsonl")!=x["ranking_sha256"] for x in results):
        raise RuntimeError("source rankings changed during audit")
    names=["seed","mode","epsilon","n_all","n_judged","n_unjudged","historical_mean_recall_at_10","historical_mean_ndcg_at_10",
           "all_mean_recall_at_10","all_mean_ndcg_at_10","judged_mean_recall_at_10","judged_mean_ndcg_at_10",
           "summary_1109_matches_recomputed","reported_to_300_multiplier","ranking_sha256"]
    out.mkdir(parents=True,exist_ok=False)
    csvpath=out/"historical_scifact_300qid_reaudit.csv"
    with csvpath.open("x",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(results)
    metadata={"schema":"ipm_scifact_historical_300qid_reaudit_v1","status":"PASS_12",
       "interpretation":"Historical stored 1109-query means have been recomputed and 300 judged-query metrics recovered without retrieval. Not comparable to new GTE until model and ranking protocols are audited.",
       "input_sha256":{"qrels/test.tsv":sha(qpath),"retrieval_all.csv":sha(summary)},
       "result_sha256":sha(csvpath),"rankings_checked":12,"judged_queries":300,
       "unjudged_queries":809,"retrieval_executed":False,"originals_modified":False}
    with (out/"audit_manifest.json").open("x") as f:json.dump(metadata,f,indent=2);f.write("\n")
    print("SCIFACT_300QID_REAUDIT=PASS_12")
    print("HISTORICAL_UNJUDGED_IN_DENOMINATOR=YES")
    print("RETRIEVAL_EXECUTED=NO")
    print(f"OUTPUT={out}")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(f"SCIFACT_300QID_REAUDIT_FAIL {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(2)
