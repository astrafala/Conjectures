#!/usr/bin/env python3
"""Read a conjectured P-RECURSIVE recurrence -- one with polynomial coefficients in n.

    Conjecture D-finite with recurrence n*a(n) +2*(-2*n+1)*a(n-1) +16*(-n+3)*a(n-2)
      +32*(2*n-7)*a(n-3)=0.
    Conjecture: (n+2)*a(n) +(-5*n-3)*a(n-1) +(5*n-2)*a(n-2) + ... = 0.

`ratrec` reads constant coefficients only, so every one of these is invisible to every sweep
here. There are **459 open entries** in the pool carrying such a claim -- larger than the
linked-a-file vein -- and the machinery to settle them is already in the repository:
`holonomic.prove` decides the claim outright when the generating function is algebraic, by
turning it into an identity of functions rather than a check of terms.

`read(line)` returns `[p_0(n), p_1(n), ...]`, the coefficient of a(n-i), in the order and
sense `holonomic.prove` wants. The parse is done by substituting a distinct symbol for each
a(n-i) and letting sympy collect: writing a regex for the arithmetic would be writing a small
computer-algebra system badly, and these lines carry nested signs and products that defeat one.
"""
import re

import sympy as sp

n = sp.Symbol('n')

SHIFT = re.compile(r'a\(\s*n\s*([-+])\s*(\d+)\s*\)')
PLAIN = re.compile(r'a\(\s*n\s*\)')
# `[^:]*` here ate the whole line when there was no colon at all -- "Conjecture D-finite with
# recurrence n*a(n) + ... = 0." has none, and the marker stripper removed the recurrence with it
MARK = re.compile(r'^\s*(?:Conjectur\w*(?:\s+to\s+be)?|Empirical)\s*:?\s*', re.I)
DFIN = re.compile(r'^\s*D-?finite\s+with\s+recurrence\s*:?\s*', re.I)
ATTR = re.compile(r'\s*[-—]\s*_[^_]+_,.*$')


def read(line, maxorder=40):
    """[p_0, ..., p_r] with sum_i p_i(n) a(n-i) = 0, or None."""
    t = ' '.join(line.split())
    t = ATTR.sub('', t)
    t = re.sub(r'\[_[^_]+_[^\]]*\]', '', t)
    t = MARK.sub('', t)
    t = DFIN.sub('', t)
    t = t.strip().rstrip('.').strip()
    # a range qualifier is not part of the algebra
    t = re.sub(r'\s*,?\s*(?:for\s+)?n\s*[><=]+\s*\d+\s*$', '', t, flags=re.I)
    if 'a(n' not in t:
        return None
    # only a(n) and a(n-i) may appear; a(n+i), a(2n), A-numbers and functions are out of scope
    if re.search(r'a\(\s*n\s*\+', t) or re.search(r'A\d{6}', t):
        return None
    body = t.split('=')
    if len(body) == 1:
        expr_s, rhs_s = body[0], '0'
    elif len(body) == 2:
        expr_s, rhs_s = body
    else:
        return None
    if rhs_s.strip() not in ('0', ''):
        # an inhomogeneous claim is a different theorem and is refused rather than dropped
        return None
    syms = {}

    def sub_shift(m):
        i = int(m.group(2)) * (1 if m.group(1) == '-' else -1)
        if i < 0 or i > maxorder:
            raise ValueError('shift out of range')
        s = syms.setdefault(i, sp.Symbol(f'_A{i}'))
        return f'({s})'

    try:
        s = SHIFT.sub(sub_shift, expr_s)
        s = PLAIN.sub(lambda m: f'({syms.setdefault(0, sp.Symbol("_A0"))})', s)
    except ValueError:
        return None
    if not syms or 0 not in syms:
        return None
    # implicit multiplication, as the corpus writes it: "(4-5n)*a(n-1)"
    s = re.sub(r'(\d)\s*n\b', r'\1*n', s)
    s = s.replace('^', '**')
    if re.search(r'[A-Za-z_]', re.sub(r'_A\d+|\bn\b', '', s)):
        return None
    loc = {'n': n}
    loc.update({f'_A{i}': v for i, v in syms.items()})
    try:
        e = sp.sympify(s, locals=loc)
    except Exception:
        return None
    # A range qualifier the stripper did not catch leaves a comparison in the string, and
    # sympify then returns a RELATIONAL -- StrictGreaterThan has no .coeff and the caller
    # dies on it rather than being told the line is unreadable.
    if not isinstance(e, sp.Expr) or e.is_Relational:
        return None
    e = sp.expand(e)
    r = max(syms)
    ps = []
    for i in range(r + 1):
        v = syms.get(i)
        c = sp.expand(e.coeff(v)) if v is not None else sp.Integer(0)
        if c.free_symbols - {n}:
            return None                      # a coefficient still mentions another a(n-j)
        ps.append(sp.Poly(c, n).as_expr() if c != 0 else sp.Integer(0))
    # every a(n-i) must be accounted for: what is left after removing them all must vanish
    rest = sp.expand(e - sum(ps[i] * syms[i] for i in syms))
    if sp.simplify(rest) != 0:
        return None
    if all(sp.Poly(p, n).total_degree() == 0 for p in ps if p != 0):
        return None                          # constant coefficients: ratrec's business
    return ps
