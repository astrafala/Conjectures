#!/usr/bin/env python3
"""Re-run every transfer81 entry through the engine as it now stands.

Thirty of these were proved, papered and ranked, and only then did a defect in the parser
turn up: `L X (n+a)` was being transposed, which rewrites conditions stated about rows into
conditions about columns. The natural orientation was not touched by the fix, but "not
touched" is a claim about code, and the roster is a claim about mathematics. So every one is
redone here from scratch, by the code that ships, and the result compared with what the
roster already says.
"""
import json
import sys

import localentry as LE
import openness
import ratrec
import uniform

MARK = __import__('re').compile(r'onjectur|Empirical', __import__('re').I)
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 400000
names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
out, res = [], {}


def note(k):
    res[k] = res.get(k, 0) + 1


for a in json.load(open('t81_cands.json')):
    nm = names[a]
    got = uniform.read(nm)
    if not got or got[0] != 'transfer81':
        note('no longer claimed by transfer81')
        continue
    en, p = got
    e = LE.get(a)
    recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                        if MARK.search(L)) if r]
    if not recs:
        note('no parsable recurrence')
        continue
    b = uniform.build(en, p, CAP)
    if b is None:
        note('state space > cap %d' % CAP)
        continue
    S = uniform.size(en, p, b)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    t = uniform.terms(en, p, b, len(d) + off + 5)
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        note('model does not match DATA')
        continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    thr = uniform.threshold(en, p, b, coeffs, order)
    if thr is None:
        note('UNRESOLVED')
        continue
    nthr = thr + off - sh
    bad = [off + k for k in range(len(d))
           if off + k > nthr and k - order >= 0 and
           d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
    if bad:
        note('claim contradicted by DATA')
        out.append({'anum': a, 'FAILS': True, 'name': nm, 'bad': bad[:3]})
        continue
    note('PROVED')
    out.append({'anum': a, 'name': nm, 'engine': en, 'S': S, 'order': order,
                'offset': off, 'shift': sh, 'nthr': nthr, 'nterms': len(d),
                'claimed': dd, 'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    print('ok', a, S, flush=True)

json.dump(out, open('t81_verified.json', 'w'), indent=1)
print(res)
