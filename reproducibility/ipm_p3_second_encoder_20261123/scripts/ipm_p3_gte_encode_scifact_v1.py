#!/usr/bin/env python3
"""P3 SciFact GTE encoding once; immutable inputs, isolated output, pinned weights.

Does NOT rank, run Guard, overwrite E5 vectors or modify frozen experiments.
CPU default; --device mps optional. Corpus/query construction EXACTLY follows
the frozen P3 preflight, with no model-specific prefixes.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from pathlib import Path
import numpy as np

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(4<<20),b""):h.update(b)
    return h.hexdigest()

def items(p,kind):
    ids=[];texts=[];hashes=[]
    with p.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():continue
            obj=json.loads(line)
            key=str(obj.get("_id",obj.get("id","")))
            text=(str(obj.get("title","") or "")+"\n"+str(obj.get("text","") or "")).strip() if kind=="corpus" else str(obj.get("text","") or "").strip()
            if not key or not text:raise ValueError("missing corpus/query ID or text")
            ids.append(key);texts.append(text);hashes.append(hashlib.sha256(text.encode("utf-8")).hexdigest())
    if len(ids)!=len(set(ids)):raise ValueError("duplicate IDs")
    return ids,texts,hashes

def ids_hash(ids):
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()

def text_hash(h):
    return hashlib.sha256("\n".join(h).encode("utf-8")).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--preflight",required=True,type=Path)
    p.add_argument("--weight-smoke",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--device",choices=("cpu","mps"),default="mps")
    p.add_argument("--batch-size",type=int,default=8)
    a=p.parse_args()
    root=a.root.expanduser().resolve(strict=True)
    pf=a.preflight.expanduser().resolve(strict=True)
    ws=a.weight_smoke.expanduser().resolve(strict=True)
    out=a.out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink() or out==root or root in out.parents or out in root.parents:
        raise ValueError("output must be new and outside research root")
    if a.batch_size<1 or a.batch_size>128:raise ValueError("invalid batch size")
    pfpath=pf/"p3_preflight_manifest.json"
    pre=json.loads(pfpath.read_text())
    weight=json.loads((ws/"weight_smoke.json").read_text())
    e=pre["encoder"]
    assert pre["status"]=="PREFLIGHT_PASS_NO_SCIENTIFIC_EMBEDDINGS_GENERATED"
    assert weight["status"]=="PASS_WEIGHTS_CLS_ONLY"
    assert weight["preflight_sha256"]==sha(pfpath)
    assert weight["model_revision"]==e["resolved_revision"]
    assert weight["code_revision"]==e["resolved_code_revision"]
    assert e["model_id"]=="Alibaba-NLP/gte-multilingual-base"
    assert e["resolved_revision"]=="9bbca17d9273fd0d03d5725c7a4b0f6b45142062"
    assert e["resolved_code_revision"]=="40ced75c3017eb27626c9d4ea981bde21a2662f4"
    assert e["output_dimension"]==768 and e["max_length"]==512
    data=root/"private_data/beir/scifact"
    sourcepaths={"corpus.jsonl":data/"corpus.jsonl","queries.jsonl":data/"queries.jsonl","qrels/test.tsv":data/"qrels/test.tsv"}
    for key,path in sourcepaths.items():
        if path.is_symlink() or sha(path)!=pre["dataset_input_sha256"][key]:raise ValueError("input hash changed: "+key)
    dids,docs,dh=items(sourcepaths["corpus.jsonl"],"corpus")
    qids,queries,qh=items(sourcepaths["queries.jsonl"],"query")
    assert len(dids)==5183 and len(qids)==1109
    assert ids_hash(dids)==pre["ordered_id_sha256"]["corpus_ids"]
    assert ids_hash(qids)==pre["ordered_id_sha256"]["query_ids"]
    assert text_hash(dh)==pre["constructed_text_sha256"]["corpus_text_sequence"]
    assert text_hash(qh)==pre["constructed_text_sha256"]["query_text_sequence"]
    judged=set()
    with sourcepaths["qrels/test.tsv"].open(newline="") as f:
        for row in csv.DictReader(f,delimiter="\t"):judged.add(str(row["query-id"]))
    assert len(judged)==300 and judged<=set(qids)
    selected_qids=[q for q in qids if q in judged]
    selected_queries=[queries[i] for i,q in enumerate(qids) if q in judged]
    import torch
    from transformers import AutoModel,AutoTokenizer
    if a.device=="mps" and not torch.backends.mps.is_available():
        raise ValueError("MPS unavailable: rerun in fresh path with --device cpu")
    tok=AutoTokenizer.from_pretrained(e["model_id"],revision=e["resolved_revision"])
    model=AutoModel.from_pretrained(e["model_id"],revision=e["resolved_revision"],
        code_revision=e["resolved_code_revision"],trust_remote_code=True).to(a.device).eval()
    def encode(texts,label):
        chunks=[]
        for pos in range(0,len(texts),a.batch_size):
            block=tok(texts[pos:pos+a.batch_size],padding=True,truncation=True,
                max_length=512,return_tensors="pt")
            with torch.inference_mode():
                hidden=model(**{k:v.to(a.device) for k,v in block.items()}).last_hidden_state
                z=torch.nn.functional.normalize(hidden[:,0].float(),p=2,dim=-1)
            chunks.append(z.cpu().numpy().astype(np.float32,copy=False))
            if pos==0 or pos+ a.batch_size>=len(texts) or (pos//a.batch_size+1)%50==0:
                print(f"ENCODE_{label}={min(pos+a.batch_size,len(texts))}/{len(texts)}",flush=True)
        mat=np.concatenate(chunks,axis=0)
        if mat.shape!=(len(texts),768) or not np.isfinite(mat).all():
            raise ValueError(label+" bad embedding shape/finite")
        if np.max(np.abs(np.linalg.norm(mat,axis=1)-1))>2e-5:
            raise ValueError(label+" not unit length")
        return mat
    docmat=encode(docs,"CORPUS")
    qrymat=encode(selected_queries,"QUERIES")
    for key,path in sourcepaths.items():
        if sha(path)!=pre["dataset_input_sha256"][key]:raise RuntimeError("source changed during encoding: "+key)
    out.mkdir(parents=True,exist_ok=False)
    np.save(out/"corpus_embeddings_fp32.npy",docmat,allow_pickle=False)
    np.save(out/"judged_query_embeddings_fp32.npy",qrymat,allow_pickle=False)
    (out/"corpus_doc_ids.json").write_text(json.dumps(dids,ensure_ascii=False)+"\n")
    (out/"judged_query_ids.json").write_text(json.dumps(selected_qids,ensure_ascii=False)+"\n")
    report={
        "schema":"ipm_p3_gte_scifact_encoded_v1","status":"PASS",
        "encoder":e,"device":a.device,"batch_size":a.batch_size,
        "test_qids":300,"doc_count":5183,"input_preflight_sha256":sha(pfpath),
        "weight_smoke_sha256":sha(ws/"weight_smoke.json"),
        "dataset_input_sha256":pre["dataset_input_sha256"],
        "outputs_sha256":{p.name:sha(p) for p in out.iterdir() if p.is_file()},
        "software":{"python":sys.version.split()[0],"torch":torch.__version__,
                    "transformers":__import__("transformers").__version__,
                    "numpy":np.__version__},
        "retrieval_executed":False,
        "originals_modified":False}
    (out/"encoding_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("P3_ENCODE_PASS")
    print("CORPUS_EMBEDDINGS=5183x768")
    print("JUDGED_QUERY_EMBEDDINGS=300x768")
    print("RETRIEVAL_EXECUTED=NO")
    print(f"OUTPUT={out}")
if __name__=="__main__":
    try:main()
    except Exception as ex:
        print(f"P3_ENCODE_FAIL {type(ex).__name__}: {ex}",file=sys.stderr)
        raise SystemExit(2)
