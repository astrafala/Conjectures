#!/usr/bin/env python3
"""Binary arrays whose w-bit windows, read as numbers, do not decrease along a row or a column.

    Number of (n+2) X 9 binary arrays with consecutive windows of three bits considered as a
      binary number nondecreasing in every row and column.

The width W is fixed and the height grows, so rows are the natural direction of the walk. Two
conditions apply. Along a ROW the W-w+1 windows of w consecutive bits, read as binary numbers,
must not decrease left to right: that is a property of the row alone and it is extremely
restrictive -- of the 512 binary rows of width 9, only 14 survive it for w = 3 and 21 for
w = 4. Down a COLUMN the same must hold of the vertical windows, and a vertical window spans w
rows, so comparing two consecutive ones needs w+1 rows; the state is therefore the last w rows,
each of them one of that handful.

The entry's height is n + w - 1, which is why the name reads (n+1), (n+2), (n+3) as the window
widens: the array must be at least w tall to have a vertical window at all.
"""
import re
from itertools import product

WORD = {'two': 2, 'three': 3, 'four': 4, 'five': 5}

NAME = re.compile(
    r'(?i)^Number of \(n\s*\+\s*(\d+)\)\s*X\s*(\d+) binary arrays with consecutive windows of '
    r'(two|three|four|five) bits considered as a binary number nondecreasing in every row and '
    r'column\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\d(])', ' X ', nm)
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    off, W, w = int(m.group(1)), int(m.group(2)), WORD[m.group(3).lower()]
    # the height is n + w - 1 and the name says n + off, so the two must agree; a name where
    # they do not is not this shape and guessing which is right would be inventing the entry
    if off != w - 1 or W < w or W > 12 or w > 5:
        return None
    return {'engine': 'binwin', 'W': W, 'w': w, 'frac': 1}


def _val(bits):
    v = 0
    for b in bits:
        v = v * 2 + b
    return v


def _rowok(r, w):
    vals = [_val(r[i:i + w]) for i in range(len(r) - w + 1)]
    return all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))


def build(p, cap=2000000):
    W, w = p['W'], p['w']
    rows = [r for r in product((0, 1), repeat=W) if _rowok(r, w)]
    if not rows:
        return None
    R = len(rows)
    # a state is the last w rows; only those already consistent down every column are kept
    def colok(block):
        """block is w+1 rows: check the two vertical windows of every column"""
        for j in range(W):
            a = _val([block[t][j] for t in range(w)])
            b = _val([block[t + 1][j] for t in range(w)])
            if a > b:
                return False
        return True

    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    # the first w rows are unconstrained beyond the row condition: no vertical window closes
    # before row w, so every w-tuple of admissible rows is a start
    start = [sid(t) for t in product(range(R), repeat=w)]
    if len(start) > cap:
        return None
    adj = {}
    i = 0
    while i < len(states):
        s = states[i]
        out = []
        for k in range(R):
            blk = [rows[t] for t in s] + [rows[k]]
            if colok(blk):
                out.append(sid(s[1:] + (k,)))
        adj[i] = out
        i += 1
        if len(states) > cap:
            return None
    import lumpauto
    stv = [0] * len(states)
    for j in start:
        stv[j] = 1
    wadj, wstart, wend, S = lumpauto.lump(adj, stv, [1] * len(states))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(states), 'rows': R, 'w': w}


def terms(b, N):
    """out[n] counts the arrays of height w-1+n: the start already holds w rows, so out[1]
    is the height-w array and the entry's a(1) is out[1]."""
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    out = [0, sum(v * e for v, e in zip(vec, ev))]
    for _ in range(N + 1):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v * e for v, e in zip(vec, ev)))
    return out


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
