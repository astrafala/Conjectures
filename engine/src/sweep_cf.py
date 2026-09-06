"""Entries that state an explicit closed form rather than a recurrence."""
import json, re, os, sys, collections, importlib
from fractions import Fraction
from math import factorial
import localentry as LE, openness, closedform as CF

ENG = ['transfer3', 'transfer9', 'transfer6', 'transfer16', 'transfer12', 'transfer10',
       'transfer8', 'transfer14', 'transfer11', 'transfer15', 'transfer13', 'transfer7']
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
targets = json.load(open(os.environ.get('TARGETS', 'polyclosed_cands.json')))


def model_values(eng, p, b, N):
    """a(0..N) as Fractions, None where the engine has no value at that index."""
    if eng in ('transfer6', 'transfer3'):
        st, adj = b
        tm = M[eng].terms if eng == 'transfer6' else T2.terms
        fr = p['frac'] if eng == 'transfer6' else 1
        t = tm(adj, len(st), N + 2)
        return [Fraction(v, fr) for v in t], (st, adj)
    if eng == 'transfer10':
        adj, start, _ = b
        v = M[eng].avals(adj, start, p, N + 2)
        f = factorial(p['K']) * p['frac']
        return [None if q is None else Fraction(q, f) for q in v], (adj, start)
    adj, start, end, _ = b
    v = M[eng].avals(adj, start, end, p, N + 2)
    f = p['frac'] * (factorial(p['K']) if eng in SCALED else 1)
    return [None if q is None else Fraction(q, f) for q in v], (adj, start, end)


for a in sorted(targets):
    if a in done or a in roster:
        continue
    nm = names[a]
    e = LE.get(a)
    got = None
    for L in e['comment'] + e['formula']:
        q = CF.parse_line(L)
        if q:
            got = (q[0], q[1], L.strip()); break
    if not got:
        res['no readable closed form'] += 1; done.add(a); continue
    expr, claimed, line = got
    ann = CF.annihilator(expr)
    if ann is None:
        res['closed form has no integer annihilator'] += 1; done.add(a); continue
    coeffs, order = ann
    op, _ = openness.status(a)
    if not op:
        res['not open'] += 1; done.add(a); continue
    p = eng = None
    for en in ENG:
        try:
            r = M[en].parse_name(nm)
        except Exception:
            r = None
        if r:
            p, eng = ({'t3': r} if en == 'transfer3' else r), en; break
    if p is None:
        res['no engine reads the name'] += 1; done.add(a); continue
    try:
        if eng == 'transfer3':
            c0, al, _, _ = p['t3']
            if (al + 1) ** c0 > CAP:
                res['state space > cap'] += 1; done.add(a); continue
            b = M[eng].build(*p['t3'])
        else:
            try: b = M[eng].build(p, cap=CAP)
            except TypeError: b = M[eng].build(p)
    except Exception:
        res['build failed'] += 1; done.add(a); continue
    if b is None or not b[0]:
        res['state space > cap'] += 1; done.add(a); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    N = off + len(d) + order + 12
    try:
        vals, parts = model_values(eng, p, b, N)
    except Exception:
        res['model evaluation failed'] += 1; done.add(a); continue
    # tie the model to the entry: it must reproduce every published term exactly
    shifts = [0] if eng not in ('transfer6', 'transfer3') else [0, 1, 2]
    base = None
    for s in shifts:
        seq = [vals[off + k + s] if off + k + s < len(vals) else None for k in range(len(d))]
        if all(v is not None and v.denominator == 1 and v.numerator == d[k]
               for k, v in enumerate(seq)):
            base = s; break
    if base is None:
        res['model does not match DATA'] += 1; done.add(a); continue
    try:
        if eng in ('transfer6', 'transfer3'):
            th = M[eng].threshold if eng == 'transfer6' else T2.threshold
            st, adj = parts
            thr = th(adj, len(st), coeffs, order)
            thr = None if thr is None else thr - base
        elif eng == 'transfer10':
            adj, start = parts
            thr = M[eng].threshold(adj, start, coeffs, order, p)
        else:
            adj, start, end = parts
            thr = M[eng].threshold(adj, start, end, coeffs, order, p)
    except Exception:
        res['threshold failed'] += 1; done.add(a); continue
    if thr is None:
        res['model does not satisfy the annihilator'] += 1; done.add(a); continue
    # both a and f obey the same monic recurrence beyond thr, so agreement on `order`
    # consecutive indices there propagates forever
    lo = max(thr + 1, off)
    idx = list(range(lo, lo + order))
    try:
        agree = all(vals[i + base] is not None and vals[i + base] == CF.value(expr, i)
                    for i in idx)
    except Exception:
        res['closed form evaluation failed'] += 1; done.add(a); continue
    if not agree:
        res['closed form FAILS beyond the threshold'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm, 'line': line})
        done.add(a); json.dump(hits, open(HITS, 'w'), indent=1)
        json.dump(sorted(done), open(DONE, 'w')); continue
    # tighten: the first index from which the closed form holds for good
    first = lo
    while first > off and vals[first - 1 + base] is not None and \
            vals[first - 1 + base] == CF.value(expr, first - 1):
        first -= 1
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': nm, 'engine': eng, 'line': line,
                 'expr': sympy_str(expr) if False else str(expr),
                 'coeffs': {int(k): str(v) for k, v in coeffs.items()},
                 'order': order, 'thr': thr, 'first': first, 'claimed': claimed,
                 'offset': off, 'nterms': len(d), 'S': len(b[0]), 'base': base})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)
json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
