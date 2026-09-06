#!/usr/bin/env python3
"""A row-major clause on an array that is walked across its COLUMNS.

    Number of R X n 0..m arrays with no element x(i,j) adjacent to value m-x(i,j)
    <directions>, top left element zero, and 1 appearing before 2 3 and 4, and 2 appearing
    before 3 in row major order.

The forbidden-pair condition is settled between two consecutive columns, so the walk runs left
to right and the state is one column.  The clause is the difficulty.  It speaks of ROW MAJOR
order, and a walk across columns does not visit the cells in row major order, so the running
"values seen so far" that works for an `n X W' entry is simply the wrong set here.  That is why
`transfer47' refuses this shape outright.

What is true is that the row major position of the FIRST occurrence of a value v is decided by
two numbers: the least row r_v in which v occurs anywhere, and then the least column c_v in
which v occurs in that row.  Comparing two values is comparing (r_v, c_v) lexicographically.
So the walk carries, for each value the clause names, the smallest row in which it has been
seen so far, together with the order in which those smallest rows were attained --- and nothing
else.  Two values sharing a smallest row cannot have attained it in the same column, since that
would put both of them in one cell, so the attainment order breaks every tie the rows leave.

One thing does not work here and must not be attempted: pruning during the walk.  A value's
smallest row can DROP at any later column, which reorders the first occurrences retroactively,
so the clause is a property of the finished array and is tested in the ACCEPTING states, never
along the way.

The state is therefore (last column, ordered set partition of the named values by smallest
row).  It is built by reachability from the legal first columns, so only the partitions the
condition actually produces are ever materialised.
"""
import re
from itertools import product

import namecanon
import transfer19
import lumpauto

CLASS = {'horizontal': [(0, 1)], 'vertical': [(1, 0)],
         'diagonal': [(1, 1)], 'antidiagonal': [(1, -1)]}
_W1 = r'(?:horizontal|vertical|diagonal|antidiagonal)(?:ly)?'
NBSET = r'(' + _W1 + r'(?:[, ]+(?:or |and )?' + _W1 + r')*)'
NAME = re.compile(
    r'^Number of\s+(\d+)\s*X\s*n\s+0\.\.(\d+)\s+arrays with no element x\(i,j\) adjacent to '
    r'value\s+(\d+)\s*-\s*x\(i,j\)\s+' + NBSET + r'\s*,\s*(.*?)\s*\.?\s*$', re.I)
PREC = re.compile(r'(\d+)\s+appearing before\s+((?:\d+[\s,]*(?:and\s+)?)+?)\s*'
                  r'(?=,|\bin row major\b|$)', re.I)
TL = re.compile(r'top left element zero', re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.match(nm)
    if not m:
        return None
    R, alpha = int(m.group(1)), int(m.group(2))
    if int(m.group(3)) != alpha or R < 1 or alpha < 1:
        return None
    D = []
    for w in re.findall(_W1, m.group(4).lower()):
        D += CLASS[re.sub(r'ly$', '', w)]
    D = sorted(set(D))
    rest = m.group(5)
    if not TL.search(rest) or 'row major order' not in rest.lower():
        return None
    prec = []
    for g in PREC.finditer(rest):
        lo = int(g.group(1))
        for hi in re.findall(r'\d+', g.group(2)):
            prec.append((lo, int(hi)))
    if not prec or any(not (0 <= v <= alpha) for pr in prec for v in pr):
        return None
    return {'R': R, 'alpha': alpha, 'dirs': D, 'prec': sorted(set(prec)), 'frac': 1}


def _order(part, k):
    """the named values in row major order of first occurrence; buckets low row first."""
    out = []
    for b in part:
        out.extend(b)
    return out


def _accepts(part, prec, tracked):
    pos = {}
    for v in _order(part, len(tracked)):
        pos[v] = len(pos)
    for lo, hi in prec:
        if hi in pos and (lo not in pos or pos[lo] > pos[hi]):
            return False
    return True


def build(p, cap=200000):
    R, A, m = p['R'], p['alpha'] + 1, p['alpha']
    D = [tuple(t) for t in p['dirs']]
    if A ** R > 200000:
        return None
    inside = [di for di, dj in D if dj == 0]      # pairs inside one column
    # An offset reaching into the PREVIOUS column names the same pair as its negation reaching
    # into the next one: (di,-1) on the cell (i,j) is (-di,+1) on the cell it points at. Both
    # have to be normalised to the +1 side before c and e can be read as consecutive columns.
    # Without that, `antidiagonally' is silently tested as `diagonally'.
    across = [(di if dj > 0 else -di) for di, dj in D if dj != 0]
    cols = [c for c in product(range(A), repeat=R)
            if all(c[i] + c[i + di] != m
                   for di in inside for i in range(R) if 0 <= i + di < R)]
    if not cols:
        return None
    tracked = sorted({v for pr in p['prec'] for v in pr})

    def ok_across(c, e):
        """c then e as consecutive columns."""
        for i in range(R):
            for di in across:
                x = i + di
                if 0 <= x < R and c[i] + e[x] == m:
                    return False
        return True

    def advance(part, col):
        """part is a tuple of R tuples, bucket r holding the values whose least row is r."""
        where = {}
        for r, b in enumerate(part):
            for v in b:
                where[v] = r
        newpart = [list(b) for b in part]
        for i in range(R):                       # a smaller row is seen first
            v = col[i]
            if v in tracked and where.get(v, R + 1) > i:
                if v in where:
                    newpart[where[v]].remove(v)
                newpart[i].append(v)
                where[v] = i
        return tuple(tuple(b) for b in newpart)

    empty = tuple(() for _ in range(R))
    start_states, index, states, adj = [], {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    frontier = []
    for ci, c in enumerate(cols):
        if c[0] != 0:                            # top left element zero
            continue
        s = (ci, advance(empty, c))
        i = sid(s)
        start_states.append(i)
        frontier.append(i)
    if not states:
        return None
    seen = set(frontier)
    while frontier:
        u = frontier.pop()
        ci, part = states[u]
        c = cols[ci]
        for ei, e in enumerate(cols):
            if not ok_across(c, e):
                continue
            v = sid((ei, advance(part, e)))
            if len(states) > cap:
                return None
            adj[u].append(v)
            if v not in seen:
                seen.add(v)
                frontier.append(v)
    S = len(states)
    start = [0] * S
    for i in set(start_states):
        start[i] = 1
    # the clause is a property of the FINISHED array: a value's least row can still drop, so it
    # is tested here and never along the walk
    end = [1 if _accepts(part, p['prec'], tracked) else 0 for _, part in states]
    # states with the same future are merged. The bookkeeping a state carries for the clause
    # stops mattering once the rows it names are settled, so the reduction is large, and the
    # annihilation test's length is governed by the state count.
    return lumpauto.lump(adj, start, end)


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
