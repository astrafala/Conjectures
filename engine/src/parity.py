#!/usr/bin/env python3
"""Recurrences settled from a closed form that depends on the parity of n.

A large OEIS family posts formulas like

    a(n) = C(n+3, ceiling(n/2))*C(n+2, floor(n/2)) - C(n+3, ceiling((n-1)/2))*...
    a(n) = binomial(n, floor(n/2)) - binomial(n, floor(n/2)-3)
    a(2*n+1) = binomial(4*n+1, 2*n),  a(2*n) = binomial(4*n-1, 2*n-1) + ...

None of these is a hypergeometric term in n -- floor and (-1)^n are not -- so the closed
form engine refuses them. Split by parity and they become two, one for each residue:
writing a(2m) = e_0(m) and a(2m+1) = e_1(m), both are ordinary hypergeometric expressions
in m, and a recurrence of order r in n becomes two identities in m, since a(n-i) reaches
whichever parity class n-i belongs to. Each identity is then decided by the same
similarity-class argument as before.

The two halves must BOTH hold; a recurrence that works on the even indices and fails on
the odd ones is not proved, and is reported as such.
"""
import re
import sympy as sp

n = sp.Symbol('n')
m = sp.Symbol('m', integer=True)   # so that floor(2m/2) reduces to m


def halves(e):
    """(e_0(m), e_1(m)) with a(2m) = e_0(m) and a(2m+1) = e_1(m), or None."""
    try:
        e0 = sp.simplify(sp.powsimp(e.subs(n, 2 * m), force=False))
        e1 = sp.simplify(sp.powsimp(e.subs(n, 2 * m + 1), force=False))
    except Exception:
        return None
    if e0.has(sp.floor, sp.ceiling) or e1.has(sp.floor, sp.ceiling):
        return None                     # the split did not resolve the rounding
    return e0, e1


def combination(ps, e0, e1, odd):
    """sum_i p_i(n) a(n-i) written in m, at n = 2m (odd=False) or n = 2m+1 (odd=True).

    a(2j) = e_0(j) and a(2j+1) = e_1(j), so which half each term reaches is decided by
    the parity of n-i, which is the parity of i flipped when n is odd.
    """
    N = 2 * m + 1 if odd else 2 * m
    tot = sp.Integer(0)
    for i, p in enumerate(ps):
        if p == 0:
            continue
        c = sp.expand(p.subs(n, N))
        if odd:
            # n - i = 2m+1-i : even when i is odd, odd when i is even
            term = e0.subs(m, m - (i - 1) // 2) if i % 2 else e1.subs(m, m - i // 2)
        else:
            # n - i = 2m-i : even when i is even
            term = e0.subs(m, m - i // 2) if i % 2 == 0 else e1.subs(m, m - (i + 1) // 2)
        tot += c * term
    return sp.expand(tot)
