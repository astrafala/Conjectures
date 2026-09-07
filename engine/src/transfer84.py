#!/usr/bin/env python3
"""Arrays in which no column dominates the one before it in every row.

    Number of n X 3 0..2 arrays with no column j greater than column j-1 in all rows.
    Number of n X 4 0..3 arrays with no column j greater than or equal to than column j-1
        in all rows.
    Number of n X 3 arrays with rows being permutations of 0..2 and no column j greater than
        column j-1 in all rows.

The condition is not local in the rows --- "in all rows" quantifies over the whole array ---
but it is a conjunction of independent per-row facts, and that is what makes it a walk. For
each of the L-1 adjacent column pairs, keep one bit: has every row so far had column j above
column j-1? Adding a row can only clear bits, never set them, and the array is admissible
exactly when every bit has been cleared by the end. So the state is that bit mask and nothing
else: at most 2^(L-1) vertices however large the alphabet is.

Rows with the same bit pattern behave identically, so the digraph carries one edge per row
and the multiplicity does the counting.
"""
import re
from itertools import permutations, product

import lumpauto
import namecanon
import transfer19

HEAD = re.compile(
    r'^(?:Number of|number of)\s+(.+?)\s+'
    r'(?:(binary|0\.\.(\d+))\s+)?arrays\s+with\s+(.+?)\s*\.?\s*$', re.I)
PERM = re.compile(r'^rows being permutations of 0\.\.(\d+) and (.+)$', re.I)
COND = re.compile(r'^no column j greater than (?:or equal to (?:than )?)?column j-1 '
                  r'in all rows$', re.I)
GE = re.compile(r'greater than or equal to', re.I)
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X \(?(\d+)\)?$', re.I), 'rows'),
    (re.compile(r'^n X \(?(\d+)\)?$', re.I), 'rows0'),
]


def _shape(s):
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        return (int(m.group(2)), int(m.group(1))) if kind == 'rows' else (int(m.group(1)), 0)
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    sh = _shape(m.group(1).strip())
    if sh is None:
        return None
    L, a = sh
    cond = m.group(4).strip()
    perm = False
    k = None
    g = PERM.match(cond)
    if g:
        perm = True
        k = int(g.group(1)) + 1
        cond = g.group(2).strip()
    if not COND.match(cond):
        return None
    if k is None:
        if m.group(2) is None:
            return None
        k = 2 if m.group(2).lower() == 'binary' else int(m.group(3)) + 1
    if perm and k != L:
        return None                     # a permutation of 0..k-1 has to fill the row
    if not 2 <= L <= 7 or not 2 <= k <= 7:
        return None
    return {'L': L, 'a': a, 'k': k, 'perm': perm, 'strict': not GE.search(nm), 'frac': 1}


def build(p, cap=200000):
    L, k = p['L'], p['k']
    rows = permutations(range(k)) if p['perm'] else product(range(k), repeat=L)
    full = (1 << (L - 1)) - 1
    # how many rows realise each pattern of "column j sits above column j-1"
    tally = {}
    for r in rows:
        b = 0
        for j in range(1, L):
            if (r[j] > r[j - 1]) if p['strict'] else (r[j] >= r[j - 1]):
                b |= 1 << (j - 1)
        tally[b] = tally.get(b, 0) + 1
    if not tally:
        return None
    masks = sorted({full & b for b in tally} | {full})
    reach, frontier = set(), [full]
    while frontier:
        u = frontier.pop()
        if u in reach:
            continue
        reach.add(u)
        for b in tally:
            v = u & b
            if v not in reach:
                frontier.append(v)
    states = sorted(reach)
    index = {s: i for i, s in enumerate(states)}
    S = len(states)
    if S > cap:
        return None
    adj = [[] for _ in range(S)]
    start = [0] * S
    for b, n in tally.items():                 # the first row starts the mask off
        adj_from = full & b
        start[index[adj_from]] += n
    for u in states:
        for b, n in tally.items():
            adj[index[u]] += [index[u & b]] * n
    end = [1 if s == 0 else 0 for s in states]
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
