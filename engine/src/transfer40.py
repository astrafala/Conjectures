#!/usr/bin/env python3
"""Subblock statistics compared with the NEIGHBOURING subblocks, including `equal to SOME'.

Name shapes, for an $(n+K-1)\\times W$ array over $\\{0,\\dots,m\\}$ and $K\\in\\{2,3\\}$:

    every K X K subblock <stat> equal to some horizontal or vertical neighbor K X K subblock
        <stat>
    every K X K subblock <stat> equal to exactly one or two horizontal and vertical neighbor
        K X K subblock <stat>s
    no K X K subblock <stat> equal to any horizontal or vertical neighbor K X K subblock <stat>
    no K X K subblock sum differing from a horizontal or vertical neighbor subblock sum by more
        than <d>

with `diagonal or antidiagonal' available in place of `horizontal or vertical', and the
statistics trace, determinant, permanent, sum, and `diagonal sum less antidiagonal sum'.

`No ... equal to any' and the bounded-difference form are conditions on a PAIR of neighbouring
subblocks, so K consecutive array rows are a state and nothing else is needed. `Equal to some'
and `equal to exactly one or two' are not: a subblock's condition cannot be settled until the
row BELOW it exists. The state therefore carries, besides the K rows, a tally per subblock of
the row just completed --- for `some' a single bit saying whether it has already been matched,
for `exactly one or two' a count capped at three, three being already too many. A step adds the
matches with the new subblock row, requires the old row's tallies to be acceptable, and starts
the new row's tallies from its own horizontal matches. A state is accepting when its own
tallies are already acceptable, which is what makes the LAST subblock row come out right.
"""
import re
from itertools import product

import namecanon
import transfer19

FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
SHAPE = re.compile(r'\(\s*n\s*\+\s*(\d+)\s*\)\s*X\s*(\d+)\s+(?:0\.\.(\d+)|(binary))\s+arrays'
                   r'\s+with\s+', re.I)
STATW = r'(trace|determinant|permanent|sum|diagonal sum less antidiagonal sum)'
NB = r'(horizontal or vertical|horizontal and vertical|diagonal or antidiagonal)'
BLK = r'(\d)\s*X\s*\4'

SOME = re.compile(r'(?:every|each) (\d)\s*X\s*\1 subblock ' + STATW + r' equal to some ' + NB +
                  r' neighbor \d\s*X\s*\d subblock ' + STATW + r'\s*\.?\s*$', re.I)
NONE = re.compile(r'no (\d)\s*X\s*\1 subblock (?:having a )?' + STATW + r' equal to any ' + NB +
                  r' neighbor \d\s*X\s*\d subblock ' + STATW + r'\s*\.?\s*$', re.I)
CNT = re.compile(r'(?:every|each) (\d)\s*X\s*\1 subblock ' + STATW + r' equal to exactly one '
                 r'or two ' + NB + r' neighbor \d\s*X\s*\d subblock ' + STATW +
                 r's?\s*\.?\s*$', re.I)
MAXD = re.compile(r'no (\d)\s*X\s*\1 subblock (sum) differing from a ' + NB +
                  r' neighbor subblock sum by more than (\w+)\s*\.?\s*$', re.I)

NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
OFF = {'horizontal or vertical': [(0, 1), (1, 0)],
       'horizontal and vertical': [(0, 1), (1, 0)],
       'diagonal or antidiagonal': [(1, 1), (1, -1)]}


def parse_name(nm):
    nm = namecanon.canon(nm)
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    frac = 1
    m = FRAC.match(norm)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        norm = norm[m.end():]
    else:
        m = HEAD.match(norm)
        if not m:
            return None
        norm = norm[m.end():]
    m = SHAPE.match(norm)
    if not m:
        return None
    d, W = int(m.group(1)), int(m.group(2))
    alpha = 1 if m.group(4) else int(m.group(3))
    body = norm[m.end():]
    for rx, kind in ((SOME, 'some'), (CNT, 'count'), (NONE, 'none'), (MAXD, 'maxdiff')):
        c = rx.match(body)
        if not c:
            continue
        K = int(c.group(1))
        if d < K - 1 or K not in (2, 3) or W < K or alpha < 1:
            return None
        stat = c.group(2).lower()
        if kind == 'maxdiff':
            lim = c.group(4).lower()
            lim = int(lim) if lim.isdigit() else NUM.get(lim)
            if lim is None:
                return None
        else:
            if c.group(4).lower().rstrip('s') != stat:
                return None
            lim = None
        return {'K': K, 'W': W, 'alpha': alpha, 'kind': kind, 'stat': stat,
                'nb': c.group(3).lower(), 'lim': lim, 'frac': frac}
    return None


def _stat(name, B, K):
    if name == 'trace':
        return sum(B[i][i] for i in range(K))
    if name == 'sum':
        return sum(sum(r) for r in B)
    if name == 'diagonal sum less antidiagonal sum':
        return sum(B[i][i] for i in range(K)) - sum(B[i][K - 1 - i] for i in range(K))
    if K == 2:
        p, q, r, s = B[0][0], B[0][1], B[1][0], B[1][1]
        return p * s - q * r if name == 'determinant' else p * s + q * r
    tot = 0
    for perm in ((0, 1, 2), (1, 2, 0), (2, 0, 1), (0, 2, 1), (2, 1, 0), (1, 0, 2)):
        sgn = 1 if perm in ((0, 1, 2), (1, 2, 0), (2, 0, 1)) else -1
        pr = B[0][perm[0]] * B[1][perm[1]] * B[2][perm[2]]
        tot += pr if (name == 'permanent' or sgn > 0) else -pr
    return tot


def build(p, cap=40000):
    K, W, A, kind = p['K'], p['W'], p['alpha'] + 1, p['kind']
    if A ** (K * W) > 8 * cap:
        return None
    nb = W - K + 1
    hor = [dj for (di, dj) in OFF[p['nb']] if di == 0]
    ver = [dj for (di, dj) in OFF[p['nb']] if di == 1]
    rows = list(product(range(A), repeat=W))

    def vals(t):
        return tuple(_stat(p['stat'], [[t[i][j + c] for c in range(K)] for i in range(K)], K)
                     for j in range(nb))

    flagged = kind in ('some', 'count')
    cap3 = 3

    def selftally(v):
        out = []
        for j in range(nb):
            c = 0
            for dj in hor:
                for s in (dj, -dj):
                    k = j + s
                    if 0 <= k < nb and v[j] == v[k]:
                        c += 1
            out.append(min(c, cap3))
        return tuple(out)

    def selfok(v):
        for j in range(nb):
            for dj in hor:
                for s in (dj, -dj):
                    k = j + s
                    if 0 <= k < nb:
                        if kind == 'none' and v[j] == v[k]:
                            return False
                        if kind == 'maxdiff' and abs(v[j] - v[k]) > p['lim']:
                            return False
        return True

    base, index, states = [], {}, []

    def sid(s):
        i = index.get(s)
        if i is None:
            i = index[s] = len(states)
            states.append(s)
        return i

    tup = list(product(rows, repeat=K))
    vv = {}
    seeds = []
    for t in tup:
        v = vals(t)
        if not flagged and not selfok(v):
            continue
        vv[t] = v
        seeds.append(t)
        if len(seeds) > 8 * cap:
            return None
    for t in seeds:
        sid((t, selftally(vv[t])) if flagged else t)
        if len(states) > cap:
            return None
    bysuffix = {}
    for t in seeds:
        bysuffix.setdefault(t[:K - 1], []).append(t)
    adj = [None] * len(states)
    qi = 0
    while qi < len(states):
        st = states[qi]
        t, f = st if flagged else (st, None)
        v = vv[t]
        row = []
        for u in bysuffix.get(t[1:], ()):
            w = vv[u]
            match = [0] * nb
            good = True
            for j in range(nb):
                for dj in ver:
                    k = j + dj
                    if 0 <= k < nb:
                        eq = (v[j] == w[k])
                        if kind == 'none' and eq:
                            good = False
                        if kind == 'maxdiff' and abs(v[j] - w[k]) > p['lim']:
                            good = False
                        if eq:
                            match[j] += 1
                    k2 = j - dj
                    if 0 <= k2 < nb and dj:
                        pass
            if not good:
                continue
            if not flagged:
                row.append(sid(u))
                continue
            # the old row is finalised now; the new row starts from its own horizontal tally
            ok = True
            newf = list(selftally(w))
            for j in range(nb):
                tot = min(f[j] + match[j], cap3)
                if kind == 'some' and tot == 0:
                    ok = False
                    break
                if kind == 'count' and tot not in (1, 2):
                    ok = False
                    break
                # the match is mutual: it also counts for the subblock below
                for dj in ver:
                    k = j + dj
                    if 0 <= k < nb and v[j] == w[k]:
                        newf[k] = min(newf[k] + 1, cap3)
            if not ok:
                continue
            row.append(sid((u, tuple(newf))))
            if len(states) > cap:
                return None
        adj[qi] = row
        qi += 1
        while len(adj) < len(states):
            adj.append(None)
    S = len(states)
    # only the states whose tally came from their own row may BEGIN an array: a state built
    # during the walk carries a match with the row above it, which the first row cannot have
    start = [0] * S
    for t in seeds:
        start[index[(t, selftally(vv[t])) if flagged else t]] = 1
    if flagged:
        end = [1 if all((x > 0) if kind == 'some' else (x in (1, 2)) for x in s[1]) else 0
               for s in states]
    else:
        end = [1] * S
    return adj, start, end, S


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
