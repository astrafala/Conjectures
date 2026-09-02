"""Independent re-check of the unified-sweep papers."""
import json, os
import localentry as LE, uniform
DONE = 'audit_uni_done.json'
hits = [x for x in json.load(open('uniall_hits.json')) if not x.get('FAILS')]
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
prob, n = [], 0
for h in hits:
    a = h['anum']
    if a in done:
        continue
    got = uniform.read(h['name'])
    if not got:
        prob.append((a, 'name no longer read')); done.add(a); continue
    en, p = got
    b = None
    for cap in (h['S'] + 1, 4 * h['S'] + 8, 40000):
        b = uniform.build(en, p, cap)
        if b is not None:
            break
    if b is None:
        prob.append((a, 'model no longer builds')); done.add(a); continue
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    sh, off, nthr, order = h['shift'], h['offset'], h['nthr'], h['order']
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    t = uniform.terms(en, p, b, max(len(d) + off, nthr - off + sh + 45) + 6)
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    if tv[sh:sh + len(d)] != d:
        prob.append((a, 'model no longer reproduces the DATA')); done.add(a); continue
    A = lambda m: tv[m - off + sh] if 0 <= m - off + sh < len(tv) else None
    bad = [m for m in range(nthr + 1, nthr + 41)
           if A(m) is not None and A(m - order) is not None and
           A(m) != sum(c * A(m - i) for i, c in coeffs.items())]
    if bad:
        prob.append((a, 'CLAIM FAILS at', bad[:3]))
    elif nthr - order >= off and A(nthr) is not None and A(nthr - order) is not None:
        if A(nthr) == sum(c * A(nthr - i) for i, c in coeffs.items()):
            prob.append((a, 'range not tight at', nthr))
    done.add(a); n += 1
    json.dump(sorted(done), open(DONE, 'w'))
print('chunk', n, 'cumulative', len(done), 'of', len(hits), 'problems', len(prob))
for q in prob:
    print(q)
