#!/usr/bin/env python3
"""a(n) = g(n) + c(n) * Sum_{k=lo..hi} F(n,k) -- a sum that is not the whole right side.

sumparse.py requires the right-hand side to BE a summation, so it refuses

    a(n) = n! * Sum_{k=0..n} 5^k/k!                 (A080954)
    a(n) = 1 + Sum_{k=2..n} n!/k!                   (A094294)
    a(n) = binomial(2*n+1,n) + Sum_{i=...} ...      (A055836)

although the summand is exactly what creative telescoping wants. Twenty-two entries in the
residue are of this shape.

The extra pieces cost one step. Telescoping gives an operator L with L(S) = 0 for
S(n) = Sum_k F(n,k). Since a = g + c*S, we have S = (a - g)/c, and substituting turns L
into an operator on a: writing L = sum_j sigma_j(n) N^j,

    sum_j sigma_j(n) * (a(n+j) - g(n+j)) / c(n+j) = 0,

which after multiplying by the least common denominator is an inhomogeneous recurrence for
a with right-hand side sum_j sigma_j(n) g(n+j) * (c(n)/c(n+j)) -- a polynomial when g and c
are. One application of a difference operator that annihilates it makes it homogeneous, and
that is the known side.
"""
import re
import sympy as sp

n, k = sp.symbols('n k')
SUM = re.compile(r"Sum_\{\s*([a-zA-Z])\s*=\s*([^}]*?)\.\.([^}]*?)\s*\}", re.I)
LOCALS = {'n': n, 'binomial': sp.binomial, 'factorial': sp.factorial, 'C': sp.binomial,
          'floor': sp.floor, 'ceiling': sp.ceiling, 'sqrt': sp.sqrt, 'gamma': sp.gamma}


def _ready(s):
    s = s.replace("^", "**")
    s = re.sub(r"(\d)\s*([a-zA-Z(])", r"\1*\2", s)
    s = re.sub(r"\)\s*\(", r")*(", s)
    s = re.sub(r"\b(\d+)!", r"factorial(\1)", s)
    s = re.sub(r"([a-zA-Z_]\w*)!", r"factorial(\1)", s)
    s = re.sub(r"\)!", ")_FACT_", s)
    s = s.replace(")_FACT_", ")")
    return s


def split(line):
    """(g, c, F, idx, lo, hi) for a(n) = g(n) + c(n)*Sum_{idx=lo..hi} F, or None."""
    m = re.match(r"^\s*a\(n\)\s*=\s*(.+)$", line.split(" - _")[0].strip().rstrip("."), re.I)
    if not m:
        return None
    body = re.sub(r",?\s*(with|where|for)\s.*$", "", m.group(1), flags=re.I).strip().rstrip(".")
    sm = SUM.search(body)
    if not sm or SUM.search(body[sm.end():]):
        return None                      # no sum, or a second one: not this shape
    idx = sp.Symbol(sm.group(1))
    lo_s, hi_s = sm.group(2), sm.group(3)
    # the summand runs to the end of the line, or to a top-level + / - outside brackets
    rest = body[sm.end():]
    depth, cut = 0, len(rest)
    for i, ch in enumerate(rest):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth < 0:
                cut = i; break
    summand_s, tail = rest[:cut], rest[cut:]
    head = body[:sm.start()]
    # head is "g +" or "c *" or empty
    g_s, c_s = "0", "1"
    h = head.strip()
    if h.endswith("*"):
        c_s = h[:-1].strip() or "1"
    elif h.endswith("+"):
        g_s = h[:-1].strip() or "0"
    elif h.endswith("-"):
        g_s = h[:-1].strip() or "0"; c_s = "-1"
    elif h:
        return None
    try:
        loc = dict(LOCALS); loc[str(idx)] = idx
        g = sp.sympify(_ready(g_s), locals=loc)
        c = sp.sympify(_ready(c_s), locals=loc)
        F = sp.sympify(_ready(summand_s), locals=loc)
        lo = sp.sympify(_ready(lo_s), locals=loc)
        hi = sp.sympify(_ready(hi_s), locals=loc)
    except Exception:
        return None
    for e in (g, c, F, lo, hi):
        if not isinstance(e, sp.Expr):
            return None
    if (g.free_symbols | c.free_symbols) - {n}:
        return None
    if F.free_symbols - {n, idx} or c == 0:
        return None
    if tail.strip():
        return None
    return g, c, F, idx, lo, hi
