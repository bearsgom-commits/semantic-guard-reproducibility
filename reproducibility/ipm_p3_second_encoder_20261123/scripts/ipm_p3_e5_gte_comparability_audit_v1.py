#!/usr/bin/env python3
"""Read-only E5 versus GTE SciFact input/protocol comparability audit.

Does NOT run retrieval, embeddings, Guard or attack. Check exact ID alignment,
qrels source, corpus/query embeddings, and metadata. Reports what cannot be
established from existing files without inventing an E5 encoding protocol.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from pathlib import Path
import numpy as np

E5="intfloat_multilingual-e5-base"
EXPECTED=(5183,1109,300)
def hashfile(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda:f.read(4<<20),b""):h.update(data)
    return h.hexdigest()
def required(path):
    if not path.is_file() or path.is_symlink():raise ValueError(f"missing/symlinked source: {path}")
    return path
def ordered_ids(path):
    v=json.loads(required(path).read_text(encoding="utf-8"))
    if not isinstance(v,list):raise ValueError("ordered ID list required")
    ids=[str(t) for t in v]
    if len(ids)!=len(set(ids)):raise ValueError("duplicate IDs")
    return ids
def qrels_qids(path):
    qs=set();ds=set()
    with required(path).open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f,delimiter="\t")
        if not {"query-id","corpus-id","score"}<=set(reader.fieldnames or []):raise ValueError("invalid qrels")
        for row in reader:
            qs.add(str(row["query-id"]));ds.add(str(row["corpus-id"]))
    return qs,ds
def mat_stats(p,shape):
    m=np.load(required(p),mmap_mode="r",allow_pickle=False)
    if m.shape!=shape or m.dtype!=np.float32:
        raise ValueError(f"unexpected {p} matrix {m.shape}, {m.dtype}")
    norms=np.linalg.norm(m,axis=1)
    if not np.isfinite(m).all() or not np.isfinite(norms).all():
        raise ValueError("nonfinite embeddings")
    return {"shape":list(m.shape),"dtype":str(m.dtype),
        "norm_min":float(norms.min()),"norm_max":float(norms.max()),
        "norm_mean":float(norms.mean()),"zero_norm_count":int(np.sum(norms<1e-10)),
        "embedding_sha256":hashfile(p)}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--gte-encoded",required=True,type=Path)
    p.add_argument("--gte-audit",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    root=a.root.expanduser().resolve(strict=True)
    gte=a.gte_encoded.expanduser().resolve(strict=True)
    audit=a.gte_audit.expanduser().resolve(strict=True)
    out=a.out.expanduser().resolve(strict=False)
    if out.exists() or out.is_symlink():raise ValueError("output must be new")
    for x in (root,gte,audit):
        if x==out or x in out.parents or out in x.parents:raise ValueError("output overlaps inputs")
    src=root/"artifacts/scifact"/E5/"stage3/shared"
    qrel=root/"private_data/beir/scifact/qrels/test.tsv"
    e5_docs=src/"corpus_embeddings_fp32.npy"
    e5_queries=src/"query_embeddings_fp32.npy"
    e5_doc_ids=src/"corpus_doc_ids.json"
    e5_query_ids=src/"query_ids.json"
    gte_docs=gte/"corpus_embeddings_fp32.npy"
    gte_queries=gte/"judged_query_embeddings_fp32.npy"
    gte_doc_ids=gte/"corpus_doc_ids.json"
    gte_query_ids=gte/"judged_query_ids.json"
    encm_path=gte/"encoding_manifest.json"
    auditm_path=audit/"audit_manifest.json"
    em=json.loads(required(encm_path).read_text())
    am=json.loads(required(auditm_path).read_text())
    if em["status"]!="PASS" or am["status"]!="PASS_12":
        raise ValueError("prior GTE runs not PASS")
    if hashfile(qrel)!=em["dataset_input_sha256"]["qrels/test.tsv"]:
        raise ValueError("qrels mismatch with GTE preflight")
    if hashfile(qrel)!=am["input_hashes"]["qrels"]:
        raise ValueError("qrels mismatch with GTE 12-cell audit")
    for name,digest in em["outputs_sha256"].items():
        if hashfile(gte/name)!=digest:raise ValueError(f"GTE input mutated: {name}")
    ed=ordered_ids(e5_doc_ids);eq=ordered_ids(e5_query_ids)
    gd=ordered_ids(gte_doc_ids);gq=ordered_ids(gte_query_ids)
    judged,judged_docs=qrels_qids(qrel)
    if (len(ed),len(eq),len(gq))!=EXPECTED or len(gd)!=len(ed):
        raise ValueError("unexpected collection counts")
    if not judged<=set(eq) or set(gq)!=judged or not judged_docs<=set(ed):
        raise ValueError("qrels ID alignment failed")
    doc_order_equal=(ed==gd)
    doc_set_equal=(set(ed)==set(gd))
    qid_order_e5_judged=[q for q in eq if q in judged]
    judged_order_equal=(qid_order_e5_judged==gq)
    e5_query_pos={qid:i for i,qid in enumerate(eq)}
    e5_selected_indices=[e5_query_pos[q] for q in gq]
    esd=mat_stats(e5_docs,(5183,768))
    esq=mat_stats(e5_queries,(1109,768))
    gsd=mat_stats(gte_docs,(5183,768))
    gsq=mat_stats(gte_queries,(300,768))
    # This records index mapping, not the sensitive IDs themselves.
    mapping_hash=hashlib.sha256(np.asarray(e5_selected_indices,dtype=np.int64).tobytes()).hexdigest()
    # E5 encoder's actual tokenizer/prefix/revision cannot be inferred from its embeddings.
    gate=("ID_ORDER_AND_COHORT_MATCHED_PREPROCESSING_UNVERIFIED"
          if doc_order_equal and judged_order_equal else
          "BLOCKED_CORPUS_OR_QUERY_ORDER_MISMATCH")
    original={str(p.relative_to(root)):hashfile(p) for p in (e5_docs,e5_queries,e5_doc_ids,e5_query_ids,qrel)}
    gtehash={p.name:hashfile(p) for p in (gte_docs,gte_queries,gte_doc_ids,gte_query_ids,encm_path)}
    result={
       "schema":"ipm_p3_e5_gte_comparability_audit_v1",
       "status":gate,
       "e5_corpus_ids_exact_order_equal_gte":doc_order_equal,
       "e5_corpus_ids_equal_set_gte":doc_set_equal,
       "e5_judged_query_ids_exact_order_equal_gte":judged_order_equal,
       "e5_judged_query_ids_equal_set_gte":set(qid_order_e5_judged)==set(gq),
       "qrels_query_ids_identical_gte":set(gq)==judged,
       "e5_full_query_count":len(eq),"gte_judged_query_count":len(gq),
       "e5_judged_query_indices_order_hash":mapping_hash,
       "vector_stats":{"e5_docs":esd,"e5_queries":esq,
                       "gte_docs":gsd,"gte_judged_queries":gsq},
       "gte_document_input_rule":em["encoder"].get("query_prefix","")+" / "+
                                  em["encoder"].get("passage_prefix",""),
       "gte_model_revision":em["encoder"]["resolved_revision"],
       "gte_code_revision":em["encoder"]["resolved_code_revision"],
       "e5_model_revision":"NOT_VERIFIED",
       "e5_title_body_join_and_prefixes":"NOT_VERIFIED_FROM_ORIGINAL_ENCODER_SOURCE",
       "e5_max_length_and_pooling":"NOT_VERIFIED_FROM_ORIGINAL_ENCODER_SOURCE",
       "e5_query_corpus_embedding_lineage":"PREEXISTING_FILES_WITH_SHA_ONLY",
       "ranker_method":"E5 factorial and GTE pilot both use float32 dot/argpartition/argsort and same DCG, but original preprocessing provenance unresolved",
       "inference":"This audit cannot adjudicate E5-versus-GTE model superiority or explain an E5 SciFact performance anomaly.",
       "original_source_hashes":original,
       "gte_input_hashes":gtehash,
       "gte_audit_manifest_sha256":hashfile(auditm_path),
       "retrieval_executed":False,"guard_executed":False,
       "originals_modified":False,
       "required_next":["Recover actual E5 embedding creator source, model revision and config",
         "Verify E5 title/body, query/passage prefixes, pooling, token limit, ordering",
         "Audit historical E5 SciFact low nDCG on identical judged qids before making cross-model claims"]
    }
    if any(hashfile(root/k)!=v for k,v in original.items()):
        raise RuntimeError("source mutated during audit")
    out.mkdir(parents=True,exist_ok=False)
    output=out/"comparability_audit.json"
    with output.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
    print("P3_E5_GTE_COMPARABILITY_AUDIT="+gate)
    print("CORPUS_ID_ORDER_MATCH="+str(doc_order_equal).upper())
    print("JUDGED_QID_ORDER_MATCH="+str(judged_order_equal).upper())
    print("RETRIEVAL_EXECUTED=NO")
    print("E5_ENCODING_PROVENANCE_VERIFIED=NO")
    print(f"OUTPUT={out}")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(f"P3_COMPARABILITY_AUDIT_FAIL {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(2)
