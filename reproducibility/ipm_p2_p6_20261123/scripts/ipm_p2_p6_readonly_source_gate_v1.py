#!/usr/bin/env python3
"""Read-only two-source gate: historical ReID exact code and frozen-v18 claim-location inventory."""
from pathlib import Path
import argparse,hashlib,zipfile,re,json,sys

V18="08c0a2e6462c805b70fe3650d7c6bef28b359cb97759df3c0d64a3417dbafdc8"
REID="e934489d54acbf83592a7de25ef5bb2a5b72dc57f33853e50ef4ca3363710bca"
def sha_bytes(x):return hashlib.sha256(x).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--research",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 args=ap.parse_args()
 root=args.research.expanduser().resolve(strict=True)
 out=args.out.expanduser().resolve(strict=False)
 if out.exists() or out.is_symlink() or out==root or root in out.parents or out in root.parents:
  raise ValueError("Output directory must be new and outside research root")
 archive=root/"manuscript_review/20261120_stage1b_v18/IPM_STAGE1B_V18_VALIDATED_MANUSCRIPT_BUNDLE_20261120.zip"
 with zipfile.ZipFile(archive) as z:
  raw=z.read("manuscript_v18_candidate.tex")
 if sha_bytes(raw)!=V18:raise ValueError("Frozen v18 SHA mismatch")
 lines=raw.decode("utf-8").splitlines()
 pattern=re.compile(r"fiqa|scifact|trec.?covid|ndcg|recall|qrels|re.?id|membership|security|privacy|\\begin\{table|\\caption",re.I)
 matches=[(i,s.strip()) for i,s in enumerate(lines,1) if pattern.search(s)]
 # Search exact historical ReID name and hash under expected source directories.
 candidates=[]
 for folder in (root/"repo",root/"scripts",root/"_reproducibility_runs"):
  if not folder.is_dir():continue
  for p in folder.rglob("*.py"):
   if p.is_symlink() or not p.is_file() or p.stat().st_size>2_000_000:continue
   if "reid" not in p.name.lower():continue
   digest=sha_file(p)
   candidates.append({"relative_path":str(p.relative_to(root)),"sha256":digest,"exact_historical_source":digest==REID})
 out.mkdir(parents=True,exist_ok=False)
 # Claim listing is private until manuscript author authorizes publication.
 report=["# Frozen v18 relevant claim lines — PRIVATE","",
  "v18_sha256="+V18,"matches="+str(len(matches)),""]
 report += ["L"+str(i)+": "+s[:450] for i,s in matches]
 (out/"v18_claim_lines_PRIVATE.md").write_text("\n".join(report)+"\n",encoding="utf-8")
 result={"v18_source_hash":"PASS","v18_line_count":len(lines),
         "v18_relevant_line_count":len(matches),
         "reid_candidates":candidates,
         "exact_reid_found":any(x["exact_historical_source"] for x in candidates),
         "originals_modified":False,"retrieval_executed":False}
 (out/"source_gate.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("V18_SOURCE_GATE=PASS")
 print("V18_RELEVANT_LINES=",len(matches))
 print("REID_CANDIDATES=",len(candidates))
 for c in candidates[:20]:
  print("REID_SOURCE=",c["relative_path"],"SHA256=",c["sha256"],"MATCH=",str(c["exact_historical_source"]).upper())
 print("HISTORICAL_REID_SOURCE=", "FOUND" if result["exact_reid_found"] else "NOT_FOUND_IN_SCANNED_PY")
 print("ORIGINALS_MODIFIED=NO")
 print("OUTPUT=",out)
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("SOURCE_GATE_FAILED",type(e).__name__,str(e),file=sys.stderr)
  raise SystemExit(2)
