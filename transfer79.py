#!/usr/bin/env python3
"""P X Q matrices over 0..n with rows and columns nondecreasing: plane partitions in a box.

    Number of P X Q matrices with elements in 0..n with each row and each column in
    nondecreasing order.

Reversing the rows and the columns turns such a matrix into a plane partition whose parts are
at most n and whose shape fits in a P X Q rectangle, so a(n) is the number of plane partitions
in a P x Q x n box.  MacMahon's box theorem gives that number, and the triple product
TELESCOPES in the third index:

    prod_{k=1..n} (i+j+k-1)/(i+j+k-2) = (n+i+j-1)/(i+j-1),

so
                       a(n) = prod_{i=1..P} prod_{j=1..Q} (n+i+j-1)/(i+j-1),

visibly a POLYNOMIAL in n of degree P*Q.  Nothing about Ehrhart theory is needed to see it, and
nothing about transfer matrices applies --- the shape is fixed and it is the alphabet that
grows.

Each entry carries its own product formula, marked empirical:

    set p,q,r to n,Q,P (in any order) in s=p+q+r-1;
    a(n) = prod_{i=0..r-1} binomial(s,p+i)*i!/(s-i)^(r-i-1).

Multiplying through by its denominator turns the claim into an identity between two polynomials
in n whose degrees are bounded explicitly, so checking it at enough points PROVES it.  That is
the whole content: the classical part is MacMahon's, and it is already recorded on these
entries; what is settled here is the entry's own expression, and the generating function where
one is conjectured.
"""
import re
from fractions import Fraction
from math import comb, factorial

import namecanon

NAME = re.compile(r'^Number of (\d+)\s*X\s*(\d+) matrices with elements in 0\.\.n with each row '
                  r'and each column in nondecreasing order', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.match(nm)
    if not m:
        return None
    P, Q = int(m.group(1)), int(m.group(2))
    if P < 1 or Q < 1:
        return None
    return {'P': P, 'Q': Q, 'frac': 1}


def macmahon(P, Q, n):
    """plane partitions in a P x Q x n box, as an exact integer"""
    v = Fraction(1)
    for i in range(1, P + 1):
        for j in range(1, Q + 1):
            v *= Fraction(n + i + j - 1, i + j - 1)
    assert v.denominator == 1
    return v.numerator


def entryform(p, q, r):
    """the entry's own product, evaluated exactly"""
    s = p + q + r - 1
    v = Fraction(1)
    for i in range(r):
        v *= Fraction(comb(s, p + i) * factorial(i), (s - i) ** (r - i - 1))
    return v


def degrees(P, Q):
    """(deg of the entry product's numerator, deg of its denominator)"""
    r, q = P, Q
    dn = sum(q + r - 1 - i for i in range(r))
    dd = sum(r - 1 - i for i in range(r))
    return dn, dd


def identity_holds(P, Q):
    """MacMahon(n) * D(n) - N(n) is a polynomial of degree at most dn; check it at dn+1 points.

    Both sides are evaluated exactly in Q, so this is a proof and not a sample."""
    dn, dd = degrees(P, Q)
    for n in range(dn + 1):
        if Fraction(macmahon(P, Q, n)) != entryform(n, Q, P):
            return False, n
    return True, dn + 1


def terms(P, Q, N, off=0):
    return [macmahon(P, Q, off + k) for k in range(N + 1)]


def gf_numerator(P, Q):
    """a(n) is a polynomial of degree P*Q, so sum a(n)x^n = N(x)/(1-x)^(PQ+1); return N."""
    d = P * Q
    a = [macmahon(P, Q, n) for n in range(d + 1)]
    # N(x) = (1-x)^(d+1) * sum a(n) x^n, truncated: coefficients are the (d+1)-fold differences
    N = []
    for k in range(d + 1):
        s = 0
        for i in range(k + 1):
            s += (-1) ** i * comb(d + 1, i) * a[k - i]
        N.append(s)
    while N and N[-1] == 0:
        N.pop()
    return N
