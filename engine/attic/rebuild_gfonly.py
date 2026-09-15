#!/usr/bin/env python3
"""Rewrite the generating-function papers whose model is not a walk, in place.

`unibuild' wrote the digraph paper for every engine and 461 installed papers described a
digraph that does not exist; `qpbuild' was written to fix that. `gfonlybuild' was never given
the same correction, and 219 of ITS installed papers say the same false thing -- 216 of them
about two-dimensional automata, whose axis is no walk on any graph. This regenerates each from
the corrected builder, compiles it, and replaces the installed PDF at its ranked path. The
rank, the A-number and the verdict do not change; only the text does.

The date each paper prints is the day its result was obtained, recovered from the map the
paper-date pass keeps, never the day its prose was rewritten.
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfonlybuild
import qpbuild

ONLY = set(sys.argv[1:])
# `papers/' is not the authority: rank.py deletes and rebuilds the whole directory from
# `papers-old-numbering/', keyed by build number. A rebuild that writes only to the ranked
# path is therefore thrown away by the next ranking -- silently, with the paper reverting to
# the text it was rewritten to fix. The build-numbered copy is what must be written; the
# ranked path is updated too so the change is visible before the next ranking.
ENG = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
BUILDNO = {}
for _n, _v in ENG.items():
    BUILDNO.setdefault(_v['anum'], []).append(_n)

rank = {r['anum']: r for r in json.load(open('rank-map.json'))}
hits = [h for h in json.load(open('gfonly_hits.json'))
        if not h.get('FAILS') and h.get('engine') in qpbuild.SHORT and h['anum'] in rank]
if ONLY:
    hits = [h for h in hits if h['engine'] in ONLY]
done, failed = 0, []
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    dd = 'build/gfo%s' % a
    os.makedirs(dd, exist_ok=True)
    try:
        open(dd + '/p.tex', 'w').write(gfonlybuild.build(h))
    except Exception as exc:
        failed.append('%s(%s)' % (a, type(exc).__name__))
        continue
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = dd + '/p.pdf'
    if not (os.path.exists(pdf) and os.path.getsize(pdf) > 50000):
        failed.append(a)
        continue
    for _n in BUILDNO.get(a, ()):
        shutil.copyfile(pdf, 'papers-old-numbering/{}-{}.pdf'.format(
            _n, 'DISPROOF' if ENG[_n].get('disproof') else 'PROOF'))
    shutil.copyfile(pdf, rank[a]['path'])
    done += 1
print('rebuilt', done, 'failed', len(failed))
if failed:
    print('  failed:', ' '.join(failed[:20]))
