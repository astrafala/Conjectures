#!/usr/bin/env python3
"""A linear ODE for an algebraic function, and the recurrence its coefficients satisfy.

sympy's holonomic module handles exponentials, logs and Bessel functions but gives up on
many of the algebraic generating functions OEIS actually posts. Those are the easy case
if you build the ODE yourself.

If A satisfies P(x, A) = 0 with P of degree d in y, then K = Q(x)[y]/(P) is a
d-dimensional vector space over Q(x), and it is closed under d/dx: differentiating
P(x, A) = 0 gives A' = -P_x/P_y, and the quotient is taken inside K. So A, A', ..., A^(d)
are d+1 elements of a d-dimensional space and are linearly dependent over Q(x). That
dependency is the ODE, and it is exact -- no series, no truncation.

The ODE then gives the recurrence directly. Writing L = sum_{j,k} q_{j,k} x^k D^j and
A = sum_n a_n x^n, the term x^k D^j contributes (n)_j a_n x^{n-j+k}, so collecting the
coefficient of x^m gives

    sum_{j,k} q_{j,k} (m+j-k)_j a_{m+j-k} = 0,

a linear recurrence with polynomial coefficients. That is what the rest of the pipeline
consumes.
"""
import sympy as sp
import algfield as af

x, y, n = sp.symbols('x y n')


def ode_from_poly(P, maxorder=6):
    """A linear ODE annihilating the root of P, as coefficients of D^0..D^r. None if none."""
    K = af.Field(P.as_expr() if isinstance(P, sp.Poly) else P)
    d = K.P.degree()
    cur = sp.Poly(y, y)                     # A itself
    derivs = [K.red(cur)]
    for _ in range(min(maxorder, d) + 1):
        derivs.append(K.red(K.deriv(derivs[-1])))
    # each derivative is a polynomial in y of degree < d over Q(x): read as a vector
    for r in range(1, len(derivs)):
        M = sp.Matrix([[sp.cancel(derivs[j].as_expr().coeff(y, i)) for j in range(r + 1)]
                       for i in range(d)])
        ns = M.nullspace()
        if ns:
            v = ns[0]
            coeffs = [sp.cancel(sp.together(v[j])) for j in range(r + 1)]
            den = sp.lcm([sp.denom(c) for c in coeffs])
            coeffs = [sp.expand(sp.cancel(c * den)) for c in coeffs]
            while len(coeffs) > 1 and coeffs[-1] == 0:
                coeffs.pop()
            if len(coeffs) > 1:
                return coeffs
    return None


def recurrence_from_ode(qs):
    """Coefficients of a(n+j) for the recurrence the ODE implies, lowest shift first.

    Returns (list of coefficients indexed by shift from the lowest, lowest shift), or
    None if the ODE does not produce a usable relation.
    """
    terms = {}                              # shift -> coefficient polynomial in n
    for j, q in enumerate(qs):
        q = sp.expand(q)
        if q == 0:
            continue
        p = sp.Poly(q, x)
        for (k,), c in zip(p.monoms(), p.coeffs()):
            s = k - j                       # a_{m+j-k} sits at shift j-k... see below
            # x^k D^j A contributes (m+j-k)_j a_{m+j-k} to the coefficient of x^m
            sh = j - k
            terms[sh] = sp.expand(terms.get(sh, 0)
                                  + c * sp.rf(n + sh - j + 1, j))
    if not terms:
        return None
    lo, hi = min(terms), max(terms)
    out = [sp.expand(terms.get(s, sp.Integer(0))) for s in range(lo, hi + 1)]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    while len(out) > 1 and out[0] == 0:
        out.pop(0)
        lo += 1
    return (out, lo) if len(out) > 1 else None
