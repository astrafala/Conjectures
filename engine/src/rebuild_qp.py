#!/usr/bin/env python3
"""Rewrite the papers whose model is not a walk, and recompile them in place.

`build_new.py' only writes papers for hits that are not yet in the roster, so a builder fixed
after a batch was installed reaches nothing. These 461 were written by `unibuild', which says
the count is a walk on a digraph -- true of most engines here and false of these seven. This
regenerates each from `qpbuild', compiles it, and replaces the installed PDF at its ranked
path. The rank, the A-number and the verdict do not change; only the text does.
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qpbuild

ONLY = set(sys.argv[1:])
rank = {r['anum']: r for r in json.load(open('rank-map.json'))}
hits = [h for h in json.load(open('uniall_hits.json'))
        if not h.get('FAILS') and h.get('engine') in qpbuild.SHORT]
if ONLY:
    hits = [h for h in hits if h['engine'] in ONLY]
done, missing, failed = 0, [], []
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    r = rank.get(a)
    dd = 'build/un%s' % a
    os.makedirs(dd, exist_ok=True)
    open(dd + '/p.tex', 'w').write(qpbuild.build(h))
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = dd + '/p.pdf'
    if not (os.path.exists(pdf) and os.path.getsize(pdf) > 50000):
        failed.append(a)
        continue
    if r is None:
        missing.append(a)
        continue
    shutil.copyfile(pdf, r['path'])
    done += 1
print('rebuilt', done, 'not installed yet', len(missing), 'failed', len(failed))
if failed:
    print('  failed:', ' '.join(failed[:20]))
