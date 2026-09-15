"""Chunked re-check of the 3 X 3 subblock papers."""
import json, os, collections
import localentry as LE, transfer17 as T
DONE = 'audit17_done.json'
hits = [x for x in json.load(open('transfer17_hits.json')) if not x.get('FAILS')]
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
prob = []; n = 0
for h in hits:
    a = h['anum']
    if a in done:
        continue
    p = T.parse_name(h['name'])
    st, adj = T.build(p, cap=h['S'] + 1)
    d = [int(v) for v in LE.get(a)['data'].split(',') if v.strip()]
    sh, off, nthr, order = h['shift'], h['offset'], h['nthr'], h['order']
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    N = max(len(d), nthr - off + sh + 45) + 6
    t = [v // p['frac'] for v in T.terms(adj, len(st), N)]
    if t[sh:sh + len(d)] != d:
        prob.append((a, 'model no longer reproduces the DATA'))
    else:
        A = lambda m: t[m - off + sh] if 0 <= m - off + sh < len(t) else None
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
