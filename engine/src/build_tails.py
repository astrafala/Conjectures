#!/usr/bin/env python3
"""Compile a paper for every tail-recovered order-line result.

    PAPER_DATE='8 September 2026' python3 src/build_tails.py [shard] [nshards]

build/ot<anum>, its own prefix: build/un and build/ow already belong to other builders for
the same entries, and two builders writing the same directory leaves whichever ran last, which
once cost a hundred papers their stored source.
"""
import json
import os
import subprocess
import sys
import zlib

import tailbuild

SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
recs = json.load(open('ordtails.json'))['proved']
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
made, bad = 0, []
for h in sorted(recs, key=lambda x: x['anum']):
    a = h['anum']
    if a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    dd = f'build/ot{a}'
    if os.path.exists(f'{dd}/p.pdf') and os.path.getsize(f'{dd}/p.pdf') > 40000:
        made += 1
        continue
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(tailbuild.build(h))
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
