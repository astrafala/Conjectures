#!/usr/bin/env python3
"""Conjectured identities between different OEIS entries.

A great many conjectures have the shape

    a(n) = c_1 * A111111(n+k_1) + c_2 * A222222(n+k_2) + <polynomial in n>,

which is not a recurrence at all and so was invisible to every engine here. When each
entry involved posts a generating function, the identity is a single identity between
generating functions, and the same residual test decides it: form

    F_a(x) - sum_j c_j * (shift of F_j)(x) - (polynomial part)(x)

and ask whether it is a polynomial. It usually is not zero -- these claims typically hold
only past a small boundary, exactly as with the closed-form variant -- so testing for
zero would score every one of them a failure.

Shifts are handled on the index the OEIS entry itself uses: F_B(x) = sum_{n>=0} b(n) x^n
with b(n) = 0 below the entry's offset, so b(n+k) has generating function
(F_B - sum_{m<k} b(m) x^m) / x^k and b(n-k) has x^k F_B.
"""
import os, re
import sympy as sp
from prove_rec import parse_gf
from holonomic import taylor

x, n = sp.symbols('x n')
ROOT = "/home/user/oeis/oeisdata/seq"

TERM = re.compile(r"A(\d{6})\(\s*n\s*([+-]\s*\d+)?\s*\)")
EMPIRIC = re.compile(r"empirical|conjectur|guessed", re.I)


def fields(a):
    p = f"{ROOT}/{a[:4]}/{a}.seq"
    if not os.path.exists(p):
        return None
    f = {}
    for line in open(p, errors="ignore"):
        if line.startswith("%"):
            f.setdefault(line[1], []).append(
                re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
    return f


def series_of(a):
    """(F, data, offset) with F the g.f. indexed as the entry indexes it."""
    f = fields(a)
    if not f:
        return None
    data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
    try:
        terms = [int(t) for t in data.split(",") if t.strip()]
    except ValueError:
        return None
    if len(terms) < 8:
        return None
    off = int((f.get("O") or ["0"])[0].split(",")[0])
    for l in f.get("F", []):
        m = re.match(r"G\.f\.\s*:?\s*(.+)", l.strip(), re.I)
        if not m or EMPIRIC.search(l):
            continue
        src = m.group(1).strip()
        try:
            G = parse_gf(src, 'x', raw=src)
            N = min(len(terms) - 1, 9)
            base = taylor(G, off + N + 4)
        except Exception:
            continue
        for sh in (0, 1, 2, -1, -2):
            idx = [off + k - sh for k in range(N + 1)]
            if any(i < 0 or i >= len(base) for i in idx):
                continue
            if all(sp.simplify(base[i] - terms[k]) == 0 for k, i in enumerate(idx)):
                return sp.together(x ** sh * G), terms, off
    return None


def shifted(F, terms, off, k, N):
    """Generating function of m -> b(m+k), in the entry's own indexing."""
    if k == 0:
        return F
    if k < 0:
        return sp.together(x ** (-k) * F)
    coeffs = taylor(F, k + 2)
    head = sum(coeffs[m] * x ** m for m in range(k))
    return sp.together((F - head) / x ** k)


def parse_identity(body):
    """Split 'a(n) = ...' into (list of (coeff, anum, shift), polynomial part)."""
    b = body.split(" - _")[0]
    b = re.sub(r"\bfor\s+n\s*[><=].*$", "", b)
    b = re.sub(r",?\s*(with|where)\s.*$", "", b, flags=re.I)
    b = b.strip().rstrip(".").strip().rstrip(",").strip()
    parts = re.split(r"(?<![<>=!])=(?!=)", b)
    if len(parts) < 2:
        return None
    lhs, rhs = parts[0], parts[1]
    if lhs.strip() != "a(n)":
        return None
    refs = []

    def grab(m):
        refs.append(("A" + m.group(1),
                     int((m.group(2) or "0").replace(" ", ""))))
        return f"REF{len(refs)-1}"

    rhs2 = TERM.sub(grab, rhs)
    if re.search(r"A\d{6}", rhs2):
        return None
    rhs2 = rhs2.replace("^", "**")
    rhs2 = re.sub(r"(\d)\s*\(", r"\1*(", rhs2)
    rhs2 = re.sub(r"\)\s*\(", r")*(", rhs2)
    rhs2 = re.sub(r"(\d)\s*n\b", r"\1*n", rhs2)
    rhs2 = re.sub(r"(\d)\s*(REF\d+)", r"\1*\2", rhs2)
    syms = {f"REF{i}": sp.Symbol(f"REF{i}") for i in range(len(refs))}
    try:
        e = sp.expand(sp.sympify(rhs2, locals={**syms, 'n': n}))
    except Exception:
        return None
    if e.free_symbols - {n} - set(syms.values()):
        return None
    out = []
    rest = e
    for i, (a, k) in enumerate(refs):
        s = syms[f"REF{i}"]
        c = sp.expand(e.coeff(s))
        if c.has(*syms.values()):
            return None                     # product of two entries: not a g.f. identity
        out.append((c, a, k))
        rest = sp.expand(rest - c * s)
    if rest.has(*syms.values()):
        return None
    if not sp.expand(rest).is_polynomial(n):
        return None
    return out, sp.expand(rest)


def poly_gf(p, N):
    """Generating function of n -> p(n) for a polynomial p, as p(theta) [1/(1-x)]."""
    q = sp.Poly(p, n) if p != 0 else None
    if q is None:
        return sp.Integer(0)
    base = 1 / (1 - x)
    out = sp.Integer(0)
    for (j,), c in zip(q.monoms(), q.coeffs()):
        t = base
        for _ in range(j):
            t = sp.cancel(x * sp.diff(t, x))
        out += c * t
    return sp.together(out)


def theta_apply(p, F):
    """c(theta) F for a polynomial c in n."""
    if p == 0:
        return sp.Integer(0)
    q = sp.Poly(p, n)
    powers = [sp.together(F)]
    deg = q.degree() if q.total_degree() >= 0 else 0
    for _ in range(deg):
        powers.append(sp.cancel(x * sp.diff(powers[-1], x)))
    out = sp.Integer(0)
    for (j,), c in zip(q.monoms(), q.coeffs()):
        out += c * powers[j]
    return sp.together(out)


def is_polynomial(e):
    e = sp.cancel(sp.together(sp.simplify(e)))
    num, den = sp.fraction(e)
    if not den.is_polynomial(x) or sp.Poly(den, x).total_degree() != 0:
        return False, None
    out = sp.expand(sp.cancel(e))
    if not out.is_polynomial(x) or (out.free_symbols - {x}):
        return False, None
    return True, out
