"""Independent re-check of every closed-form paper.

Deliberately does NOT import the sweep: the model values are recomputed here from the
engines directly, so a transcription error in the sweep's own bookkeeping shows up as a
disagreement rather than being reproduced. Three checks per paper: the claim holds for sixty
indices past its stated start; it fails just below that start (so the range is tight); and
the entry's published DATA agrees with the closed form wherever the claim covers it.
"""
import json, importlib, collections
from fractions import Fraction
from math import factorial
import sympy, localentry as LE, closedform as CF
import transfer2 as T2

n = sympy.Symbol('n')
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
M = {}


def mod(e):
    if e not in M:
        M[e] = importlib.import_module(e)
    return M[e]


def values(eng, nm, off, N, d):
    """{i: a(i)} for i = off..N, with the alignment pinned by the published DATA."""
    m = mod(eng)
    r = m.parse_name(nm)
    if eng == 'transfer4':
        K, al, H, V, L = r
        st, adj = m.build(K, al, H, V, L)
        model = [len(m.rows_ok(K, al, H, L))] + T2.terms(adj, len(st), N - off + 2)
        return {off + i: Fraction(v) for i, v in enumerate(model)}, len(st)
    if eng == 'transfer5':
        K, al, same, counts, nb, ul0 = r
        st, adj, start, end = m.build(K, al, same, counts, nb, ul0)
        model = [m.one_row(K, al, same, counts, nb, ul0)] + m.terms(adj, start, end, N - off + 2)
        return {off + i: Fraction(v) for i, v in enumerate(model)}, len(st)
    if eng == 'transfer3':
        st, adj = m.build(*r)
        t = [Fraction(v) for v in T2.terms(adj, len(st), N + 3)]
        S = len(st)
    elif eng == 'transfer6':
        st, adj = m.build(r)
        t = [Fraction(v, r['frac']) for v in m.terms(adj, len(st), N + 3)]
        S = len(st)
    elif eng == 'transfer10':
        b = None
        for cap in (20000, 40000, 200000, 2000000):
            b = m.build(r, cap=cap)
            if b is not None:
                break
        adj, start, _ = b
        f = factorial(r['K']) * r['frac']
        t = [None if q is None else Fraction(q, f) for q in m.avals(adj, start, r, N + 3)]
        S = len(adj)
    else:
        b = None
        for cap in (20000, 40000, 200000, 2000000):
            b = m.build(r, cap=cap)
            if b is not None:
                break
        adj, start, end, _ = b
        f = r['frac'] * (factorial(r['K']) if eng in SCALED else 1)
        t = [None if q is None else Fraction(q, f) for q in m.avals(adj, start, end, r, N + 3)]
        S = len(adj)
    for s in range(0, 4):
        if all(off + k + s < len(t) and t[off + k + s] is not None and
               t[off + k + s] == d[k] for k in range(len(d))):
            return {i: t[i + s] for i in range(len(t) - s)}, S
    return None, S


if __name__ == "__main__":
    hits = [h for h in json.load(open('cf_hits.json')) if not h.get('FAILS')]
    prob, res = [], collections.Counter()
    for h in hits:
        a, eng, off, first = h['anum'], h['engine'], h['offset'], h['first']
        e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        expr = sympy.sympify(h['expr'], locals={'n': n}, rational=True)
        vals, S = values(eng, h['name'], off, first + 60, d)
        if vals is None:
            prob.append((a, 'model does not reproduce the DATA')); continue
        # transfer4 and transfer5 return their values already aligned, so check the tie to
        # the entry explicitly here rather than relying on the alignment search
        if any(vals.get(off + k) is None or vals[off + k] != d[k] for k in range(len(d))):
            prob.append((a, 'model does not reproduce the DATA')); continue
        bad = [i for i in range(first, first + 60)
               if vals.get(i) is not None and vals[i] != CF.value(expr, i)]
        if bad:
            prob.append((a, 'CLAIM FAILS at', bad[:3])); continue
        if first > off:
            i = first - 1
            if vals.get(i) is not None and vals[i] == CF.value(expr, i):
                prob.append((a, 'range not tight at', i))
        bd = [off + k for k in range(len(d))
              if off + k >= first and Fraction(d[k]) != CF.value(expr, off + k)]
        if bd:
            prob.append((a, 'DATA contradicts the closed form at', bd[:3]))
        res[eng] += 1
    print('checked', len(hits), dict(res))
    print('problems', len(prob))
    for q in prob[:20]:
        print(q)
