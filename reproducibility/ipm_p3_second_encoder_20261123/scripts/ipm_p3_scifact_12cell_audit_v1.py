#!/usr/bin/env python3
"""Read-only, fail-closed audit and 2x2 descriptive contrasts for P3 12-cell GTE SciFact.

Recompute all 3*4*300 ranking metrics from frozen SciFact qrels, and check
every output/input digest, matched ordered query IDs, Guard projection digests.
No model loading, Guard rerun, embedding regeneration or retrieval.
Output in fresh external directory only. No inferential CI claimed.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np

SEEDS=(7,13,42)
CELLS=((128,4),(128,10),(320,4),(320,10))
GUARD_SHA="8762a47804738160784f95d14e56a5217d09c13f4043f573991fbe6a2c72056d"
RANKER_SHA="09ecb4d855417189f9dca36dcf67913ac1b08cb2051f7a09bbfb8b7f5f16a3a5"

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for part in iter(lambda:f.read(4<<20),b""):h.update(part)
    return h.hexdigest()

def load_qrels(path):
    m={}
    with path.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f,delimiter="\t")
        assert {"query-id","corpus-id","score"} <= set(reader.fieldnames or [])
        for r in reader:
            q,d=str(r["query-id"]),str(r["corpus-id"])
            if d in m.setdefault(q,{}):raise ValueError("duplicate qrel")
            m[q][d]=int(float(r["score"]))
    return m

def dcg(rels):
    return sum((2**r-1)/np.log2(i+2) for i,r in enumerate(rels[:10]))

def metric(pred,rels):
    relevant={d for d,v in rels.items() if v>0}
    recall=len(set(pred[:10])&relevant)/len(relevant) if relevant else 0.0
    ideal=dcg(sorted(rels.values(),reverse=True))
    ndcg=dcg([rels.get(d,0) for d in pred[:10]])/ideal if ideal else 0.0
    return float(recall),float(ndcg)

def safe_output(root,enc,runs,out):
    out=out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink():raise ValueError("new output required")
    for p in (root,enc,*runs):
        p=p.resolve(strict=True)
        if out==p or p in out.parents or out in p.parents:
            raise ValueError("output nested in/protecting inputs")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True,type=Path)
    ap.add_argument("--encoded",required=True,type=Path)
    ap.add_argument("--seed7",required=True,type=Path)
    ap.add_argument("--seed13",required=True,type=Path)
    ap.add_argument("--seed42",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args()
    root=a.root.expanduser().resolve(strict=True)
    enc=a.encoded.expanduser().resolve(strict=True)
    runs={7:a.seed7.expanduser().resolve(strict=True),
          13:a.seed13.expanduser().resolve(strict=True),
          42:a.seed42.expanduser().resolve(strict=True)}
    out=safe_output(root,enc,list(runs.values()),a.out)
    qrels_path=root/"private_data/beir/scifact/qrels/test.tsv"
    guard_path=root/"repo/src/guard_repr.py"
    ranker_path=root/"repo/src/stage3/run_dense_retrieval.py"
    assert sha(guard_path)==GUARD_SHA and sha(ranker_path)==RANKER_SHA
    enc_manifest=enc/"encoding_manifest.json"
    em=json.loads(enc_manifest.read_text())
    assert em["status"]=="PASS" and em["doc_count"]==5183 and em["test_qids"]==300
    assert em["encoder"]["resolved_revision"]=="9bbca17d9273fd0d03d5725c7a4b0f6b45142062"
    assert em["encoder"]["resolved_code_revision"]=="40ced75c3017eb27626c9d4ea981bde21a2662f4"
    assert sha(qrels_path)==em["dataset_input_sha256"]["qrels/test.tsv"]
    for fn,digest in em["outputs_sha256"].items():
        assert sha(enc/fn)==digest, "encoded input changed: "+fn
    dids=[str(x) for x in json.loads((enc/"corpus_doc_ids.json").read_text())]
    qids=[str(x) for x in json.loads((enc/"judged_query_ids.json").read_text())]
    assert len(dids)==len(set(dids))==5183 and len(qids)==len(set(qids))==300
    didset=set(dids)
    qrels=load_qrels(qrels_path)
    assert set(qids)==set(qrels) and {d for x in qrels.values() for d in x}<=didset
    results=[]
    per_seed={}
    for seed in SEEDS:
        folder=runs[seed]
        pm=json.loads((folder/"pilot_manifest.json").read_text())
        assert pm["status"]=="PASS_PROSPECTIVE_SECOND_ENCODER_PILOT"
        assert pm["seed"]==seed and pm["cell_count"]==4
        assert pm["input_sha256"]["guard_repr.py"]==GUARD_SHA
        assert pm["input_sha256"]["run_dense_retrieval.py"]==RANKER_SHA
        assert pm["input_sha256"]["qrels/test.tsv"]==sha(qrels_path)
        assert pm["input_sha256"]["encoding_manifest.json"]==sha(enc_manifest)
        for key,val in em["outputs_sha256"].items():
            assert pm["input_sha256"][f"encoded/{key}"]==val
        assert sha(folder/"pilot_summary_4cells.csv")==pm["output_sha256"]["pilot_summary_4cells.csv"]
        with (folder/"pilot_summary_4cells.csv").open(newline="") as f:
            summaries=list(csv.DictReader(f))
        assert len(summaries)==4
        summary_map={(int(r["dimension"]),int(r["quantization_bits"])):r for r in summaries}
        assert set(summary_map)==set(CELLS)
        values={}
        for dim,bits in CELLS:
            sub=folder/f"scifact_s{seed}_D{dim}_B{bits}"
            ranks=sub/"test_rankings_top100.jsonl"
            cm=json.loads((sub/"cell_manifest.json").read_text())
            expected=pm["output_sha256"][f"scifact_s{seed}_D{dim}_B{bits}/test_rankings_top100.jsonl"]
            assert sha(ranks)==expected==cm["rankings_sha256"]
            assert (cm["dimension"],cm["quantization_bits"],cm["seed"])==(dim,bits,seed)
            assert cm["tested_queries"]==300
            rs=[json.loads(line) for line in ranks.read_text().splitlines() if line.strip()]
            assert len(rs)==300 and [str(x["qid"]) for x in rs]==qids
            recalls=[];ndcgs=[]
            for item in rs:
                pred=[str(x) for x in item["top_doc_ids"]]
                scores=np.asarray(item["top_scores"],dtype=float)
                assert len(pred)==len(set(pred))==100 and set(pred)<=didset
                assert scores.shape==(100,) and np.isfinite(scores).all()
                assert np.max(np.diff(scores))<=1e-6
                recall,ndcg=metric(pred,qrels[str(item["qid"])])
                assert abs(recall-float(item["recall_at_10"]))<1e-12
                assert abs(ndcg-float(item["ndcg_at_10"]))<1e-12
                recalls.append(recall);ndcgs.append(ndcg)
            ar=float(np.mean(recalls));an=float(np.mean(ndcgs))
            assert abs(ar-float(cm["mean_recall_at_10"]))<1e-12
            assert abs(an-float(cm["mean_ndcg_at_10"]))<1e-12
            assert abs(an-float(summary_map[dim,bits]["mean_ndcg_at_10"]))<1e-12
            assert abs(ar-float(summary_map[dim,bits]["mean_recall_at_10"]))<1e-12
            values[dim,bits]=an
            results.append({"seed":seed,"dimension":dim,"quantization_bits":bits,
                 "recall_at_10":ar,"ndcg_at_10":an,"rankings_sha256":sha(ranks)})
            print(f"P3_AUDIT_CELL_PASS seed={seed} D={dim} B={bits} nDCG10={an:.8f}",flush=True)
        per_seed[seed]=values
    effects=[]
    for seed,v in per_seed.items():
        effects.append({
            "seed":seed,
            "dimension_main":((v[320,4]-v[128,4])+(v[320,10]-v[128,10]))/2,
            "bits_main":((v[128,10]-v[128,4])+(v[320,10]-v[320,4]))/2,
            "interaction_difference_of_differences":(v[320,10]-v[320,4])-(v[128,10]-v[128,4]),
        })
    group_means={f"D{d}_B{b}":float(np.mean([per_seed[s][d,b] for s in SEEDS])) for d,b in CELLS}
    pooled={k:float(np.mean([e[k] for e in effects])) for k in ("dimension_main","bits_main","interaction_difference_of_differences")}
    # Verify immutable originals before writing output.
    assert sha(guard_path)==GUARD_SHA and sha(ranker_path)==RANKER_SHA
    assert sha(qrels_path)==em["dataset_input_sha256"]["qrels/test.tsv"]
    for fn,digest in em["outputs_sha256"].items():assert sha(enc/fn)==digest
    out.mkdir(parents=True,exist_ok=False)
    def csv_write(p,rows):
        with p.open("x",encoding="utf-8",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
            writer.writeheader();writer.writerows(rows)
    csv_write(out/"audited_12cells.csv",results)
    csv_write(out/"factorial_effects_3seeds.csv",effects)
    record={
        "schema":"ipm_p3_scifact_12cell_audit_v1","status":"PASS_12",
        "dataset":"scifact","encoder":"Alibaba-NLP/gte-multilingual-base",
        "model_revision":em["encoder"]["resolved_revision"],
        "code_revision":em["encoder"]["resolved_code_revision"],
        "seeds":list(SEEDS),"tested_queries_per_cell":300,
        "tested_cells":12,"same_ordered_judged_qids":True,
        "mean_ndcg_by_cell":group_means,"descriptive_mean_effects":pooled,
        "inference":"Descriptive only, no confidence intervals or hypothesis tests",
        "input_hashes":{
            "qrels":sha(qrels_path),"guard":sha(guard_path),"ranker":sha(ranker_path),
            "encoded_manifest":sha(enc_manifest),
            **{f"seed{seed}/pilot_manifest":sha(folder/"pilot_manifest.json") for seed,folder in runs.items()},
        },
        "output_hashes":{
            "audited_12cells.csv":sha(out/"audited_12cells.csv"),
            "factorial_effects_3seeds.csv":sha(out/"factorial_effects_3seeds.csv"),
        },
        "scope":"12 GTE SciFact cells; not a cross-encoder equivalence or privacy result"
    }
    with (out/"audit_manifest.json").open("x") as f:
        json.dump(record,f,indent=2,allow_nan=False);f.write("\n")
    print("P3_12CELL_AUDIT=PASS_12")
    print(f"DIMENSION_EFFECT_MEAN={pooled['dimension_main']:.8f}")
    print(f"BITS_EFFECT_MEAN={pooled['bits_main']:.8f}")
    print(f"INTERACTION_MEAN={pooled['interaction_difference_of_differences']:.8f}")
    print(f"OUTPUT={out}")

if __name__=="__main__":
    try:main()
    except Exception as ex:
        print(f"P3_12CELL_AUDIT=FAIL {type(ex).__name__}: {ex}",file=sys.stderr)
        raise SystemExit(2)
