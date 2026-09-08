#!/usr/bin/env python3
"""Rows of an elementary cellular automaton, read as numbers.

    Binary representation of the n-th iteration of the "Rule 175" elementary cellular
    automaton starting with a single ON (black) cell.
    Decimal representation of the n-th iteration of the "Rule 155" elementary cellular
    automaton starting with a single ON (black) cell.

The row at step n is the light cone |x| <= n, so a word of length 2n+1. "Binary
representation" reads that word as a DECIMAL number whose digits are its bits; "decimal
representation" reads it as a binary number. Both are the value of the word in a base.

Two things have to be right before any of this is a proof.

**The background.** Outside the cone the cells never met the initial one, so they follow the
orbit of the all-zero configuration, which for a rule with 000 -> 1 is not zero. Simulating on
a padded array with too little padding lets that background travel inward at one cell per step
and corrupt the cone: rule 175's row came out as 110111111111110 at step 7 instead of
110111111111111, and only the tail was wrong, which is exactly the kind of error that survives
a check of the first few terms. The padding here exceeds the number of steps, so no background
cell can reach the cone.

**The shape.** For 51 of these rules the row settles into

    w(n+p) = L + w(n) + R

with L and R fixed words and |L| + |R| = 2p, and then the value satisfies an exact linear
recurrence. The identity is not assumed from a few terms: the cellular automaton is a local
map, so once it holds at two consecutive n past the settling point -- which fixes every 3-cell
window at both boundaries -- it holds at every later n by induction. `certify` below reports
the settling point and how far the identity was checked beyond it.
"""
import re

HEAD = re.compile(
    r'^\s*(Binary|Decimal) representation of the n-th iteration of the '
    r'"Rule (\d+)" elementary cellular automaton starting with a single ON \(black\) cell'
    r'\s*\.?\s*$', re.I)


def rows(rule, steps):
    """the light-cone rows w(0..steps) as strings of length 1, 3, 5, ..."""
    pad = steps + 2
    W = 2 * (steps + pad) + 1
    C = W // 2
    row = [0] * W
    row[C] = 1
    out = []
    for n in range(steps + 1):
        out.append(''.join(map(str, row[C - n:C + n + 1])))
        nxt = [0] * W
        for i in range(1, W - 1):
            nxt[i] = (rule >> ((row[i - 1] << 2) | (row[i] << 1) | row[i + 1])) & 1
        row = nxt
    return out


def shape(ws):
    """(n0, p, L, R) with w(n+p) = L + w(n) + R for every n >= n0, or None"""
    for p in range(1, 9):
        for n0 in range(1, 16):
            if n0 + 2 * p + 6 >= len(ws):
                continue
            a, b = ws[n0], ws[n0 + p]
            if len(b) != len(a) + 2 * p:
                continue
            for cut in range(2 * p + 1):
                if b[cut:cut + len(a)] != a:
                    continue
                L, R = b[:cut], b[cut + len(a):]
                if all(ws[n + p] == L + ws[n] + R for n in range(n0, len(ws) - p)):
                    return n0, p, L, R
    return None


def parse_name(nm):
    m = HEAD.match(re.sub(r'\s+', ' ', nm).strip())
    if not m:
        return None
    rule = int(m.group(2))
    if not 0 <= rule <= 255:
        return None
    return {'rule': rule, 'base': 10 if m.group(1).lower() == 'binary' else 2, 'frac': 1}


def build(p, cap=200000):
    ws = rows(p['rule'], 46)
    s = shape(ws)
    if s is None:
        return None
    n0, per, L, R = s
    # the annihilator of a(n): the shape gives a(n+p) = a(n)*B^|R| + val(L)*B^(2n+1+|R|)
    # + val(R), so (S^p - B^|R|) kills the first term and leaves a geometric B^(2n) and a
    # constant, which (S - B^2)(S - 1) kills in turn
    return {'rule': p['rule'], 'B': p['base'], 'n0': n0, 'p': per, 'L': L, 'R': R,
            'ws': ws, 'S': per + 2}


def terms(b, N):
    """a(n) = the row at step n read in base B, for n = 0, 1, 2, ..."""
    B = b['B']
    ws = b['ws'] if N < len(b['ws']) else rows(b['rule'], N + 1)
    out = []
    for n in range(N + 1):
        v = 0
        for ch in ws[n]:
            v = v * B + (1 if ch == '1' else 0)
        out.append(v)
    return out


def certify(b, upto=46):
    """how far past the settling point the shape identity was checked"""
    ws = rows(b['rule'], upto)
    n0, p, L, R = b['n0'], b['p'], b['L'], b['R']
    k = 0
    for n in range(n0, len(ws) - p):
        if ws[n + p] != L + ws[n] + R:
            break
        k += 1
    return k


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    last, run = None, 0
    # The scan must start at j = order, the FIRST index at which the recurrence can be
    # evaluated. Starting at order+1 skipped that index, so a recurrence the entry itself
    # claims only "for n > 2" was reported as holding from the start -- and the sweep then
    # tested index 2, found it false, and called the entry's conjecture contradicted. Six
    # entries were flagged that way and every one was this off-by-one, not a false conjecture.
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
