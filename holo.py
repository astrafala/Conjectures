#!/usr/bin/env python3
"""Settle a conjectured recurrence through a D-finite annihilator of the g.f.

Every generating-function engine here so far worked inside a field chosen to fit the
expression: one square root, several square roots, an algebraic function field, a
differential module with a log and an exponential. That is a ladder of special cases, and
entries that post a Bessel function or a hypergeometric series fall off the end of it.

The general statement underneath all of them is that the generating function is D-finite:
it satisfies a linear ODE with polynomial coefficients. From such an ODE the coefficients
satisfy a linear recurrence with polynomial coefficients, obtained by reading off powers
of x, and the conjectured recurrence is then settled the same way as everywhere else --
by right division in the Ore algebra Q(n)[N].

The annihilating ODE is produced by sympy's holonomic module, which closes over sums,
products, composition, algebraic functions, exp, log, and the Bessel and hypergeometric
families. Nothing about it is taken on trust: the recurrence it returns is re-derived
against the entry's own terms before use, and the division is multiplied back out.
"""
import sympy as sp
from sympy.holonomic import expr_to_holonomic

x, n = sp.symbols('x n')


def _polys(rec):
    """The recurrence's coefficients as sympy expressions in n, for N^0..N^r."""
    out = []
    for q in rec.listofpoly:
        try:
            coeffs = q.to_list()                     # descending powers
        except AttributeError:
            out.append(sp.sympify(q))
            continue
        e = sum(sp.Rational(str(c)) * n ** (len(coeffs) - 1 - i)
                for i, c in enumerate(coeffs))
        out.append(sp.expand(e))
    return out


def annihilator(A, maxorder=8):
    """(coefficients of N^0..N^r, first index the recurrence is asserted from), or None."""
    try:
        h = expr_to_holonomic(A, x=x)
    except Exception:
        return None
    try:
        seq = h.to_sequence()
    except Exception:
        return None
    if not seq or len(seq) != 1:
        return None                 # several pieces: the recurrence is not one relation
    piece = seq[0]
    s = piece[0]
    ints = [t for t in piece[1:] if isinstance(t, (int, sp.Integer))]
    start = int(max(ints)) if ints else 0
    ps = _polys(s.recurrence)
    while len(ps) > 1 and sp.expand(ps[-1]) == 0:
        ps.pop()
    if len(ps) - 1 > maxorder or len(ps) < 2:
        return None
    return ps, start


def align_shift(ps, coeffs, start, span=3, npts=6):
    """The index shift s with sum_j ps_j(m) coeffs[m+j+s] = 0, or None.

    sympy's to_sequence does not always index its recurrence by the power of x: when the
    expansion has a leading zero the sequence it returns can be the coefficients from the
    first nonzero term on. Rather than reverse-engineer which convention applies when,
    the shift is found by testing it against the coefficients -- the same discipline used
    for the closed forms, and for the same reason: a convention guessed wrong is silent.
    """
    r = len(ps) - 1
    for s_ in [0] + [d for k in range(1, span + 1) for d in (k, -k)]:
        seen, ok = 0, True
        for m in range(max(start, max(0, -s_)), len(coeffs) - r - max(0, s_)):
            tot = sum(sp.expand(ps[j]).subs(n, m) * coeffs[m + j + s_]
                      for j in range(r + 1))
            if sp.simplify(tot) != 0:
                ok = False
                break
            seen += 1
            if seen >= npts:
                break
        if ok and seen >= max(3, r):
            return s_
    return None


def check_on_terms(ps, coeffs, start, npts=6):
    """The derived recurrence, evaluated on the coefficients we actually have.

    The point is not to prove anything -- the ODE does that -- but to catch a mistake in
    reading sympy's output into this convention, which is exactly the kind of error that
    otherwise survives all the way into a paper.
    """
    r = len(ps) - 1
    seen = 0
    for m in range(start, len(coeffs) - r):
        tot = sum(sp.nsimplify(sp.expand(ps[j]).subs(n, m), rational=True) * coeffs[m + j]
                  for j in range(r + 1))
        if sp.simplify(tot) != 0:
            return False
        seen += 1
        if seen >= npts:
            break
    return seen >= 3
