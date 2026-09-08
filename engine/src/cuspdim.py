#!/usr/bin/env python3
"""Dimensions of spaces of cusp forms, which are given by an exact classical formula.

    Dimension of the space of weight 2n cusp forms for Gamma_0( 13 ).

Nothing in this repository resembles this: there is no array to count and no transfer matrix
to build. There is instead a closed formula, and it settles the conjecture outright.

For even $k\\ge4$ (Diamond--Shurman, Theorem 3.5.1),

    dim S_k(Gamma_0(N)) = (k-1)(g-1) + (k/2 - 1) e_inf + floor(k/4) e_2 + floor(k/3) e_3,

and dim S_2 = g, dim S_0 = 0. Every quantity on the right is elementary integer arithmetic in
N: the index mu = N prod_{p|N} (1 + 1/p); the elliptic counts e_2 and e_3, which vanish when
4 | N and 9 | N respectively and are otherwise products of (1 + (-1/p)) and (1 + (-3/p)) over
the primes dividing N; the cusp count e_inf = sum_{d|N} phi(gcd(d, N/d)); and the genus
g = 1 + mu/12 - e_2/4 - e_3/3 - e_inf/2.

With k = 2n the right-hand side is linear in n except for floor(n/2) and floor(2n/3), so a(n)
is a QUASI-POLYNOMIAL of period 6 and satisfies a(n+6) = a(n) + 6A + 3 e_2 + 4 e_3 exactly.
That is why a conjectured linear recurrence on one of these entries is decidable: the formula
gives every term, so the recurrence can be checked against a sequence that is known in closed
form rather than sampled.
"""
import re
from math import gcd

DIM = re.compile(
    r'^\s*Dimension of the space of weight\s+(\d*)\s*n\s+cusp forms for\s+'
    r'Gamma_0\s*\(\s*(\d+)\s*\)\s*\.?\s*$', re.I)


def _primes(n):
    out, d = [], 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def _phi(n):
    r = n
    for p in _primes(n):
        r -= r // p
    return r


def _kron_m1(p):
    """(-1/p): 1 if p = 1 mod 4, -1 if p = 3 mod 4, 0 if p = 2"""
    if p == 2:
        return 0
    return 1 if p % 4 == 1 else -1


def _kron_m3(p):
    """(-3/p): 1 if p = 1 mod 3, -1 if p = 2 mod 3, 0 if p = 3"""
    if p == 3:
        return 0
    return 1 if p % 3 == 1 else -1


def invariants(N):
    """(mu, e_2, e_3, e_inf, g) for Gamma_0(N), all exact integers except g"""
    ps = _primes(N)
    mu = N
    for p in ps:
        mu = mu // p * (p + 1)
    e2 = 0 if N % 4 == 0 else 1
    if e2:
        for p in ps:
            e2 *= 1 + _kron_m1(p)
    e3 = 0 if N % 9 == 0 else 1
    if e3:
        for p in ps:
            e3 *= 1 + _kron_m3(p)
    einf = sum(_phi(gcd(d, N // d)) for d in range(1, N + 1) if N % d == 0)
    # g = 1 + mu/12 - e2/4 - e3/3 - einf/2, an integer; computed over a common denominator
    num = 12 + mu - 3 * e2 - 4 * e3 - 6 * einf
    if num % 12:
        raise ArithmeticError(f'genus of Gamma_0({N}) is not an integer: {num}/12')
    return mu, e2, e3, einf, num // 12


_INV = {}


def _cached(N):
    got = _INV.get(N)
    if got is None:
        got = _INV[N] = invariants(N)
    return got


def dim_S(k, N):
    """dim S_k(Gamma_0(N)) for even k >= 0"""
    if k % 2 or k < 0:
        raise ValueError('this covers even weights only')
    # invariants(N) walks every divisor of N, and terms() asks for hundreds of weights on the
    # same N; without this the cusp count was recomputed once per term
    _, e2, e3, einf, g = _cached(N)
    if k == 0:
        return 0
    if k == 2:
        return g
    return ((k - 1) * (g - 1) + (k // 2 - 1) * einf
            + (k // 4) * e2 + (k // 3) * e3)


def parse_name(nm):
    m = DIM.match(re.sub(r'\s+', ' ', nm).strip())
    if not m:
        return None
    mult = int(m.group(1)) if m.group(1) else 1
    N = int(m.group(2))
    if mult % 2 or mult < 2 or N < 1 or N > 5000:
        return None
    try:
        invariants(N)
    except ArithmeticError:
        return None
    return {'N': N, 'mult': mult, 'frac': 1}


def build(p, cap=200000):
    inv = invariants(p['N'])
    # the period-6 quasi-polynomial satisfies a monic recurrence of order 8, so eight
    # consecutive vanishing residuals certify a conjectured one; S is that bound
    return {'N': p['N'], 'mult': p['mult'], 'inv': inv, 'S': 8}


def terms(b, N):
    """a(n) = dim S_{mult * n} for n = 0, 1, 2, ..."""
    return [dim_S(b['mult'] * n, b['N']) for n in range(N + 1)]


def threshold(b, coeffs, order):
    t = terms(b, 2 * b['S'] + order + 40)
    last, run = None, 0
    for j in range(order + 1, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < b['S'] + order:
        return None
    return last if last is not None else 0
