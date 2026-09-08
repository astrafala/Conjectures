"""Entries that state an explicit closed form rather than a recurrence."""
import json, re, os, sys, collections, importlib, zlib
from fractions import Fraction
from math import factorial
import signal
import localentry as LE, openness, closedform as CF, uniform


class _T(Exception):
    pass


# Without a per-entry alarm one slow build eats the whole run: this sweep sat at 26 entries
# across four separate windows, processing nothing, because it was inside a single build the
# whole time. Every other sweep here already has this.
signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(_T()))
BUDGET = int(os.environ.get('BUDGET', '45'))

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


# Sharded. One entry whose terms computation runs past the window ate every window on its
# own -- the sweep restarted at the head of the pool each time, reached the same entry, and
# processed nothing else. The counter printed an empty dict six runs in a row and that is what
# it meant. Shards divide the pool by A-number, so a blocker only stalls its own shard.
SHARD = int(os.environ.get('CFSHARD', '0'))
NSHARD = int(os.environ.get('CFNSHARD', '1'))

for a in sorted(targets):
    if a in done or a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
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
    # A per-entry alarm cannot save a build that spends its whole time inside one C-level
    # call: signals are delivered at bytecode boundaries, so materialising 4^8 rows and their
    # pairs blocks it completely. This sweep sat at 26 entries across five windows for exactly
    # that reason. The estimate below is made from the parse, before anything is built.
    W = p.get('W') or p.get('fixed') or p.get('cols')
    A = p.get('alpha')
    if isinstance(W, int) and isinstance(A, int) and W > 0:
        try:
            rows = (A + 1) ** W
        except Exception:
            rows = None
        if rows is not None and rows * rows > 64 * CAP:
            res[f'too big to be worth starting: {rows} rows at cap {CAP}'] += 1
            done.add(a); json.dump(sorted(done), open(DONE, 'w')); continue
    try:
        signal.alarm(BUDGET)
        b = uniform.build(eng, p, CAP)
        signal.alarm(0)
    except _T:
        signal.alarm(0); res['build timed out'] += 1; done.add(a)
        json.dump(sorted(done), open(DONE, 'w')); continue
    except Exception:
        signal.alarm(0); res['build failed'] += 1; done.add(a)
        json.dump(sorted(done), open(DONE, 'w')); continue
    if b is None:
        res['state space > cap'] += 1; done.add(a); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    N = off + len(d) + order + 12
    try:
        signal.alarm(BUDGET)
        vals, parts = model_values(eng, p, b, N)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['model evaluation failed'] += 1; done.add(a)
        json.dump(sorted(done), open(DONE, 'w')); continue
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
                 'offset': off, 'nterms': len(d), 'S': uniform.size(eng, p, b), 'base': base})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)
json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
