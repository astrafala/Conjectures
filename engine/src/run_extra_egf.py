#!/usr/bin/env python3
"""Second, still-open recurrence conjecture on A066052 (transcendental e.g.f.)."""
import json
import sympy as sp
import logexp as le
from prove_rec import parse_gf, parse_conj

x, n = sp.symbols('x n')
EXTRA = json.load(open("extra-conj.json"))
cache = json.load(open("egf-cache.json"))
out = {}
for a, meta in EXTRA.items():
    v = cache.get(a)
    if not v:
        continue
    A = parse_gf(v["gfs"][0], 'x', raw=v["gfs"][0])
    m = le.to_module(A)
    coeffs, u, g = m
    ps = parse_conj(meta["others"][0])
    B = le.residual_egf(coeffs, u, g, ps, n)
    ok, P = le.is_polynomial(B)
    print(a, "PROVED" if ok else "residual not polynomial", "B=", sp.sstr(P) if ok else "")
    if ok:
        deg = sp.Poly(P, x).total_degree() if P != 0 else 0
        out[a] = {"anum": a, "mode": "egf", "status": "PROVED", "B": sp.sstr(P),
                  "degree": int(deg), "order": len(ps) - 1, "gf": sp.sstr(A)}
json.dump(out, open("extra-egf-results.json", "w"), indent=1, sort_keys=True)
