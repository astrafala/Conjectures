#!/usr/bin/env python3
"""Decide a conjectured constant-coefficient recurrence against a FACTUAL rational g.f.

If A(x) = sum_{n>=off} a(n) x^n and the conjecture is a(n) = sum_i c_i a(n-i) for n > d,
put C(x) = 1 - sum_i c_i x^i. Then

    sum_n ( a(n) - sum_i c_i a(n-i) ) x^n  =  C(x) A(x),

so the recurrence holds for every n > d if and only if C(x)A(x) is a polynomial of degree
at most d. For a rational A that is a finite polynomial computation and is exact.

Everything is checked before use: the g.f. is expanded and matched against every published
term of the entry, and the recurrence is evaluated on those terms in integer arithmetic.
"""
import re
import sympy as sp

x = sp.Symbol('x')

GF_HEAD = re.compile(r'^\s*(?:o\.)?g\.f\.\s*:?\s*', re.I)
ATTRIB = re.compile(r'\s*-\s*_[^_]+_.*$')
TRAILER = re.compile(r'\s*\((?:End|Start|Follows[^)]*)\)\s*\.?\s*$', re.I)
REFUSE = re.compile(r'Sum_|Product_|\bA\d{6}\b|sqrt|floor|ceiling|\bmod\b|hypergeom|'
                    r'Integral|RootOf|continued|\.\.\.|\bQ\(|\bexp\b|\blog\b|theta|'
                    r'\bwhere\b|\bif\b|\by\b', re.I)


def parse_gf(line):
    s = ATTRIB.sub('', line)
    s = TRAILER.sub('', s).strip()
    if not GF_HEAD.match(s):
        return None
    s = GF_HEAD.sub('', s).strip().rstrip('.').strip()
    if not s or REFUSE.search(s):
        return None
    s = s.replace('^', '**')
    try:
        e = sp.sympify(s, locals={'x': x})
    except Exception:
        return None
    if not e.free_symbols <= {x}:
        return None
    try:
        if not e.is_rational_function(x):
            return None
    except Exception:
        return None
    return sp.together(sp.cancel(e))


REC = re.compile(r'a\(n\)\s*=\s*(.+?)(?:\s+for\b|\s*$)', re.I)
# the coefficient may be EMPTY, as in "+a(n-20)"; requiring one character here
# silently dropped every recurrence with an implicit coefficient of 1
TERM = re.compile(r'([+-]?\s*[^+-]*?)\*?\s*a\(n\s*-\s*(\d+)\)')
FORN = re.compile(r'for\s+n\s*(>=|>|\\ge)\s*(\d+)', re.I)


def parse_rec(line):
    """Return (coeffs dict i->c, threshold d or None) for a constant-coefficient claim."""
    body = ATTRIB.sub('', line)
    body = re.sub(r'^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*', '', body, flags=re.I)
    m = REC.search(body)
    if not m:
        return None
    rhs = m.group(1).strip().rstrip('.')
    if 'a(n)' in rhs or re.search(r'a\(n\s*\+', rhs):
        return None
    coeffs = {}
    consumed = 0
    for tm in TERM.finditer(rhs):
        raw = tm.group(1).replace(' ', '')
        i = int(tm.group(2))
        if raw in ('', '+'):
            c = sp.Integer(1)
        elif raw == '-':
            c = sp.Integer(-1)
        else:
            if re.search(r'[a-zA-Z]', raw):      # a coefficient involving n: not C-finite
                return None
            try:
                c = sp.Rational(sp.sympify(raw))
            except Exception:
                return None
        coeffs[i] = coeffs.get(i, 0) + c
        consumed += len(tm.group(0))
    if not coeffs:
        return None
    leftover = TERM.sub('', rhs).replace(' ', '')
    if leftover.strip('+-*'):                     # an inhomogeneous piece: out of scope
        return None
    f = FORN.search(body)
    d = None
    if f:
        d = int(f.group(2)) if f.group(1) == '>' else int(f.group(2)) - 1
    return coeffs, d


def series_of(expr, N):
    """Exact Taylor coefficients 0..N of a rational function, by long division."""
    num, den = sp.fraction(sp.cancel(sp.together(expr)))
    pn = sp.Poly(sp.expand(num), x).all_coeffs()[::-1]
    pd = sp.Poly(sp.expand(den), x).all_coeffs()[::-1]
    if pd[0] == 0:
        return None
    out = []
    for n in range(N + 1):
        v = (pn[n] if n < len(pn) else 0)
        v -= sum(pd[k] * out[n - k] for k in range(1, min(n, len(pd) - 1) + 1))
        out.append(sp.nsimplify(v / pd[0]))
    return out


def residual_degree(expr, coeffs):
    """Degree of C(x)*A(x) if it is a polynomial, else None."""
    C = sp.Integer(1) - sum(c * x ** i for i, c in coeffs.items())
    prod = sp.cancel(sp.together(sp.expand(C) * expr))
    num, den = sp.fraction(prod)
    if sp.simplify(sp.degree(den, x)) == 0:
        return sp.degree(sp.expand(num / den), x)
    q, r = sp.div(sp.expand(num), sp.expand(den), x)
    if sp.expand(r) == 0:
        return sp.degree(q, x)
    return None
