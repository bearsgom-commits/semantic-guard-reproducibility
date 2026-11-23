#!/usr/bin/env python3
"""Read-only P4 gate: verify stored E5 prospective 36 cells used judged BEIR test-qrels."""
import argparse,hashlib,json,sys
from collections import Counter
from pathlib import Path

EXPECTED={"fiqa":648,"scifact":300,"trec-covid":50}
SEEDS={7,13,42}
FACTOR={(128,4),(128,10),(320,4),(320,10)}
def checksum(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(4<<20),b""):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--search-root",type=Path,default=Path.home()/"Downloads")
    ap.add_argument("--out",type=Path,default=Path.home()/"Downloads/IPM_P4_36_MANIFEST_AUDIT_20261123")
    a=ap.parse_args()
    base=a.search_root.expanduser().resolve(strict=True);out=a.out.expanduser().resolve()
    if out.exists() or out.is_symlink():raise ValueError("output directory already exists")
    if not base.is_dir():raise ValueError("search root must be a directory")
    if out==base:raise ValueError("output cannot be root")
    # Only manifest names from the prospective 2x2 experiment; no source text or raw embeddings.
    candidates=[]
    for p in base.rglob("cell_manifest.json"):
        if p.is_symlink():continue
        try:
            d=json.loads(p.read_text(encoding="utf-8"))
        except (ValueError,OSError,UnicodeError):continue
        if d.get("schema")=="ipm_ablation_factorial_v1":candidates.append((p,d))
    print("FACTORIAL_MANIFEST_CANDIDATES=",len(candidates),flush=True)
    groups={}
    issues=[]
    for p,d in candidates:
        try:
            ds=str(d["dataset"]);seed=int(d["seed"]);dim=int(d["dimension"]);bits=int(d["quantization_bits"])
            key=(ds,seed,dim,bits)
            if ds not in EXPECTED or seed not in SEEDS or (dim,bits) not in FACTOR:
                issues.append(f"UNEXPECTED_CELL {key}");continue
            if key in groups:
                issues.append(f"DUPLICATE_CELL {key}");continue
            group={"dataset":ds,"seed":seed,"dimension":dim,"quantization_bits":bits,
              "tested_queries":d.get("tested_queries"),
              "cohort":d.get("cohort"),"status":d.get("status"),
              "manifest_sha256":checksum(p)}
            errors=[]
            if int(d.get("tested_queries",-1))!=EXPECTED[ds]:errors.append("TESTED_QUERY_COUNT")
            if str(d.get("cohort"))!="BEIR test qrels judged queries only":errors.append("COHORT")
            if str(d.get("status"))!="NEW_PROSPECTIVE_EXPERIMENT_NOT_HISTORICAL_REPLAY":errors.append("STATUS")
            ranks=p.parent/"test_rankings_top100.jsonl"
            if not ranks.is_file() or ranks.is_symlink():errors.append("RANKING_ABSENT")
            else:
                h=checksum(ranks)
                if h!=d.get("output_sha256",{}).get("test_rankings_top100.jsonl"):errors.append("RANKING_HASH")
                qids=set(); rows=0
                with ranks.open(encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():continue
                        r=json.loads(line);qid=str(r["qid"]);rows+=1
                        if qid in qids:errors.append("DUPLICATE_QID");break
                        qids.add(qid)
                if rows!=EXPECTED[ds]:errors.append("ROW_COUNT")
                group["ranking_sha256"]=h
            group["issues"]=sorted(set(errors))
            groups[key]=group
            if errors:issues.append(f"FAIL_CELL {key} {','.join(errors)}")
        except Exception as exc:issues.append(f"MALFORMED_MANIFEST {p.name} {type(exc).__name__}")
    required={(ds,s,d,b) for ds in EXPECTED for s in SEEDS for d,b in FACTOR}
    missing=sorted(required-set(groups))
    if missing:issues.append(f"MISSING_CELLS {len(missing)}")
    if not candidates:issues.append("NO_MANIFESTS_FOUND")
    status="PASS_36" if not issues and len(groups)==36 else "REVIEW_REQUIRED"
    result={"schema":"ipm_p4_factorial_36_cohort_manifest_audit_v1",
            "status":status,"manifests_found":len(candidates),"unique_cells":len(groups),
            "expected_cells":36,"missing":[list(x) for x in missing],
            "issues":issues,"cells":[groups[k] for k in sorted(groups)],
            "retrieval_executed":False,"source_modified":False}
    out.mkdir(parents=True,exist_ok=False)
    (out/"manifest_audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("P4_FACTORIAL_36_COHORT_AUDIT=",status)
    print("UNIQUE_CELLS=",len(groups))
    print("MISSING_CELLS=",len(missing))
    for issue in issues[:15]:print("ISSUE=",issue)
    print("RETRIEVAL_EXECUTED=NO")
    print("OUTPUT=",out)
    if status!="PASS_36":raise SystemExit(2)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(f"FATAL {type(e).__name__}: {e}",file=sys.stderr);raise SystemExit(2)
