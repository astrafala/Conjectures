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


def _mul(a, b, N):
    return [sp.cancel(sum(a[j] * b[i - j] for j in range(i + 1))) for i in range(N)]


def _div(a, b, N):
    if sp.cancel(b[0]) == 0:
        return None
    out = [sp.Integer(0)] * N
    for i in range(N):
        out[i] = sp.cancel((a[i] - sum(b[j] * out[i - j] for j in range(1, i + 1))) / b[0])
    return out


def _compose(e, s, N):
    """The series of a rational function e(x) with x replaced by the series s.

    Composition is done on coefficient lists rather than by substituting into the
    expression and expanding: substituting a series into a rational function and calling
    expand is what made this unusable on anything but polynomials.
    """
    num, den = sp.fraction(sp.cancel(sp.together(e)))
    def poly_comp(p):
        p = sp.Poly(sp.expand(p), x)
        acc = [sp.Integer(0)] * N
        power = [sp.Integer(1)] + [sp.Integer(0)] * (N - 1)
        coeffs = p.all_coeffs()[::-1]          # ascending
        for c in coeffs:
            acc = [sp.cancel(acc[i] + c * power[i]) for i in range(N)]
            power = _mul(power, s, N)
        return acc
    a, b = poly_comp(num), poly_comp(den)
    return _div(a, b, N)


def series(f, g, N):
    """The first N coefficients of A(t), from the residue formula.

    No closed form for the root is needed, which is the point: the minimal polynomial can
    have degree five or more in y, where none exists.
    """
    xs = [sp.Integer(0)] * N                    # the branch x(t), as a series in t
    for _ in range(N + 1):
        gs = _compose(g, xs, N)
        if gs is None:
            return None
        nxt = [sp.Integer(0)] + gs[:N - 1]      # multiply by t
        if nxt == xs:
            break
        xs = nxt
    fs = _compose(f, xs, N)
    dg_ = _compose(sp.diff(g, x), xs, N)
    if fs is None or dg_ is None:
        return None
    den = [sp.Integer(1) - (dg_[0] * 0)] + [sp.Integer(0)] * (N - 1)
    den = [sp.Integer(1)] + [sp.cancel(-dg_[i - 1]) for i in range(1, N)]
    return _div(fs, den, N)


def pick_factor(P, ser, N):
    """The irreducible factor of P that the series satisfies.

    Substituting a truncated series into a polynomial and asking for the result to vanish
    identifies the branch without ever solving for it.
    """
    best = None
    for e in branch_factors(P):
        v = sp.expand(e.subs(y, sum(ser[i] * t ** i for i in range(N))))
        if all(sp.cancel(v.coeff(t, i)) == 0 for i in range(N - sp.Poly(e, y).degree())):
            if best is None or sp.Poly(e, y).degree() < sp.Poly(best, y).degree():
                best = e
    return best
