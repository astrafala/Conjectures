#!/usr/bin/env python3
"""Compile a paper for every min-filter result.

    PAPER_DATE='8 September 2026' python3 src/build_mf.py

build/mf<anum>: its own prefix, because build/cf belongs to the closed-form builder for the
same entries and two builders writing one directory leaves whichever ran last.
"""
import json
import os
import subprocess

import mfbuild

recs = json.load(open('mfcf_hits.json'))
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
made, bad = 0, []
for h in sorted(recs, key=lambda x: x['anum']):
    a = h['anum']
    if a in roster or h.get('FAILS'):
        continue
    dd = f'build/mf{a}'
    if os.path.exists(f'{dd}/p.pdf') and os.path.getsize(f'{dd}/p.pdf') > 40000:
        made += 1
        continue
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(mfbuild.build(h))
    except Exception as exc:
        bad.append((a, str(exc)))
        continue
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = f'{dd}/p.pdf'
    if os.path.exists(pdf) and os.path.getsize(pdf) > 40000:
        if 'There were undefined references' in open(f'{dd}/p.log', errors='ignore').read():
            bad.append((a, 'undefined references'))
        else:
            made += 1
    else:
        bad.append((a, 'no pdf'))
print(f'{made} papers built, {len(bad)} problems')
for a, w in bad[:10]:
    print('  ', a, w)
