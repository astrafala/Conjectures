#!/usr/bin/env python3
"""Conjectured recurrences that follow from a generating function the entry already records.

Many entries carry an empirical recurrence AND, separately, a `G.f.:` line contributed by
someone else and NOT marked conjectural. If that generating function is rational, the
recurrence is a consequence of it and needs no combinatorial model at all:

    write G(x) = sum_n a(n) x^n and D(x) = 1 - sum_i c_i x^i for the conjectured recurrence;
    then  a(n) - sum_i c_i a(n-i) = [x^n] D(x)G(x),

so the recurrence holds for every n past the degree of D(x)G(x), provided that product is a
polynomial --- which is exactly the condition that the recurrence's characteristic polynomial
is a multiple of the one the generating function's denominator supplies.

The result is conditional on the entry's generating function, which is stated as a fact rather
than as a conjecture; the paper says so and quotes it with its contributor. As a check that the
line is the right one, the series is expanded and compared against every published term.
"""
import re
import sympy

x = sympy.Symbol('x')
GFLINE = re.compile(r'^\s*(?:G\.f\.|Generating function)\s*[:.]\s*(.*)$', re.I)
CONJ = re.compile(r'\b(conjecture|conjectured|conjecturally|empirical)\b', re.I)
ATTR = re.compile(r'\s*-\s*_[^_]+_,.*$')


def parse_gf(line):
    """the rational function, or None."""
    m = GFLINE.match(line.strip())
    if not m:
        return None
    body = ATTR.sub('', m.group(1)).strip()
    body = re.sub(r'\(End\)\s*$', '', body).strip().rstrip('.').strip()
    if not body or CONJ.search(body):
        return None
    # a bare "G.f.: A(x) satisfies ..." or anything naming another sequence is out of scope
    if re.search(r'satisf|where|for\s|sum_|Sum_|prod|Prod|A\d{6}|!|integral', body):
        return None
    body = body.replace('^', '**')
    if not re.fullmatch(r'[-+*/()0-9x. ]+', body):
        return None
    try:
        expr = sympy.sympify(body, locals={'x': x}, rational=True)
    except Exception:
        return None
    if not expr.has(x):
        return None
    try:
        num, den = sympy.fraction(sympy.cancel(sympy.together(expr)))
        if not (sympy.Poly(num, x) and sympy.Poly(den, x)):
            return None
    except Exception:
        return None
    return expr


def series(expr, N):
    """[x^0..x^N] coefficients as Fractions, or None."""
    try:
        num, den = sympy.fraction(sympy.cancel(sympy.together(expr)))
        pn = sympy.Poly(num, x).all_coeffs()[::-1]
        pd = sympy.Poly(den, x).all_coeffs()[::-1]
    except Exception:
        return None
    if not pd or pd[0] == 0:
        return None
    out = []
    for n in range(N + 1):
        s = pn[n] if n < len(pn) else sympy.Integer(0)
        for i in range(1, min(n, len(pd) - 1) + 1):
            s -= pd[i] * out[n - i]
        out.append(sympy.nsimplify(s / pd[0]))
    return out


def residual_degree(expr, coeffs):
    """degree of D(x)G(x), or None if that product is not a polynomial."""
    D = 1 - sum(sympy.Integer(int(c)) * x ** int(i) for i, c in coeffs.items())
    H = sympy.cancel(sympy.together(D * expr))
    num, den = sympy.fraction(H)
    try:
        pd = sympy.Poly(den, x)
    except Exception:
        return None
    if pd.degree() != 0:
        return None
    try:
        return sympy.Poly(num, x).degree()
    except Exception:
        return None
