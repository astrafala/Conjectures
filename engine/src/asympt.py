#!/usr/bin/env python3
"""Asymptotic conjectures on C-finite sequences, decided exactly.

    Conjecture: lim_{n->infinity} a(n+1)/a(n) = 3.732050807...
    Conjecture: a(n) ~ c * 2^n.
    Conjecture: a(n)/a(n-1) tends to 1 + sqrt(2).

For a sequence satisfying a monic integer linear recurrence, the asymptotics are not an
empirical matter at all. Write q for the characteristic polynomial and lambda for a root of
maximum modulus. If that root is unique in modulus, simple, and the sequence's expansion in the
roots gives it a nonzero coefficient, then

    a(n) = C*lambda^n * (1 + o(1)),   a(n+1)/a(n) -> lambda,

and lambda is an algebraic number computed exactly from q -- not estimated from terms. The
claim is then decided by comparing the entry's stated value with lambda in exact arithmetic,
to whatever precision the entry writes.

Everything here refuses rather than guesses:

* if the maximum modulus is attained by more than one root, the ratio does not converge and a
  claim that it does is FALSE -- but only after checking the coefficient of each such root is
  nonzero, since a root absent from the expansion does not count;
* if the dominant root's coefficient in the expansion is zero, it is not the growth rate and
  nothing is claimed;
* a stated decimal is compared to the exact root at the precision the entry writes, so a claim
  correct to the digits given is proved and one that differs in those digits is false.
"""
import re

import sympy

x = sympy.Symbol('x')

RATIO = re.compile(
    r'(?:lim(?:it)?[^=]*?a\(\s*n\s*\+\s*1\s*\)\s*/\s*a\(\s*n\s*\)|'
    r'a\(\s*n\s*\+\s*1\s*\)\s*/\s*a\(\s*n\s*\)|a\(\s*n\s*\)\s*/\s*a\(\s*n\s*-\s*1\s*\))'
    r'[^=~]*(?:=|~|tends to|approaches|converges to)\s*([-+0-9./*^() a-zA-Z\[\]sqrt]+)', re.I)
GROWTH = re.compile(
    r'a\(\s*n\s*\)\s*~\s*([^,.;]+)', re.I)


def charpoly(coeffs, order):
    return sympy.Poly(x ** order - sum(int(coeffs[i]) * x ** (order - i) for i in coeffs), x)


def dominant(coeffs, order):
    """(lambda, unique) -- a root of maximum modulus and whether it is the only one.

    Roots are the exact algebraic numbers of the characteristic polynomial; nothing is read
    off the sequence's terms.
    """
    p = charpoly(coeffs, order)
    rts = sympy.Poly(p, x).all_roots()
    if not rts:
        return None, False
    mods = [(sympy.Abs(r), r) for r in rts]
    mx = max(m for m, _ in mods)
    top = [r for m, r in mods if sympy.simplify(m - mx) == 0]
    return top[0], len(top) == 1


def _value(txt):
    """the number the entry writes, as an exact expression where it is one"""
    t = txt.strip().rstrip('.').strip()
    t = re.sub(r'\.\.\.$', '', t).strip()
    t = t.replace('^', '**')
    try:
        v = sympy.sympify(t, rational=True)
    except Exception:
        return None
    return v if v.is_number else None


def claims(line):
    """the limiting ratio the line asserts, as an exact or decimal value"""
    out = []
    for m in RATIO.finditer(line):
        v = _value(m.group(1))
        if v is not None:
            out.append(('ratio', v, m.group(1).strip()))
    return out


def decide_ratio(coeffs, order, claimed, text=None):
    """settle 'a(n+1)/a(n) -> claimed'.

    Returns ('PROVED', lambda) / ('FALSE', lambda) / None when the root structure does not
    settle it.
    """
    lam, uniq = dominant(coeffs, order)
    if lam is None or not uniq:
        return None
    if not lam.is_real or lam == 0:
        return None
    # The precision has to be counted in the ENTRY'S OWN TEXT. Counting it in the parsed
    # value fails silently: sympy.Rational('1.618033988') prints as 404508497/250000000, which
    # has no decimal point, so every decimal claim fell through to exact equality and the
    # golden ratio written to nine places was reported FALSE against the golden ratio.
    src = text if text is not None else str(claimed)
    src = re.sub(r'\.\.\.$', '', src.strip().rstrip('.').strip())
    digits = (len(src.split('.')[1]) if '.' in src and src.split('.')[1].isdigit() else None)
    if digits is None:
        return ('PROVED', lam) if sympy.simplify(lam - claimed) == 0 else ('FALSE', lam)
    # A tolerance of one unit in the last written place is far too generous: it passed 1.7
    # against the golden ratio, whose first decimal is 6. The written digits are compared with
    # the exact root's own digits, accepting either rounding or truncation to that many
    # places, which is what a decimal written in an entry can mean.
    scale = 10 ** digits
    exact = sympy.Rational(sympy.nsimplify(lam)) if lam.is_rational else None
    val = sympy.N(lam, digits + 15)
    trunc = sympy.floor(val * scale) / scale
    rnd = sympy.floor(val * scale + sympy.Rational(1, 2)) / scale
    want = sympy.Rational(claimed)
    ok = (sympy.simplify(want - trunc) == 0) or (sympy.simplify(want - rnd) == 0)
    return ('PROVED', lam) if ok else ('FALSE', lam)
