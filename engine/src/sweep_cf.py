"""Entries that state an explicit closed form rather than a recurrence."""
import json, re, os, sys, collections, importlib
from fractions import Fraction
from math import factorial
import localentry as LE, openness, closedform as CF, uniform

# No engine list here. It named twelve, which was all of them when this was written and is
# twelve of eighty-three now, so every closed-form entry whose model needs a later engine was
# recorded as "no engine reads the name". `uniform` knows all of them, evaluates each through
# one interface, and handles the ones whose interface differs.
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
# a run on a different target list must not write into the standing one: HITS and DONE were
# fixed names, so pointing TARGETS at a new pool silently reused the old run's `done` set and
# processed nothing
HITS = os.environ.get('HITS', 'cf_hits.json')
DONE = os.environ.get('DONE', 'cf_done.json')
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
targets = json.load(open(os.environ.get('TARGETS', 'polyclosed_cands.json')))


def model_values(eng, p, b, N):
    """a(0..N) as Fractions, None where the engine has no value at that index."""
    return uniform.terms(eng, p, b, N + 2), b


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
    try:
        got_eng = uniform.read(nm)
    except Exception:
        got_eng = None
    if not got_eng:
        res['no engine reads the name'] += 1; done.add(a); continue
    eng, p = got_eng
    try:
        b = uniform.build(eng, p, CAP)
    except Exception:
        res['build failed'] += 1; done.add(a); continue
    if b is None:
        res['state space > cap'] += 1; done.add(a); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    N = off + len(d) + order + 12
    try:
        vals, parts = model_values(eng, p, b, N)
    except Exception:
        res['model evaluation failed'] += 1; done.add(a); continue
    # tie the model to the entry: it must reproduce every published term exactly
    shifts = [0, 1, 2]
    base = None
    for s in shifts:
        seq = [vals[off + k + s] if off + k + s < len(vals) else None for k in range(len(d))]
        if all(v is not None and v.denominator == 1 and v.numerator == d[k]
               for k, v in enumerate(seq)):
            base = s; break
    if base is None:
        res['model does not match DATA'] += 1; done.add(a); continue
    try:
        thr = uniform.threshold(eng, p, b, coeffs, order)
        thr = None if thr is None else thr - base
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
