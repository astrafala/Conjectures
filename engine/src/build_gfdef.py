#!/usr/bin/env python3
"""Compile a paper for every recurrence that follows from a generating function stated as fact.

    PAPER_DATE='8 September 2026' python3 src/build_gfdef.py [shard] [nshards]

build/gd<anum>: its own prefix. build/gf belongs to the earlier run of this vein and two
builders writing one directory leaves whichever ran last, which has cost this project a
hundred papers their stored source once already.
"""
import json
import os
import subprocess
import sys
import zlib

import gfbuild

SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
recs = json.load(open('gfdef_hits.json'))
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
live = json.load(open('deep-check/livenew.json'))
kept = set(live['kept'])
made, bad, notlive = 0, [], 0
for h in sorted(recs, key=lambda x: x['anum']):
    a = h['anum']
    if a in roster or h.get('FAILS') or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    # nothing is built for an entry the live re-check has not confirmed still open
    if a not in kept:
        notlive += 1
        continue
    dd = f'build/gd{a}'
    if os.path.exists(f'{dd}/p.pdf') and os.path.getsize(f'{dd}/p.pdf') > 40000:
        made += 1
        continue
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(gfbuild.build(h))
    except Exception as exc:
        bad.append((a, str(exc)[:60]))
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
print(f'{made} papers built, {len(bad)} problems, {notlive} not yet live-confirmed')
for a, w in bad[:8]:
    print('  ', a, w)
