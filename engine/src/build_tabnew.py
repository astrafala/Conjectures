#!/usr/bin/env python3
"""Compile a paper for every newly settled T(n,k) table, columns and rows alike.

`tablebuild2` was written with a one-off driver reading `tab2_hits.json`. The running sweeps
write `tabnew_hits.json` and `rownew_hits.json`, and nothing built from those, so 73 settled
tables were sitting with no paper. Both files hold the same record shape and
`tablebuild2.build` already handles a record whose settled lines are rows rather than columns.

    PAPER_DATE='8 September 2026' python3 src/build_tabnew.py
"""
import json
import os
import subprocess

import tablebuild2

recs = {}
for f in ('tabnew_hits.json', 'rownew_hits.json'):
    if not os.path.exists(f):
        continue
    for h in json.load(open(f)):
        a = h.get('anum')
        if not a or not h.get('cols'):
            continue
        # an entry can appear in both files -- its columns settled by one sweep and its rows
        # by the other. One paper per entry, carrying both.
        if a in recs:
            have = {(c.get('mode', 'col'), c['k']) for c in recs[a]['cols']}
            recs[a]['cols'] += [c for c in h['cols']
                                if (c.get('mode', 'col'), c['k']) not in have]
        else:
            recs[a] = dict(h)
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
made, bad = 0, []
for a, h in sorted(recs.items()):
    if a in roster:
        continue
    dd = f'build/tb3{a}'
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(tablebuild2.build(h))
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
for a, w in bad[:12]:
    print('  ', a, w)
