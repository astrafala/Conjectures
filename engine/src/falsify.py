"""Test every parsed-but-unpapered entry's conjectured recurrence far beyond its DATA.

Proving a recurrence needs S+1 matrix-vector products; DISPROVING one needs only enough
terms to reach a failure. So the entries whose state space is past the proving cap, and the
ones whose annihilation run was cut off, can still be decided in the negative cheaply.
"""
import json, re, os, sys, collections, importlib, time
from math import factorial
import localentry as LE, ratrec, openness, uniform

MARK = re.compile(r'onjectur|Empirical', re.I)
# There is no engine list here. It named eleven engines, which was all of them when this was
# written and is now eleven of eighty-three, so seventy-two engines' worth of entries were
# never even parsed and no conjecture of theirs was ever tested for failure. `uniform` knows
# all of them and evaluates each through one interface, which also removes the per-engine
# `avals` dispatch below --- most engines have no such method, and the AttributeError was
# being swallowed and counted as an evaluation error.
names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
EXTRA = 40
out = json.load(open('falsify.json')) if os.path.exists('falsify.json') else []
done = {x['anum'] for x in out}
res = collections.Counter()

for a in sorted(names):
    if a in roster or a in done:
        continue
    nm = names[a]
    try:
        got_eng = uniform.read(nm)
    except Exception:
        got_eng = None
    if not got_eng:
        continue
    eng, p = got_eng
    e = LE.get(a)
    recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                        if MARK.search(L)) if r]
    if not recs:
        res['no recurrence'] += 1; continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        built = uniform.build(eng, p, CAP)
    except Exception:
        res['build error'] += 1; continue
    if built is None:
        res['over cap'] += 1; continue
    t0 = time.time()
    try:
        vals = uniform.terms(eng, p, built, off + len(d) + EXTRA)
    except Exception:
        res['eval error'] += 1; continue
    # uniform.terms already returns the sequence in the entry's own scaling, as exact
    # rationals; a term that is not an integer is one the model cannot pin and is left out
    got = [None if (v is None or v.denominator != 1) else v.numerator for v in vals]
    if got[off:off + len(d)] != d:
        res['DATA mismatch'] += 1; continue
    # the entry's own bound: a recurrence stated ``for n>5'' says nothing at n=5, and
    # flagging it there is a false alarm, not a disproof
    lo = off + order
    if dd is not None:
        lo = max(lo, int(dd) + 1)
    bad = []
    for n in range(lo, len(got)):
        if got[n] is None or any(got[n - i] is None for i in coeffs):
            continue
        if got[n] != sum(c * got[n - i] for i, c in coeffs.items()):
            bad.append(n)
    if bad:
        res['RECURRENCE FAILS'] += 1
        out.append({'anum': a, 'engine': eng, 'order': order, 'claimed': dd,
                    'fails_at': bad[:12], 'nterms': len(d), 'offset': off,
                    'coeffs': {int(k): str(v) for k, v in coeffs.items()}, 'name': nm})
        print('FAILS', a, bad[:6], flush=True)
    else:
        res['holds to n=%d' % (len(got) - 1)] += 0
        res['holds'] += 1
    json.dump(out, open('falsify.json', 'w'), indent=1)
print(dict(res))
