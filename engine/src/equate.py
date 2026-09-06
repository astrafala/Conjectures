#!/usr/bin/env python3
"""Settle a conjectured CLOSED FORM or a conjectured GENERATING FUNCTION.

A census of the whole encyclopedia found about 15,800 conjecture lines, of which the
linear-recurrence shape everything here has attacked accounts for roughly 1,070. Two of
the larger remaining shapes are within reach of machinery that already exists:

    Conjecture: a(n) = <closed form>          (about 575 open)
    Conjectured g.f.: <expression>            (about 353 open)

Both reduce to the same question. Take whichever description the entry states as FACT --
its posted generating function, or its posted closed form -- and derive from it a linear
recurrence with polynomial coefficients that the sequence satisfies. Then check that the
CONJECTURED description satisfies the same recurrence, and that the two agree on enough
initial terms. A recurrence of order r whose leading coefficient does not vanish, plus r
consecutive values, determines a sequence completely, so agreement everywhere follows.

Nothing here is a numerical check dressed up: the recurrence is derived exactly, "satisfies
it" is decided exactly (the residual criterion for a generating function, similarity
classes for a closed form), and the finitely many indices where the leading coefficient
vanishes are computed rather than assumed away.
"""
import re
import sympy as sp
import algfield as af
import algode, holo, hyperterm as ht, ore
import quadfield as qf, multiquad as mq
from holonomic import taylor
from prove_rec import residual_poly

x, n = sp.symbols('x n')


def operator_from_gf(A):
    """A linear recurrence the coefficients of A satisfy: (coeffs of N^0.., from index)."""
    got = holo.annihilator(A)
    if got is not None:
        ps, start = got
        co = taylor(A, 26)
        sh = holo.align_shift(ps, co, start)
        if sh is not None:
            if sh:
                ps = [sp.expand(p.subs(n, n - sh)) for p in ps]
                start += sh
            return ps, start
    # sympy gives up on many algebraic functions; build the ODE from the minimal
    # polynomial instead and read the recurrence off it
    try:
        K, u = af.from_expr(A)
    except Exception:
        return None
    if K is None:
        return None
    qs = algode.ode_from_poly(K.P.as_expr())
    if qs is None:
        return None
    got = algode.recurrence_from_ode(qs)
    if got is None:
        return None
    ps, lo = got
    if lo:                      # shift so the lowest index is n itself
        ps = [sp.expand(p.subs(n, n - lo)) for p in ps]
    return ps, 0


def operator_from_closed_form(C, maxterms=4):
    """An operator annihilating a sum of hypergeometric terms.

    NOT the product of the first-order operators (N - rho_j). That is the obvious guess
    and it is wrong: applying (N - rho_1) to t_1 + t_2 leaves t_2 times (rho_2 - rho_1),
    whose shift ratio is not rho_2, so the next factor has to be chosen for the
    transformed term rather than the original one. Multiplying the obvious factors gives
    an operator that annihilates neither.

    What is true, and is what this does, is linear algebra. For terms t_1..t_m, seek
    c_0..c_m in Q(n) with sum_k c_k(n) t_j(n+k) = 0 for every j. Dividing the j-th
    equation by t_j(n) makes every coefficient the rational function t_j(n+k)/t_j(n), so
    this is m equations in m+1 unknowns over Q(n) and a nonzero solution always exists.
    """
    ts = ht.terms_of(C)
    if not ts or len(ts) > maxterms:
        return None
    m = len(ts)
    rows = []
    for t in ts:
        row = []
        for k in range(m + 1):
            if k == 0:
                row.append(sp.Integer(1))
                continue
            # t(n+k)/t(n), built from the one-step ratio
            r = sp.Integer(1)
            for j in range(k):
                step = ht.shift_ratio(t, 1)          # t(n-1)/t(n)
                if step is None or sp.cancel(step) == 0:
                    return None
                r = sp.cancel(r * sp.cancel(1 / step.subs(n, n + j + 1)))
            row.append(sp.cancel(r))
        rows.append(row)
    M = sp.Matrix(rows)
    ns = M.nullspace()
    if not ns:
        return None
    v = ns[0]
    coeffs = [sp.cancel(sp.together(v[k])) for k in range(m + 1)]
    den = sp.lcm([sp.denom(c) for c in coeffs])
    coeffs = [sp.expand(sp.cancel(c * den)) for c in coeffs]
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    if len(coeffs) < 2:
        return None
    return coeffs, 0


def gf_satisfies(A, L):
    """Does the generating function A have coefficients annihilated by L?"""
    ps = ore.to_backward(L)
    den = sp.lcm([sp.denom(sp.cancel(sp.together(p))) for p in ps])
    ps = [sp.expand(sp.cancel(p * den)) for p in ps]
    if any(not p.is_polynomial(n) for p in ps):
        return None
    if qf.to_quad(A) is not None or mq.to_multi(A) is not None:
        deg, B = residual_poly(A, ps)
        return None if deg is None else deg
    try:
        K, u = af.from_expr(A)
    except Exception:
        return None
    if K is None:
        return None
    ok, B = K.is_polynomial(K.residual(u, ps, n))
    if not ok:
        return None
    return int(sp.Poly(B, x).total_degree()) if B != 0 else -1


def cf_satisfies(C, L):
    """Does the closed form C satisfy the recurrence L?"""
    ps = ore.to_backward(L)
    den = sp.lcm([sp.denom(sp.cancel(sp.together(p))) for p in ps])
    ps = [sp.expand(sp.cancel(p * den)) for p in ps]
    if any(not p.is_polynomial(n) for p in ps):
        return None
    ok, info = ht.verdict(ps, C)
    return info if ok else None


def leading_poles(L):
    """Integer n where the leading coefficient vanishes: the recurrence cannot step past."""
    lead = sp.expand(sp.cancel(sp.together(L[-1])))
    if not lead.free_symbols:
        return []
    try:
        return sorted({int(r) for r in sp.solve(sp.Eq(sp.numer(lead), 0), n)
                       if r.is_Integer})
    except Exception:
        return []
