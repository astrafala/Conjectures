"""Chunked re-check of the recovered table lines."""
import json, os, re
from fractions import Fraction
import localentry as LE, uniform, bmrec, tablecol, tablerow
P62 = (1 << 61) - 1
DONE = 'audit_ordline_done.json'
hits = json.load(open('ordline_hits.json'))
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
prob, n = [], 0
for h in hits:
    a = h['anum']
    if a in done:
        continue
    for c in h['cols']:
        rn = (tablecol if c['mode'] == 'col' else tablerow).rewrite(h['name'], c['k'])
        got = uniform.read(rn)
        if not got:
            prob.append((a, c['k'], 'name no longer read')); continue
        en, p = got
        b = None
        for cap in (c['S'] + 1, 4 * c['S'] + 8, 40000):
            b = uniform.build(en, p, cap)
            if b is not None:
                break
        if b is None:
            prob.append((a, c['k'], 'rebuild failed')); continue
        S = uniform.size(en, p, b)
        t = uniform.terms(en, p, b, 2 * S + 8)
        tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
        seq = [v for v in tv[c['shift']:] if v is not None]
        L0 = bmrec.bm_mod([v % P62 for v in seq], P62)
        k = min(c['order'] + 4, max(0, len(seq) - 2 * c['order'] - 4))
        Lt = bmrec.bm_mod([v % P62 for v in seq[k:]], P62)
        if L0 != c['order'] or Lt != c['order']:
            prob.append((a, c['k'], 'orders', L0, Lt, 'stated', c['order'])); continue
        Lx, cs = bmrec.bm([Fraction(v) for v in seq])
        rec = {i + 1: int(cc) for i, cc in enumerate(cs)}
        if Lx != c['order'] or rec != {int(x): int(y) for x, y in c['coeffs'].items()}:
            prob.append((a, c['k'], 'coefficients differ on re-derivation')); continue
        bad = [i for i in range(Lx, min(len(seq), 3 * Lx + 20))
               if seq[i] != sum(rec[j] * seq[i - j] for j in rec)]
        if bad:
            prob.append((a, c['k'], 'recurrence fails at', bad[:3]))
    done.add(a); n += 1
    json.dump(sorted(done), open(DONE, 'w'))
json.dump(sorted(done), open(DONE, 'w'))
print('chunk', n, 'cumulative', len(done), 'of', len(hits), 'problems', len(prob))
for q in prob[:10]:
    print(q)
