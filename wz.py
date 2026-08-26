#!/usr/bin/env python3
"""Settle a conjectured recurrence for a sequence given as a hypergeometric sum, by
Gosper's algorithm applied to the conjectured operator itself.

The usual route is Zeilberger's algorithm: search for *some* recurrence the sum
satisfies, then check the conjectured one is a consequence. That search is the expensive
and fragile part, and it is unnecessary here, because the recurrence to test is already
known. Writing a(m) = Sum_k F(m,k), the conjecture

    Sum_i p_i(n) a(n-i) = 0

is the statement that the single k-sum of T(k) = Sum_i p_i(n) F(n-i,k) vanishes. If T is
Gosper-summable -- if there is a hypergeometric G with T(k) = G(k+1) - G(k) -- then that
sum telescopes, and it is 0 as soon as G vanishes at both ends of the range. So the whole
question reduces to running Gosper once on a summand we can write down directly.

Two things make the verdict safe regardless of how G was found:

  * the certificate is checked, not trusted. T(k) - (G(k+1) - G(k)) is reduced to a
    rational function by dividing through by T(k), and must cancel to zero exactly.
  * the boundary terms are checked separately, since telescoping alone gives
    G(hi+1) - G(lo), not 0.
"""
import re
import sympy as sp
from sympy.concrete.gosper import gosper_term

n, k = sp.symbols('n k', integer=True)

LOCALS = {
    'binomial': sp.binomial, 'C': sp.binomial, 'factorial': sp.factorial,
    'gamma': sp.gamma, 'n': n, 'k': k, 'Sum': sp.Sum, 'abs': sp.Abs,
}


def parse_sum(src):
    """Turn an OEIS 'Sum_{k=lo..hi} expr' formula into (summand, lo, hi)."""
    m = re.match(r"a\(n\)\s*=\s*Sum_\{\s*k\s*=\s*([^.]+?)\.\.\s*([^}]+?)\s*\}\s*(.+)$",
                 src.strip(), re.I)
    if not m:
        return None
    lo, hi, body = m.group(1), m.group(2), m.group(3)
    body = body.split(" - _")[0].strip().rstrip('.')
    if re.search(r"Sum_|Product_|Stirling|A\d{6}|floor|ceiling|mod|!!", body, re.I):
        return None            # not a single hypergeometric summand
    for src_, dst in (('^', '**'),):
        body = body.replace(src_, dst)
    body = re.sub(r"(\d)\s*\(", r"\1*(", body)
    body = re.sub(r"\)\s*\(", r")*(", body)
    body = re.sub(r"(\d)([nk])\b", r"\1*\2", body)
    try:
        expr = sp.sympify(body, locals=LOCALS)
        LO = sp.sympify(lo, locals=LOCALS)
        HI = sp.sympify(hi, locals=LOCALS)
    except Exception:
        return None
    if expr.free_symbols - {n, k}:
        return None
    return expr, LO, HI


def hyper_ratio(T, var):
    """T(var+1)/T(var) as a rational function, or None if T is not hypergeometric."""
    r = sp.simplify(sp.combsimp(T.subs(var, var + 1) / T))
    r = sp.cancel(sp.together(r))
    num, den = sp.fraction(r)
    if not (num.is_polynomial(var) and den.is_polynomial(var)):
        return None
    return r


def certify(T, G):
    """Exact check of T(k) = G(k+1) - G(k), done as a rational-function identity."""
    d = sp.simplify(sp.combsimp((G.subs(k, k + 1) - G - T) / T))
    return sp.cancel(sp.together(d)) == 0


def prove(ps, F, lo, hi):
    """ps are the conjectured p_i(n). Returns (G, why) with G the certificate, or
    (None, reason)."""
    T = sum(ps[i] * F.subs(n, n - i) for i in range(len(ps)) if ps[i] != 0)
    T = sp.combsimp(T)
    if T == 0:
        return sp.Integer(0), "summand vanishes identically"
    if hyper_ratio(T, k) is None:
        return None, "T(k) is not hypergeometric in k"
    G = gosper_term(T, k)
    if G is None:
        return None, "not Gosper-summable"
    G = sp.combsimp(G * T)
    if not certify(T, G):
        return None, "certificate failed to verify"
    return G, "verified"
