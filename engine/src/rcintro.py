#!/usr/bin/env python3
"""Arrays whose new values are introduced in order along every row AND every column.

    Number of n X 4 0..2 arrays with new values introduced in each row and column in
      sequential order starting with zero.
    Number of n X 4 nonnegative integer arrays with new values introduced in each row and
      column in sequential order starting with zero.

The ROW condition is a property of one row: reading it left to right, a value may appear only
when every smaller one already has. So the admissible rows are a fixed finite set, computed
once.

The COLUMN condition is not a property of any window, and does not need to be: the values arrive
in order, so all the state a column needs is HOW MANY values have been introduced in it so far.
The vertex is therefore one counter per column, the width being fixed, and adding a row r asks
only that r_j not exceed the j-th counter, incrementing it when it equals it.

The alphabet needs no bound in the second form. A row of width k has at most k distinct values
and its own introduction order forces r_j <= j, so no entry of the array can exceed k-1 however
"nonnegative integer" is read; the two forms differ only in where the alphabet cap bites.
"""
import re
from itertools import product

NAME = re.compile(
    r'(?i)^Number of n\s*X\s*(\d+) (?:0\.\.(\d+)|nonnegative integer) arrays with new values '
    r'introduced in each row and column in sequential order starting with zero\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\d(])', ' X ', nm)
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    k = int(m.group(1))
    A = int(m.group(2)) if m.group(2) is not None else k - 1
    if k < 1 or k > 9 or A < 0:
        return None
    A = min(A, k - 1)                      # a row of width k introduces at most k values
    return {'engine': 'rcintro', 'k': k, 'A': A, 'frac': 1}


def _rows(k, A):
    out = []
    for r in product(range(A + 1), repeat=k):
        u = 0
        ok = True
        for v in r:
            if v > u:
                ok = False
                break
            if v == u:
                u += 1
        if ok:
            out.append(r)
    return out


def build(p, cap=2000000):
    k, A = p['k'], p['A']
    rows = _rows(k, A)
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    s0 = sid((0,) * k)
    adj = {}
    i = 0
    while i < len(states):
        c = states[i]
        out = []
        for r in rows:
            nc = []
            ok = True
            for j in range(k):
                if r[j] > c[j]:
                    ok = False
                    break
                nc.append(c[j] + 1 if r[j] == c[j] else c[j])
            if ok:
                out.append(sid(tuple(nc)))
        adj[i] = out
        i += 1
        if len(states) > cap:
            return None
    import lumpauto
    st = [0] * len(states)
    st[s0] = 1
    wadj, wstart, wend, S = lumpauto.lump(adj, st, [1] * len(states))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(states), 'rows': len(rows)}


def terms(b, N):
    """out[n] counts the n X k arrays; out[0] = 1 is the empty array."""
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    out = [sum(v * e for v, e in zip(vec, ev))]
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
