#!/usr/bin/env python3
"""A decision procedure for statements about a P-recursive sequence modulo a fixed integer.

A census of the encyclopedia found roughly 1,100 open conjectures of the form

    a(n) == c (mod k)            a(n) is divisible by k
    a(p) == c (mod p^3)          a(n) mod k is eventually periodic

and none had been attempted here. For a FIXED modulus they are not hard; they are
decidable, and the reason is finiteness.

Suppose a satisfies sum_{j=0}^{r} p_j(n) a(n+j) = 0 with polynomial coefficients. Modulo k
each p_j(n) depends only on n mod k, because a polynomial with integer coefficients is
periodic in n modulo k. So the pair

    state(n) = ( n mod k , (a(n), a(n+1), ..., a(n+r-1)) mod k )

determines state(n+1) whenever the leading coefficient p_r(n) is invertible modulo k, and
there are only k * k^r states. The orbit therefore enters a cycle, and both the pre-period
and the period are found exactly by iterating until a state repeats. Once they are known,
ANY statement about a(n) mod k -- for all n, for n in an arithmetic progression, "is
eventually periodic with period dividing d" -- is decided by inspecting one pre-period and
one period. No search, no bound assumed, no term left unchecked.

The one hypothesis that can fail is invertibility of the leading coefficient. When
gcd(p_r(n), k) > 1 at a reachable n the next term is not determined modulo k and the
argument stops; that case is refused rather than guessed at, and the offending n is
reported.
"""
import sympy as sp

n = sp.Symbol('n')


def coeffs_mod(ps, k):
    """The recurrence coefficients as functions of n mod k, as tables of length k."""
    r = len(ps) - 1
    tab = []
    for p in ps:
        P = sp.Poly(sp.expand(p), n)
        tab.append([int(P.eval(m)) % k for m in range(k)])
    return tab, r


def orbit(ps, init, off, k, cap=2_000_000):
    """(pre-period, period, the sequence of states) for a(n) mod k, or None.

    ps are the coefficients of sum_j p_j(n) a(n+j) = 0, `init` the r starting values
    a(off..off+r-1), and off the index they start at.
    """
    tab, r = coeffs_mod(ps, k)
    if r < 1:
        return None
    state = (off % k, tuple(v % k for v in init[:r]))
    if len(init) < r:
        return None
    seen, order = {}, []
    m = off
    while len(order) < cap:
        if state in seen:
            return seen[state], len(order) - seen[state], order
        seen[state] = len(order)
        order.append(state)
        lead = tab[r][m % k]
        g = sp.gcd(lead, k)
        if g != 1:
            return ("not invertible", m, int(lead))
        inv = pow(lead, -1, k)
        nxt = (-sum(tab[j][m % k] * state[1][j] for j in range(r))) * inv % k
        state = ((m + 1) % k, state[1][1:] + (nxt,))
        m += 1
    return None


def values(ps, init, off, k, upto):
    """a(off..upto) modulo k, computed with the recurrence rather than stored terms."""
    tab, r = coeffs_mod(ps, k)
    out = [v % k for v in init[:r]]
    m = off
    while off + len(out) <= upto:
        lead = tab[r][m % k]
        if sp.gcd(lead, k) != 1:
            return None
        inv = pow(lead, -1, k)
        nxt = (-sum(tab[j][m % k] * out[len(out) - r + j] for j in range(r))) * inv % k
        out.append(nxt)
        m += 1
    return out


def _divisors(m):
    out = []
    d = 1
    while d * d <= m:
        if m % d == 0:
            out.append(d)
            if d != m // d:
                out.append(m // d)
        d += 1
    return sorted(out)


def eventual_period(ps, init, off, k):
    """(pre-period start index, MINIMAL period) of a(n) mod k, or a refusal tuple.

    The state machine gives a period, but not the smallest one: the state carries n mod k
    so that the polynomial coefficients can be evaluated, and when those coefficients do
    not actually depend on n that inflates the period by a factor of k. Fibonacci mod 11
    comes out as 110 rather than 10 that way. A conjecture of the form "the period divides
    phi(k)" would then be refused although it holds, so the minimal period of the VALUE
    sequence is extracted here, and the pre-period is shortened as far as it goes.
    """
    got = orbit(ps, init, off, k)
    if got is None:
        return None
    if got[0] == "not invertible":
        return got
    pre, per, order = got
    vals = values(ps, init, off, k, off + pre + 3 * per + len(ps))
    if vals is None:
        return None
    # smallest p dividing per with vals[i] == vals[i+p] for every i at or past the
    # pre-period, checked over two full cycles
    span = pre + 2 * per
    best = per
    for p in _divisors(per):
        if all(vals[i] == vals[i + p] for i in range(pre, min(span, len(vals) - p))):
            best = p
            break
    # and the earliest index from which that period already holds
    start = pre
    while start > 0 and all(vals[i] == vals[i + best]
                            for i in range(start - 1, min(span, len(vals) - best))):
        start -= 1
    return off + start, best
