"""Chunked re-check of the order-recovery papers: the minimal order of the whole sequence AND
of a tail must both equal the order the entry states, which is what makes the recurrence
unique. Also re-derives the coefficients and tests them on the entry's published terms."""
import json, os
from fractions import Fraction
import localentry as LE, uniform, bmrec
P62 = (1 << 61) - 1
DONE = 'audit_ord_done.json'
hits = [x for x in json.load(open('ord_hits.json')) if not x.get('FAILS')]
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
prob, n = [], 0
for h in hits:
    a = h['anum']
    if a in done:
        continue
    en, p = uniform.read(h['name'])
    b = None
    for cap in (h['S'] + 1, 4 * h['S'] + 8, 40000, 400000):
        b = uniform.build(en, p, cap)
        if b is not None:
            break
    if b is None:
        prob.append((a, 'rebuild failed')); done.add(a); n += 1; continue
    S = uniform.size(en, p, b)
    t = uniform.terms(en, p, b, 2 * S + 8)
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    seq = [v for v in tv[h['shift']:] if v is not None]
    d = [int(v) for v in LE.get(a)['data'].split(',') if v.strip()]
    if seq[:len(d)] != d:
        prob.append((a, 'model no longer reproduces the DATA')); done.add(a); n += 1; continue
    L0 = bmrec.bm_mod([v % P62 for v in seq], P62)
    k = min(h['order'] + 4, max(0, len(seq) - 2 * h['order'] - 4))
    Lt = bmrec.bm_mod([v % P62 for v in seq[k:]], P62)
    if L0 != h['order'] or Lt != h['order']:
        prob.append((a, 'orders', L0, Lt, 'stated', h['order']))
    else:
        Lx, cs = bmrec.bm([Fraction(v) for v in seq])
        rec = {i + 1: int(c) for i, c in enumerate(cs)}
        if Lx != h['order'] or rec != {int(x): int(y) for x, y in h['coeffs'].items()}:
            prob.append((a, 'coefficients differ on re-derivation'))
        else:
            bad = [i for i in range(h['order'], len(seq))
                   if seq[i] != sum(rec[j] * seq[i - j] for j in rec)]
            if bad:
                prob.append((a, 'recovered recurrence fails at', bad[:3]))
    done.add(a); n += 1
    json.dump(sorted(done), open(DONE, 'w'))
json.dump(sorted(done), open(DONE, 'w'))
print('chunk', n, 'cumulative', len(done), 'of', len(hits), 'problems', len(prob))
for q in prob[:10]:
    print(q)
