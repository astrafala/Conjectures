#!/usr/bin/env python3
"""Same residual test, for entries whose generating function is exponential.

For an e.g.f. A(x) = sum_m a(m) x^m/m!, a shift DOWN is an integral, which is
awkward; so re-index the conjecture forward first. Given

    sum_{i=0..r} p_i(n) a(n-i) = 0    (n >= n0),

put n = m + r and j = r - i, so with q_j(m) := p_{r-j}(m + r),

    sum_{j=0..r} q_j(m) a(m+j) = 0    (m >= n0 - r).

Now a shift UP is a derivative: sum_m a(m+j) x^m/m! = A^(j)(x). And multiplying the
coefficient of x^m/m! by q_j(m) is q_j(theta) with theta = x d/dx. Hence

    B(x) = sum_j q_j(theta)[ A^(j) ]

is the e.g.f. of b(m), so the conjecture holds for all m > d exactly when B is a
polynomial of degree at most d. Identical criterion, and the field Q(x)[sqrt(D)] is
closed under d/dx as well as theta, so the test stays exact.
"""
import sympy as sp
import quadfield as qf
import multiquad as mq

x = sp.Symbol('x')
n = sp.Symbol('n')


def reindex(ps):
    """p_i(n) for a(n-i)  ->  q_j(m) for a(m+j)."""
    r = len(ps) - 1
    m = sp.Symbol('n')
    return [sp.expand(ps[r - j].subs(m, m + r)) for j in range(r + 1)]


def residual_egf(A, ps):
    qs = reindex(ps)
    q = qf.to_quad(A)
    if q is not None:
        cur = q
        tot = (sp.Integer(0), sp.Integer(0), q[2])
        for j, poly in enumerate(qs):
            if poly != 0:
                tot = qf.add(tot, qf.apply_poly_theta(poly, cur, 0, n)
                             if False else _apply_q(poly, cur))
            cur = qf.deriv(cur)
        return qf.is_polynomial(tot)
    m = mq.to_multi(A)
    if m is None:
        raise ValueError("g.f. not in a multiquadratic extension of Q(x)")
    coeffs, Ds = m
    cur = coeffs
    tot = {}
    for j, poly in enumerate(qs):
        if poly != 0:
            tot = mq.add(tot, mq.apply_poly_theta(poly, cur, Ds, 0, n))
        cur = mq.deriv(cur, Ds)
    return mq.is_polynomial(tot)


def _apply_q(poly, uvD):
    """q(theta) applied to a quadfield element."""
    p = sp.Poly(sp.expand(poly), n)
    deg = max(mo[0] for mo in p.monoms()) if p.monoms() else 0
    powers = [uvD]
    for _ in range(deg):
        powers.append(qf.theta_quad(powers[-1]))
    out = (sp.Integer(0), sp.Integer(0), uvD[2])
    for (j,), c in zip(p.monoms(), p.coeffs()):
        out = qf.add(out, qf.scale(powers[j], c))
    return out
