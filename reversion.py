#!/usr/bin/env python3
"""Generating functions posted as a series reversion.

OEIS writes these as `Series_Reversion(f(x))`, sometimes wrapped: `(1/x)*Series_Reversion(x/G(x))`,
`Series_Reversion(...)^2`. The parser refused them outright, but a reversion of an
algebraic function is algebraic, and its minimal polynomial is a resultant away.

Let R be the reversion, so f(R) = x by definition, and let the entry's generating
function be A = E(x, R) for whatever wrapper E the entry uses. Eliminating R between

    y - E(x, R) = 0        and        f(R) - x = 0

gives a polynomial in x and y that A satisfies. Taking the resultant does the
elimination; the factor with the entry's own expansion is then the minimal polynomial,
and algfield.py takes it from there.
"""
import re
import sympy as sp

x, y, R = sp.symbols('x y R')

REV = re.compile(r"Series[_ ]?Reversion|series reversion|reversion of", re.I)


def _clean(s):
    s = s.strip().rstrip('.')
    s = s.replace('^', '**')
    s = re.sub(r"(\d)\s*\(", r"\1*(", s)
    s = re.sub(r"\)\s*\(", r")*(", s)
    s = re.sub(r"(\d)\s*([xyR])\b", r"\1*\2", s)
    return s


def parse(src, locals_=None):
    """Return the polynomial P(x, y) satisfied by the entry's g.f., or None."""
    if not REV.search(src):
        return None
    s = src.strip().rstrip('.')
    s = re.sub(r"^A\(x\)\s*=\s*", "", s, flags=re.I)
    s = re.sub(r"^is\s+(the\s+)?", "", s, flags=re.I)
    s = re.sub(r"series[_ ]?reversion", "REV", s, flags=re.I)
    s = re.sub(r"reversion\s+of\s+", "REV", s, flags=re.I)
    m = re.search(r"REV\s*\(", s)
    if m:
        i = m.end() - 1
        depth, j = 0, i
        while j < len(s):
            if s[j] == '(':
                depth += 1
            elif s[j] == ')':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            return None
        inner, outer = s[i + 1:j], s[:m.start()] + "@REV@" + s[j + 1:]
    else:
        m = re.search(r"REV", s)
        if not m:
            return None
        inner, outer = s[m.end():], "@REV@"
    loc = {'x': x, 'y': y, 'R': R}
    if locals_:
        loc.update(locals_)
    try:
        f = sp.sympify(_clean(inner), locals=loc)
        E = sp.sympify(_clean(outer.replace("@REV@", "R")), locals=loc)
    except Exception:
        return None
    if (f.free_symbols - {x}) or (E.free_symbols - {x, R}):
        return None
    eq1 = sp.expand(sp.numer(sp.together(y - E)))
    eq2 = sp.expand(sp.numer(sp.together(f.subs(x, R) - x)))
    if not (eq1.is_polynomial(R) and eq2.is_polynomial(R)):
        return None
    try:
        P = sp.resultant(sp.Poly(eq1, R), sp.Poly(eq2, R))
    except Exception:
        return None
    P = sp.expand(sp.factor(P))
    if P == 0 or not P.is_polynomial(x, y):
        return None
    return P


def branch_factors(P):
    """Irreducible factors of P as candidate minimal polynomials."""
    out = []
    for f, _ in sp.factor_list(sp.Poly(P, y))[1]:
        e = f.as_expr()
        if sp.Poly(e, y).degree() >= 1:
            out.append(sp.expand(e))
    return out or [sp.expand(P)]
