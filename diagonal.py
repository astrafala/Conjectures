#!/usr/bin/env python3
"""Generating functions for sequences defined by coefficient extraction.

A large family of entries is defined not by a formula for a(n) but by an instruction:

    a(n) = [x^n] f(x) g(x)^n .

Those entries look formula-free, and every engine here skipped them. They are not. Such a
sequence is a diagonal, and its generating function is algebraic and computable.

Write A(t) = sum_n a(n) t^n. Reading [x^n] as a contour integral,

    A(t) = sum_n t^n (1/2pi i) \oint f(x) g(x)^n x^(-n-1) dx
         = (1/2pi i) \oint f(x) / (x - t g(x)) dx,

the geometric sum converging on a small enough circle. The integrand has one pole inside
that circle: the branch x(t) of x = t g(x) with x(0) = 0, which exists and is unique when
g(0) != 0 -- this is the setting of Lagrange inversion. Taking the residue there,

    A(t) = f(x(t)) / (1 - t g'(x(t))).                                            (*)

So A is an algebraic function of t, and its minimal polynomial follows by eliminating x
between

    x - t g(x) = 0        and        y (1 - t g'(x)) - f(x) = 0,

which is a resultant. That polynomial is then handed to algfield.py, and the conjectured
recurrence is settled by the usual residual test.

Nothing here is taken from the entry except its own definition of a(n). The branch is
chosen by matching the published terms, and the resulting series is checked against them
before use.
"""
import re
import sympy as sp

x, t, y = sp.symbols('x t y')


def parse_extraction(src):
    """Turn '[x^n] f(x)*g(x)^n' into (f, g), or None."""
    s = src.split(" - _")[0].strip().rstrip('.')
    s = re.sub(r"^a\(n\)\s*=\s*", "", s, flags=re.I)
    m = re.match(r"\[\s*x\^\(?n\)?\s*\]\s*(.+)$", s)
    if not m:
        m = re.match(r"[Cc]oefficient of x\^n in\s*(.+)$", s)
    if not m:
        return None
    body = m.group(1).strip().rstrip('.')
    body = body.replace("^", "**")
    body = re.sub(r"(\d)\s*\(", r"\1*(", body)
    body = re.sub(r"\)\s*\(", r")*(", body)
    body = re.sub(r"(\d)\s*x\b", r"\1*x", body)
    body = re.sub(r"\)\s*x\b", r")*x", body)
    n = sp.Symbol('n')
    try:
        e = sp.sympify(body, locals={'x': x, 'n': n})
    except Exception:
        return None
    if e.free_symbols - {x, n}:
        return None
    # split into the part carrying the exponent n and the rest
    f, g = sp.Integer(1), sp.Integer(1)
    for fac in sp.Mul.make_args(e if e.is_Mul else sp.together(e)):
        b, ex = fac.as_base_exp()
        if ex.has(n):
            # the exponent must be linear in n: q*n + r, with q an integer
            pn = sp.Poly(sp.expand(ex), n)
            if pn.degree() != 1:
                return None
            q, r = pn.coeff_monomial(n), pn.coeff_monomial(1)
            if not q.is_Integer or r.has(n):
                return None
            g *= b ** q
            if r != 0:
                f *= b ** r
        else:
            f *= fac
    if g == 1 or g.has(n) or f.has(n):
        return None
    return sp.cancel(f), sp.cancel(g)


def minimal_polynomial(f, g):
    """Eliminate x between x = t g(x) and y (1 - t g') = f to get P(t, y)."""
    if sp.simplify(g.subs(x, 0)) == 0:
        return None                      # no branch through the origin
    e1 = sp.numer(sp.together(x - t * g))
    e2 = sp.numer(sp.together(y * (1 - t * sp.diff(g, x)) - f))
    try:
        P = sp.resultant(sp.Poly(sp.expand(e1), x), sp.Poly(sp.expand(e2), x))
    except Exception:
        return None
    P = sp.expand(sp.factor(P))
    if P == 0 or not P.is_polynomial(t, y):
        return None
    return P


def branch_factors(P):
    out = []
    for fac, _ in sp.factor_list(sp.Poly(P, y))[1]:
        e = fac.as_expr()
        if sp.Poly(e, y).degree() >= 1:
            out.append(sp.expand(e))
    return out or [sp.expand(P)]
