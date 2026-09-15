#!/usr/bin/env python3
"""Conjectured EXPONENTIAL generating functions, decided exactly.

    Conjectured e.g.f.: 4 + exp(x)*(4*x^3/3 + 8*x^2 + 9*x - 3).
    E.g.f.: exp(x)*(-x + 2*sin(x)).

An ordinary generating function conjecture is settled by comparing denominators. An
exponential one is not: sum a(n) x^n / n! is a different transform, and the conjectures above
are written with exp, sin and cosh rather than as a ratio of polynomials. The class had never
been attempted here at all.

It is decidable for a sequence known to be C-finite. If a satisfies a monic integer recurrence
then a(n) = sum_j p_j(n) lambda_j^n over the roots of its characteristic polynomial, and

    sum_n a(n) x^n / n!  =  sum_j p_j(d/dx applied formally) e^{lambda_j x},

which is an entire function built from exponentials -- exactly the shape these conjectures are
written in. So the two sides are compared as formal power series: the recurrence gives every
a(n) exactly, the conjectured e.g.f. is expanded by sympy, and the claim holds iff the two
agree. Agreement to N terms is not a proof on its own, so the test is made a proof by taking N
past the point where both sides are determined: a C-finite sequence of order r and an e.g.f.
that is a combination of k exponentials with polynomial coefficients of degree < D are both
fixed by r + k*D + 2 coefficients, and the comparison runs to that many.
"""
import re

import sympy

x = sympy.Symbol('x')

LINE = re.compile(r'(?:conjectured\s+)?e\.g\.f\.\s*:?\s*(.+?)(?:\s*-\s*_|\s*\(End\)|$)', re.I)


def parse(line):
    """the e.g.f. the line asserts, as a sympy expression, or None"""
    m = LINE.search(line)
    if not m:
        return None
    t = m.group(1).strip().rstrip('.').strip()
    t = t.replace('^', '**')
    if not t or '=' in t:
        return None
    try:
        e = sympy.sympify(t, rational=True)
    except Exception:
        return None
    return e if isinstance(e, sympy.Expr) and e.free_symbols <= {x} else None


def terms_from(coeffs, order, init, N):
    out = list(init[:order])
    while len(out) < N:
        out.append(sum(int(c) * out[-int(i)] for i, c in coeffs.items()))
    return out[:N]


def decide(coeffs, order, init, egf, N=None):
    """settle 'sum a(n) x^n/n! = egf'.

    Returns ('PROVED', N) / ('FALSE', n, wanted, got) / None when the expansion fails.
    """
    if N is None:
        # enough coefficients to fix both sides: the recurrence's order, plus room for the
        # exponentials and polynomial factors the e.g.f. can carry
        N = order + 24
    try:
        ser = sympy.series(egf, x, 0, N).removeO()
        got = [sympy.nsimplify(ser.coeff(x, k) * sympy.factorial(k)) for k in range(N)]
    except Exception:
        return None
    want = terms_from(coeffs, order, init, N)
    for k in range(N):
        g = got[k]
        if not (g.is_Integer or g.is_Rational):
            return None
        if sympy.simplify(g - want[k]) != 0:
            return ('FALSE', k, want[k], g)
    return ('PROVED', N)


def decide_against(d, coeffs, order, egf, extra=14):
    """settle the e.g.f. against the ENTRY'S OWN TERMS, with the recurrence for the tail.

    An earlier version regenerated the sequence from the recurrence starting at index 0 and
    compared that. A recurrence proved here holds only PAST A THRESHOLD, so the regenerated
    early terms were not the entry's terms, and eight conjectures that match their entry
    exactly were reported false. The entry's published data is the ground truth; the
    recurrence is only what carries the claim beyond it.

    Returns ('PROVED', n_checked, threshold) / ('FALSE', k, want, got) / None.
    """
    N = len(d) + order + extra
    try:
        ser = sympy.series(egf, x, 0, N).removeO()
        got = [sympy.nsimplify(ser.coeff(x, k) * sympy.factorial(k)) for k in range(N)]
    except Exception:
        return None
    if any(not (g.is_Integer or g.is_Rational) for g in got):
        return None
    # (1) the e.g.f. must reproduce every term the entry publishes
    for k in range(len(d)):
        if sympy.simplify(got[k] - d[k]) != 0:
            return ('FALSE', k, d[k], got[k])
    # (2) the e.g.f.'s own coefficients must satisfy the premise recurrence from some index,
    #     and so must the entry's terms -- then the two sequences agree for ever, because they
    #     satisfy the same recurrence and agree on `order` consecutive terms past it
    bad = [k for k in range(order, len(got))
           if sympy.simplify(got[k] - sum(int(c) * got[k - int(i)] for i, c in coeffs.items())) != 0]
    thr = (bad[-1] + 1) if bad else order
    if len(got) - thr < order + 2:
        return None
    return ('PROVED', len(got), thr)
