#!/usr/bin/env python3
"""A conjectured generating function, proved from a recurrence the entry states as fact.

The largest vein in this project runs one way: a generating function the entry records as
fact, and a conjectured recurrence that follows from it. The corpus also contains the mirror
image, and nothing had ever asked about it -- an entry that states

    a(n) = 2*a(n-1) + a(n-2) for n > 3.          (fact, no conjectural word)

and, separately,

    G.f.: x*(1 - x)/(1 - 2*x - x^2) (conjectured). - _Colin Barker_, ...

2,809 entries outside the roster carry a conjectured rational generating function; 1,262 of
them state a recurrence or a closed form as fact. The conjecture follows from that premise by
polynomial algebra, with no model and no name to read.

The argument. Write b_k = a(off + k) for the published terms and D(x) = 1 - sum_i c_i x^i for
the stated recurrence. The recurrence says b_k = sum_i c_i b_{k-i} for every k >= K, so the
product D(x)*B(x) has no coefficient beyond x^(K-1): it is the polynomial

    P(x) = sum_{k < K} ( b_k - sum_i c_i b_{k-i} ) x^k ,

every coefficient of which is fixed by finitely many published terms. Hence B = P/D EXACTLY,
as an identity of rational functions and not as an agreement of finitely many coefficients.
The conjecture says B = N/D2 after the shift s that lines the conjectured series up with the
entry's data, so it is true exactly when

    ( g(x) - (its first s coefficients) ) / x^s  -  P(x)/D(x)  =  0

as a rational function -- one cancellation, decided exactly.
"""
import sympy

import gfrec

x = sympy.Symbol('x')


def denominator(coeffs):
    """D(x) = 1 - sum c_i x^i for the recurrence a(n) = sum c_i a(n-i)."""
    return 1 - sum(sympy.nsimplify(c) * x ** int(i) for i, c in coeffs.items())


def numerator(coeffs, b, K):
    """P(x) = the polynomial D(x)*B(x), given the recurrence holds from index K on.

    Needs K + max(i) published terms; returns None when the data does not reach that far or
    the recurrence is contradicted at or after K, which means the entry's threshold is not
    the one written down and the premise cannot be pinned.
    """
    order = max(int(i) for i in coeffs)
    if len(b) < K + order:
        return None
    cs = {int(i): sympy.nsimplify(c) for i, c in coeffs.items()}
    P = sympy.Integer(0)
    for k in range(len(b)):
        v = sympy.nsimplify(b[k]) - sum(c * sympy.nsimplify(b[k - i])
                                        for i, c in cs.items() if i <= k)
        if k >= K:
            if v != 0:
                return None          # the stated recurrence fails on published data
        else:
            P += v * x ** k
    return sympy.expand(P)


def implies(g, shift, coeffs, b, K):
    """True when the stated recurrence forces the conjectured generating function g."""
    P = numerator(coeffs, b, K)
    if P is None:
        return None
    D = denominator(coeffs)
    head = gfrec.series(g, shift) if shift else []
    if head is None:
        return None
    t = g - sum(head[j] * x ** j for j in range(shift))
    try:
        lhs = sympy.cancel(sympy.together(t / x ** shift))
        return sympy.simplify(sympy.cancel(lhs - P / D)) == 0
    except Exception:
        return None


def coeffs_from_annihilator(q):
    """{i: c_i} for a(n) = sum c_i a(n-i), from closedform.annihilator's answer.

    A closed form the entry states as fact is a premise of exactly the same strength as a
    stated recurrence: sum_j p_j(n) lambda_j^n satisfies the recurrence whose characteristic
    polynomial is prod_j (x - lambda_j)^(deg p_j + 1), so the generating function argument
    runs unchanged once that polynomial is read as coefficients.
    """
    co = q[0] if isinstance(q, tuple) else q
    if not co:
        return None
    return {int(i): sympy.nsimplify(c) for i, c in co.items() if sympy.nsimplify(c) != 0}
