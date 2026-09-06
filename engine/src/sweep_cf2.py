"""Entries that state an explicit closed form rather than a recurrence.

The threshold is read off the sequence of VALUES rather than from each engine's own index
convention. The engine's threshold routine is used only for the fact it actually proves --
that the residual vanishes from some point on and stays zero -- and the exact point is then
located by differencing the model's own a(n) values. Two engines here prepend a term to the
walk (a one-row count that the walk itself does not produce), so their walk index and their
n index differ by a constant; reading the point off the values removes that whole class of
error rather than encoding a constant per engine.
"""
import json, re, os, sys, collections, importlib
from fractions import Fraction
from math import factorial
import localentry as LE, openness, closedform as CF

ENG = ['transfer3', 'transfer9', 'transfer6', 'transfer16', 'transfer12', 'transfer10',
       'transfer8', 'transfer14', 'transfer11', 'transfer15', 'transfer13', 'transfer7',
       'transfer4', 'transfer5']
M = {e: importlib.import_module(e) for e in ENG}
import transfer2 as T2
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
HITS, DONE = 'cf_hits.json', 'cf_done.json'
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
targets = json.load(open(os.environ.get('TARGETS', 'cf_all_cands.json')))


def prepare(a, nm):
    """(engine, parsed, built, S) or None."""
    for en in ENG:
        try:
            r = M[en].parse_name(nm)
        except Exception:
            continue
        if not r:
            continue
        if en == 'transfer3':
            cols, al, _, _ = r
            if (al + 1) ** cols > CAP:
                return 'cap'
            b = M[en].build(*r)
            return en, {'t3': r}, b, len(b[0])
        if en == 'transfer4':
            K, al, H, V, L = r
            if ((al + 1) ** K) ** (L - 1) > CAP:
                return 'cap'
            b = M[en].build(K, al, H, V, L)
            if not b[0]:
                return 'cap'
            return en, {'t4': r}, b, len(b[0])
        if en == 'transfer5':
            K, al, same, counts, nb, ul0 = r
            if ((al + 1) ** K) ** 2 > CAP:
                return 'cap'
            b = M[en].build(K, al, same, counts, nb, ul0)
            if not b[0]:
                return 'cap'
            return en, {'t5': r}, b, len(b[0])
        try:
            b = M[en].build(r, cap=CAP)
        except TypeError:
            b = M[en].build(r)
        if b is None or not b[0]:
            return 'cap'
        return en, r, b, len(b[0])
    return None


def avalues(eng, p, b, off, N):
    """{n: a(n)} as Fractions for n = off .. N, using each engine's own convention."""
    if eng == 'transfer4':
        K, al, H, V, L = p['t4']
        st, adj = b
        rows = M[eng].rows_ok(K, al, H, L)
        model = [len(rows)] + T2.terms(adj, len(st), N - off + 2)
        return {off + i: Fraction(v) for i, v in enumerate(model)}
    if eng == 'transfer5':
        K, al, same, counts, nb, ul0 = p['t5']
        st, adj, start, end = b
        model = [M[eng].one_row(K, al, same, counts, nb, ul0)] + \
                M[eng].terms(adj, start, end, N - off + 2)
        return {off + i: Fraction(v) for i, v in enumerate(model)}
    if eng in ('transfer6', 'transfer3'):
        st, adj = b
        tm = M[eng].terms if eng == 'transfer6' else T2.terms
        fr = p['frac'] if eng == 'transfer6' else 1
        t = [Fraction(v, fr) for v in tm(adj, len(st), N + 3)]
        return t                                   # alignment fixed by the DATA search
    if eng == 'transfer10':
        adj, start, _ = b
        f = factorial(p['K']) * p['frac']
        v = M[eng].avals(adj, start, p, N + 3)
        return {i: (None if q is None else Fraction(q, f)) for i, q in enumerate(v)}
    adj, start, end, _ = b
    f = p['frac'] * (factorial(p['K']) if eng in SCALED else 1)
    v = M[eng].avals(adj, start, end, p, N + 3)
    return {i: (None if q is None else Fraction(q, f)) for i, q in enumerate(v)}


def engine_threshold(eng, p, b, coeffs, order):
    if eng in ('transfer6', 'transfer3'):
        st, adj = b
        th = M[eng].threshold if eng == 'transfer6' else T2.threshold
        return th(adj, len(st), coeffs, order)
    if eng == 'transfer4':
        st, adj = b
        return T2.threshold(adj, len(st), coeffs, order)
    if eng == 'transfer5':
        st, adj, start, end = b
        return M[eng].threshold(adj, start, end, coeffs, order, len(st))
    if eng == 'transfer10':
        adj, start, _ = b
        return M[eng].threshold(adj, start, coeffs, order, p)
    adj, start, end, _ = b
    return M[eng].threshold(adj, start, end, coeffs, order, p)


for a in sorted(targets):
    if a in done or a in roster:
        continue
    nm = names[a]
    e = LE.get(a)
    got = None
    for L in e['comment'] + e['formula']:
        q = CF.parse_line(L)
        if q:
            try:
                ann = CF.annihilator(q[0])
            except Exception:
                ann = None
            if ann:
                got = (q[0], q[1], L.strip(), ann); break
    if not got:
        res['no readable closed form'] += 1; done.add(a); continue
    expr, claimed, line, (coeffs, order) = got
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); continue
    pr = prepare(a, nm)
    if pr is None:
        res['no engine reads the name'] += 1; done.add(a); continue
    if pr == 'cap':
        res['state space > cap'] += 1; done.add(a); continue
    eng, p, b, S = pr
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        t = engine_threshold(eng, p, b, coeffs, order)
    except Exception:
        res['threshold failed'] += 1; done.add(a); continue
    if t is None:
        res['model does not satisfy the annihilator'] += 1; done.add(a); continue
    NMAX = off + t + order + 20
    try:
        vals = avalues(eng, p, b, off, NMAX)
    except Exception:
        res['model evaluation failed'] += 1; done.add(a); continue
    if isinstance(vals, list):                      # transfer6/transfer3: find the shift
        found = None
        for s in (0, 1, 2):
            if all(off + k + s < len(vals) and vals[off + k + s].denominator == 1 and
                   vals[off + k + s].numerator == d[k] for k in range(len(d))):
                found = s; break
        if found is None:
            res['model does not match DATA'] += 1; done.add(a); continue
        vals = {i: vals[i + found] for i in range(len(vals) - found)}
    else:
        if not all(vals.get(off + k) is not None and vals[off + k].denominator == 1 and
                   vals[off + k].numerator == d[k] for k in range(len(d))):
            res['model does not match DATA'] += 1; done.add(a); continue
    # the engine's own threshold has already PROVED the residual vanishes for good; all
    # that is needed here is enough values to locate the last nonzero one, which the margin
    # check below enforces directly
    idx = [i for i in range(off + order, NMAX + 1) if vals.get(i) is not None]

    def resid(i):
        return vals[i] - sum(c * vals[i - j] for j, c in coeffs.items())
    try:
        bad = [i for i in idx if all(vals.get(i - j) is not None for j in coeffs)
               and resid(i) != 0]
    except Exception:
        res['residual failed'] += 1; done.add(a); continue
    thr = max(bad) if bad else off + order - 1
    top = max(idx)
    if top - thr < order + 4:
        res['no margin past the threshold'] += 1; done.add(a); continue
    lo = max(thr + 1, off)
    try:
        if not all(vals.get(i) is not None and vals[i] == CF.value(expr, i)
                   for i in range(lo, lo + order)):
            res['closed form FAILS beyond the threshold'] += 1
            hits.append({'anum': a, 'FAILS': True, 'name': nm, 'line': line})
            done.add(a); json.dump(hits, open(HITS, 'w'), indent=1)
            json.dump(sorted(done), open(DONE, 'w')); continue
    except Exception:
        res['closed form evaluation failed'] += 1; done.add(a); continue
    first = lo
    while first > off and vals.get(first - 1) is not None and \
            vals[first - 1] == CF.value(expr, first - 1):
        first -= 1
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': nm, 'engine': eng, 'line': line, 'expr': str(expr),
                 'coeffs': {int(k): str(v) for k, v in coeffs.items()},
                 'order': order, 'thr': thr, 'first': first, 'claimed': claimed,
                 'offset': off, 'nterms': len(d), 'S': S, 'base': 0})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)
json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
