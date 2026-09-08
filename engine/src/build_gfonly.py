#!/usr/bin/env python3
"""Compile a paper for every conjectured generating function proved from a model.

    PAPER_DATE='8 September 2026' python3 src/build_gfonly.py [shard] [nshards]

The vein kept its results in its own sharded files and had no installer of its own: the only
builder read the unsharded `gfonly_hits.json' and did not run pdflatex. 312 proved results sat
in those files with nothing to turn them into papers.
"""
import glob
import json
import os
import subprocess
import sys
import zlib

import atomicjson
import gfonlybuild
import localentry as LE
import uniform

SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
recs = {}
for f in sorted(glob.glob('gfonly_hits*.json')):
    for h in atomicjson.load(f, []) or []:
        if isinstance(h, dict) and h.get('anum') and not h.get('FAILS'):
            recs.setdefault(h['anum'], h)
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
kept = set()
for f in glob.glob('deep-check/livenew*.json'):
    try:
        kept |= set(json.load(open(f))['kept'])
    except Exception:
        pass
made, bad, notlive, stale = 0, [], 0, []
for a, h in sorted(recs.items()):
    if a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    if a not in kept:
        notlive += 1
        continue
    # A hit records the bound S its run was working with. Bounds get corrected -- the
    # two-dimensional automaton bound was too small until today -- and a run already in
    # flight keeps writing the old one. Rebuild the bound from the model now and refuse the
    # hit if it was proved against a smaller one; the sweep will find it again.
    try:
        got = uniform.read(LE.get(a)['name'])
        b = uniform.build(got[0], got[1], 20000) if got else None
        now = uniform.size(got[0], got[1], b) if b else None
    except Exception:
        now = None
    if now is None or int(h.get('S', 0)) < int(now):
        stale.append(a)
        # and remove any PDF an earlier run built under the old bound, or install_vein
        # would find it on disk and install it regardless
        try:
            os.remove(f'build/gfo{a}/p.pdf')
        except OSError:
            pass
        continue
    dd = f'build/gfo{a}'
    if os.path.exists(f'{dd}/p.pdf') and os.path.getsize(f'{dd}/p.pdf') > 40000:
        made += 1
        continue
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(gfonlybuild.build(h))
    except Exception as exc:
        bad.append((a, str(exc)[:70]))
        continue
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = f'{dd}/p.pdf'
    if os.path.exists(pdf) and os.path.getsize(pdf) > 40000:
        log = open(f'{dd}/p.log', errors='ignore').read()
        if 'There were undefined references' in log:
            bad.append((a, 'undefined references'))
        else:
            made += 1
    else:
        bad.append((a, 'pdf too small or missing'))
print(f'shard {SHARD}: {made} papers, {len(bad)} failed, {notlive} not confirmed live, '
      f'{len(stale)} proved against a bound since corrected')
for a, why in bad[:15]:
    print('   ', a, why)
