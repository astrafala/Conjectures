#!/usr/bin/env python3
"""Read a generating function written as "G.f. f: f(z) = ... (k=0, l=1)".

Seventy entries with an open conjectured recurrence state their generating function this
way, and every parser here refused all of them, for three reasons at once: the prefix is
often mistyped "G.f f:" with no full stop, the variable is z rather than x, and the
expression carries free parameters k and l plus the symbols a(0) and a(1), whose values sit
in a parenthetical at the end of the line and in the entry's own DATA.

The family is worth the trouble because of what it says:

    f(z) = (1 - sqrt(1 - 4*z*(a(0) - z*a(0)^2 + z*a(1) + (k+l)*z^2/(1-z) + k*z^2/(1-z)^2)))/(2*z)

is an explicit QUADRATIC generating function -- one square root over Q(x) -- which is the
field the residual-polynomial criterion was built for first and handles exactly.
"""
import re
import sympy as sp

x, z = sp.symbols('x z')
HEAD = re.compile(r"^\s*G\.?f\.?\s*f?\s*:?\s*f?\s*\(z\)\s*=\s*", re.I)
ASSIGN = re.compile(r"\(([^()]*=[^()]*)\)\s*\.?\s*$")


def parse(line, data, off):
    """The generating function as an expression in x, or None.

    a(0) and a(1) are taken from the entry's own terms, so the formula is closed with the
    entry's data rather than with anything assumed.
    """
    m = HEAD.match(line)
    if not m:
        return None
    body = line[m.end():].strip()
    subs = {}
    am = ASSIGN.search(body)
    if am:
        for part in am.group(1).split(","):
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            try:
                subs[sp.Symbol(k.strip())] = sp.Integer(int(v.strip()))
            except Exception:
                return None
        body = body[:am.start()].strip()
    body = body.rstrip(".").strip()
    # a(0), a(1), ... come from the published terms
    for j in sorted({int(t) for t in re.findall(r"a\((\d+)\)", body)}, reverse=True):
        if j - off < 0 or j - off >= len(data):
            return None
        body = body.replace(f"a({j})", f"({data[j - off]})")
    body = body.replace("^", "**")
    try:
        e = sp.sympify(body, locals={'z': z, 'sqrt': sp.sqrt})
    except Exception:
        return None
    if not isinstance(e, sp.Expr):
        return None
    e = e.subs(subs)
    if e.free_symbols - {z}:
        return None
    return sp.together(e.subs(z, x))
