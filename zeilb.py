#!/usr/bin/env python3
"""Creative telescoping when the summand does NOT vanish outside the summation range.

zeil.py refuses those, and they were the second largest pile of failures. The refusal is
right as far as it goes: summing

    sum_i sigma_i(n) F(n+i,k)  =  G(n,k+1) - G(n,k),      G = R*F                    (*)

over k gives sum_i sigma_i(n) a(n+i) = 0 only when two separate things happen -- the
telescoped boundary G vanishes at both ends, and the range of k does not itself move
with n. Neither holds in general, and when they fail the honest conclusion is not "no
result" but an INHOMOGENEOUS recurrence

    sum_i sigma_i(n) a(n+i)  =  h(n),

where h(n) is written out explicitly: the two boundary values of G, plus the terms of
F(n+i,.) that lie inside the common summation window but outside the range belonging to
a(n+i). All of it is a finite, closed-form expression in n.

An inhomogeneous recurrence still settles a conjecture. If h is hypergeometric, the
first-order operator M = N - h(n+1)/h(n) annihilates it, so M*L annihilates a(n) and the
conjecture is tested against M*L by the same right division as before. If h turns out to
be 0 the recurrence was homogeneous all along and L is used directly.

Limits are taken where the summation bounds are linear in n with slope 0 or 1, which is
what the entries actually use. Anything else is refused rather than guessed at, and so is
any certificate whose denominator has a pole at an integer inside the window -- there the
telescoping itself would be invalid, not merely inconvenient.
"""
import sympy as sp
from zeil import n, k, ratio, telescoper, verify

N_ = sp.Symbol('N')


def _linear(e):
    """(slope, intercept) if e = a*n + b with a in {0,1} and b an integer, else None."""
    if e in (sp.oo, -sp.oo):
        return None
    try:
        p = sp.Poly(sp.expand(e), n)
    except sp.PolynomialError:
        return None
    if p.degree() > 1:
        return None
    a = sp.nsimplify(p.coeff_monomial(n)) if p.degree() == 1 else sp.Integer(0)
    b = sp.nsimplify(p.coeff_monomial(1))
    if a not in (0, 1) or not b.is_Integer:
        return None
    return int(a), int(b)


def _value(G, kk):
    """G at k = kk, taken as a limit where a pole of the certificate meets a zero of F.

    The certificate for sum_k C(n,k)2^k is k/(k-n-1), which has a pole exactly at the
    first k above the range -- and C(n,n+1) = 0 there, so G is perfectly finite. Refusing
    on the pole alone would throw away the commonest case there is.
    """
    Gg = G.rewrite(sp.gamma) if G.has(sp.binomial, sp.factorial) else G
    v = Gg.subs(k, kk)
    try:
        v = sp.simplify(sp.combsimp(v))
    except Exception:
        try:
            v = sp.simplify(v)
        except Exception:
            return None
    if v.has(sp.nan, sp.zoo, sp.oo) or v.has(sp.Symbol('zoo')):
        try:
            v = sp.limit(Gg, k, kk)
        except Exception:
            return None
        if v.has(sp.nan, sp.zoo, sp.oo):
            return None
    return v


def poles_safe(F, R, lo, hi, r):
    """Every integer pole of the certificate inside the telescoping window must be
    cancelled by a zero of F, or the cancellation the argument relies on is not there."""
    den = sp.denom(sp.cancel(sp.together(R)))
    if not den.has(k):
        return True
    try:
        roots = sp.solve(sp.Eq(sp.expand(den), 0), k)
    except Exception:
        return False
    G = sp.together(R * F)
    for rho in roots:
        rho = sp.simplify(rho)
        placed = rho.is_number and rho.is_integer
        if not placed:
            d = sp.simplify(rho - n)
            placed = d.is_number and d.is_integer
        if not placed:
            if rho.is_number:
                continue          # a non-integer pole never lands on a summation index
            return False          # a pole we cannot place is refused
        if _value(G, rho) is None:
            return False
    return True


def inhomogeneity(F, sig, R, lo, hi):
    """h(n) with sum_i sigma_i(n) a(n+i) = h(n), or None if the shape is not supported."""
    r = len(sig) - 1
    L0, H0 = _linear(lo), _linear(hi)
    if L0 is None or H0 is None:
        return None
    (al, bl), (ah, bh) = L0, H0
    if not poles_safe(F, R, lo, hi, r):
        return None
    # the window common to every a(n+i): from the lowest lower bound to the highest upper
    L = al * n + bl                      # lo is non-decreasing in i, so min at i = 0
    H = ah * (n + r) + bh                # hi is non-decreasing in i, so max at i = r
    G = sp.together(R * F)

    hi_val, lo_val = _value(G, H + 1), _value(G, L)
    if hi_val is None or lo_val is None:
        return None
    h = hi_val - lo_val
    # what each a(n+i) is missing relative to the common window
    for i in range(r + 1):
        loi, hii = al * (n + i) + bl, ah * (n + i) + bh
        below = int(sp.simplify(loi - L))        # terms of F(n+i,.) below a(n+i)'s range
        above = int(sp.simplify(H - hii))        # and above it
        if below < 0 or above < 0 or below > 8 or above > 8:
            return None
        extra = sp.Integer(0)
        for j in range(below):
            extra += F.subs({n: n + i, k: L + j})
        for j in range(above):
            extra += F.subs({n: n + i, k: hii + 1 + j})
        if extra != 0:
            h -= sig[i] * extra
    try:
        return sp.simplify(sp.combsimp(sp.together(h)))
    except Exception:
        return sp.simplify(h)


def annihilator(sig, h):
    """The operator that kills a(n), given sum_i sigma_i a(n+i) = h(n).

    h = 0 leaves L untouched. Otherwise M = N - h(n+1)/h(n) kills h when h is
    hypergeometric, and M*L kills a. Returns (coefficients of N^0.., description).
    """
    L = [sp.cancel(t) for t in sig]
    if h is None:
        return None, "no inhomogeneity could be computed"
    if sp.simplify(h) == 0:
        return L, "homogeneous: the boundary and range corrections cancel"
    rho = sp.cancel(sp.together(sp.simplify(h.subs(n, n + 1) / h)))
    num, den = sp.fraction(rho)
    if not (num.is_rational_function(n) and den.is_rational_function(n)):
        return None, "the inhomogeneity is not hypergeometric"
    if sp.simplify(rho.subs(n, n + 1) * 0) != 0:
        return None, "unexpected"
    # M = N - rho, acting on the left:  (M*L)_j = L_{j-1}(n+1) - rho * L_j
    out = []
    for j in range(len(L) + 1):
        a = L[j - 1].subs(n, n + 1) if 0 <= j - 1 < len(L) else sp.Integer(0)
        b = rho * L[j] if 0 <= j < len(L) else sp.Integer(0)
        out.append(sp.cancel(sp.together(a - b)))
    while len(out) > 1 and sp.cancel(out[-1]) == 0:
        out.pop()
    return out, "inhomogeneous, cleared by one extra order"


def check_numeric(F, lo, hi, sig, h, data, off, npts=5):
    """The inhomogeneous recurrence, evaluated on the entry's own terms.

    This proves nothing -- the certificate identity is what proves it -- but a symbolic
    slip in the boundary bookkeeping shows up here immediately, and has.
    """
    r = len(sig) - 1
    seen = 0
    for m in range(off, off + len(data) - r):
        idx = m - off
        if idx + r >= len(data):
            break
        try:
            lhs = sum(sp.nsimplify(sp.simplify(sig[i].subs(n, m))) * data[idx + i]
                      for i in range(r + 1))
            rhs = sp.nsimplify(sp.simplify(h.subs(n, m)))
        except Exception:
            return None
        if not (lhs.is_number and rhs.is_number):
            return None
        if sp.simplify(lhs - rhs) != 0:
            return False
        seen += 1
        if seen >= npts:
            break
    return seen >= 3
