#!/usr/bin/env python3
"""Which entries state a closed form as FACT and conjecture a recurrence.

Both halves have to be tested with the parsers the sweep actually uses, not with a rough
string test: "a(n) = " catches English prose like "a(n) is the number of sublattices of index
n", and a scan built on that reported 1,190 entries that the sweep could not use at all.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closedform as CF
import conjlines
import localentry as LE
import ratrec

CONJ = re.compile(r'onjectur|mpirical|It appears|Apparently', re.I)
OUT = 'deep-check/factscan.json'
allconj = json.load(open('/tmp/allconj.json'))
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
out = json.load(open(OUT)) if os.path.exists(OUT) else {}
for a in allconj:
    if a in out or a in roster:
        continue
    try:
        e = LE.get(a)
    except Exception:
        out[a] = 0
        continue
    if not any(ratrec.parse_rec(L) for L in conjlines.lines(e)):
        out[a] = 0
    else:
        out[a] = 0
        for L in e['comment'] + e['formula']:
            if CONJ.search(L):
                continue
            q = CF.parse_line(L, bare=True)
            if q and q[0] is not None:
                out[a] = 1
                break
    if len(out) % 400 == 0:
        json.dump(out, open(OUT, 'w'))
json.dump(out, open(OUT, 'w'))
pool = sorted(a for a, v in out.items() if v)
open('deep-check/factcf.txt', 'w').write('\n'.join(pool) + '\n')
print(f'{len(out)} scanned, {len(pool)} usable -> deep-check/factcf.txt')
