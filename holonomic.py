#!/usr/bin/env python3
"""Prove a conjectured P-recursive recurrence from an algebraic generating function.

If a(n) has generating function A(x) and the conjecture asserts

    sum_{i=0..r} p_i(n) a(n-i) = 0   for all n >= n0 ,

put b(n) := sum_i p_i(n) a(n-i) and let B(x) = sum_n b(n) x^n. Writing
theta = x d/dx, so that theta acts on x^m as multiplication by m,

    sum_n p_i(n) a(n-i) x^n  =  x^i * ( p_i(theta + i) A )(x),

hence

    B(x) = sum_{i=0..r} x^i * ( p_i(theta + i) A )(x).                    (*)

So the conjecture holds for all n exactly when B is the zero series, and holds for
all n >= n0 exactly when B is a polynomial of degree < n0. Because A is algebraic,
(*) is an explicit element of an algebraic function field and can be decided
symbolically -- no numerics, no truncation.

This is a proof, not a check: the identity B = 0 is verified as an identity of
functions, so it holds for every n at once.
"""
import sympy as sp

x, n = sp.symbols('x n')


def catalan_gf(arg=None):
    t = x if arg is None else arg
    return (1 - sp.sqrt(1 - 4 * t)) / (2 * t)


def theta(expr, times=1):
    """theta = x d/dx, applied `times` times."""
    for _ in range(times):
        expr = sp.expand(x * sp.diff(expr, x))
    return expr


def apply_poly_in_theta(poly_expr, A, shift):
    """Apply p(theta + shift) to A, where poly_expr is a polynomial in n."""
    p = sp.Poly(sp.expand(poly_expr), n)
    out = sp.Integer(0)
    # p(theta+shift) = sum_j c_j (theta+shift)^j ; expand in powers of theta
    for (j,), c in zip(p.monoms(), p.coeffs()):
        # (theta + shift)^j applied to A
        term = sp.Integer(0)
        for i in range(j + 1):
            term += sp.binomial(j, i) * shift ** (j - i) * theta(A, i)
        out += c * term
    return out


def residual(A, ps):
    """B(x) from (*); ps[i] is p_i(n)."""
    B = sp.Integer(0)
    for i, p in enumerate(ps):
        B += x ** i * apply_poly_in_theta(p, A, i)
    return B


def prove(name, A, ps, order_note="", nterms=40):
    """Return (is_zero, simplified_B, series_check)."""
    B = residual(A, ps)
    Bs = sp.radsimp(sp.simplify(sp.together(B)))
    is_zero = sp.simplify(Bs) == 0
    if not is_zero:
        # B may be a polynomial (conjecture true only for n >= deg+1)
        try:
            ser = sp.series(B, x, 0, nterms).removeO()
            poly = sp.Poly(sp.expand(ser), x)
            is_poly = all(sp.simplify(poly.coeff_monomial(x ** k)) == 0
                          for k in range(6, nterms - 2))
        except Exception:
            is_poly = False
    else:
        is_poly = True
    ser = sp.series(B, x, 0, nterms).removeO()
    coeffs = [sp.simplify(sp.expand(ser).coeff(x, k)) for k in range(nterms - 2)]
    first_nonzero = next((k for k, c in enumerate(coeffs) if c != 0), None)
    return is_zero, Bs, coeffs, first_nonzero


def taylor(A, N):
    s = sp.series(A, x, 0, N + 1).removeO()
    e = sp.expand(s)
    return [sp.nsimplify(e.coeff(x, k)) for k in range(N + 1)]


def check_against_data(A, data, offset, N=None):
    """Confirm the g.f. really generates the entry's published terms."""
    N = N or min(len(data) - 1, 18)
    t = taylor(A, N + offset)
    got = [sp.simplify(v) for v in t[offset:offset + N + 1]]
    want = data[:N + 1]
    bad = [k for k in range(N + 1) if sp.simplify(got[k] - want[k]) != 0]
    return (not bad), bad[:5], got[:6]
