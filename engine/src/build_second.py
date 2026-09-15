#!/usr/bin/env python3
"""Write and compile the further-conjecture papers.

    PAPER_DATE='15 September 2026' python3 src/build_second.py
    ALLOW_SECOND=1 python3 src/install_vein.py sd snd_all_hits.json second-conjecture

These are SECOND papers on entries that already have one, so they need `ALLOW_SECOND`: the
ordinary installer skips an entry already on the roster, which is right for every other vein
and wrong for this one.
"""
import json
import os
import subprocess

import sndbuild
import withdrawnset

HITS = os.environ.get('HITS', 'snd_all_hits.json')
made, failed = 0, []
for h in sorted(json.load(open(HITS)), key=lambda r: r.get('anum', '')):
    a = h.get('anum')
    if not a or h.get('FAILS') or not h.get('settled'):
        continue
    if withdrawnset.blocked(a, 'second-conjecture'):
        continue
    dd = f'build/sd{a}'
    os.makedirs(dd, exist_ok=True)
    try:
        open(f'{dd}/p.tex', 'w').write(sndbuild.build(h))
    except Exception as exc:
        failed.append((a, f'builder: {exc}')); continue
    for _ in range(2):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    if os.path.exists(f'{dd}/p.pdf') and os.path.getsize(f'{dd}/p.pdf') > 40000:
        made += 1
    else:
        failed.append((a, 'no pdf'))
print(f'{made} papers, {len(failed)} problems')
for a, why in failed[:10]:
    print('  ', a, why)
