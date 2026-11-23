#!/usr/bin/env python3
"""Read-only, bounded local E5 embedding-source provenance discovery.

Scans only code/config/manifests in local research root, never BEIR source text,
raw embeddings, queries, qrels or row-level outputs. Writes findings OUTSIDE
research root. Discovery is not proof that a file generated historic vectors.
"""
from pathlib import Path
import argparse,hashlib,json,re,sys
PATTERNS=[
    ("e5_model",re.compile(r"multilingual.e5.base|intfloat[/_-]multilingual",re.I)),
    ("e5_prefix",re.compile(r"(?<![a-z])query:\s|(?<![a-z])passage:\s",re.I)),
    ("encoder",re.compile(r"AutoModel\.from_pretrained|SentenceTransformer\(|AutoTokenizer\.from_pretrained",re.I)),
    ("pooling",re.compile(r"average_pool|mean_pool|last_hidden_state|attention_mask|pooler_output",re.I)),
    ("output_embedding",re.compile(r"corpus_embeddings_fp32|query_embeddings_fp32|corpus_doc_ids\.json|query_ids\.json",re.I)),
]
EXTS={".py",".sh",".md",".txt",".toml",".yaml",".yml",".json",".ini",".cfg",".log"}
SKIP={"private_data",".git","node_modules",".venv","venv","__pycache__","site-packages","checkpoints","huggingface","cache","wandb"}
MAX_BYTES=2_000_000
MAX_MATCHES=10
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for v in iter(lambda:f.read(1<<20),b""):h.update(v)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    root=a.root.expanduser().resolve(strict=True)
    out=a.out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink() or out==root or root in out.parents or out in root.parents:
        raise ValueError("new output outside research root required")
    found=[]
    for base in (root/"repo",root/"scripts",root/"environment",root/"docs"):
        if not base.is_dir(): continue
        for path in base.rglob("*"):
            if any(x in SKIP for x in path.relative_to(base).parts):continue
            if not path.is_file() or path.is_symlink() or path.suffix.lower() not in EXTS:continue
            if path.stat().st_size>MAX_BYTES:continue
            try:lines=path.read_text(encoding="utf-8").splitlines()
            except (UnicodeError,OSError):continue
            matches=[]
            for number,line in enumerate(lines,1):
                kinds=[name for name,pattern in PATTERNS if pattern.search(line)]
                if kinds:
                    matches.append({"line":number,"patterns":kinds,
                     "line_sha256":hashlib.sha256(line.encode("utf-8")).hexdigest()})
                if len(matches)>=MAX_MATCHES:break
            if matches:
                found.append({"path":str(path.relative_to(root)),"sha256":digest(path),
                              "matches":matches,
                              "candidate_relevance":sum(len(x["patterns"]) for x in matches)})
    found.sort(key=lambda x:(-x["candidate_relevance"],x["path"]))
    out.mkdir(parents=True,exist_ok=False)
    result={"schema":"ipm_p3_e5_encoder_lineage_scan_v1",
            "classification":"SOURCE_DISCOVERY_ONLY_NOT_PROVEN_GENERATOR",
            "search_roots":["repo","scripts","environment","docs"],
            "source_count":len(found),"candidates":found[:200],
            "raw_source_text_emitted":False,
            "next":"Inspect top candidates locally and compare exact historical embedding run logs and output hashes."}
    (out/"source_candidates.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("P3_E5_SOURCE_DISCOVERY=PASS")
    print("MATCHED_SOURCE_FILES="+str(len(found)))
    for c in found[:15]:
        patterns=sorted({p for row in c["matches"] for p in row["patterns"]})
        print("CANDIDATE="+c["path"]+" PATTERNS="+",".join(patterns))
    print("E5_ENCODING_PROVENANCE_VERIFIED=NO")
    print("OUTPUT="+str(out))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("P3_E5_SOURCE_DISCOVERY_FAIL "+type(e).__name__+": "+str(e),file=sys.stderr)
        raise SystemExit(2)
