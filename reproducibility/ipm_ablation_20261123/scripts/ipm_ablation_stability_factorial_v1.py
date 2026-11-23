#!/usr/bin/env python3
"""Read-only Stage3 RAW-vs-new 36-cell stability analysis.

Reproduces *the supplied* compute_stability.py definitions, on test-judged
queries only. It does not claim to re-run historical experiments or security
analysis. Outputs are written to a NEW separate directory only.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
import sys
import numpy as np

DATASETS = (("fiqa", "fiqa", 648), ("scifact", "scifact", 300),
            ("trec_covid", "trec-covid", 50))
SEEDS = (7, 13, 42)
FACTORS = ((128, 4), (128, 10), (320, 4), (320, 10))
METRICS = ("top1_same", "overlap_at_10", "kendall_tau_at_50", "flip_at_10", "stability_score_raw")

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read_jsonl(path, expected=None):
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing/unsafe rankings: {path}")
    rows = {}
    with path.open(encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            qid = str(r['qid'])
            docs = tuple(str(x) for x in r['top_doc_ids'])
            if qid in rows or len(docs) != 100 or len(set(docs)) != 100:
                raise ValueError(f"Duplicate qid or invalid Top100: {path}: {qid}")
            rows[qid] = dict(r, top_doc_ids=docs)
    if expected is not None and len(rows) != expected:
        raise ValueError(f"Row count mismatch {path}: {len(rows)} != {expected}")
    return rows

def read_metrics(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing/unsafe metrics: {path}")
    result = {}
    with path.open(encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            q = str(row['qid'])
            if q in result:
                raise ValueError(f"Duplicated metrics query: {q}")
            result[q] = int(float(row['hit_at_10']))
            if result[q] not in (0,1):
                raise ValueError(f"Invalid hit@10 for {q}")
    return result

def read_qrels(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing/unsafe qrels: {path}")
    data = defaultdict(dict)
    with path.open(encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            try:
                score = int(float(r['score']))
            except (ValueError,TypeError):
                continue
            data[str(r['query-id'])][str(r['corpus-id'])] = score
    return dict(data)

def hit_at_10(docs, relevance):
    return int(any(relevance.get(d, 0) > 0 for d in docs[:10]))

def tau_on_union_original(ref_docs, tgt_docs, pool_k=50):
    """Vectorized equivalent of supplied pairwise tau_on_union(), including ties.

    Missing documents are given rank 1e9; ties get counted as discordant
    unless both rank-order signs are equal, just like original source.
    """
    pool = list(dict.fromkeys(ref_docs[:pool_k] + tgt_docs[:pool_k]))
    n = len(pool)
    if n < 2:
        return 1.0
    rm = {doc: i for i, doc in enumerate(ref_docs)}
    tm = {doc: i for i, doc in enumerate(tgt_docs)}
    rr = np.asarray([rm.get(doc, 10**9) for doc in pool], dtype=np.int64)
    tr = np.asarray([tm.get(doc, 10**9) for doc in pool], dtype=np.int64)
    i, j = np.triu_indices(n, 1)
    same = (np.sign(rr[i] - rr[j]) == np.sign(tr[i] - tr[j]))
    return float((2 * np.count_nonzero(same) - len(same)) / len(same))

def load_cell(results, ds, seed, dim, bits, expected):
    cell = results / f'{ds}_s{seed}_D{dim}_B{bits}'
    mp = cell / 'cell_manifest.json'
    ranking = cell / 'test_rankings_top100.jsonl'
    if not mp.is_file() or mp.is_symlink():
        raise ValueError(f"Missing/unsafe manifest: {mp}")
    m = json.loads(mp.read_text(encoding='utf-8'))
    if (m.get('schema'), m.get('dataset'), m.get('seed'), m.get('dimension'),
            m.get('quantization_bits'), m.get('tested_queries')) != (
            'ipm_ablation_factorial_v1', ds, seed, dim, bits, expected):
        raise ValueError(f"Manifest condition mismatch: {cell}")
    if sha256(ranking) != m['output_sha256']['test_rankings_top100.jsonl']:
        raise ValueError(f"Output SHA256 mismatch: {ranking}")
    return read_jsonl(ranking, expected), m

def run(args):
    root, results, report = map(lambda p: Path(p).expanduser().resolve(),
                                (args.root, args.results, args.report_dir))
    if not root.is_dir() or not results.is_dir() or root == results:
        raise ValueError('Invalid root/results')
    for parent in (root, results):
        if report == parent or parent in report.parents or report in parent.parents:
            raise ValueError('Report directory cannot overlap source/results directory')
    if report.exists():
        raise FileExistsError(f'Never overwrite existing report: {report}')
    if args.overlap_k != 10 or args.kendall_pool_k != 50:
        raise ValueError('Original confirmed parameters are overlap_k=10, kendall_pool_k=50')

    query_rows, summary_rows = [], []
    checks = []
    for raw_ds, ds, expected in DATASETS:
        qrel_name = 'trec-covid' if ds == 'trec-covid' else ds
        qp = root / 'private_data/beir' / qrel_name / 'qrels/test.tsv'
        qrels = read_qrels(qp)
        if len(qrels) != expected:
            raise ValueError(f'Qrels judged query count {ds}: {len(qrels)} != {expected}')
        for seed in SEEDS:
            refbase = root / 'runs' / raw_ds / f'seed{seed}' / 'retrieval/stage3/raw/eps_00'
            raw = read_jsonl(refbase / 'rankings_top100.jsonl')
            raw_hit = read_metrics(refbase / 'metrics_query.csv')
            if not set(qrels).issubset(raw) or not set(qrels).issubset(raw_hit):
                raise ValueError(f'Missing judged qids in RAW dataset={ds} seed={seed}')
            # Ensure stored RAW binary decisions and ranks agree with current test qrels.
            for qid, relevances in qrels.items():
                calc = hit_at_10(raw[qid]['top_doc_ids'], relevances)
                if calc != raw_hit[qid]:
                    raise ValueError(f'RAW hit mismatch: {ds} seed={seed} qid={qid} stored={raw_hit[qid]} calculated={calc}')
            for dim, bits in FACTORS:
                cellname = f'{ds}_s{seed}_D{dim}_B{bits}'
                cell, manifest = load_cell(results, ds, seed, dim, bits, expected)
                if set(cell) != set(qrels):
                    raise ValueError(f'Test qids differ from qrels: {cellname}')
                rows = []
                for qid, relevant in qrels.items():
                    rd = raw[qid]['top_doc_ids']
                    td = cell[qid]['top_doc_ids']
                    ref_hit = raw_hit[qid]
                    tgt_hit = hit_at_10(td, relevant)
                    if int(cell[qid]['hit_at_10']) != tgt_hit:
                        raise ValueError(f'Ablation hit mismatch: {cellname} qid={qid}')
                    top1 = int(rd[0] == td[0])
                    overlap = len(set(rd[:10]) & set(td[:10])) / 10.0
                    tau = tau_on_union_original(rd, td, 50)
                    flip = int(ref_hit != tgt_hit)
                    stability = 0.4 * top1 + 0.4 * overlap + 0.2 * (1 - flip)
                    record = dict(dataset=ds, seed=seed, dimension=dim, bits=bits,
                                  qid=qid, top1_same=top1, overlap_at_10=overlap,
                                  kendall_tau_at_50=tau, flip_at_10=flip,
                                  stability_score_raw=stability,
                                  raw_hit_at_10=ref_hit, target_hit_at_10=tgt_hit)
                    rows.append(record)
                vals = {m: sum(float(r[m]) for r in rows) / len(rows) for m in METRICS}
                summary_rows.append(dict(dataset=ds, seed=seed, dimension=dim,
                                         bits=bits, n_queries=len(rows), **vals))
                query_rows.extend(rows)
                print(f'CELL_PASS={cellname} queries={len(rows)} '
                      f'top1={vals["top1_same"]:.8f} overlap10={vals["overlap_at_10"]:.8f} '
                      f'tau50={vals["kendall_tau_at_50"]:.8f} flip10={vals["flip_at_10"]:.8f}', flush=True)
                checks.append(cellname)

    if len(checks) != 36:
        raise ValueError(f'Cell count {len(checks)} != 36')
    # Blocked factorial contrast: first average each cell over three fixed seeds.
    mean_rows = []
    effect_rows = []
    for _, ds, _ in DATASETS:
        group = [r for r in summary_rows if r['dataset'] == ds]
        cells = {}
        for d,b in FACTORS:
            reps = [r for r in group if (r['dimension'],r['bits'])==(d,b)]
            if len(reps) != 3: raise ValueError('Missing seed')
            cells[d,b] = {m: sum(r[m] for r in reps)/3 for m in METRICS}
            mean_rows.append(dict(dataset=ds, dimension=d, bits=b, **cells[d,b]))
        for m in METRICS:
            a,b,c,d = (cells[key][m] for key in FACTORS)
            # d=320,10; c=320,4; b=128,10; a=128,4
            effects = {
                'dimension_320_minus_128': ((c-a)+(d-b))/2,
                'bits_10_minus_4': ((b-a)+(d-c))/2,
                'interaction_difference_of_differences': (d-c)-(b-a)
            }
            for name, delta in effects.items():
                effect_rows.append(dict(dataset=ds, metric=m, effect=name, delta=delta))

    report.mkdir(parents=True, exist_ok=False)
    def save_csv(filename, records):
        with (report/filename).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f, fieldnames=list(records[0]))
            w.writeheader(); w.writerows(records)
    save_csv('stability_query_36.csv', query_rows)
    save_csv('stability_cells_36.csv', summary_rows)
    save_csv('stability_factorial_means_12.csv', mean_rows)
    save_csv('stability_factorial_effects_descriptive_15.csv', effect_rows)
    protocol = {
      'status':'DESCRIPTIVE_ANALYSIS_NOT_STATISTICAL_INFERENCE',
      'source':'User-supplied compute_stability.py / aggregate_stage3.py',
      'comparison':'Historical RAW retrieval files vs 36 NEW PROSPECTIVE factor cells, judged test qids only',
      'parameters':{'overlap_k':10,'kendall_pool_k':50,'seeds':list(SEEDS)},
      'definitions':{
        'top1_same':'int(raw_top1_doc_id == target_top1_doc_id)',
        'overlap_at_10':'len(set(raw_top10) & set(target_top10)) / 10',
        'kendall_tau_at_50':'original tau_on_union; union top50; missing ranks=1e9; tied comparisons not corrected',
        'flip_at_10':'int(raw_hit_at_10 != target_hit_at_10); hit means at least one qrels rel>0 in top10',
        'stability_score_raw':'0.4*top1 + 0.4*overlap + 0.2*(1-flip)'
      },
      'limitations':['RAW source search implementation differs from prospective exact search until proven otherwise',
                     'No attribution of RAW-vs-ablation differences solely to Guard transformation',
                     'Descriptive 2x2 effects across three fixed seeds only; no CIs/p-values in this tool',
                     'Not a security evaluation or behavioral/operational decision measurement',
                     'Stored rankings are used without rerunning retrieval'],
      'source_file_sha256':{
          'compute_stability.py':sha256(root/'repo/src/stage3/compute_stability.py'),
          'aggregate_stage3.py':sha256(root/'repo/src/stage3/aggregate_stage3.py'),
          'common.yaml':sha256(root/'repo/configs/stage3/common.yaml')
      },
      'n_cells':len(summary_rows),'n_query_records':len(query_rows)
    }
    (report/'analysis_protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'STABILITY_CELLS={len(summary_rows)}')
    print(f'STABILITY_QUERY_RECORDS={len(query_rows)}')
    print(f'STABILITY_EFFECT_RECORDS={len(effect_rows)}')
    print('STABILITY_STATUS=PASS_ALL_36')
    print('ORIGINALS_AND_EXPERIMENT_RESULTS_WRITTEN=NO')
    print(f'NEW_REPORT_DIRECTORY={report}')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',required=True)
    p.add_argument('--results',required=True)
    p.add_argument('--report-dir',required=True)
    p.add_argument('--overlap-k',type=int,default=10)
    p.add_argument('--kendall-pool-k',type=int,default=50)
    a=p.parse_args()
    try: run(a)
    except Exception as e:
        print(f'STABILITY_STATUS=FAIL {type(e).__name__}: {e}',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
