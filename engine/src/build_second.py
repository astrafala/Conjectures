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

# snd_hits.json, not snd_all_hits.json. merge_sharded.py has written the merged file under the
# first name since the vein was sharded; this read the second, which stopped at 203 records on
# 15 September while the sweep went on to settle 419. 138 results sat held because the
# installer and the merge disagreed about a file name.
HITS = os.environ.get('HITS', 'snd_hits.json')
ROSTER = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
made, failed, nopremise = 0, [], []
for h in sorted(json.load(open(HITS)), key=lambda r: r.get('anum', '')):
    a = h.get('anum')
    if not a or h.get('FAILS') or not h.get('settled'):
        continue
    if withdrawnset.blocked(a, 'second-conjecture'):
        continue
    # THE PREMISE MUST BE ON THE ROSTER (STATE.md defect 45). `premise_kind: proved in this
    # project' means a sweep recorded a proof, not that a paper states one, and the two came
    # apart: 42 records carry that label for entries with no paper and no surviving coeffs
    # record anywhere -- six of them because the paper their premise came from was WITHDRAWN,
    # under `gf-conjecture', which `withdrawnset.blocked(a, "second-conjecture")' does not
    # catch because a withdrawal blocks the ARGUMENT and this rests ON that argument. An entry
    # on the roster is the one condition that is checkable here and cannot go stale silently.
    if a not in ROSTER:
        nopremise.append(a)
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
print(f'{made} papers, {len(failed)} problems, '
      f'{len(nopremise)} refused for a premise that is not on the roster')
if nopremise:
    print('  no published premise: ' + ' '.join(sorted(nopremise)[:12])
          + (' ...' if len(nopremise) > 12 else ''))
for a, why in failed[:10]:
    print('  ', a, why)
