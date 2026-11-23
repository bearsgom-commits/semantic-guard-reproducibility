#!/usr/bin/env python3
"""Read-only provenance audit of legacy attack summaries versus prospective diagonal cells.

Does not establish security equivalence and NEVER reports off-diagonal security results.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

DATASETS = {'fiqa': 'fiqa', 'scifact': 'scifact', 'trec-covid': 'trec_covid'}
SEEDS = (7, 13, 42)
DIAGONAL = ((0, 128, 4), (32, 320, 10))
ATTACKS = ('mia', 'mia_matched', 'reid')


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def safe_json(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('missing/unsafe file: ' + str(path))
    return json.loads(path.read_text(encoding='utf-8'))


def select_attack_dir(root, artifact_slug, display_slug, seed, attack, eps):
    # TREC-COVID has historically used both spellings in runs/ and artifacts/.
    possibilities = []
    for slug in dict.fromkeys((artifact_slug, display_slug)):
        path = root / 'runs' / slug / ('seed' + str(seed)) / 'attacks' / 'stage3' / ('%s_eps_%02d' % (attack, eps))
        if path.joinpath('run_meta.json').is_file() and path.joinpath('attack_summary.json').is_file():
            possibilities.append(path)
    if len(possibilities) == 0:
        raise ValueError('attack files not found under either dataset slug')
    if len(possibilities) > 1:
        # Do not guess which duplicated run is authoritative.
        raise ValueError('multiple attack directories: ' + '; '.join(map(str, possibilities)))
    return possibilities[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--report-dir', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.expanduser().resolve(strict=True)
    results = args.results.expanduser().resolve(strict=True)
    report = args.report_dir.expanduser().absolute()
    if report.exists():
        parser.error('refusing to overwrite report-dir: ' + str(report))
    records, issues = [], []
    for display, artifact in DATASETS.items():
        for seed in SEEDS:
            for eps, dim, bits in DIAGONAL:
                cell = results / f'{display}_s{seed}_D{dim}_B{bits}'
                manifest = safe_json(cell / 'cell_manifest.json')
                canonical = root / 'artifacts' / artifact / 'intfloat_multilingual-e5-base' / 'stage3' / f'seed{seed}' / f'eps_{eps:02d}' / 'guard_embeddings.npy'
                for attack in ATTACKS:
                    label = f'{display}/s{seed}/eps{eps}/{attack}'
                    rec = {'dataset': display, 'seed': seed, 'eps': eps, 'dimension': dim, 'bits': bits, 'attack': attack, 'status': '', 'path_match': '', 'target_dim_match': '', 'manifest_source_match': '', 'sample_size': '', 'attack_name': '', 'membership_mode': '', 'note': ''}
                    try:
                        folder = select_attack_dir(root, artifact, display, seed, attack, eps)
                        meta = safe_json(folder / 'run_meta.json')
                        summary = safe_json(folder / 'attack_summary.json')
                        if int(summary.get('seed', -1)) != seed or int(summary.get('epsilon', -1)) != eps:
                            raise ValueError('attack summary seed/epsilon mismatch')
                        if summary.get('dataset', '').replace('_','-') != display:
                            raise ValueError('attack summary dataset mismatch')
                        path = meta.get('guard_embedding_path')
                        if not path:
                            raise ValueError('missing explicit guard_embedding_path')
                        # Do not load embedding vectors; resolve path without modifying it.
                        linked = Path(path).expanduser().resolve(strict=False)
                        rec['path_match'] = str(linked == canonical.resolve(strict=False))
                        if rec['path_match'] != 'True':
                            raise ValueError('attack does not use canonical diagonal Guard artifact')
                        if not canonical.is_file():
                            raise ValueError('canonical historical Guard artifact missing')
                        target_dim = meta.get('target_dim', summary.get('target_dim'))
                        guard_shape = meta.get('guard_shape')
                        rec['target_dim_match'] = 'UNREPORTED' if target_dim is None else str(int(target_dim) == dim)
                        if guard_shape is not None and int(guard_shape[-1]) != dim:
                            raise ValueError('guard_shape dimensional mismatch')
                        if rec['target_dim_match'] == 'False':
                            raise ValueError('target_dim mismatch')
                        rec['manifest_source_match'] = 'NOT_IN_ATTACK_META'
                        rec['sample_size'] = summary.get('sample_size', '')
                        rec['attack_name'] = summary.get('attack_name', '')
                        rec['membership_mode'] = summary.get('membership_mode', '')
                        rec['status'] = 'PATH_AND_LABEL_ALIGNED_NOT_SECURITY_EQUIVALENT'
                        rec['note'] = 'No direct matrix/hash binding to attack run; prior sampled-vector audit separate'
                    except Exception as exc:
                        rec['status'] = 'REVIEW_REQUIRED'
                        rec['note'] = str(exc)
                        issues.append(label + ': ' + str(exc))
                    records.append(rec)
                    print('LINEAGE', label, rec['status'], rec['note'], flush=True)
    # The report is written only to a brand-new, separate location, never original results.
    report.mkdir(parents=True, exist_ok=False)
    with (report / 'security_lineage_diagonal_54.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)
    protocol = {'purpose': 'Read-only legacy-security provenance inventory; no attack performed',
                'record_count': len(records), 'issues': issues, 'status_counts': dict(Counter(r['status'] for r in records)),
                'limitations': ['Only two historical diagonal conditions, no off-diagonal attacks', 'No query vector identity or all-row corpus identity proven', 'Guard path and epsilon labels cannot prove attack comparability', 'Old MIA and matched MIA use different inference designs', 'No derived privacy guarantees', 'No original or factorial files modified']}
    (report / 'security_lineage_protocol.json').write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (report / 'SHA256SUMS.txt').write_text('\n'.join(file_hash(report / n) + '  ' + n for n in ('security_lineage_diagonal_54.csv', 'security_lineage_protocol.json')) + '\n', encoding='utf-8')
    print(f'LINEAGE_RECORDS={len(records)}')
    print(f'LINEAGE_ISSUES={len(issues)}')
    print('LINEAGE_STATUS=' + ('PASS_PATH_LABEL_54_SECURITY_EQUIVALENCE_UNPROVEN' if not issues else 'REVIEW_REQUIRED'))
    print('ORIGINALS_AND_EXPERIMENT_RESULTS_WRITTEN=NO')
    print('NEW_REPORT_DIRECTORY=' + str(report))
    return 0 if not issues else 2


if __name__ == '__main__':
    raise SystemExit(main())
