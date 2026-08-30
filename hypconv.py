#!/usr/bin/env python3
"""Read a hypergeometric value as the sum it stands for.

Fifty-nine entries state their known side as

    a(n) = hypergeom([1/2 - n/2, -n/2, n + 1], [1, 1], 4)

and every parser here refused the line, because "hypergeom" is not a function cfparse
knows and the line is not a Sum_ that sumparse can read. But pFq is a sum by definition,

    pFq(a; b; z) = Sum_{k >= 0} (prod_i (a_i)_k / prod_j (b_j)_k) z^k / k! ,

whose summand is a proper hypergeometric term in (n, k) whenever the parameters are linear
in n. That is exactly the input creative telescoping wants, so the whole class becomes
reachable by machinery already built and already validated.

The sum terminates when some upper parameter is a nonpositive integer for every n in
range -- the usual case here, where one of them is -n or -n/2. A non-terminating series is
refused: an infinite sum of a term that does not vanish is not something the boundary
bookkeeping in zeilb.py is set up to certify.
"""
import re
import sympy as sp

n, k = sp.symbols('n k')
LOCALS = {'n': n, 'k': k, 'binomial': sp.binomial, 'factorial': sp.factorial,
          'gamma': sp.gamma, 'sqrt': sp.sqrt, 'Pi': sp.pi, 'pi': sp.pi}

CALL = re.compile(r"\b(hypergeom|hyper|HypergeometricPFQ)\s*\(", re.I)
PFQ = re.compile(r"\b(\d)F(\d)\s*\(", re.I)


def _lists(body):
    """Split 'hypergeom(...)' arguments into (upper, lower, z), honouring nesting."""
    depth, cur, parts = 0, "", []
    for ch in body:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
            continue
        cur += ch
    parts.append(cur)
    if len(parts) != 3:
        return None
    def lst(s):
        s = s.strip()
        # parameter lists are written [..], {..} or (..) depending on the contributor
        if len(s) > 1 and s[0] in "[{(" and s[-1] in "]})":
            s = s[1:-1]
        return [p for p in s.split(",") if p.strip()]
    return lst(parts[0]), lst(parts[1]), parts[2]


def _body(line, m):
    """The text inside the call that starts at m."""
    i = m.end() - 1
    depth = 0
    for j in range(i, len(line)):
        if line[j] in "([{":
            depth += 1
        elif line[j] in ")]}":
            depth -= 1
            if depth == 0:
                return line[i + 1:j], j
    return None, None


def parse(line):
    """(summand, lo, hi, prefactor) for a line a(n) = <prefactor> * pFq(...), or None."""
    s = re.sub(r"^\s*a\(n\)\s*=\s*", "", line.strip().rstrip("."), flags=re.I)
    s = s.replace("^", "**")
    s = re.sub(r"\b(\d)F(\d)\s*\(", "hypergeom(", s)
    s = s.replace(";", ",")
    m = CALL.search(s)
    if m is None:
        return None
    body, end = _body(s, m)
    if body is None:
        return None
    ls = _lists(body)
    if ls is None:
        return None
    up, lo_, z = ls
    pre = (s[:m.start()] + "1" + s[end + 1:]).strip()
    pre = re.sub(r"\*\s*$", "", pre).strip() or "1"
    try:
        up = [sp.sympify(_ready(u), locals=LOCALS) for u in up]
        lo_ = [sp.sympify(_ready(u), locals=LOCALS) for u in lo_]
        z = sp.sympify(_ready(z), locals=LOCALS)
        pre = sp.sympify(_ready(pre), locals=LOCALS)
    except Exception:
        return None
    if any(e.free_symbols - {n} for e in up + lo_ + [z, pre]):
        return None
    # where does it terminate? an upper parameter -n + c with c an integer <= 0 gives k <= n - c
    hi = None
    for u in up:
        p = sp.Poly(u, n) if u.has(n) else None
        if p is None or p.degree() != 1:
            continue
        c1, c0 = p.coeff_monomial(n), p.coeff_monomial(1)
        if c1 == -1 and c0.is_Integer and c0 <= 0:
            cand = n + c0
            hi = cand if hi is None else sp.Min(hi, cand)
    if hi is None:
        return None                     # non-terminating: not certifiable here
    F = pre * z ** k / sp.factorial(k)
    for u in up:
        F *= sp.rf(u, k)
    for b in lo_:
        F /= sp.rf(b, k)
    # NOT simplified. sympy rewrites rf(-n, k) through gamma of a negative argument and
    # produces sin(pi*n) factors; the Pochhammer form is what makes the shift quotient
    # F(n,k+1)/F(n,k) visibly rational, which is the whole point.
    return sp.together(F), sp.Integer(0), hi, pre


def _ready(s):
    s = s.strip().replace("^", "**")
    s = re.sub(r"(\d)\s*\(", r"\1*(", s)
    s = re.sub(r"\)\s*\(", r")*(", s)
    s = re.sub(r"(\d)\s*([a-zA-Z])", r"\1*\2", s)
    s = re.sub(r"\bC\(", "binomial(", s)
    return s


if __name__ == "__main__":
    import json
    for a, line in json.load(open("hyp_cands.json")):
        r = parse(line)
        print(f"{a}  {'OK ' if r else 'no '} {line[:80]}")
        if r:
            print(f"      F = {r[0]}   k = 0..{r[2]}")
