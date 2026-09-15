#!/usr/bin/env python3
"""Write and compile the recurrence-to-generating-function papers.

    PAPER_DATE='15 September 2026' python3 src/build_recgf.py
    python3 src/install_vein.py rg rg_all_hits.json recurrence-to-gf

The vein had results and no builder at all: six proved records sat in `rg_hits_*.json` with
nothing to turn them into papers, the same gap `build_gfonly` was written to close.
"""
import json
import os
import subprocess

import rgbuild
import withdrawnset

HITS = os.environ.get('HITS', 'rg_all_hits.json')
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
made, failed = 0, []
for h in sorted(json.load(open(HITS)), key=lambda r: r.get('anum', '')):
    a = h.get('anum')
    if not a or h.get('FAILS') or a in roster or withdrawnset.blocked(a, 'recurrence-to-gf'):
        continue
    dd = f'build/rg{a}'
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(rgbuild.build(h))
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
