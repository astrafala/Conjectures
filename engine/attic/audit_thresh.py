"""Recompute each paper's threshold DIRECTLY from the model's own terms.

The engines' threshold routine starts its residual test at the first index its walk length
allows (n_lo + order). For a pair-state engine n_lo is 2, so the smallest one or two indices
at which the recurrence can be stated are never TESTED, and the routine reports the weakest
conclusion consistent with that. The claim it yields is true but weaker than the truth, and
for an entry whose line carries no range it falls short of the entry's own assertion.
"""
import json, re, glob, importlib, collections, sys
from math import factorial
import localentry as LE, ratrec
MARK = re.compile(r'onjectur|Empirical', re.I)
ENG = {'transfer6': None, 'transfer7': None, 'transfer8': None, 'transfer9': None,
       'transfer10': None, 'transfer11': None, 'transfer12': None, 'transfer13': None,
       'transfer14': None, 'transfer15': None, 'transfer16': None}
for k in ENG:
    ENG[k] = importlib.import_module(k)
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
res = collections.Counter(); out = {}
files = sys.argv[1:]
for f in files:
    mod = ENG[f.split('_')[0]]
    name = f.split('_')[0]
    for h in json.load(open(f)):
        if h.get('FAILS'):
            continue
        a = h['anum']
        e = LE.get(a)
        try:
            p = mod.parse_name(e['name'])
        except Exception:
            p = None
        if p is None:
            res['unparsed'] += 1; continue
        try:
            try: b = mod.build(p, cap=400000)
            except TypeError: b = mod.build(p)
        except Exception:
            res['build failed'] += 1; continue
        if b is None:
            res['too big'] += 1; continue
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                            if MARK.search(L)) if r]
        if not recs:
            res['no rec'] += 1; continue
        coeffs, dd = recs[0]; order = max(coeffs)
        N = off + len(d) + 30
        try:
            if name == 'transfer10':
                vals = mod.avals(b[0], b[1], p, N)
            else:
                vals = mod.avals(b[0], b[1], b[2], p, N)
        except Exception:
            res['eval failed'] += 1; continue
        fac = p.get('frac', 1) * (factorial(p['K']) if name in SCALED else 1)
        got = [None if v is None or v % fac else v // fac for v in vals]
        if got[off:off + len(d)] != d:
            res['DATA MISMATCH'] += 1; continue
        first = off + order
        worst = first - 1
        for n in range(first, len(got)):
            if got[n] is None or any(n - i < 0 or got[n - i] is None for i in coeffs):
                continue
            if got[n] != sum(c * got[n - i] for i, c in coeffs.items()):
                worst = n
        old = h.get('nthr', h.get('threshold'))
        out[a] = {'old': old, 'true': worst, 'order': order, 'offset': off,
                  'claimed': dd, 'engine': name}
        if old is None: res['no old threshold'] += 1
        elif worst < old: res['UNDERSTATED'] += 1
        elif worst > old: res['OVERSTATED (would be a real error)'] += 1
        else: res['exact'] += 1
json.dump(out, open('audit_thresh_%s.json' % files[0].split('_')[0], 'w'))
print(dict(res))
