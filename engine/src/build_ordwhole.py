#!/usr/bin/env python3
"""Compile a paper for every whole-sequence order-line result."""
import json
import os
import subprocess

import ordbuild

hits = json.load(open('ordwhole_hits.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
made, bad = 0, []
for h in sorted(hits, key=lambda x: x['anum']):
    if h['anum'] in roster:
        continue
    # NOT build/un<anum>: that is the general builder's directory for the same entry, and
    # both writing there means whichever ran last leaves its p.tex and p.pdf behind. The
    # source mirror matches a paper to its source by the PDF's hash, so after a collision the
    # hash no longer matches and the paper is left with no source at all --- which is exactly
    # what happened to all 100 of these.
    dd = f"build/ow{h['anum']}"
    os.makedirs(dd, exist_ok=True)
    open(f'{dd}/p.tex', 'w').write(ordbuild.build(h))
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = f'{dd}/p.pdf'
    if os.path.exists(pdf) and os.path.getsize(pdf) > 40000:
        log = open(f'{dd}/p.log', errors='ignore').read()
        if 'There were undefined references' in log:
            bad.append((h['anum'], 'undefined references'))
        else:
            made += 1
    else:
        bad.append((h['anum'], 'no pdf'))
print(made, 'papers built,', len(bad), 'problems')
for a, w in bad[:10]:
    print('  ', a, w)
