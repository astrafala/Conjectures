#!/usr/bin/env python3
"""Read the conjectured recurrences ratrec refuses, and turn them into ones it can use.

Two shapes account for most of what the corpus writes and no sweep can read.

**Several claims on one line.** The line is a sentence, not an expression:

    Conjecture: a(n) = n*(961*n+1). a(n) = 3*a(n-1)-3*a(n-2)+a(n-3). G.f.: 2*x*(481+480*x)/(1-x)^3.

ratrec's REC regex takes everything after the first `a(n) =' to the end of the line, so the
recurrence in the middle is never seen. Splitting the line into clauses first recovers it, and
recovers the closed form and the generating function beside it as separate claims -- which
they are: the entry names them separately, so by the counting rule they are separate results.

**An inhomogeneous piece.** `a(n) = a(n-1) + a(n-2) + a(n-3) - 2' is refused outright, and
there is no reason for that: if a(n) - sum_i c_i a(n-i) = K for every n past the threshold,
then b(n) = a(n) - a(n-1) satisfies the homogeneous recurrence, so a itself satisfies the one
whose characteristic polynomial is p(x)(x - 1), of order r + 1. A constant is the common case;
a polynomial inhomogeneity of degree d needs (x - 1)^(d+1) and is handled the same way. The
threshold rises by one for each factor, because the difference at index n uses index n - 1.
"""
import re

import sympy as sp

n = sp.Symbol('n')
x = sp.Symbol('x')

# A clause ends at a full stop or semicolon that is not inside brackets and does not sit
# between two digits (2.5) or after a single capital (E. g.).
SPLIT = re.compile(r'(?<![0-9A-Z])[.;](?=\s|$)')
TERM = re.compile(r'([+-]?\s*[^+-]*?)\*?\s*a\(n\s*-\s*(\d+)\)')
HEAD = re.compile(r'^\s*(?:Conjectur\w*|Empirical|It appears that|Apparently)\s*\d*\s*[:.,]?\s*',
                  re.I)
ATTRIB = re.compile(r'\s*-\s*_[^_]+_.*$')
TAILMARK = re.compile(r'\s*\(\s*conjectur\w*\s*\.?\s*\)\s*$', re.I)
FORN = re.compile(r'for\s+n\s*(>=|>|\\ge)\s*(\d+)', re.I)


def clauses(line):
    """the separate claims written on one line, each with the leading marker removed."""
    s = ATTRIB.sub('', line.strip())
    s = re.sub(r'\(\s*(?:Start|End)\s*\)', '', s, flags=re.I)
    depth, out, cur = 0, [], ''
    for i, ch in enumerate(s):
        if ch in '([{':
            depth += 1
        elif ch in ')]}':
            depth = max(0, depth - 1)
        if depth == 0 and SPLIT.match(s, i):
            out.append(cur)
            cur = ''
            continue
        cur += ch
    out.append(cur)
    return [HEAD.sub('', TAILMARK.sub('', c).strip()).strip() for c in out if c.strip()]


def _rhs(c):
    m = re.match(r'^a\(n\)\s*=\s*(.+)$', c, re.I)
    return m.group(1).strip() if m else None


def parse_rec(clause):
    """(coeffs, threshold) for a clause, INHOMOGENEOUS ones included, or None.

    An inhomogeneous recurrence is returned as the homogeneous one it implies, so every caller
    that already knows what to do with a characteristic polynomial needs no change.
    """
    rhs = _rhs(clause)
    if rhs is None:
        return None
    body = re.sub(r'\s+for\b.*$', '', rhs).strip().rstrip('.').strip()
    if 'a(n)' in body or re.search(r'a\(n\s*\+', body):
        return None
    coeffs = {}
    for tm in TERM.finditer(body):
        raw = tm.group(1).replace(' ', '')
        i = int(tm.group(2))
        if raw in ('', '+'):
            c = sp.Integer(1)
        elif raw == '-':
            c = sp.Integer(-1)
        else:
            if re.search(r'[a-zA-Z]', raw):
                return None
            try:
                c = sp.Rational(sp.sympify(raw))
            except Exception:
                return None
        coeffs[i] = coeffs.get(i, 0) + c
    if not coeffs:
        return None
    leftover = TERM.sub('', body).replace(' ', '')
    thr = None
    f = FORN.search(rhs)
    if f:
        thr = int(f.group(2)) if f.group(1) != '>=' else int(f.group(2)) - 1
    if not leftover.strip('+-*'):
        return {int(k): v for k, v in coeffs.items()}, thr
    # an inhomogeneous piece: a polynomial in n, and nothing else
    try:
        g = sp.sympify(leftover.replace('^', '**'), locals={'n': n})
    except Exception:
        return None
    if not isinstance(g, sp.Expr) or not g.free_symbols <= {n}:
        return None
    try:
        d = sp.Poly(g, n).degree() if g.has(n) else 0
    except Exception:
        return None
    if d > 6:
        return None
    r = max(coeffs)
    p = x ** r - sum(sp.nsimplify(c) * x ** (r - int(i)) for i, c in coeffs.items())
    q = sp.expand(p * (x - 1) ** (d + 1))
    cs = sp.Poly(q, x).all_coeffs()
    out = {}
    for i in range(1, len(cs)):
        c = -sp.nsimplify(cs[i] / cs[0])
        if c != 0:
            out[i] = c
    if not out:
        return None
    return out, (thr + d + 1 if thr is not None else None)


def recurrences(line):
    """every recurrence claimed on this line, as (clause, coeffs, threshold)."""
    got = []
    for c in clauses(line):
        r = parse_rec(c)
        if r:
            got.append((c, r[0], r[1]))
    return got
