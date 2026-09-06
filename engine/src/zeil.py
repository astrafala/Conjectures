#!/usr/bin/env python3
"""Zeilberger's algorithm: derive a recurrence for a sum from the summand itself.

The earlier attempt (wz.py) ran Gosper on the conjectured operator directly and closed
nothing. That was the wrong shape of question. Gosper only succeeds when the conjectured
operator is *exactly* a telescoper, and a conjectured recurrence is usually not minimal --
it is whatever a fitting program happened to find, often of higher order than necessary.

Creative telescoping asks the right question instead. For F(n,k) hypergeometric in both
variables, look for polynomials sigma_0..sigma_r in n and a rational certificate R(n,k)
with

    sum_i sigma_i(n) F(n+i,k)  =  R(n,k+1) F(n,k+1) - R(n,k) F(n,k).                (*)

Summing (*) over all k makes the right side telescope to nothing, so
L = sum_i sigma_i(n) N^i annihilates a(n) = sum_k F(n,k). That L is DERIVED, not guessed,
and it comes from the definition of the sequence rather than from any posted generating
function. The conjectured operator is then settled by right division against L
(see ore.py) -- which is exactly the step that lets a non-minimal conjecture through.

Everything here is a search followed by a proof. The ansatz below is heuristic: divide (*)
through by F(n,k), clear denominators, and solve a linear system for the sigma_i and the
coefficients of the certificate. Whatever comes out is then VERIFIED as an exact rational
identity, so a wrong guess cannot become a wrong theorem -- it just fails the check.
"""
import sympy as sp

n, k = sp.symbols('n k')


def ratio(F, var, shift=1):
    """F(var+shift)/F(var) as a rational function, or None if it is not one."""
    r = sp.simplify(sp.combsimp(F.subs(var, var + shift) / F))
    r = sp.cancel(sp.together(r))
    num, den = sp.fraction(r)
    if not (num.is_rational_function(k, n) and den.is_rational_function(k, n)):
        return None
    return r


def _denominators(rho, rhos):
    """Candidate denominators for the certificate.

    Zeilberger's certificate is a rational function, not a polynomial, and its
    denominator is built from the ones already present in F(n+i,k)/F(n,k) and
    F(n,k+1)/F(n,k). Rather than run the full Gosper-Petkovsek normalisation, try the
    denominators that actually occur, and their shifts -- a wrong guess costs a failed
    linear solve, never a wrong answer, because every candidate is verified.
    """
    cands = [sp.Integer(1)]
    seen = set()
    for r in list(rhos) + [rho]:
        den = sp.denom(sp.cancel(sp.together(r)))
        for d in (den, den.subs(k, k - 1), sp.expand(den * den.subs(k, k - 1))):
            d = sp.expand(d)
            if d == 1 or sp.sstr(d) in seen:
                continue
            seen.add(sp.sstr(d))
            cands.append(d)
    return cands


def telescoper(F, order, degbound=6):
    """Search for (sigma, R) satisfying (*) at the given order. None if not found."""
    rho = ratio(F, k)                       # F(n,k+1)/F(n,k)
    if rho is None:
        return None
    rhos = [sp.Integer(1)]
    for i in range(1, order + 1):
        r = ratio(F, n, i)                  # F(n+i,k)/F(n,k)
        if r is None:
            return None
        rhos.append(r)

    sig = sp.symbols(f's0:{order + 1}')
    for w in _denominators(rho, rhos):
        for D in range(degbound + 1):
            ys = sp.symbols(f'y0:{D + 1}')
            R = sum(ys[j] * k ** j for j in range(D + 1)) / w
            Rp = R.subs(k, k + 1)
            expr = sum(sig[i] * rhos[i] for i in range(order + 1)) - (Rp * rho - R)
            num, _ = sp.fraction(sp.cancel(sp.together(expr)))
            try:
                poly = sp.Poly(sp.expand(num), k)
            except sp.PolynomialError:
                continue
            unknowns = list(sig) + list(ys)
            try:
                sol = sp.solve([sp.expand(c) for c in poly.all_coeffs()],
                               unknowns, dict=True)
            except Exception:
                continue
            for s in sol:
                sigv = [sp.together(s.get(t, t)) for t in sig]
                free = set()
                for v in sigv:
                    free |= (v.free_symbols & set(unknowns))
                for f0 in (sorted(free, key=str) or [None]):
                    pick = {f: (1 if f is f0 else 0) for f in free}
                    sv = [sp.cancel(v.subs(pick)) for v in sigv]
                    if all(sp.simplify(t) == 0 for t in sv):
                        continue
                    Rv = sp.cancel(R.subs({t: s.get(t, t) for t in ys}).subs(pick))
                    if verify(F, sv, Rv, rho, rhos):
                        return sv, Rv
    return None


def verify(F, sig, R, rho=None, rhos=None):
    """Check (*) exactly, as a rational identity after dividing by F(n,k)."""
    rho = rho if rho is not None else ratio(F, k)
    if rho is None:
        return False
    if rhos is None:
        rhos = [sp.Integer(1)] + [ratio(F, n, i) for i in range(1, len(sig))]
        if any(r is None for r in rhos):
            return False
    lhs = sum(sig[i] * rhos[i] for i in range(len(sig)))
    rhs = R.subs(k, k + 1) * rho - R
    return sp.cancel(sp.together(sp.simplify(lhs - rhs))) == 0


def natural_boundary(F, lo, hi, order, span=4):
    """The telescoped sum vanishes only if F is zero outside the stated k-range."""
    for m in range(max(order + 2, 4), max(order + 2, 4) + 4):
        try:
            k0, k1 = int(lo.subs(n, m)), int(hi.subs(n, m))
        except Exception:
            return False
        for kk in list(range(k0 - span, k0)) + list(range(k1 + 1, k1 + span + 1)):
            try:
                v = sp.simplify(F.subs({n: m, k: kk}))
            except Exception:
                return False
            if v != 0:
                return False
    return True
