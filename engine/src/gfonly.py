#!/usr/bin/env python3
"""Settle a conjectured GENERATING FUNCTION for an entry that has no conjectured recurrence.

Every sweep in this repository gates on a parsable recurrence, so an entry whose only
conjecture is a generating function was never examined at all -- not refused, never reached.
There are 162 such entries outside the roster, and an engine reads the name of 49 of them.

The argument is finite and exact. The model gives a(n) as a walk count on S states, so
A(x) = sum a(n)x^n is N1(x)/D1(x) with D1(x) = det(I - xM) of degree at most S and deg N1 < S.
The conjecture says A = N2/D2. Then

    R(x) = N1*D2 - N2*D1

is a polynomial of degree at most S - 1 + deg D2, and A = N2/D2 exactly when R = 0. Since
D1(0) = D2(0) = 1 up to scaling, R vanishes if and only if the two power series agree to order
deg R, so comparing S + deg N2 + deg D2 + 1 coefficients PROVES the identity rather than
sampling it.
"""
import re
import sympy
import gfrec

x = sympy.Symbol('x')
MARK = re.compile(r'^\s*(?:Empirical|Conjectur\w*)\b\s*[:,]?\s*', re.I)
GF = re.compile(r'\bG\.?\s*f\.?\s*:?\s*', re.I)


def clean(line):
    """the generating-function expression on this line, or None.

    The shared parser wants a bare `G.f.:'. The corpus also writes `Empirical g.f.: ...',
    `Conjecture: g.f. ...' and `Empirical: G.f.: ...', and refuses all of them -- the first
    because of the marker, the second because there is no colon after `g.f.'."""
    s = line.strip()
    s2 = MARK.sub('', s, count=1)
    m = GF.search(s2)
    if not m or m.start() > 2:
        return None
    return 'G.f.: ' + s2[m.end():]


def parse(line):
    c = clean(line)
    return None if c is None else gfrec.parse_gf(c)


def degrees(expr):
    num, den = sympy.fraction(sympy.cancel(sympy.together(expr)))
    return sympy.Poly(num, x).degree(), sympy.Poly(den, x).degree()


def coefficients_needed(S, expr):
    dn, dd = degrees(expr)
    return int(S + dn + dd + 2)
