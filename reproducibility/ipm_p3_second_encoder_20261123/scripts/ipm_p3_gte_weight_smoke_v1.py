#!/usr/bin/env python3
"""Pinned GTE weights/CLS smoke test, not SciFact retrieval."""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for x in iter(lambda:f.read(1<<20),b""): h.update(x)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--device",choices=("cpu","mps"),default="cpu")
    a=ap.parse_args()
    root=a.preflight.expanduser().resolve(strict=True)
    out=a.out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink() or out==root or root in out.parents or out in root.parents:
        raise ValueError("output must be new, separate directory")
    path=root/"p3_preflight_manifest.json"
    m=json.loads(path.read_text())
    e=m["encoder"]
    assert m["status"]=="PREFLIGHT_PASS_NO_SCIENTIFIC_EMBEDDINGS_GENERATED"
    assert e["model_id"]=="Alibaba-NLP/gte-multilingual-base"
    assert e["resolved_revision"]=="9bbca17d9273fd0d03d5725c7a4b0f6b45142062"
    assert e["resolved_code_revision"]=="40ced75c3017eb27626c9d4ea981bde21a2662f4"
    assert e["output_dimension"]==768 and e["max_length"]==512
    assert e["pooling"]=="last_hidden_state[:,0] (CLS), then L2 normalize"
    import torch
    from transformers import AutoModel, AutoTokenizer
    if a.device=="mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS not available")
    tok=AutoTokenizer.from_pretrained(e["model_id"],revision=e["resolved_revision"])
    model=AutoModel.from_pretrained(
        e["model_id"],revision=e["resolved_revision"],
        code_revision=e["resolved_code_revision"],trust_remote_code=True
    ).to(a.device).eval()
    texts=["What evidence supports the claim?","The study reports experimental evidence."]
    batch=tok(texts,max_length=512,padding=True,truncation=True,return_tensors="pt")
    with torch.inference_mode():
        last=model(**{k:v.to(a.device) for k,v in batch.items()}).last_hidden_state
        v=torch.nn.functional.normalize(last[:,0].float(),p=2,dim=-1).cpu().numpy()
    assert v.shape==(2,768) and np.isfinite(v).all()
    assert np.max(np.abs(np.linalg.norm(v,axis=1)-1))<1e-5
    data={"status":"PASS_WEIGHTS_CLS_ONLY","preflight_sha256":sha(path),
          "model_revision":e["resolved_revision"],"code_revision":e["resolved_code_revision"],
          "device":a.device,"torch":torch.__version__,
          "transformers":__import__("transformers").__version__,
          "shape":[2,768],"cosine":float(v[0]@v[1]),
          "embedding_sha256":hashlib.sha256(v.tobytes()).hexdigest(),
          "input_scope":"two synthetic sentences; no SciFact content",
          "retrieval_executed":False}
    out.mkdir(parents=True,exist_ok=False)
    (out/"weight_smoke.json").write_text(json.dumps(data,indent=2)+"\n")
    print("P3_WEIGHT_SMOKE_PASS")
    print("MODEL_WEIGHTS_LOADED=YES")
    print("EMBEDDING_SHAPE=2x768")
    print("RETRIEVAL_EXECUTED=NO")
    print(f"OUTPUT={out}")

if __name__=="__main__":
    try: main()
    except Exception as ex:
        print(f"P3_WEIGHT_SMOKE_FAIL {type(ex).__name__}: {ex}",file=sys.stderr)
        raise SystemExit(2)
