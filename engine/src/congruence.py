#!/usr/bin/env python3
"""A decision procedure for congruence conjectures on C-finite sequences.

If a(n) has a RATIONAL generating function P(x)/Q(x) with integer coefficients and
Q(0) = 1, then a satisfies a linear recurrence with constant integer coefficients of
order r = deg Q. Modulo m the state vector

    s(n) = ( a(n), a(n+1), ..., a(n+r-1) )  in  (Z/m)^r

evolves by a fixed linear map, and (Z/m)^r is FINITE. So the orbit is eventually
cyclic, the cycle is reachable by iteration, and every state the sequence ever takes
modulo m can be enumerated exhaustively in at most m^r steps.

That makes "a(n) == c (mod m) for all n >= n0" DECIDABLE, not merely testable: we
enumerate the preperiod and the whole cycle and check every state. A claim that
survives is proved for all n at once; a claim that fails yields an explicit
counterexample index, which is a disproof.
"""
import sympy as sp

x = sp.Symbol('x')


def recurrence_from_gf(A, maxorder=40):
    """Return (coeffs, init, r): a(n) = sum_i coeffs[i]*a(n-1-i), plus enough initial terms."""
    A = sp.cancel(sp.together(A))
    num, den = sp.fraction(A)
    if not (num.is_polynomial(x) and den.is_polynomial(x)):
        return None
    P, Q = sp.Poly(num, x), sp.Poly(den, x)
    if Q.degree() == 0 or Q.degree() > maxorder:
        return None
    q = [sp.nsimplify(Q.coeff_monomial(x ** k), rational=True) for k in range(Q.degree() + 1)]
    if q[0] == 0:
        return None
    q = [sp.Rational(t, 1) * sp.Rational(1, 1) / q[0] for t in q]
    if any(t.q != 1 for t in [sp.Rational(t) for t in q]):
        return None
    q = [int(sp.Rational(t)) for t in q]
    r = len(q) - 1
    # a(n) = -(q1 a(n-1) + ... + qr a(n-r))   for n > deg P
    coeffs = [-q[i] for i in range(1, r + 1)]
    ser = sp.series(A, x, 0, 2 * r + P.degree() + 6).removeO()
    e = sp.expand(ser)
    init = []
    for k in range(2 * r + P.degree() + 4):
        c = sp.nsimplify(e.coeff(x, k), rational=True)
        if c.free_symbols or sp.Rational(c).q != 1:
            return None
        init.append(int(c))
    start = P.degree() + 1          # recurrence valid from this index on
    return coeffs, init, r, start


def orbit_mod(coeffs, init, r, start, m, limit=2_000_000):
    """Every residue a(n) mod m for n >= start, exhaustively.

    Returns (residues_seen, preperiod_values, cycle_values) or None if the state
    space was not exhausted within `limit` steps.
    """
    seq = [v % m for v in init]
    if len(seq) < start + r:
        return None
    state = tuple(seq[start:start + r])
    seen = {}
    order = []
    n = start
    while n - start < limit:
        if state in seen:
            i = seen[state]
            return order[:i], order[i:]
        seen[state] = len(order)
        order.append(state[0])
        nxt = sum(coeffs[i] * state[r - 1 - i] for i in range(r)) % m
        state = tuple(list(state[1:]) + [nxt])
        n += 1
    return None


def decide(A, m, c, n0_index):
    """Decide 'a(n) == c (mod m) for all n >= n0_index'. Returns (verdict, detail)."""
    got = recurrence_from_gf(A)
    if got is None:
        return None, "generating function is not rational with integer coefficients"
    coeffs, init, r, start = got
    if n0_index < start:
        n0_index = start
    orb = orbit_mod(coeffs, init, r, n0_index, m)
    if orb is None:
        return None, "state space not exhausted"
    pre, cyc = orb
    bad = [i for i, v in enumerate(pre + cyc) if v % m != c % m]
    if bad:
        return False, f"fails at offset {bad[0]} past n0 (residue {(pre + cyc)[bad[0]]})"
    return True, (f"preperiod {len(pre)}, cycle length {len(cyc)}; every reachable "
                  f"state has residue {c % m}")


def decide_precursive(ps, init, off, m, c, n0, limit=400_000):
    """Decide a congruence for a P-RECURSIVE sequence.

    With sum_i p_i(n) a(n-i) = 0 the step map depends on n, but only through n mod m
    (the coefficients are polynomials, so p_i(n) mod m has period dividing m). So the
    state (n mod m, a(n-1),...,a(n-r) mod m) lives in a FINITE set of size at most
    m^(r+1), the orbit is eventually cyclic, and the congruence is decidable exactly as
    in the constant-coefficient case.

    The one requirement is that the leading coefficient p_0(n) be invertible mod m for
    every n reached; otherwise the next term is not determined modulo m and the method
    must report that rather than guess.
    """
    import sympy as sp
    n = sp.Symbol('n')
    r = len(ps) - 1
    if len(init) < r + 1:
        return None, "not enough initial terms"
    p0 = sp.Poly(ps[0], n)
    tail = [sp.Poly(p, n) for p in ps[1:]]

    vals = [v % m for v in init]
    start = max(r, n0 - off)
    if start + 1 > len(vals):
        return None, "n0 beyond the published terms"

    seen = {}
    order = []
    idx = start
    while idx - start < limit:
        nn = idx + off
        key = (nn % m, tuple(vals[idx - r:idx]))
        if key in seen:
            i = seen[key]
            pre, cyc = order[:i], order[i:]
            bad = [k for k, v in enumerate(pre + cyc) if v % m != c % m]
            if bad:
                return False, f"fails at offset {bad[0]} past n={n0}"
            return True, (f"preperiod {len(pre)}, cycle length {len(cyc)}; every "
                          f"reachable state has residue {c % m}")
        seen[key] = len(order)
        if idx < len(vals):
            cur = vals[idx]
        else:
            lead = int(p0.eval(nn)) % m
            if sp.gcd(lead, m) != 1:
                return None, f"leading coefficient not invertible mod {m} at n={nn}"
            s = 0
            for i, P in enumerate(tail, start=1):
                s = (s + int(P.eval(nn)) * vals[idx - i]) % m
            cur = (-s * pow(lead, -1, m)) % m
            vals.append(cur)
        order.append(cur)
        idx += 1
    return None, "state space not exhausted"
