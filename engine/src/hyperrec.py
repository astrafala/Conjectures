#!/usr/bin/env python3
"""A conjectured P-recursive recurrence against a HYPERGEOMETRIC closed form stated as fact.

    A034267  a(n) = binomial(2*n, n+1)*(n^2+n+1)/(n+2);            [fact]
             Conjecture D-finite with recurrence
               -(n+2)*(11*n-7)*a(n) + 2*(23*n^2+44*n+30)*a(n-1)
               - 4*(n+5)*(2*n-3)*a(n-2) = 0.                       [conjecture]

When the stated closed form is hypergeometric -- a(n)/a(n-1) a rational function of n -- the
sequence satisfies an exact FIRST-order recurrence with polynomial coefficients, and any
conjectured recurrence of higher order is settled by reducing it with that ratio. What comes out
is an identity in Q(n), not an agreement of finitely many terms.

This matters because 228 entries in the P-recursive pool state no generating function at all,
which is what every other route here needs.

`closedform.parse_line` cannot be used to find these: it refuses `binomial(...)` outright, so a
census built on it sees none of the shape that makes this argument work -- it found exactly one
candidate pool-wide, and that one was not binomial. The reader here is separate and deliberately
narrow: binomials, factorials, powers and rational functions, and nothing else.
"""
import re

import sympy as sp

n = sp.Symbol('n')
_LOC = {'n': n, 'binomial': sp.binomial, 'C': sp.binomial, 'factorial': sp.factorial,
        'sqrt': sp.sqrt, 'Sum': None, 'Product': None}
LHS = re.compile(r'^\s*a\(\s*n\s*\)\s*=(?!=)\s*(.+?)\s*[;.]?\s*$')
BAD = re.compile(r'Sum_|Prod_|Product_|Integral|hypergeom|A\d{6}|\bmod\b|floor|ceiling'
                 r'|sigma|phi\(|gcd|prime|log|exp\(|sin|cos', re.I)
ATTR = re.compile(r'\s*[-—]\s*_[^_]+_,.*$')
RANGE = re.compile(r',?\s*for\s+n\s*>=?\s*\d+\s*$', re.I)


def closed(line):
    """the closed form as an expression in n, or None"""
    t = RANGE.sub('', ATTR.sub('', ' '.join(line.split()))).strip()
    m = LHS.match(t)
    if not m:
        return None
    body = m.group(1).strip().rstrip(';').rstrip('.')
    if BAD.search(body) or not body:
        return None
    body = body.replace('^', '**')
    body = re.sub(r'(\d)\s*(?=[A-Za-z(])', r'\1*', body)
    body = re.sub(r'(\))\s*(?=[A-Za-z(])', r'\1*', body)
    body = re.sub(r'(\d+|\))\s*!', r'factorial(\1)', body)
    names = set(re.findall(r'[A-Za-z]\w*', body))
    if names - {'n', 'binomial', 'C', 'factorial', 'sqrt'}:
        return None
    try:
        expr = sp.sympify(body, locals=_LOC)
    except Exception:
        return None
    return expr if expr.has(n) else None


def ratio(f):
    """a(n)/a(n-1) as a rational function of n, or None when it is not one"""
    try:
        r = sp.simplify(sp.combsimp(f / f.subs(n, n - 1)))
    except Exception:
        return None
    return r if r.is_rational_function(n) else None


def settles(ps, r):
    """does the first-order ratio r prove the conjectured recurrence `ps`?

    `ps` maps the shift i to the polynomial coefficient of a(n-i). Reducing every term to a
    multiple of a(n-k) with k the largest shift leaves a rational function of n alone; the
    conjecture holds exactly when that function is identically zero.
    """
    k = max(ps)
    tot = 0
    for i, p in ps.items():
        fac = 1
        for j in range(i + 1, k + 1):          # a(n-i) = a(n-k) * prod r(n-j+1)
            fac *= r.subs(n, n - j + 1)
        tot += sp.together(p * fac)
    try:
        return sp.simplify(sp.together(tot)) == 0
    except Exception:
        return False
