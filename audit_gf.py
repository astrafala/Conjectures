"""Independent re-check of the generating-function papers.

Re-reads the entry, re-parses the generating function from its own line, expands the series
afresh, and checks: it reproduces every published term; the conjectured recurrence holds on
the series for sixty indices past the stated threshold; and it FAILS at the threshold itself,
so the range claimed is exactly the true one.
"""
import json, os, re
import sympy
import localentry as LE, gfrec

DONE = 'audit_gf_done.json'
hits = [x for x in json.load(open('gf_hits.json')) if not x.get('FAILS')]
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
prob, n = [], 0
for h in hits:
    a = h['anum']
    if a in done:
        continue
    e = LE.get(a)
    g = None
    for L in e['comment'] + e['formula']:
        if L.strip() == h['gfline']:
            g = gfrec.parse_gf(L)
            break
    if g is None:
        prob.append((a, 'g.f. line no longer read')); done.add(a); n += 1; continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off, sh, nthr, order = h['offset'], h['shift'], h['nthr'], h['order']
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    N = max(len(d) + off, nthr - off + sh + 62) + 4
    s = gfrec.series(g, N)
    if s is None:
        prob.append((a, 'series failed')); done.add(a); n += 1; continue
    if any(s[sh + k] != d[k] for k in range(len(d))):
        prob.append((a, 'g.f. no longer reproduces the DATA')); done.add(a); n += 1; continue
    A = lambda m: s[m - off + sh] if 0 <= m - off + sh < len(s) else None
    bad = [m for m in range(nthr + 1, nthr + 61)
           if A(m) is not None and A(m - order) is not None and
           A(m) != sum(c * A(m - i) for i, c in coeffs.items())]
    if bad:
        prob.append((a, 'CLAIM FAILS at', bad[:3]))
    elif A(nthr) is not None and A(nthr - order) is not None and nthr - order >= off:
        if A(nthr) == sum(c * A(nthr - i) for i, c in coeffs.items()):
            prob.append((a, 'range not tight at', nthr))
    done.add(a); n += 1
    json.dump(sorted(done), open(DONE, 'w'))
json.dump(sorted(done), open(DONE, 'w'))
print('chunk', n, 'cumulative', len(done), 'of', len(hits), 'problems', len(prob))
for q in prob[:20]:
    print(q)
