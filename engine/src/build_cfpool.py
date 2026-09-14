#!/usr/bin/env python3
"""Write and compile the closed-form papers for one hits file.

`compile_cf.py` compiles a p.tex that is already on disk and nothing in the repository wrote
it -- the closed-form papers were written by hand, once, which is why a second closed-form
pool had no builder at all. This writes them.

    HITS=linkpoly_hits.json CFPREFIX=lp PAPER_DATE='14 September 2026' \
        python3 src/build_cfpool.py
"""
import json
import os
import subprocess

import cfbuild
import localentry as LE
import withdrawnset

HITS = os.environ.get('HITS', 'cf_hits.json')
PREFIX = os.environ.get('CFPREFIX', 'cf')
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}

made, failed = 0, []
for h in sorted(json.load(open(HITS)), key=lambda x: x.get('anum', '')):
    a = h.get('anum')
    if not a or h.get('FAILS') or a in roster or withdrawnset.blocked(a, 'closed-form'):
        continue
    dd = f'build/{PREFIX}{a}'
    if os.path.exists(f'{dd}/p.pdf') and os.path.getsize(f'{dd}/p.pdf') > 50000:
        continue
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(cfbuild.build(h))
    except Exception as exc:
        failed.append((a, f'builder: {exc}'))
        continue
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    if os.path.exists(f'{dd}/p.pdf') and os.path.getsize(f'{dd}/p.pdf') > 50000:
        made += 1
    else:
        failed.append((a, 'no pdf'))
print(f'{made} papers, {len(failed)} problems')
for a, why in failed:
    print('  ', a, why)
