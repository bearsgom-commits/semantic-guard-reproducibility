#!/usr/bin/env python3
"""Read-only historical Re-ID alignment audit; no embeddings or attacks regenerated.

Compares the *order* of BEIR corpus IDs, canonical E5 document IDs, and the
existing historical attack_item.csv row doc IDs, per available seed/epsilon.
Does NOT assume equal vector-row count proves correctness. Writes only counts
and hashes, not private document or document-ID lists.
"""
import argparse,csv,hashlib,json,sys
from pathlib import Path
import numpy as np

def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()

def corpus_ids(p):
 ids=[]
 with p.open(encoding="utf-8") as f:
  for line in f:
   if line.strip():
    item=json.loads(line)
    ids.append(str(item["_id"]))
 return ids

def guard_path(root,seed,eps):
 return root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3"/f"seed{seed}"/f"eps_{eps:02d}"/"guard_embeddings.npy"

def attack_path(root,seed,eps):
 return root/"runs/scifact"/f"seed{seed}"/"attacks/stage3"/f"reid_eps_{eps:02d}"/"attack_item.csv"

def inspect(root,seed,eps,canonical,canonical_count):
 attack=attack_path(root,seed,eps)
 guard=guard_path(root,seed,eps)
 data={"seed":seed,"epsilon":eps,"attack_item_present":attack.is_file(),
       "guard_emb_present":guard.is_file(),"corpus_count":canonical_count}
 if guard.is_file():
  vec=np.load(guard,mmap_mode="r",allow_pickle=False)
  data["guard_embedding_shape"]=list(vec.shape)
  data["guard_sha256"]=sha(guard)
 if not attack.is_file():
  data["status"]="ATTACK_ITEM_MISSING"
  return data
 rows=0;order_ok=True;ids_unique=set();duplicates=0;unknown=0;nn_missing=0
 canonical_set=set(canonical)
 with attack.open(encoding="utf-8",newline="") as f:
  reader=csv.DictReader(f)
  required={"doc_id","nn_raw_doc_id","reid_hit","top1_leak_hit","top5_leak_hit","top10_leak_hit"}
  if not required<=set(reader.fieldnames or []):
   data["status"]="UNEXPECTED_ATTACK_COLUMNS"
   data["columns"]=reader.fieldnames
   return data
  for item in reader:
   doc=str(item["doc_id"]);nn=str(item["nn_raw_doc_id"])
   if rows>=canonical_count or canonical[rows]!=doc:order_ok=False
   if doc in ids_unique:duplicates+=1
   ids_unique.add(doc)
   if doc not in canonical_set:unknown+=1
   if nn not in canonical_set:nn_missing+=1
   rows+=1
 data.update({"attack_rows":rows,"attack_sha256":sha(attack),
   "attack_doc_ids_match_canonical_prefix_in_order":order_ok,
   "duplicate_attack_doc_ids":duplicates,"unknown_attack_doc_ids":unknown,
   "nn_raw_doc_ids_not_in_canonical":nn_missing,
   "attack_rows_equal_canonical_count":rows==canonical_count,
   "attack_rows_equal_guard_count":guard.is_file() and rows==data["guard_embedding_shape"][0]})
 # Prefix agreement is only evidence of ordered IDs where the original row
 # mapping is truly prefix-preserving. Shortfall is an explicit cohort risk.
 if not guard.is_file():
  data["status"]="GUARD_FILE_MISSING"
 elif (not order_ok or duplicates or unknown or nn_missing or rows>canonical_count or
       data["guard_embedding_shape"][0]!=canonical_count):
  data["status"]="ROW_ALIGNMENT_FAIL"
 elif rows!=canonical_count:
  data["status"]="PREFIX_ONLY_REVIEW_REQUIRED"
 else:
  data["status"]="ID_ORDER_GATE_PASS_WITH_ASSUMPTIONS"
 return data

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--root",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 args=ap.parse_args()
 root=args.root.expanduser().resolve(strict=True)
 out=args.out.expanduser().resolve(strict=False)
 if out.exists() or out.is_symlink() or out==root or root in out.parents or out in root.parents:
  raise ValueError("output must be new and outside research root")
 cp=root/"private_data/beir/scifact/corpus.jsonl"
 ip=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_doc_ids.json"
 rp=root/"artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_embeddings_fp32.npy"
 if not (cp.is_file() and ip.is_file() and rp.is_file()):
  raise ValueError("missing canonical corpus/id/raw files")
 corpus=corpus_ids(cp)
 canonical=[str(x) for x in json.loads(ip.read_text(encoding="utf-8"))]
 arr=np.load(rp,mmap_mode="r",allow_pickle=False)
 base={"corpus_count":len(corpus),"canonical_id_count":len(canonical),
       "raw_embedding_shape":list(arr.shape),
       "corpus_canonical_id_order_equal":corpus==canonical,
       "unique_corpus_ids":len(set(corpus))==len(corpus),
       "sha256":{"corpus_jsonl":sha(cp),"canonical_ids":sha(ip),"raw_embedding":sha(rp)}}
 entries=[inspect(root,seed,eps,canonical,len(canonical)) for seed in (7,13,42) for eps in (0,8,16,32,64)]
 base["scanned_attack_conditions"]=len(entries)
 base["present_attack_items"]=sum(e["attack_item_present"] for e in entries)
 base["statuses"]={k:sum(e["status"]==k for e in entries) for k in sorted(set(e["status"] for e in entries))}
 base["entries"]=entries
 base["retrieval_executed"]=False
 base["attack_executed"]=False
 base["originals_modified"]=False
 if not base["corpus_canonical_id_order_equal"] or not base["unique_corpus_ids"] or arr.shape[0]!=len(canonical):
  base["status"]="CANONICAL_ID_ALIGNMENT_FAIL"
 elif base["present_attack_items"]==0:
  base["status"]="ATTACK_RECORDS_NOT_FOUND"
 elif any(e["status"]=="ROW_ALIGNMENT_FAIL" for e in entries):
  base["status"]="ROW_ALIGNMENT_FAIL"
 elif any(e["status"]=="PREFIX_ONLY_REVIEW_REQUIRED" for e in entries):
  base["status"]="PREFIX_ONLY_REVIEW_REQUIRED"
 elif any(e["status"]=="ID_ORDER_GATE_PASS_WITH_ASSUMPTIONS" for e in entries):
  base["status"]="PARTIAL_AUDIT_PASS_REVIEW_MISSING"
 else:
  base["status"]="REVIEW_REQUIRED"
 out.mkdir(parents=True,exist_ok=False)
 (out/"alignment_audit.json").write_text(json.dumps(base,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("P2_SCIFACT_REID_ALIGNMENT=",base["status"])
 print("CORPUS_CANONICAL_ID_ORDER_EQUAL=",str(base["corpus_canonical_id_order_equal"]).upper())
 print("PRESENT_ATTACK_ITEMS=",base["present_attack_items"])
 for e in entries:
  if e["attack_item_present"]:
   print("ATTACK seed=",e["seed"],"eps=",e["epsilon"],"rows=",e["attack_rows"],
        "guard_shape=",e.get("guard_embedding_shape"),"status=",e["status"])
 print("ATTACK_EXECUTED=NO")
 print("OUTPUT=",out)
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("P2_SCIFACT_REID_ALIGNMENT_ERROR",type(e).__name__,str(e),file=sys.stderr)
  raise SystemExit(2)
