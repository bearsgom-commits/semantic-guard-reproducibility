#!/usr/bin/env python3
"""Read-only inventory of IP&M Stage 3 MIA inputs and run artifacts.

Does not copy/upload private data or read contents of full embeddings.
The resulting JSON contains local absolute paths: share only after inspection.
Usage: python3 scripts/inventory_local_mia.py [--root PATH] [--output PATH]
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATASETS = ('fiqa', 'scifact', 'trec_covid')
SEEDS = (7, 13, 42)
EPS = (0, 2, 4, 8, 16, 32, 64)
MODEL = 'intfloat_multilingual-e5-base'
FILES = ('attack_summary.json', 'run_meta.json', 'sampling_indices.json', 'attack_item.csv')

def sha256_small(path, max_bytes=4*1024*1024):
    if path.stat().st_size > max_bytes:
        return None
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024*1024), b''):
            h.update(part)
    return h.hexdigest()

def evidence(path, root):
    if not path or not path.is_file():
        return {'present': False}
    stat = path.stat()
    return {
        'present': True,
        'relative_path': str(path.relative_to(root)),
        'size_bytes': stat.st_size,
        'sha256_if_le_4MiB': sha256_small(path),
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path.home()/'Downloads/research/semantic-guard')
    p.add_argument('--output', type=Path, default=Path.home()/'Downloads/ipm_remaining_evidence_inventory.json')
    a = p.parse_args()
    root = a.root.expanduser().resolve()
    if not root.is_dir():
        p.error(f'Project directory not found: {root}')
    rows = []
    for ds in DATASETS:
        for seed in SEEDS:
            for eps in EPS:
                aliases = list(dict.fromkeys((ds, ds.replace('_','-'))))
                candidates = [root/'artifacts'/d/MODEL/'stage3'/f'seed{seed}'/f'eps_{eps:02d}'/'guard_embeddings.npy' for d in aliases]
                guard = next((q for q in candidates if q.is_file()), None)
                out_candidates = [root/'runs'/d/f'seed{seed}'/'attacks'/'stage3'/f'mia_matched_eps_{eps:02d}' for d in aliases]
                attack = next((q for q in out_candidates if q.is_dir()), None)
                rows.append({
                    'dataset': ds, 'seed': seed, 'epsilon': eps,
                    'guard_embedding': evidence(guard, root),
                    'attack_dir_present': bool(attack),
                    'attack_outputs': {name: evidence((attack/name) if attack else None, root) for name in FILES},
                })
    counts = {
        'conditions': len(rows),
        'embedding_present': sum(bool(r['guard_embedding']['present']) for r in rows),
        'attack_summary_present': sum(bool(r['attack_outputs']['attack_summary.json']['present']) for r in rows),
        'run_meta_present': sum(bool(r['attack_outputs']['run_meta.json']['present']) for r in rows),
        'sampling_indices_present': sum(bool(r['attack_outputs']['sampling_indices.json']['present']) for r in rows),
        'attack_item_present': sum(bool(r['attack_outputs']['attack_item.csv']['present']) for r in rows),
    }
    report = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'project_root': str(root),
        'read_only': True,
        'no_file_upload_performed': True,
        'method': 'Checks expected canonical paths only, no recursive search; absence does not prove artifact is not elsewhere',
        'counts': counts,
        'conditions': rows,
    }
    out = a.output.expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print('INVENTORY', out)
    for k, v in counts.items():
        print(f'{k}: {v}')
    print('NOTE: Local paths are included. Review the JSON before sharing; no upload was performed.')

if __name__ == '__main__':
    main()
