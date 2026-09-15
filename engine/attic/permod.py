#!/usr/bin/env python3
"""Eventual periodicity of a(n) mod k, decided from the entry's exponential g.f.

Eighty open entries conjecture that a(n) reduced modulo k is eventually periodic for every
k, forty-two of them Peter Bala's. The theorem behind it is mechanical once one condition
is checked.

Suppose the e.g.f. satisfies A(x) = G(e^x - 1) with G(y) = sum_j c_j y^j and every c_j an
integer. Since (e^x - 1)^j / j! is the e.g.f. of the Stirling numbers S(n,j),

    a(n) = sum_{j>=0} c_j * j! * S(n,j),

a finite sum for each n. Fix k. Then j! == 0 (mod k) for all j past some J(k), so modulo k
the sum truncates to j <= J(k) -- finitely many terms, uniformly in n. Each S(n,j) mod k is
eventually periodic in n (the Stirling recurrence S(n+1,j) = j*S(n,j) + S(n,j-1) makes the
vector (S(n,0),...,S(n,J)) mod k a finite-state orbit), so a(n) mod k is a fixed integer
combination of finitely many eventually periodic sequences, hence eventually periodic.

So the whole conjecture reduces to: is G(y) = A(log(1+y)) an integer power series? That is
what this module decides. For the e.g.f.s these entries carry -- rational functions of
e^x -- the substitution is exact and G is a rational function of y, so integrality is
decided on a rational function rather than estimated from a truncation.
"""
import re
import sympy as sp

x, y = sp.symbols('x y')


def to_y(A):
    """G(y) with A(x) = G(e^x - 1), as an exact expression when the substitution is exact.

    e^x appears in these e.g.f.s as a whole; replacing every occurrence of e^x by 1 + y is
    exact and needs no series at all. Only if some e^(c x) with c != 1 survives is a series
    fallback used.
    """
    E = sp.exp(x)
    G = A.subs(E, 1 + y)
    # e^(c*x) for integer c is (1+y)^c
    for p in list(G.atoms(sp.Pow)) + list(G.atoms(sp.exp)):
        if isinstance(p, sp.exp):
            arg = sp.expand(p.args[0])
            c = sp.simplify(arg / x) if arg.has(x) else None
            if c is not None and c.is_Integer:
                G = G.subs(p, (1 + y) ** int(c))
    G = sp.together(sp.cancel(G))
    return None if G.has(x) else G


def integral_series(G, N=40):
    """(True, coefficients) if G is a power series in y with integer coefficients."""
    try:
        s = sp.series(G, y, 0, N).removeO()
    except Exception:
        return False, None
    p = sp.Poly(sp.expand(s), y)
    co = [sp.nsimplify(c, rational=True) for c in p.all_coeffs()[::-1]]
    if any(c.q != 1 for c in [sp.Rational(t) for t in co]):
        return False, None
    return True, [int(c) for c in co]


def rational_in_y(G):
    """True when G is a rational function of y -- then integrality is exact, not sampled."""
    return bool(G.is_rational_function(y))


def denominator_constant_term(G):
    """The constant term of the denominator; +-1 makes an integer series automatic."""
    num, den = sp.fraction(sp.cancel(sp.together(G)))
    try:
        return sp.Poly(sp.expand(den), y).eval(0)
    except Exception:
        return None
