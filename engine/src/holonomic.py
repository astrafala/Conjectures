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
    return [sp.nsimplify(e.coeff(x, k), rational=True) for k in range(N + 1)]


def check_against_data(A, data, offset, N=None):
    """Confirm the g.f. really generates the entry's published terms."""
    N = N or min(len(data) - 1, 18)
    t = taylor(A, N + offset)
    got = [sp.simplify(v) for v in t[offset:offset + N + 1]]
    want = data[:N + 1]
    bad = [k for k in range(N + 1) if sp.simplify(got[k] - want[k]) != 0]
    return (not bad), bad[:5], got[:6]


# ---------------------------------------------------------------------------
# Deciding the same thing in the quadratic field, instead of through `simplify`.
#
# `prove` calls sympy's `simplify` and then takes two forty-term series of an expression full
# of nested radicals; it manages about two entries in seven minutes, which is what the P-
# recursive sweep spends almost all of its time on. It does not need to.
#
# Every generating function this sweep accepts is algebraic of degree 2 -- one square root --
# so A = P + Q*sqrt(D) with P, Q, D rational. theta = x d/dx preserves that shape, because
# d/dx sqrt(D) = D'/(2 sqrt(D)) = (D'/(2D)) sqrt(D). So B = R + S*sqrt(D) with R, S rational,
# and B is a polynomial in x exactly when S = 0 and R is a polynomial. Both are decided by
# `cancel` on rational functions, which is polynomial arithmetic and fast.
#
# This is the same decision, not a cheaper approximation of it: the reduction y^2 -> D is an
# identity in the field, and `quadratic` refuses outright when A is not of that shape rather
# than pretending.

def _split_sqrt(A):
    """(P, Q, D) with A = P + Q*sqrt(D), or None when A is not quadratic in one radical."""
    rads = {p for p in A.atoms(sp.Pow)
            if p.exp.is_Rational and sp.denom(p.exp) == 2 and p.base.free_symbols <= {x}}
    bases = {p.base for p in rads}
    if len(bases) != 1:
        return None
    D = bases.pop()
    y = sp.Symbol('_y')
    # Both sqrt(D) and 1/sqrt(D) occur, and the second is the commoner of the two in this
    # corpus: "(3*x - 1 + (7*x^2-6*x+1)/sqrt(5*x^2-6*x+1))/(2*x^2)". Requiring the exponent to
    # be exactly +1/2 rejected those, they fell through to the slow route, and one of them
    # stalled the whole sweep on its first entry. 1/sqrt(D) is y/D.
    reps = {}
    for p in rads:
        if p.exp == sp.Rational(1, 2):
            reps[p] = y
        elif p.exp == sp.Rational(-1, 2):
            reps[p] = y / D
        elif sp.denom(p.exp) == 2:
            k = (p.exp - sp.Rational(1, 2)) / 1
            if not k.is_Integer:
                return None
            reps[p] = y * D ** int(k)
        else:
            return None
    E = sp.cancel(sp.together(A.subs(reps)))
    num, den = sp.fraction(E)
    try:
        pn = sp.Poly(sp.expand(num), y)
        pd = sp.Poly(sp.expand(den), y)
    except sp.PolynomialError:
        return None
    if pn.degree() > 1 or pd.degree() > 1:
        return None
    # rationalise the denominator: (a + b y)/(c + d y) = (a + b y)(c - d y)/(c^2 - d^2 D)
    a1, b1 = pn.nth(0), pn.nth(1)
    c1, d1 = pd.nth(0), pd.nth(1)
    denom = sp.cancel(c1 ** 2 - d1 ** 2 * D)
    if denom == 0:
        return None
    P = sp.cancel((a1 * c1 - b1 * d1 * D) / denom)
    Q = sp.cancel((b1 * c1 - a1 * d1) / denom)
    return P, Q, D


def _theta_pair(P, Q, D):
    """theta applied to P + Q*sqrt(D), as a new (P, Q) pair."""
    dP = sp.cancel(x * sp.diff(P, x))
    dQ = sp.cancel(x * (sp.diff(Q, x) + Q * sp.diff(D, x) / (2 * D)))
    return dP, dQ


def quadratic(A, ps, maxdeg=200):
    """(ok, degB) deciding the claim in Q(x)[y]/(y^2 - D), or None when A is not quadratic.

    ok is True when B is zero or a polynomial; degB is its degree (-1 when B = 0).
    """
    sp_ = _split_sqrt(A)
    if sp_ is None:
        return None
    P, Q, D = sp_
    RP, RQ = sp.Integer(0), sp.Integer(0)
    for i, p in enumerate(ps):
        if p == 0:
            continue
        # p_i(theta + i) applied to A, then multiplied by x^i
        poly = sp.Poly(sp.expand(p.subs(sp.Symbol('n'), sp.Symbol('n'))), sp.Symbol('n'))
        cur = (P, Q)
        acc = (sp.Integer(0), sp.Integer(0))
        # Horner in theta: sum_k c_k (theta + i)^k A
        coeffs = poly.all_coeffs()[::-1]          # c_0, c_1, ...
        term = (P, Q)
        for k, c in enumerate(coeffs):
            if c != 0:
                acc = (sp.cancel(acc[0] + c * term[0]), sp.cancel(acc[1] + c * term[1]))
            t0, t1 = _theta_pair(term[0], term[1], D)
            term = (sp.cancel(t0 + i * term[0]), sp.cancel(t1 + i * term[1]))
        RP = sp.cancel(RP + x ** i * acc[0])
        RQ = sp.cancel(RQ + x ** i * acc[1])
    if sp.cancel(RQ) != 0:
        return False, None
    R = sp.cancel(sp.together(RP))
    num, den = sp.fraction(R)
    q, r = sp.div(sp.expand(num), sp.expand(den), x)
    if sp.expand(r) != 0:
        return False, None
    qq = sp.Poly(sp.expand(q), x)
    if qq.total_degree() > maxdeg:
        return False, None
    return True, (-1 if q == 0 else qq.degree())
