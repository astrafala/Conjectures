#!/usr/bin/env python3
"""Exact arithmetic in the differential module Q(x)[log(u), exp(g)].

The algebraic machinery in quadfield/multiquad only reaches algebraic generating
functions. But transcendental ones are often still finite-dimensional over Q(x) once
the right atoms are chosen, because

    D( log(u)^a )  = a * (u'/u) * log(u)^(a-1),
    D( exp(k*g) )  = k * g' * exp(k*g),

so the set of monomials  log(u)^a * exp(k*g)  (a >= 0, k in Z) spans a module over
Q(x) that is CLOSED under differentiation. No basis mixing beyond lowering the log
power, and exp never mixes at all.

An element is a dict {(a, k): coefficient in Q(x)}. Everything below is exact
rational-function arithmetic, so the residual test used for the algebraic cases
carries over verbatim: a residual is a polynomial exactly when every monomial other
than (0,0) vanishes and the (0,0) coefficient has constant denominator.
"""
import sympy as sp

x = sp.Symbol('x')


def atoms_of(expr):
    """Find the single log argument u and the single exp argument g, if any."""
    logs = {a.args[0] for a in expr.atoms(sp.log)}
    exps = set()
    for a in expr.atoms(sp.exp):
        exps.add(a.args[0])
    for p in expr.atoms(sp.Pow):
        if p.base is sp.E:
            exps.add(p.exp)
    if len(logs) > 1 or len(exps) > 1:
        return None
    u = logs.pop() if logs else None
    g = exps.pop() if exps else None
    if u is not None and not sp.cancel(u).is_rational_function(x):
        return None
    if g is not None and not sp.cancel(g).is_rational_function(x):
        return None
    return u, g


def to_module(expr, maxlog=6):
    """Return (coeffs, u, g) with expr = sum coeffs[(a,k)] * log(u)^a * exp(g)^k."""
    at = atoms_of(expr)
    if at is None:
        return None
    u, g = at
    L, E = sp.Symbol('L_'), sp.Symbol('E_')
    e = expr
    if u is not None:
        e = e.subs(sp.log(u), L)
    if g is not None:
        e = e.subs(sp.exp(g), E)
    if e.has(sp.log) or e.has(sp.exp):
        return None
    e = sp.cancel(sp.together(e))
    num, den = sp.fraction(e)
    if den.has(L) or den.has(E):
        return None          # not a polynomial in the atoms over Q(x)
    num = sp.expand(num)
    coeffs = {}
    P = sp.Poly(num, L, E) if (u is not None or g is not None) else None
    if P is None:
        c = sp.cancel(num / den)
        if c.free_symbols - {x}:
            return None
        return {(0, 0): c}, u, g
    for (a, k), c in zip(P.monoms(), P.coeffs()):
        if a > maxlog:
            return None
        cc = sp.cancel(c / den)
        if cc.free_symbols - {x}:
            return None
        coeffs[(a, k)] = sp.cancel(coeffs.get((a, k), 0) + cc)
    return coeffs, u, g


def deriv(coeffs, u, g):
    """d/dx on the module."""
    du = sp.cancel(sp.diff(u, x) / u) if u is not None else sp.Integer(0)
    dg = sp.cancel(sp.diff(g, x)) if g is not None else sp.Integer(0)
    out = {}

    def add(key, val):
        out[key] = sp.cancel(out.get(key, 0) + val)

    for (a, k), c in coeffs.items():
        add((a, k), sp.diff(c, x) + c * k * dg)
        if a > 0:
            add((a - 1, k), c * a * du)
    return {kk: v for kk, v in out.items() if sp.cancel(v) != 0}


def theta(coeffs, u, g):
    return {kk: sp.cancel(x * v) for kk, v in deriv(coeffs, u, g).items()}


def add(A, B):
    out = dict(A)
    for kk, v in B.items():
        out[kk] = sp.cancel(out.get(kk, 0) + v)
    return out


def scale(A, c):
    return {kk: sp.cancel(c * v) for kk, v in A.items()}


def apply_poly_theta(poly_in_n, coeffs, u, g, shift, nsym):
    p = sp.Poly(sp.expand(poly_in_n), nsym)
    deg = max(m[0] for m in p.monoms()) if p.monoms() else 0
    powers = [coeffs]
    for _ in range(deg):
        powers.append(theta(powers[-1], u, g))
    out = {}
    for (j,), c in zip(p.monoms(), p.coeffs()):
        term = {}
        for i in range(j + 1):
            term = add(term, scale(powers[i], sp.binomial(j, i) * shift ** (j - i)))
        out = add(out, scale(term, c))
    return out


def residual_ogf(coeffs, u, g, ps, nsym):
    """B = sum_i x^i (p_i(theta+i) A) -- the ordinary generating function case."""
    tot = {}
    for i, p in enumerate(ps):
        if p == 0:
            continue
        tot = add(tot, scale(apply_poly_theta(p, coeffs, u, g, i, nsym), x ** i))
    return tot


def residual_egf(coeffs, u, g, ps, nsym):
    """B = sum_j q_j(theta)[A^(j)] after re-indexing -- the exponential case."""
    r = len(ps) - 1
    qs = [sp.expand(ps[r - j].subs(nsym, nsym + r)) for j in range(r + 1)]
    cur = coeffs
    tot = {}
    for j, q in enumerate(qs):
        if q != 0:
            tot = add(tot, apply_poly_theta(q, cur, u, g, 0, nsym))
        cur = deriv(cur, u, g)
    return tot


def is_polynomial(coeffs):
    for kk, c in coeffs.items():
        if kk != (0, 0) and sp.cancel(c) != 0:
            return False, None
    c = sp.cancel(sp.together(coeffs.get((0, 0), sp.Integer(0))))
    num, den = sp.fraction(c)
    if not den.is_polynomial(x) or sp.Poly(den, x).total_degree() != 0:
        return False, None
    out = sp.expand(sp.cancel(c))
    if not out.is_polynomial(x) or (out.free_symbols - {x}):
        return False, None
    return True, out
