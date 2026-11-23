# IP&M P3 — E5 SciFact canonical raw embedding closeout (2026-11-23 KST)

## Author-reported final SHA check

Both canonical SHA-256 verifications **PASS**, using a Python 3.10-compatible streamed hash procedure:
- `artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/corpus_embeddings_fp32.npy` expected `f332ab059f57d4e274ff5e7b513ee19d27104a3f47c7bb98f0b0f93d643716d4`: PASS.
- `artifacts/scifact/intfloat_multilingual-e5-base/stage3/shared/query_embeddings_fp32.npy` expected `f5b831540582d681f9c2ce9abb8c14e551bc03617180db9a551fa198a0b57f92`: PASS.

The WBS05B SciFact clean-room execution `status=PASS` produced byte-identical corpus/query raw E5 embeddings and seed7 eps32 Guard embeddings. Its model snapshot revision was `d128750597153bb5987e10b1c3493a34e5a4502a` and encoder builder SHA-256 was `984e33c4ba84726bcfb2506a21bbc740bb7b52136acb7b2bbc5d551af7650b2c`.

Known encoder conditions from recovered build script/config and pinned HF snapshot:
- SentenceTransformer intfloat/multilingual-e5-base;
- corpus prefix `passage: `, query prefix `query: `;
- corpus title/newline/text construction;
- SentenceTransformer mean-token pooling; L2 normalize yes; CPU;
- 768 output dimensions.

The earlier WBS05A static `build_contract=false` and `guard_contract=false` remain recorded, but do not negate the **separate** WBS05B SciFact clean reproduction PASS; resolving those static checks would require reviewing their exact predicates.

## Remaining scientific issue
E5's historically low SciFact nDCG@10 was **not** explained by the successful encoder provenance checks. Before interpreting GTE superiority, locate the saved matched 300-qid RAW and Guard search ranking/metric outputs and audit them against unchanged qrels. Do **not** rerun the full historical E5 36-condition retrieval grid or claim source provenance alone proves ranking quality.

Evidence tier: author-shared logs and code excerpts; not a fresh independent execution by this reviewer.
