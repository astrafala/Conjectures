#!/usr/bin/env python3
"""Does an entry fall under the periodicity theorem this project already proved?

The theorem: if G(t) = sum c_k t^k has INTEGER coefficients and a(n) is defined by
sum a(n) x^n/n! = G(e^x - 1), then for every m the sequence a(n) mod m is eventually
periodic with period dividing phi(m). Twenty papers rest on it.

So for any entry conjecturing exactly that, the question is whether its exponential
generating function E(x) can be written as G(e^x - 1) with G integral. Substituting
x = log(1+t) produces G directly. Integrality is then not merely checked on the first few
coefficients: when G turns out to be a rational function of t whose denominator has
constant term +-1, every coefficient is an integer, and that is a proof rather than
evidence.
"""
import sympy as sp

x, t, n = sp.symbols('x t n')


def to_G(E, N=14):
    """(G as an expression in t, its first N series coefficients) or None."""
    try:
        G = sp.simplify(E.subs(x, sp.log(1 + t)))
    except Exception:
        return None
    try:
        s = sp.series(G, t, 0, N).removeO()
    except Exception:
        return None
    cs = [sp.nsimplify(s.coeff(t, k), rational=True) for k in range(N)]
    if any(c.has(sp.zoo, sp.nan, sp.oo) for c in cs):
        return None
    return sp.simplify(G), cs


def integral_forever(G):
    """(True, reason) when every coefficient of G is provably an integer."""
    Gt = sp.cancel(sp.together(G))
    num, den = sp.fraction(Gt)
    if not (num.is_polynomial(t) and den.is_polynomial(t)):
        return False, "G is not a rational function of t"
    Pn, Pd = sp.Poly(sp.expand(num), t), sp.Poly(sp.expand(den), t)
    if not all(c.is_Integer for c in Pn.all_coeffs() + Pd.all_coeffs()):
        return False, "G has non-integer coefficients as a rational function"
    c0 = Pd.eval(0)
    if c0 in (1, -1):
        return True, ("G is a rational function with integer coefficients whose "
                      "denominator has constant term %d, so its expansion at t = 0 has "
                      "integer coefficients" % int(c0))
    return False, f"the denominator of G has constant term {c0}, not +-1"


def stirling_values(cs, N):
    """a(n) = sum_k c_k k! S(n,k) for n < N, as exact integers when they are."""
    out = []
    for m in range(N):
        v = sum(cs[k] * sp.factorial(k) * sp.functions.combinatorial.numbers.stirling(
            m, k) for k in range(min(len(cs), m + 1)))
        out.append(sp.nsimplify(v, rational=True))
    return out
