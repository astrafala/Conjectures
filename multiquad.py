#!/usr/bin/env python3
"""Exact arithmetic in a multiquadratic extension Q(x)[sqrt(D_1),...,sqrt(D_k)].

Basis: e_S = prod_{i in S} sqrt(D_i) over subsets S of {1..k}. An element is a dict
S -> coefficient in Q(x). The point is that theta = x d/dx is DIAGONAL in this basis:

    theta( c * e_S ) = ( x c' + c * sum_{i in S} x D_i'/(2 D_i) ) * e_S ,

because (sqrt(D))' = (D'/(2D)) sqrt(D). So no basis mixing ever occurs, and deciding
whether a residual is a polynomial is: every S != {} coefficient is 0, and the empty-set
coefficient has constant denominator. All exact rational-function arithmetic.
"""
import itertools
import sympy as sp

x = sp.Symbol('x')

def _has_nested_radical(expr):
    """A radical inside another radical: the reductions here assume independent
    radicands, so such an expression must be refused rather than mis-reduced."""
    for a in expr.atoms(sp.Pow):
        if a.exp in (sp.Rational(1, 2), -sp.Rational(1, 2)):
            for b in a.base.atoms(sp.Pow):
                if b.exp in (sp.Rational(1, 2), -sp.Rational(1, 2)):
                    return True
    return False



def _radicands(expr):
    rs = []
    for a in expr.atoms(sp.Pow):
        if a.exp in (sp.Rational(1, 2), -sp.Rational(1, 2)):
            r = sp.cancel(sp.together(a.base))
            if not any(sp.cancel(r - t) == 0 for t in rs):
                rs.append(r)
    return rs


def to_multi(expr, maxk=3):
    if _has_nested_radical(expr):
        return None
    """Return (coeffs, Ds) with expr = sum_S coeffs[S] * prod_{i in S} sqrt(Ds[i])."""
    Ds = _radicands(expr)
    if len(Ds) > maxk:
        return None
    if not Ds:
        e = sp.cancel(sp.together(expr))
        if e.free_symbols - {x}:
            return None
        return {frozenset(): e}, []
    syms = [sp.Symbol(f's_{i}') for i in range(len(Ds))]
    e = expr
    for D, s in zip(Ds, syms):
        e = e.subs(sp.sqrt(D), s)
        e = e.replace(lambda t: t.is_Pow and t.base == D and t.exp == -sp.Rational(1, 2),
                      lambda t: 1 / s)
    if e.has(sp.sqrt) or any(e.has(sp.sqrt(D)) for D in Ds):
        return None
    num, den = sp.fraction(sp.together(e))
    num, den = sp.expand(num), sp.expand(den)

    def reduce_ml(p):
        """Reduce a polynomial in syms to multilinear form using s_i^2 = D_i."""
        p = sp.expand(p)
        for s, D in zip(syms, Ds):
            while True:
                q = sp.Poly(p, s)
                if q.degree() < 2:
                    break
                p = sp.expand(sum(c * D ** (k // 2) * s ** (k % 2)
                                  for (k,), c in zip(q.monoms(), q.coeffs())))
        return sp.expand(p)

    num, den = reduce_ml(num), reduce_ml(den)
    # rationalise the denominator one square root at a time
    for s in syms:
        if den.has(s):
            conj = den.subs(s, -s)
            num = reduce_ml(sp.expand(num * conj))
            den = reduce_ml(sp.expand(den * conj))
    den = sp.cancel(den)
    if den == 0 or den.has(*syms):
        return None
    coeffs = {}
    for r in range(len(syms) + 1):
        for S in itertools.combinations(range(len(syms)), r):
            mon = sp.prod([syms[i] for i in S]) if S else sp.Integer(1)
            c = num
            for i, s in enumerate(syms):
                c = sp.Poly(c, s).coeff_monomial(s if i in S else 1)
                if c is None:
                    c = sp.Integer(0)
                    break
            if c != 0:
                coeffs[frozenset(S)] = sp.cancel(c / den)
    # safer extraction: expand num over the monomial basis directly
    coeffs = {}
    P = sp.Poly(num, *syms) if syms else None
    for monom, c in zip(P.monoms(), P.coeffs()):
        if any(m > 1 for m in monom):
            return None
        S = frozenset(i for i, m in enumerate(monom) if m == 1)
        coeffs[S] = sp.cancel(coeffs.get(S, 0) + c / den)
    if any((c.free_symbols - {x}) for c in coeffs.values()):
        return None
    return coeffs, Ds


def theta(coeffs, Ds):
    out = {}
    for S, c in coeffs.items():
        extra = sum(x * sp.diff(Ds[i], x) / (2 * Ds[i]) for i in S)
        out[S] = sp.cancel(x * sp.diff(c, x) + c * extra)
    return out


def add(a, b):
    out = dict(a)
    for S, c in b.items():
        out[S] = sp.cancel(out.get(S, 0) + c)
    return out


def scale(a, k):
    return {S: sp.cancel(k * c) for S, c in a.items()}


def apply_poly_theta(poly_in_n, coeffs, Ds, shift, nsym):
    if sp.expand(poly_in_n) == 0:
        return {}
    p = sp.Poly(sp.expand(poly_in_n), nsym)
    deg = max(m[0] for m in p.monoms()) if p.monoms() else 0
    powers = [coeffs]
    for _ in range(deg):
        powers.append(theta(powers[-1], Ds))
    out = {}
    for (j,), c in zip(p.monoms(), p.coeffs()):
        term = {}
        for i in range(j + 1):
            term = add(term, scale(powers[i], sp.binomial(j, i) * shift ** (j - i)))
        out = add(out, scale(term, c))
    return out


def residual(coeffs, Ds, ps, nsym):
    tot = {}
    for i, p in enumerate(ps):
        if p == 0:
            continue
        tot = add(tot, scale(apply_poly_theta(p, coeffs, Ds, i, nsym), x ** i))
    return tot


def is_polynomial(r):
    for S, c in r.items():
        if S and sp.cancel(c) != 0:
            return False, None
    c = sp.cancel(sp.together(r.get(frozenset(), sp.Integer(0))))
    num, den = sp.fraction(c)
    if not den.is_polynomial(x) or sp.Poly(den, x).total_degree() != 0:
        return False, None
    out = sp.expand(sp.cancel(c))
    if not out.is_polynomial(x) or (out.free_symbols - {x}):
        return False, None
    return True, out


def deriv(coeffs, Ds):
    out = {}
    for S, c in coeffs.items():
        extra = sum(sp.diff(Ds[i], x) / (2 * Ds[i]) for i in S)
        out[S] = sp.cancel(sp.diff(c, x) + c * extra)
    return out
