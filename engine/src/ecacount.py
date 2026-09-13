#!/usr/bin/env python3
"""ON and OFF cell counts of an elementary cellular automaton.

    Number of ON (black) cells in the n-th iteration of the "Rule 7" elementary cellular
      automaton starting with a single ON (black) cell.
    Total number of OFF (white) cells after n iterations of the "Rule 1" ...

`ecarow' already models the ROW of an elementary automaton and derives the shape

    w(n+p) = L + w(n) + R

for every n past a settling point n0, verified over every available step. Nothing about that
certificate is specific to reading the row as a numeral. Counting its ON cells uses the same
identity and gives a shorter recurrence:

    on(n+p) = on(n) + ones(L) + ones(R),

so `on' is annihilated by (z^p - 1)(z - 1). The row at step n is the light cone, of width
2n+1, so off(n) = 2n + 1 - on(n) and (z-1)^2 kills the width; a running total adds one more
(z-1). The pre-period raises the numerator's degree, exactly as it does for the row, so
S = p + 4 + n0 covers all four wordings.

87 entries carry these four names and no engine read any of them: the row engine wanted the
word "representation" on the line. That is the same silent refusal this project keeps paying
for -- machinery already built, hidden by how a sweep chose what to look at.
"""
import re

import ecarow

HEAD = re.compile(
    r'^\s*(Total number|Number) of (ON \(black\)|OFF \(white\)) cells '
    r'(?:in the n-th iteration|after n iterations) of the '
    r'"Rule (\d+)" elementary cellular automaton starting with a single ON \(black\) cell'
    r'\s*\.?\s*$', re.I)


def parse_name(nm):
    m = HEAD.match(re.sub(r'\s+', ' ', nm).strip())
    if not m:
        return None
    rule = int(m.group(3))
    if not 0 <= rule <= 255:
        return None
    return {'rule': rule, 'on': m.group(2).lower().startswith('on'),
            'total': m.group(1).lower().startswith('total'), 'frac': 1}


def build(p, cap=200000):
    ws = ecarow.rows(p['rule'], 80)
    s = ecarow.shape(ws)
    if s is None:
        return None
    n0, per, L, R = s
    return {'rule': p['rule'], 'n0': n0, 'p': per, 'L': L, 'R': R, 'ws': ws,
            'on': p['on'], 'total': p['total'], 'S': per + 4 + n0}


def terms(b, N):
    """a(n) for n = 0, 1, 2, ... -- the entry's own index."""
    ws = b['ws'] if N < len(b['ws']) else ecarow.rows(b['rule'], N + 1)
    out, run = [], 0
    for n in range(N + 1):
        w = ws[n]
        v = w.count('1') if b['on'] else w.count('0')
        run += v
        out.append(run if b['total'] else v)
    return out


def certify(b, upto=80):
    return ecarow.certify(b, upto)


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    last, run = None, 0
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
