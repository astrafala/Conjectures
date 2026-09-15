#!/usr/bin/env python3
"""Write and compile the generating-function identity papers.

    PAPER_DATE='15 September 2026' python3 src/build_gfident.py
    python3 src/install_vein.py gi gfident_hits.json gf-identity
"""
import json
import os
import subprocess

import gfidbuild
import withdrawnset

HITS = os.environ.get('HITS', 'gfident_hits.json')
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
made, failed = 0, []
for h in sorted(json.load(open(HITS)), key=lambda r: r.get('anum', '')):
    a = h.get('anum')
    if not a or h.get('FAILS') or a in roster or withdrawnset.blocked(a, 'gf-identity'):
        continue
    dd = f'build/gi{a}'
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(gfidbuild.build(h))
    except Exception as exc:
        failed.append((a, f'builder: {exc}')); continue
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    if os.path.exists(f'{dd}/p.pdf') and os.path.getsize(f'{dd}/p.pdf') > 40000:
        made += 1
    else:
        failed.append((a, 'no pdf'))
print(f'{made} papers, {len(failed)} problems')
for a, why in failed:
    print('  ', a, why)
