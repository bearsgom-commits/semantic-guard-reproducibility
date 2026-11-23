#!/usr/bin/env python3
"""Read-only preflight for the IP&M P3 second-encoder sensitivity experiment.

No embeddings, Guard outputs, rankings, or manuscript files are generated.
The script resolves and pins the exact Hugging Face revision for
Alibaba-NLP/gte-multilingual-base, validates the SciFact BEIR input cohort, and
records a prospective encoding contract before any scientific run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata as md
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MODEL_ID_DEFAULT = "Alibaba-NLP/gte-multilingual-base"
EXPECTED = {"corpus": 5183, "queries": 1109, "test_qrels_qids": 300}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"missing/unsafe input: {path}")
    return path


def safe_new_out(root: Path, out: Path) -> Path:
    root = root.resolve(strict=True)
    out = out.expanduser().resolve(strict=False)
    if out == root or root in out.parents or out in root.parents:
        raise ValueError("output must be strictly outside research root")
    if out.exists() or out.is_symlink():
        raise FileExistsError(f"refusing overwrite: {out}")
    return out


def load_jsonl(path: Path, kind: str):
    ids = []
    text_hashes = []
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            item_id = str(obj.get("_id", obj.get("id", "")))
            if not item_id:
                raise ValueError(f"missing ID at {path}:{lineno}")
            if kind == "corpus":
                title = str(obj.get("title", "") or "")
                body = str(obj.get("text", "") or "")
                text = f"{title}\n{body}".strip()
            else:
                text = str(obj.get("text", "") or "").strip()
            if not text:
                raise ValueError(f"empty {kind} text at {path}:{lineno}")
            ids.append(item_id)
            text_hashes.append(hashlib.sha256(text.encode("utf-8")).hexdigest())
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate {kind} IDs")
    return ids, text_hashes


def load_qrels(path: Path):
    qids = set()
    docids = set()
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        if not {"query-id", "corpus-id", "score"} <= set(r.fieldnames or []):
            raise ValueError("unexpected qrels headers")
        for row in r:
            qids.add(str(row["query-id"]))
            docids.add(str(row["corpus-id"]))
    return qids, docids


def package_version(name: str):
    try:
        return md.version(name)
    except md.PackageNotFoundError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--model-id", default=MODEL_ID_DEFAULT)
    ap.add_argument("--model-revision", default=MODEL_REVISION_DEFAULT, help="official legacy-compatible pinned revision; exact full SHA is written to manifest")
    ap.add_argument("--max-length", type=int, default=512, help="prospective fixed truncation budget for the sensitivity experiment")
    a = ap.parse_args()

    root = a.root.expanduser().resolve(strict=True)
    out = safe_new_out(root, a.out)
    if a.max_length <= 0:
        raise ValueError("max length must be positive")

    data = root / "private_data" / "beir" / "scifact"
    corpus = require_file(data / "corpus.jsonl")
    queries = require_file(data / "queries.jsonl")
    qrels = require_file(data / "qrels" / "test.tsv")

    corpus_ids, corpus_text_hashes = load_jsonl(corpus, "corpus")
    query_ids, query_text_hashes = load_jsonl(queries, "query")
    qrel_qids, qrel_docids = load_qrels(qrels)
    if len(corpus_ids) != EXPECTED["corpus"] or len(query_ids) != EXPECTED["queries"] or len(qrel_qids) != EXPECTED["test_qrels_qids"]:
        raise ValueError(f"unexpected SciFact counts: corpus={len(corpus_ids)} queries={len(query_ids)} qrel_qids={len(qrel_qids)}")
    if not qrel_qids <= set(query_ids) or not qrel_docids <= set(corpus_ids):
        raise ValueError("qrels ID alignment failure")

    try:
        from huggingface_hub import model_info
        from packaging.version import Version
        from transformers import AutoConfig, AutoTokenizer
    except Exception as exc:
        raise RuntimeError("requires huggingface_hub, packaging and transformers") from exc

    transformers_version = package_version("transformers")
    if transformers_version is None or Version(transformers_version) < Version("4.36.0"):
        raise RuntimeError(f"transformers>=4.36.0 required by model card; found {transformers_version}")

    info = model_info(a.model_id, revision=a.model_revision)
    resolved_revision = str(info.sha)
    if len(resolved_revision) != 40:
        raise RuntimeError(f"unexpected resolved model revision: {resolved_revision}")

    tokenizer = AutoTokenizer.from_pretrained(a.model_id, revision=resolved_revision, trust_remote_code=True)
    config = AutoConfig.from_pretrained(a.model_id, revision=resolved_revision, trust_remote_code=True)

    probe_texts = ["query preflight", "document preflight"]
    probe = tokenizer(probe_texts, max_length=a.max_length, padding=True, truncation=True, return_tensors="np")
    if "input_ids" not in probe or probe["input_ids"].shape[0] != 2 or probe["input_ids"].shape[1] > a.max_length:
        raise RuntimeError("tokenizer preflight failed")

    hidden_size = int(getattr(config, "hidden_size", 0) or 0)
    if hidden_size != 768:
        raise RuntimeError(f"expected 768 hidden/output dimension for selected GTE candidate, got {hidden_size}")

    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": "ipm_p3_second_encoder_preflight_v1",
        "created_at_utc": now_iso(),
        "status": "PREFLIGHT_PASS_NO_SCIENTIFIC_EMBEDDINGS_GENERATED",
        "purpose": "freeze second-encoder identity and SciFact input cohort before 4-cell pilot",
        "dataset": "scifact",
        "dataset_counts": {
            "corpus": len(corpus_ids),
            "queries": len(query_ids),
            "test_qrels_qids": len(qrel_qids),
        },
        "dataset_input_sha256": {
            "corpus.jsonl": sha256(corpus),
            "queries.jsonl": sha256(queries),
            "qrels/test.tsv": sha256(qrels),
        },
        "ordered_id_sha256": {
            "corpus_ids": hashlib.sha256("\n".join(corpus_ids).encode()).hexdigest(),
            "query_ids": hashlib.sha256("\n".join(query_ids).encode()).hexdigest(),
        },
        "constructed_text_sha256": {
            "corpus_text_sequence": hashlib.sha256("\n".join(corpus_text_hashes).encode()).hexdigest(),
            "query_text_sequence": hashlib.sha256("\n".join(query_text_hashes).encode()).hexdigest(),
            "rule": "corpus=(title + newline + text).strip(); query=text.strip()",
        },
        "encoder": {
            "model_id": a.model_id,
            "requested_revision": a.model_revision,
            "resolved_revision": resolved_revision,
            "license_reported_by_hub": getattr(info, "card_data", {}).get("license") if isinstance(getattr(info, "card_data", None), dict) else None,
            "output_dimension": hidden_size,
            "pooling": "last_hidden_state[:,0] (CLS), then L2 normalize",
            "query_prefix": "",
            "passage_prefix": "",
            "max_length": a.max_length,
            "trust_remote_code": True,
            "scientific_weights_loaded": False,
        },
        "prospective_control_note": "max_length=512 is fixed for this sensitivity experiment to reduce preprocessing/context-window confounding; revision=9bbca17 follows the official legacy-transformers compatibility instruction; this manifest does not claim it reconstructs every historical E5 tokenizer detail",
        "software": {
            "python": sys.version.split()[0],
            "transformers": transformers_version,
            "huggingface_hub": package_version("huggingface-hub"),
            "torch": package_version("torch"),
            "numpy": package_version("numpy"),
        },
        "official_sources": [
            "https://huggingface.co/Alibaba-NLP/gte-multilingual-base",
            "https://aclanthology.org/2024.emnlp-industry.103/",
        ],
        "next_gate": "Do not encode corpus until this exact revision and prospective input contract are accepted; then encode once and run SciFact seed7 D/B four-cell pilot in an isolated path.",
    }
    path = out / "p3_preflight_manifest.json"
    with path.open("x", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")

    print("P3_PREFLIGHT_PASS")
    print(f"MODEL_ID={a.model_id}")
    print(f"MODEL_REVISION={resolved_revision}")
    print(f"SCIFACT_COUNTS={len(corpus_ids)}/{len(query_ids)}/{len(qrel_qids)}")
    print("SCIENTIFIC_EMBEDDINGS_GENERATED=NO")
    print(f"OUTPUT={out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P3_PREFLIGHT_FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
