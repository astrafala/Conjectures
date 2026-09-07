#!/usr/bin/env python3
"""Write and compile a paper for every proved hit that has not got one yet.

The sweep runs continuously now, so results arrive between batches and the papers have to be
built for whatever is there, by whichever builder the engine has. Engines with a builder of
their own get it; the rest get the general one. The date printed is today's, because the date
on a paper is the day the result was obtained.

    PAPER_DATE='7 September 2026' python3 src/build_new.py
"""
import importlib
import json
import os
import subprocess
import sys

import localentry as LE

# transfer17's builder prints the entry's own condition, which the sweep record does not
# carry: the parse is redone here and folded into the record so the paper can quote it
# rather than describe it in general terms.
ENRICH = {'transfer17', 'transfer6', 'transfer20', 'transfer21'}

SPECIAL = {'transfer17': 'transfer17build', 'transfer6': 'transfer6build',
           'transfer20': 'transfer20build', 'transfer21': 'transfer21build',
           'transfer38': 'transfer38build', 'transfer56': 'transfer56build',
           'transfer62': 'transfer62build',
           'transfer34': 'transfer34build', 'transfer35': 'transfer35build',
           'transfer36': 'transfer36build', 'transfer37': 'transfer37build',
           'transfer81': 't81build', 'transfer82': 't82build', 'transfer83': 't83build',
           'transfer84': 't84build', 'transfer85': 't85build', 'transfer86': 't86build',
           'transfer87': 't87build', 'transfer89': 't89build', 'transfer91': 't91build',
           'transfer92': 't92build', 'transfer93': 't93build', 'denumerant': 'denbuild'}

roster = {r['anum'] for r in json.load(open('rank-map.json'))}
hits = [h for h in json.load(open('uniall_hits.json'))
        if not h.get('FAILS') and h.get('anum') not in roster and h.get('engine')]
only = set(sys.argv[1:])
if only:
    hits = [h for h in hits if h['engine'] in only]
mods = {}
made, failed = 0, []
for h in sorted(hits, key=lambda x: x['anum']):
    name = SPECIAL.get(h['engine'], 'unibuild')
    mods.setdefault(name, importlib.import_module(name))
    if h['engine'] in ENRICH:
        eng = importlib.import_module(h['engine'])
        q = eng.parse_name(LE.get(h['anum'])['name'])
        h = dict(q, **h)
        # transfer6build predates the unified sweep and names the threshold differently
        h.setdefault('threshold', h['nthr'])
    dd = f"build/un{h['anum']}"
    os.makedirs(dd, exist_ok=True)
    open(f"{dd}/p.tex", 'w').write(mods[name].build(h))
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = f"{dd}/p.pdf"
    if os.path.exists(pdf) and os.path.getsize(pdf) > 50000:
        log = open(f"{dd}/p.log", errors='ignore').read()
        if 'LaTeX Warning: There were undefined references' in log:
            failed.append((h['anum'], 'undefined references'))
        else:
            made += 1
    else:
        failed.append((h['anum'], 'no pdf'))
print(f'{made} papers built, {len(failed)} problems')
for a, why in failed:
    print('  ', a, why)
