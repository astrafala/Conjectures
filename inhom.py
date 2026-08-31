#!/usr/bin/env python3
"""A recurrence stated as fact with an INHOMOGENEOUS term.

Several entries state their known side as

    a(n) = n*(a(n-1) - 1) + 2                       (A073591)
    a(n) = -(n-3)*a(n-1) + (n-3)*(n-2)              (A054516)
    a(n) = n*a(n-1) - (n-1)*a(n-2) - 1              (A001338)

which every reader here refused: they all expect sum_i p_i(n) a(n-i) = 0, and a term with
no a(...) in it makes the parse fail or, worse, silently drop it.

Such a recurrence is still a perfectly good known side. Write it as L(a) = h(n) with h a
polynomial of degree m. Applying the difference operator (N - 1)^(m+1) kills h, so

    (N - 1)^(m+1) L  annihilates a,

a homogeneous recurrence with polynomial coefficients of order r + m + 1. That operator is
then the known side for the usual Ore right-division test.
"""
import re
import sympy as sp
import ore

n = sp.Symbol('n')
SPLIT = re.compile(r"^\s*a\(n\)\s*=\s*(.+)$", re.I)


def parse(line):
    """(ps, h) with sum_i ps[i] a(n-i) = h(n), or None. ps[0] is the a(n) coefficient."""
    m = SPLIT.match(line.split(" - _")[0].strip().rstrip("."))
    if not m:
        return None
    body = m.group(1)
    body = re.sub(r",?\s*(with|where|for)\s.*$", "", body, flags=re.I).strip().rstrip(".")
    body = body.replace("^", "**")
    body = re.sub(r"(\d)\s*([a-zA-Z(])", r"\1*\2", body)
    body = re.sub(r"\)\s*\(", r")*(", body)
    syms, k = {}, 0
    idx = sorted({int(t) for t in re.findall(r"a\(n\s*-\s*(\d+)\)", body)})
    if not idx:
        return None
    for j in idx:
        syms[f"__a{j}__"] = sp.Symbol(f"__a{j}__")
        body = body.replace(f"a(n-{j})", f"__a{j}__").replace(f"a(n - {j})", f"__a{j}__")
    if re.search(r"a\(", body):
        return None
    try:
        e = sp.expand(sp.sympify(body, locals=dict(syms, n=n)))
    except Exception:
        return None
    if not isinstance(e, sp.Expr):
        return None
    ps = [sp.Integer(1)]
    rest = e
    for j in range(1, max(idx) + 1):
        s = syms.get(f"__a{j}__")
        if s is None:
            ps.append(sp.Integer(0)); continue
        c = sp.expand(rest.coeff(s, 1))
        if c.has(*syms.values()):
            return None                       # nonlinear in the earlier terms
        ps.append(sp.expand(-c))
        rest = sp.expand(rest - c * s)
    if rest.has(*syms.values()):
        return None
    h = sp.expand(rest)
    if h.free_symbols - {n}:
        return None
    # the inhomogeneity must be a POLYNOMIAL in n: (N-1)^(m+1) only annihilates those.
    # A binomial or factorial term is hypergeometric, not polynomial, and sp.Poly raises
    # on it rather than returning False, so guard before asking.
    if h.atoms(sp.Function) or h.has(sp.factorial) or h.has(sp.binomial):
        return None
    try:
        if h.has(n) and not sp.Poly(h, n).is_polynomial:
            return None
        if h.has(n):
            sp.Poly(h, n)
    except Exception:
        return None
    return ps, sp.expand(h)


def homogenise(ps, h):
    """The homogeneous operator (N-1)^(m+1) L, as a coefficient list in Q(n)[N]."""
    L = ore.to_operator(ps)
    if h == 0:
        return L
    m = int(sp.Poly(h, n).degree()) if h.has(n) else 0
    D = [sp.Integer(-1), sp.Integer(1)]       # N - 1, as [c0, c1] meaning c0 + c1*N
    out = L
    for _ in range(m + 1):
        out = ore.mul(D, out) if hasattr(ore, "mul") else None
        if out is None:
            return None
    return out
