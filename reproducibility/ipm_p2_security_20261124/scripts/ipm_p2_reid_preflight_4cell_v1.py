#!/usr/bin/env python3
"""Read-only P2 ReID preflight: check 4-cell existing index-membership pilot's
input SHA, cohort identities, transformation matrix SHA and recorded item hash.
No ReID inference, embedding regeneration or retrieval. Python >=3.10.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np

DIMS=(128,320)
BITS=(4,10)
def hashfile(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()
def readjson(p):
 with p.open("r",encoding="utf-8") as f:return json.load(f)
def fail(message):
 raise ValueError(message)
def main():
 a=argparse.ArgumentParser()
 a.add_argument("--root",required=True,type=Path)
 a.add_argument("--pilot",required=True,type=Path)
 a.add_argument("--out",required=True,type=Path)
 args=a.parse_args()
 root=args.root.expanduser().resolve(strict=True)
 pilot=args.pilot.expanduser().resolve(strict=True)
 out=args.out.expanduser().resolve(strict=False)
 if out.exists() or out.is_symlink() or out==root or root in out.parents or out==pilot or pilot in out.parents:
  fail("output must be a new directory outside inputs")
 manifest=readjson(pilot/"run_manifest.json")
 cohorts=readjson(pilot/"cohort_indices.json")
 checks=[]
 def check(label,valid,detail=None):
  checks.append({"name":label,"pass":bool(valid),"detail":detail})
  print(("PASS " if valid else "FAIL ")+label)
  return bool(valid)
 check("manifest_schema",manifest.get("schema")=="ipm_p2_security_pilot_manifest_v1")
 check("pilot_dataset_seed",manifest.get("dataset")=="scifact" and manifest.get("seed")==7)
 check("manifest_cohort_shared",manifest.get("shared_cohort_across_cells") is True)
 check("manifest_four_cells",len(manifest.get("cells",[]))==4)
 check("no_retrieval",manifest.get("retrieval_executed") is False)
 check("originals_unchanged",manifest.get("historical_originals_modified") is False)
 check("cohort_sha",hashfile(pilot/"cohort_indices.json")==manifest.get("cohort_indices_sha256"))
 check("pilot_summary_sha",hashfile(pilot/"pilot_summary_4cells.csv")==manifest.get("pilot_summary_sha256"))
 members=cohorts.get("member_row_indices",[])
 nonmembers=cohorts.get("nonmember_row_indices",[])
 try:
  M=[int(x) for x in members];N=[int(x) for x in nonmembers]
 except (ValueError,TypeError):
  M=[];N=[]
 check("sample_size_2500x2",len(M)==len(N)==cohorts.get("sample_size_per_class")==2500)
 check("sampling_seed",cohorts.get("sampling_seed")==20260822)
 check("cohort_disjoint",len(set(M))==2500 and len(set(N))==2500 and not(set(M)&set(N)))
 check("cohort_within_5183",len(M)==2500 and len(N)==2500 and min(M+N)>=0 and max(M+N)<5183)
 src=root/"repo/src/guard_repr.py"
 raw=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_embeddings_fp32.npy"
 ids=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_doc_ids.json"
 expected=manifest.get("input_sha256",{})
 for name,file in [("guard_repr.py",src),("corpus_embeddings_fp32.npy",raw),("corpus_doc_ids.json",ids)]:
  check("input_sha_"+name,file.is_file() and hashfile(file)==expected.get(name))
 if raw.is_file():
  arr=np.load(raw,mmap_mode="r",allow_pickle=False)
  check("raw_shape_dtype",arr.shape==(5183,768) and arr.dtype==np.float32)
 if ids.is_file():
  doc_ids=readjson(ids)
  check("doc_ids_unique_and_count",len(doc_ids)==len(set(map(str,doc_ids)))==5183)
 expected_matrices={128:"42fea5124bbe699d6dbd610629ee580e79522e740b19d2ac0577df3fe9b5256d",320:"3495b4a51026b118d91690fcc78a2ff7720a023aa4fa7411a7fcb70b890ced41"}
 for dim in DIMS:
  # Same seed-7 Guard definition; confirm known SHA without writing matrices.
  rng=np.random.default_rng(7)
  W=rng.normal(0.0,1.0,size=(768,dim)).astype(np.float32)
  W/=np.sqrt(float(dim))
  check("projection_sha_D"+str(dim),hashlib.sha256(W.tobytes()).hexdigest()==expected_matrices[dim])
 summaries={}
 for dim in DIMS:
  for bits in BITS:
   key="D"+str(dim)+"_B"+str(bits)
   folder=pilot/("scifact_s7_"+key)
   summary=folder/"attack_summary.json";item=folder/"attack_item.csv"
   if not summary.is_file() or not item.is_file():
    check("cell_"+key+"_exists",False)
    continue
   s=readjson(summary);summaries[key]=s
   check("cell_"+key+"_factors",s.get("dataset")=="scifact" and s.get("seed")==7 and s.get("dimension")==dim and s.get("quantization_bits")==bits)
   check("cell_"+key+"_matched_cohort",s.get("sample_size_per_class")==2500 and s.get("sampling_seed")==20260822 and s.get("self_exclusion_count")==2500)
   check("cell_"+key+"_projection_sha",s.get("projection_matrix_sha256")==expected_matrices[dim])
   check("cell_"+key+"_attack_item_sha",hashfile(item)==s.get("attack_item_sha256"))
   check("cell_"+key+"_is_index_membership",s.get("schema")=="ipm_p2_index_membership_proxy_v1" and s.get("attack_name")=="index_membership_proxy_matched")
   # Exact nested paths vary by runner version; SHA check only when the
   # recorded relative file reference is explicit and type safe.
   declared=manifest.get("cell_output_sha256",{}).get(key,{})
   if isinstance(declared,dict):
    for filename,recordedsha in declared.items():
     if isinstance(filename,str) and filename in ("attack_summary.json","attack_item.csv"):
      check("manifest_"+key+"_"+filename,hashfile(folder/filename)==recordedsha)
 allpass=all(x["pass"] for x in checks)
 result={"status":"PASS_4CELL_PREFLIGHT" if allpass else "REVIEW_REQUIRED",
  "checks":checks,"cells":sorted(summaries),"attacker_knowledge":"NOT_SPECIFIED_BY_HISTORICAL_INDEX_MEMBERSHIP_PILOT",
  "reid_attack_performed":False,"retrieval_executed":False,
  "originals_modified":False,
  "note":"Passing this gate validates input/cohort/lineage for designing a new ReID experiment, not its success or any privacy guarantee"}
 out.mkdir(parents=True,exist_ok=False)
 (out/"preflight.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("P2_REID_PREFLIGHT=",result["status"])
 print("REID_ATTACK_EXECUTED=NO")
 print("OUTPUT=",out)
 if not allpass:raise SystemExit(2)
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("P2_REID_PREFLIGHT_ERROR",type(e).__name__,str(e),file=sys.stderr)
  raise SystemExit(2)
