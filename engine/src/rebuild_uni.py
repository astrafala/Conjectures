#!/usr/bin/env python3
"""Rewrite installed `unibuild' papers in place, at their own dates.

`build_new.py' only writes papers for hits that are not yet in the roster, so a fix to
`unibuild' after a batch was installed reaches nothing. Same shape as `rebuild_qp.py' and for
the same reason -- see defect 13, a fix applied to one builder and not its twin -- but for the
papers the general builder wrote.

    python3 src/rebuild_uni.py winimage      only that engine's papers
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unibuild

# A rebuilt paper must keep the date its result was found. `deep-check/orig-paper-dates.json'
# covers the papers that were rewritten in earlier batches and nothing else, so for anything
# missing from it the fallback was the builder's own module default -- which is whatever day
# the builder was last edited, not the day the result was obtained. Seventeen papers were
# restamped "2 September" that way. The ranked path's entry in `paper-dates.json' is what the
# installed PDF actually prints, so that is the fallback; PAPER_DATE overrides both.
DATE0 = unibuild.DATE
_PD = {}
if os.path.exists('paper-dates.json') and os.path.exists('rank-map.json'):
    _dates = json.load(open('paper-dates.json'))
    for _r in json.load(open('rank-map.json')):
        if _r['path'] in _dates:
            _PD.setdefault(_r['anum'], _dates[_r['path']])


def _date_for(a):
    if os.environ.get('PAPER_DATE'):
        return os.environ['PAPER_DATE']
    return ORIG.get(a) or _PD.get(a) or DATE0

ONLY = set(sys.argv[1:])
# A rebuilt paper must keep the date its result was obtained, not the day its prose was
# rewritten. The dates the papers printed before the rewrite were recovered from git and
# keyed by A-number; anything not in that map is new and keeps today's.
ORIG = {}
if os.path.exists('deep-check/orig-paper-dates.json'):
    ORIG = json.load(open('deep-check/orig-paper-dates.json'))
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
# `build_new' is a SCRIPT: importing it RUNS the builder. Its SPECIAL map -- which engines go
# to a builder other than `unibuild' -- is read out of the source instead. That mistake was
# made once already, in rebuild_quote.py, and built 119 papers as a side effect.
import re as _re
SPECIAL = set(_re.findall(r"'(\w+)': '\w+build'", open('src/build_new.py').read()))
hits = [h for h in json.load(open('uniall_hits.json'))
        if not h.get('FAILS') and h.get('engine') and h['engine'] not in SPECIAL]
if ONLY:
    hits = [h for h in hits if h['engine'] in ONLY]
done, missing, failed = 0, [], []
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    r = rank.get(a)
    dd = 'build/un%s' % a
    os.makedirs(dd, exist_ok=True)
    unibuild.DATE = _date_for(a)
    open(dd + '/p.tex', 'w').write(unibuild.build(h))
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
    for _n in BUILDNO.get(a, ()):
        shutil.copyfile(pdf, 'papers-old-numbering/{}-{}.pdf'.format(
            _n, 'DISPROOF' if ENG[_n].get('disproof') else 'PROOF'))
    shutil.copyfile(pdf, r['path'])
    done += 1
print('rebuilt', done, 'not installed yet', len(missing), 'failed', len(failed))
if failed:
    print('  failed:', ' '.join(failed[:20]))
