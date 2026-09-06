"""Adversarial test: perturb each proved closed form and confirm the pipeline rejects it."""
import json, importlib, random
from fractions import Fraction
from math import factorial
import sympy, localentry as LE, closedform as CF
ENG = ['transfer3','transfer9','transfer6','transfer16','transfer12','transfer10','transfer8',
       'transfer14','transfer11','transfer15','transfer13','transfer7']
M = {e: importlib.import_module(e) for e in ENG}
import transfer2 as T2
SCALED = ('transfer7','transfer8','transfer10','transfer12','transfer16')
n = sympy.Symbol('n')
random.seed(11)
hits = [h for h in json.load(open('cf_hits.json')) if not h.get('FAILS')]
acc = rej = novals = 0
badly = []
for h in hits:
    eng = h['engine']; nm = h['name']
    r = M[eng].parse_name(nm)
    p = {'t3': r} if eng == 'transfer3' else r
    if eng == 'transfer3': b = M[eng].build(*p['t3'])
    else:
        try: b = M[eng].build(p, cap=20000)
        except TypeError: b = M[eng].build(p)
    N = h['first'] + 40 + h['base'] + 3
    if eng in ('transfer6','transfer3'):
        st, adj = b
        tm = M[eng].terms if eng == 'transfer6' else T2.terms
        fr = p['frac'] if eng == 'transfer6' else 1
        vals = [Fraction(v, fr) for v in tm(adj, len(st), N)]
    elif eng == 'transfer10':
        adj, start, _ = b
        f = factorial(p['K']) * p['frac']
        vals = [None if q is None else Fraction(q, f) for q in M[eng].avals(adj, start, p, N)]
    else:
        adj, start, end, _ = b
        f = p['frac'] * (factorial(p['K']) if eng in SCALED else 1)
        vals = [None if q is None else Fraction(q, f) for q in M[eng].avals(adj, start, end, p, N)]
    expr = sympy.sympify(h['expr'], locals={'n': n}, rational=True)
    base, first = h['base'], h['first']
    # mutate: add a nonzero integer, or bump one coefficient
    for delta in (sympy.Integer(1), n, sympy.Integer(-2)):
        mut = expr + delta
        ok = all(vals[i+base] is not None and vals[i+base] == CF.value(mut, i)
                 for i in range(first, first+20) if i+base < len(vals))
        if ok: acc += 1; badly.append((h['anum'], str(delta)))
        else: rej += 1
print('mutants rejected', rej, 'accepted', acc)
for x in badly[:10]: print(x)
