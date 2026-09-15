#!/usr/bin/env python3
"""The generating function stated as a PERIODIC continued fraction.

1,509 entries state their g.f. this way and `algf` refused every one of them -- `OUT` rejects
any line containing the words "continued fraction" outright, which was right while nothing
here could read one and wrong the moment something could. 1,015 of those are the Gladkovskii /
Barry shape with a level index,

    G.f.: Q(0), where Q(k) = 1 + (4*k+1)*x*(1+2*x)/(k+1 - ...)

and those are NOT algebraic: the level map changes with k, so there is no equation to solve.
They stay refused, and that refusal is mathematics. The other 565 are written with an ellipsis
and no index,

    G.f.: 1/(1-5x/(1-3x/(1-5x/(1-3x/(1-5x/(1-3x/(1-5x/(1-...     (continued fraction)

and every one of those that is eventually periodic is algebraic of degree exactly 2 -- never
more -- for a reason worth stating, because it is why this is cheap. Each level is

    g_i = b_i + s_i * n_i / g_{i+1},

a Moebius transformation of the level below with matrix [[b_i, s_i*n_i], [1, 0]]. Composing the
p levels of one period multiplies p such matrices; the tail is the FIXED POINT of the composite
map, so it satisfies g = (a g + b)/(c g + d), a quadratic. Any prefix before the period, and the
head of the line, are then further Moebius maps applied to that fixed point, which cannot raise
the degree. So a periodic continued fraction is a quadratic surd in x, which is exactly the
field `holonomic.quadratic` decides claims in.

The branch of the quadratic is chosen by the entry's own published terms, and nothing is
returned unless it reproduces them -- the same guard every other reader here uses, for the same
reason (A116388).
"""
import re

import sympy as sp

x = sp.Symbol('x')

TAIL = re.compile(r'\.\s*\.\s*\.|…')
NOISE = re.compile(r'\(\s*continued\s+fraction[^)]*\)|;\s*$|,\s*$', re.I)
ATTR = re.compile(r'\s*[-—]\s*_[^_]+_,.*$')
BRACKET_ATTR = re.compile(r'\s*\[\s*(?:From\s+)?_[^_]+_\s*,[^\]]*\]\s*\.?\s*$')
# a coefficient that depends on the LEVEL is what makes a continued fraction non-algebraic,
# and the corpus writes that index as k or as n -- A084261 spells its general level out as
# `[(n+1)/2]*x^2', which says in the line itself that the thing is not periodic
KINDEX = re.compile(r'\b[A-Za-z]\s*\(\s*[kn]\s*\)|\(\s*[kn]\s*[-+]|\b[kn]\s*[-+]\s*\d')
LEAD = re.compile(r'^\s*(?:o\.)?g\.f\.\s*[:=]?\s*', re.I)
NAMED = re.compile(r'^\s*[A-Za-z]\s*\(\s*[xz]\s*\)\s*=\s*')


def _openers(s):
    """positions of the '(' that are never closed -- one per level of the nest"""
    stack, open_ = [], []
    for i, ch in enumerate(s):
        if ch == '(':
            stack.append(i)
        elif ch == ')' and stack:
            stack.pop()
    return sorted(stack)


def _split_last_term(t):
    """(base, sign, numerator) -- the last top-level additive term is the numerator"""
    depth, cut = 0, None
    for i, ch in enumerate(t):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch in '+-' and depth == 0 and i > 0 and t[i - 1] not in '+-*/^(eE':
            cut = i
    if cut is None:
        return '0', '+', t.strip()
    return t[:cut].strip(), t[cut], t[cut + 1:].strip()


def levels(body):
    """[(base, sign, num)] for the head and each complete level, or None"""
    s = TAIL.split(body)[0]
    op = _openers(s)
    if len(op) < 3:
        return None
    # every level opener must be the '(' of a '/(' -- anything else is not this shape
    for i in op:
        if i == 0 or s[i - 1] != '/':
            return None
    out = []
    head = s[:op[0] - 1]
    if not head.strip():
        return None
    out.append(_split_last_term(head))
    for k in range(len(op) - 1):
        piece = s[op[k] + 1:op[k + 1] - 1]
        out.append(_split_last_term(piece))
    # the final level is cut off by the ellipsis and carries no information
    return out


def _period(lv):
    """(prefix length, period) for the level list after the head, or None.

    Requires THREE full repeats of evidence. Two is not enough and the cost of learning that
    was A084261, whose levels drift `x^2, x^2, 2*x^2, 2*x^2, 3*x^2, ...`: with two repeats
    allowed, `2*x^2, 2*x^2` reads as prefix 2 period 1, and the g.f. that came out was then
    recorded as "the stated g.f. does not generate the DATA" -- an accusation against the entry
    for a defect of mine, which is the one mistake this project keeps making. Any drifting
    continued fraction repeats its levels in PAIRS; none repeats them three times.
    """
    key = [tuple(' '.join(t.split()) for t in L) for L in lv]
    n = len(key)
    for q in range(0, min(4, n)):
        for p in range(1, 5):
            # Two repeats are enough when the period starts at the top, because a drifting
            # continued fraction never repeats its FIRST level. They are not enough once a
            # prefix is allowed: A084261 drifts `x^2, x^2, 2*x^2, 2*x^2, ...` and its second
            # pair reads as prefix 2 period 1 on two repeats. With a prefix, demand three.
            if q + (2 if q == 0 else 3) * p > n:
                continue
            if all(key[i] == key[i + p] for i in range(q, n - p)):
                return q, p
    return None


def _E(t):
    """the corpus's implicit multiplication, as a sympy expression in x"""
    import algf
    return sp.sympify(algf._implicit(t), locals={'x': x, 'z': x, 'sqrt': sp.sqrt})


def _matrix(level):
    b, s, n = level
    num = _E(n) * (1 if s == '+' else -1)
    return sp.Matrix([[_E(b), num], [1, 0]])


def candidates(body):
    """the algebraic values this periodic continued fraction can take (both branches)"""
    lv = levels(body)
    if lv is None:
        return []
    head, rest = lv[0], lv[1:-1]
    got = _period(rest)
    if got is None:
        return []
    q, p = got
    try:
        M = sp.eye(2)
        for L in rest[q:q + p]:
            M = M * _matrix(L)
        g = sp.Symbol('_g')
        # the periodic tail is the FIXED POINT of the composite Moebius map
        eq = sp.expand((M[1, 0] * g + M[1, 1]) * g - (M[0, 0] * g + M[0, 1]))
        roots = sp.solve(sp.Poly(eq, g), g)
        pre = sp.eye(2)
        for L in [head] + rest[:q]:
            pre = pre * _matrix(L)
        out = []
        for r in roots:
            v = sp.together((pre[0, 0] * r + pre[0, 1]) / (pre[1, 0] * r + pre[1, 1]))
            if not (v.free_symbols - {x}):
                out.append(v)
        return out
    except Exception:
        return []


def read(e):
    """the entry's g.f. as a quadratic surd, verified against its published terms, or None"""
    import algf
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    for L in e['formula'] + e['comment']:
        t = ' '.join(L.split())
        if 'continued fraction' not in t.lower():
            continue
        if algf.CONJ.search(t) or KINDEX.search(t):
            continue
        m = LEAD.match(t)
        if not m:
            continue
        body = NOISE.sub('', BRACKET_ATTR.sub('', ATTR.sub('', t[m.end():]))).strip()
        body = NAMED.sub('', body).strip()
        if re.search(r'A\d{6}|Sum_|Prod_|Integral|hypergeom', body, re.I):
            continue
        for A in candidates(body):
            A = algf._normalize(A, d, off)
            if algf._series_ok(A, d, off):
                return A
    return None
