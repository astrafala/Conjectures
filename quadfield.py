#!/usr/bin/env python3
"""Exact arithmetic in Q(x)[sqrt(D)], which is what these generating functions live in.

Every g.f. here is u + v*sqrt(D) with u, v, D rational functions of x. That field is
closed under theta = x d/dx, because

    theta(u + v*sqrt(D)) = x*u' + ( x*v' + x*v*D'/(2D) ) * sqrt(D),

using sqrt(D)' = D'/(2 sqrt(D)) = (D'/(2D)) * sqrt(D). So the residual B(x) can be
written exactly as P + Q*sqrt(D) with P, Q rational, and

    B is a polynomial  <=>  Q == 0 and denominator(P) is constant,

both decided by exact rational-function cancellation. No simplify(), no series
truncation, no numerics -- the verdict is a proof.
"""
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

s = sp.Symbol('s')


def to_quad(expr):
    if _has_nested_radical(expr):
        return None
    """Write expr as (u, v, D) with expr = u + v*sqrt(D), u,v,D in Q(x). None if not possible."""
    rads = {a.args[0] for a in expr.atoms(sp.Pow)
            if a.exp == sp.Rational(1, 2) or a.exp == -sp.Rational(1, 2)}
    rads = {sp.cancel(sp.together(r)) for r in rads}
    if not rads:
        e = sp.cancel(sp.together(expr))
        if e.free_symbols - {x}:
            return None
        return (e, sp.Integer(0), sp.Integer(1))
    if len(rads) != 1:
        return None
    D = rads.pop()
    e = expr.subs(sp.sqrt(D), s)
    e = e.replace(lambda t: t.is_Pow and t.exp == -sp.Rational(1, 2), lambda t: 1 / s)
    if e.has(sp.sqrt):
        return None
    num, den = sp.fraction(sp.together(e))
    num, den = sp.expand(num), sp.expand(den)
    def lin(p):
        q = sp.Poly(p, s)
        c = [sp.Integer(0), sp.Integer(0)]
        for (k,), co in zip(q.monoms(), q.coeffs()):
            c[k % 2] += co * D ** (k // 2)
        return sp.cancel(c[0]), sp.cancel(c[1])
    n0, n1 = lin(num)
    d0, d1 = lin(den)
    denom = sp.cancel(d0 ** 2 - d1 ** 2 * D)
    if denom == 0:
        return None
    u = sp.cancel((n0 * d0 - n1 * d1 * D) / denom)
    v = sp.cancel((n1 * d0 - n0 * d1) / denom)
    if (u.free_symbols | v.free_symbols | D.free_symbols) - {x}:
        return None
    return (u, v, D)


def theta_quad(uvD):
    u, v, D = uvD
    du = sp.cancel(x * sp.diff(u, x))
    dv = sp.cancel(x * sp.diff(v, x) + x * v * sp.diff(D, x) / (2 * D))
    return (du, dv, D)


def add(a, b):
    return (sp.cancel(a[0] + b[0]), sp.cancel(a[1] + b[1]), a[2])


def scale(a, c):
    return (sp.cancel(c * a[0]), sp.cancel(c * a[1]), a[2])


def apply_poly_theta(poly_in_n, uvD, shift, nsym):
    """Apply p(theta + shift)."""
    if sp.expand(poly_in_n) == 0:
        return (sp.Integer(0), sp.Integer(0), uvD[2])
    p = sp.Poly(sp.expand(poly_in_n), nsym)
    powers = [uvD]
    deg = p.degree() if p.total_degree() >= 0 else 0
    for _ in range(deg):
        powers.append(theta_quad(powers[-1]))
    out = (sp.Integer(0), sp.Integer(0), uvD[2])
    for (j,), c in zip(p.monoms(), p.coeffs()):
        term = (sp.Integer(0), sp.Integer(0), uvD[2])
        for i in range(j + 1):
            term = add(term, scale(powers[i], sp.binomial(j, i) * shift ** (j - i)))
        out = add(out, scale(term, c))
    return out


def residual(uvD, ps, nsym):
    tot = (sp.Integer(0), sp.Integer(0), uvD[2])
    for i, p in enumerate(ps):
        if sp.expand(p) == 0:
            continue
        tot = add(tot, scale(apply_poly_theta(p, uvD, i, nsym), x ** i))
    return tot


def is_polynomial(r):
    """(True, poly) if r is a polynomial in x; else (False, None)."""
    u, v, D = r
    if sp.cancel(v) != 0:
        return False, None
    u = sp.cancel(sp.together(u))
    num, den = sp.fraction(u)
    if not den.is_polynomial(x) or sp.Poly(den, x).total_degree() != 0:
        return False, None
    out = sp.expand(sp.cancel(u))
    if not out.is_polynomial(x) or (out.free_symbols - {x}):
        return False, None
    return True, out


def deriv(uvD):
    """Plain d/dx on u + v*sqrt(D); the field is closed under it too."""
    u, v, D = uvD
    du = sp.cancel(sp.diff(u, x))
    dv = sp.cancel(sp.diff(v, x) + v * sp.diff(D, x) / (2 * D))
    return (du, dv, D)
