#!/usr/bin/env python3
"""P2 prospective T1b four-cell row-level paired audit + uncertainty.
Read-only local PRIVATE target hits; write only non-identifying aggregate CIs.
SHA-validate row CSV against its own manifest and validate 4-cell hit totals.
Four prespecified 2x2 effects? Exactly three: D, B, D:B.
Paired bootstrap percentile interval Bonferroni-3 familywise 95%, fixed seed 7.
"""
import argparse,csv,hashlib,json,sys
from pathlib import Path
import numpy as np

CELLS=("D128_B4","D128_B10","D320_B4","D320_B10")
OUTCOMES=("top1","top5")
EXPECTED_TOP1={"D128_B4":210,"D128_B10":256,"D320_B4":249,"D320_B10":256}
EXPECTED_TOP5={"D128_B4":245,"D128_B10":256,"D320_B4":256,"D320_B10":256}
N=256
BOOTSTRAPS=20000
SEED=20261124

def checksum(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--pilot",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 root=a.pilot.expanduser().resolve(strict=True)
 out=a.out.expanduser().resolve(strict=False)
 if out.exists() or out.is_symlink() or out==root or root in out.parents or out in root.parents:
  raise ValueError("new output must be outside pilot input")
 man=root/"reid_manifest.json"
 rowp=root/"target_hits_PRIVATE.csv"
 sump=root/"reid_4cell_summary.csv"
 meta=json.loads(man.read_text(encoding="utf-8"))
 if meta.get("schema")!="ipm_p2_anchor_assisted_reid_v1" or meta.get("status")!="PASS_4_PROSPECTIVE_CELLS":
  raise ValueError("unexpected manifest schema/status")
 for name,fp in [("target_hits_PRIVATE.csv",rowp),("reid_4cell_summary.csv",sump)]:
  if checksum(fp)!=meta.get("output_sha256",{}).get(name):
   raise ValueError("output SHA mismatch "+name)
 expected_columns=["target_private_position"]+[f"{c}_{o}" for c in CELLS for o in OUTCOMES]
 with rowp.open("r",encoding="utf-8",newline="") as f:
  rd=csv.DictReader(f)
  if rd.fieldnames!=expected_columns:
   raise ValueError("row CSV columns unexpected")
  rows=list(rd)
 if len(rows)!=N:raise ValueError("expected 256 target rows")
 data={}
 if [int(r["target_private_position"]) for r in rows]!=list(range(N)):
  raise ValueError("target private row order mismatch")
 for c in CELLS:
  for outcome in OUTCOMES:
   values=np.asarray([int(r[f"{c}_{outcome}"]) for r in rows],dtype=np.int8)
   if not np.isin(values,[0,1]).all():raise ValueError("nonbinary hits")
   expected=(EXPECTED_TOP1 if outcome=="top1" else EXPECTED_TOP5)[c]
   if int(values.sum())!=expected:
    raise ValueError(f"reported successes disagreement: {c} {outcome}")
   data[(c,outcome)]=values.astype(np.float64)
 # Validate SUMMARY independently against row data.
 with sump.open("r",encoding="utf-8",newline="") as f:
  summaries=list(csv.DictReader(f))
 if len(summaries)!=4:raise ValueError("summary must contain exactly four rows")
 for r in summaries:
  c=f"D{r['dimension']}_B{r['bits']}"
  if c not in CELLS:raise ValueError("unrecognized condition")
  if int(r["top1_hits"])!=int(data[(c,"top1")].sum()) or int(r["top5_hits"])!=int(data[(c,"top5")].sum()):
   raise ValueError("summary totals differ from private row evidence")
 rng=np.random.default_rng(SEED)
 # Index resampling shares the same target ID across ALL cells and outcomes.
 idx=rng.integers(0,N,size=(BOOTSTRAPS,N),dtype=np.int32)
 results=[]
 for outcome in OUTCOMES:
  a0=data[("D128_B4",outcome)];b0=data[("D128_B10",outcome)]
  c0=data[("D320_B4",outcome)];d0=data[("D320_B10",outcome)]
  contrast={
   "dimension":0.5*((c0-a0)+(d0-b0)),
   "bits":0.5*((b0-a0)+(d0-c0)),
   "interaction":(d0-c0)-(b0-a0)
  }
  for name,v in contrast.items():
   point=float(v.mean())
   samples=v[idx].mean(axis=1)
   lo,hi=np.quantile(samples,[0.025/3,1-0.025/3])
   results.append({"outcome":outcome,"contrast":name,
    "point_difference":point,"bonferroni3_low":float(lo),"bonferroni3_high":float(hi),
    "fixed_seed":7,"paired_target_count":N,
    "bootstrap_replicates":BOOTSTRAPS,"bootstrap_seed":SEED})
 # A 95% familywise statement applies separately for each outcome's 3 contrasts.
 # 6 contrasts jointly are NOT protected at 95% by Bonferroni-3.
 out.mkdir(parents=True,exist_ok=False)
 keys=["outcome","contrast","point_difference","bonferroni3_low","bonferroni3_high","fixed_seed",
       "paired_target_count","bootstrap_replicates","bootstrap_seed"]
 pp=out/"paired_contrasts_bonferroni3.csv"
 with pp.open("x",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(results)
 summary={
   "schema":"ipm_p2_anchor_reid_paired_inference_v1",
   "status":"PASS_6_CONTRASTS_TWO_SEPARATE_FAMILIES",
   "interpretation":"Descriptive and conditional on fixed 256 target IDs/256 anchors/4744 candidate documents/fixed seed 7; not generalized uncertainty over seed, attacker access or anchor sampling",
   "uncertainty":"paired target bootstrap percentile Bonferroni-3 conditional simultaneous 95% per Top1 or Top5 family; not across both families",
   "input_sha256":{"reid_manifest.json":checksum(man),"target_hits_PRIVATE.csv":checksum(rowp),"reid_4cell_summary.csv":checksum(sump)},
   "output_sha256":checksum(pp),"originals_modified":False,"attack_executed":False,
   "inference_limit":"Boundary ceilings at 1.0 cause discrete/asymmetric intervals; bootstrap may underestimate uncertainty near saturation"
 }
 (out/"inference_manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 for r in results:
  print(f"{r['outcome'].upper()} {r['contrast']} effect={r['point_difference']:.6f} "
        f"CI=[{r['bonferroni3_low']:.6f},{r['bonferroni3_high']:.6f}]")
 print("P2_ANCHOR_REID_PAIRED_AUDIT=PASS_6")
 print("NO_ATTACK_RERUN=TRUE")
 print("PRIVATE_TARGET_ROWS_NOT_EXPORTED=TRUE")
 print("OUTPUT=",out)
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("P2_ANCHOR_REID_PAIRED_AUDIT_FAIL",type(e).__name__,str(e),file=sys.stderr)
  raise SystemExit(2)
