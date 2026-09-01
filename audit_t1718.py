"""Independent re-check of the 3 X 3 subblock and king-move papers.

Rebuilds each model from the entry's name, confirms it reproduces every published term,
then checks the proved recurrence directly on the model's own values well past the stated
threshold and confirms it FAILS at the threshold itself.
"""
import json, sys, collections
import localentry as LE

WHICH = sys.argv[1] if len(sys.argv) > 1 else 'both'
prob, res = [], collections.Counter()


def check17():
    import transfer17 as T
    for h in [x for x in json.load(open('transfer17_hits.json')) if not x.get('FAILS')]:
        a = h['anum']
        p = T.parse_name(h['name'])
        st, adj = T.build(p, cap=10 ** 9)
        d = [int(v) for v in LE.get(a)['data'].split(',') if v.strip()]
        N = max(len(d), h['nthr'] - h['offset'] + h['shift'] + 45) + 5
        t = [v // p['frac'] for v in T.terms(adj, len(st), N)]
        yield a, h, t, d


def check18():
    import transfer18 as T
    for h in [x for x in json.load(open('transfer18_hits.json')) if not x.get('FAILS')]:
        a = h['anum']
        p = T.parse_name(h['name'])
        adj, start, end, S = T.build(p, cap=10 ** 9)
        d = [int(v) for v in LE.get(a)['data'].split(',') if v.strip()]
        N = max(len(d), h['nthr'] - h['offset'] + h['shift'] + 45) + 5
        t = [v // p['frac'] for v in T.terms(adj, start, end, N)]
        yield a, h, t, d


def check19():
    import transfer19 as T
    for h in [x for x in json.load(open('transfer19_hits.json')) if not x.get('FAILS')]:
        a = h['anum']
        p = T.parse_name(h['name'])
        adj, start, end, S = T.build(p, cap=10 ** 9)
        d = [int(v) for v in LE.get(a)['data'].split(',') if v.strip()]
        N = max(len(d), h['nthr'] - h['offset'] + h['shift'] + 45) + 5
        t = [v // p['frac'] for v in T.terms(adj, start, end, N)]
        yield a, h, t, d


def check20():
    import transfer20 as T
    for h in [x for x in json.load(open('transfer20_hits.json')) if not x.get('FAILS')]:
        a = h['anum']
        p = T.parse_name(h['name'])
        adj, start, end, S, den = T.build(p, cap=10 ** 9)
        d = [int(v) for v in LE.get(a)['data'].split(',') if v.strip()]
        N = max(len(d), h['nthr'] - h['offset'] + h['shift'] + 45) + 5
        f = den * p['frac']
        t = [None if v % f else v // f for v in T.terms(adj, start, end, N)]
        yield a, h, t, d


def check21():
    import transfer21 as T
    for h in [x for x in json.load(open('transfer21_hits.json')) if not x.get('FAILS')]:
        a = h['anum']
        p = T.parse_name(h['name'])
        adj, start, end, S, den = T.build(p, cap=10 ** 9)
        d = [int(v) for v in LE.get(a)['data'].split(',') if v.strip()]
        N = max(len(d), h['nthr'] - h['offset'] + h['shift'] + 45) + 5
        f = den * p['frac']
        t = [None if v % f else v // f for v in T.terms(adj, start, end, N)]
        yield a, h, t, d


def run(gen, tag):
    for a, h, t, d in gen:
        sh, off, nthr = h['shift'], h['offset'], h['nthr']
        order = h['order']
        coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
        if t[sh:sh + len(d)] != d:
            prob.append((a, tag, 'model no longer reproduces the DATA')); continue
        # a(n) = t[n - off + sh]
        def A(n):
            j = n - off + sh
            return t[j] if 0 <= j < len(t) else None
        bad = [n for n in range(nthr + 1, nthr + 41)
               if A(n) is not None and A(n - order) is not None and
               A(n) != sum(c * A(n - i) for i, c in coeffs.items())]
        if bad:
            prob.append((a, tag, 'CLAIM FAILS at', bad[:3])); continue
        if A(nthr) is not None and A(nthr - order) is not None and nthr - order >= off:
            if A(nthr) == sum(c * A(nthr - i) for i, c in coeffs.items()):
                prob.append((a, tag, 'range not tight at', nthr))
        res[tag] += 1


if WHICH in ('both', '17'):
    run(check17(), 't17')
if WHICH in ('both', '18'):
    run(check18(), 't18')
if WHICH in ('both', '19'):
    run(check19(), 't19')
if WHICH in ('both', '20'):
    run(check20(), 't20')
if WHICH in ('both', '21'):
    run(check21(), 't21')
print('checked', dict(res), 'problems', len(prob))
for q in prob[:20]:
    print(q)
