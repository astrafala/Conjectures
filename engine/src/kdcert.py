#!/usr/bin/env python3
"""A finite certificate that the knight-distance field on a strip is exactly period-4.

`transfer88` was written for this family and then deliberately left out of service, with the
reason recorded in its own docstring: the transfer matrix needs

    d(i+4, j) = d(i, j) + 2                                                   (P)

for every column once i is large enough, and `<=` is immediate --- the moves (2,1) then
(2,-1) drop four rows and return to the same column --- while `>=` had only been checked over
a few hundred rows. A finite check of an infinite claim is evidence, not a proof, so nothing
was shipped. This module removes that obstruction.

The device is the pair of Bellman conditions. Let the strip be
S_C = {(i, j) : i >= 0, 0 <= j < C} with the knight graph on it, and let D be ANY function
S_C -> N u {oo}. If

    (a) D(0,0) = 0,
    (b) D(y) <= D(x) + 1 for every knight-adjacent pair x, y,
    (c) every x != (0,0) with D(x) < oo has a knight neighbour y with D(x) = D(y) + 1,

then D is the knight distance from (0,0). Both halves are one induction. (b) with (a) gives
D(x) <= d(x) by induction on d(x): a shortest path's last step is an edge. (c) gives
D(x) >= d(x) by induction on D(x), which is legitimate because (c) forces D(x) >= 1 for
x != (0,0), so D(x) = 0 happens only at the corner. Neither induction cares where D came
from, which is the point: a guessed field that passes (a), (b), (c) IS the distance.

So take the field measured on a tall board over the first few rows, DEFINE it on the whole
strip by declaring (P), and check (a), (b), (c). Conditions (b) and (c) at row i involve only
rows i-2 .. i+2; once all five of those rows lie in the region where the definition reads
D(r, j) = D(r-4, j) + 2, the condition at row i is the condition at row i-4 with 2 added to
both sides, hence the same condition. Finitely many rows therefore settle every row, and (P)
is proved rather than observed.

The same certificate settles the second thing the model needs, which is that one field serves
every board height. The entries count arrays on a board of exactly n+2 rows, and the distance
on a short board is NOT the distance on the strip: on a 3 X 3 board the centre is unreachable
while on the strip it is at distance 4. What decides it is whether a cell has a chain of
minimum-path predecessors that never needs a row the short board does not have. Write

    rho(x) = the least number of rows a board must have for x to be at distance d(x) on it,

computed by rho(0,0) = 1 and, over the minimum-path predecessors y of x,

    rho(x) = min_y max(row(x) + 1, row(y) + 1, rho(y)).

Then d_H = d on rows 0..H-1 exactly when H >= rho(x) for every x in those rows, and
rho(x) - row(x) is period-4 for the same reason the field is, so the threshold H0 beyond
which one field serves every height is a finite computation too. Below H0 -- which is 5, 5, 6,
6, 7, 8, 9 for widths 3..9 -- each board is counted on its own field, and there is nothing to
prove about a finite board.
"""
import re

KN = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
PERIOD = 4
RISE = 2                                   # d(i+4, j) - d(i, j), the (P) of the docstring
INF = float('inf')


def _bfs(R, C):
    """knight distance from (0,0) on a board of exactly R rows and C columns"""
    D = [[INF] * C for _ in range(R)]
    D[0][0] = 0
    q, k = [(0, 0)], 0
    while q:
        nq = []
        for (i, j) in q:
            for di, dj in KN:
                a, b = i + di, j + dj
                if 0 <= a < R and 0 <= b < C and D[a][b] == INF:
                    D[a][b] = D[i][j] + 1
                    nq.append((a, b))
        q = nq
        k += 1
    return D


def certify(C, R=600, window=12):
    """The certificate for width C, or None if the field is not period-4 from any row.

    Returns i0 (the first row of the periodic region), the table of rows 0..i0+2*PERIOD-1
    that the period generates the rest from, H0 (the first board height whose own field is
    the strip's), and the number of (b) and (c) checks that were carried out.
    """
    if C < 3:
        return None
    R = max(R, 40 * C)
    T = _bfs(R, C)
    top = R - 16                           # rows near the bottom edge of the scratch board
                                           # are not the strip's, so they are never read

    i0 = None
    for i in range(1, top - 5 * PERIOD - window):
        if all(T[r + PERIOD][j] == T[r][j] + RISE
               for r in range(i, i + window) for j in range(C)):
            i0 = i
            break
    if i0 is None:
        return None

    lim = i0 + 2 * PERIOD                  # the table the period generates everything from
    if lim + 6 > top:
        return None
    table = [row[:] for row in T[:lim]]

    def D(i, j):
        """the CANDIDATE field on the whole strip: the table, extended by (P)"""
        if i < 0 or not 0 <= j < C:
            return None                    # off the strip
        if i < lim:
            return table[i][j]
        q, r = divmod(i - i0, PERIOD)
        v = table[i0 + r][j]
        return v if v == INF else v + RISE * q

    # (a)
    if D(0, 0) != 0:
        return None
    # (b) and (c). Rows i0 + 2*PERIOD .. i0 + 3*PERIOD - 1 and everything above them repeat
    # rows i0 + PERIOD .. i0 + 2*PERIOD - 1 with RISE added, so checking up to i0+3*PERIOD-1
    # settles every row. Two extra periods are checked anyway; they cost nothing.
    nb = nc = 0
    hi = i0 + 5 * PERIOD
    for i in range(hi + 1):
        for j in range(C):
            v = D(i, j)
            wit = False
            for di, dj in KN:
                w = D(i + di, j + dj)
                if w is None:
                    continue
                if v != INF and not (w <= v + 1):
                    return None            # (b) fails
                nb += 1
                if v != INF and w != INF and w == v - 1:
                    wit = True
            if v != INF and (i, j) != (0, 0):
                if not wit:
                    return None            # (c) fails
                nc += 1

    # rho, and the board height from which one field serves them all
    rho = {}
    order = sorted(((D(i, j), i, j) for i in range(hi + 1) for j in range(C)
                    if D(i, j) != INF))
    for v, i, j in order:
        if (i, j) == (0, 0):
            rho[(0, 0)] = 1
            continue
        best = None
        for di, dj in KN:
            a, b = i + di, j + dj
            w = D(a, b)
            if w is None or w == INF or w != v - 1 or (a, b) not in rho:
                continue
            cand = max(i + 1, a + 1, rho[(a, b)])
            if best is None or cand < best:
                best = cand
        if best is None:
            return None
        rho[(i, j)] = best

    need = [0] * (hi + 2)                  # need[H] = max rho over the rows a height-H board has
    run = 0
    for H in range(1, hi + 2):
        for j in range(C):
            if (H - 1, j) in rho:
                run = max(run, rho[(H - 1, j)])
        need[H] = run
    H0 = None
    for H in range(1, i0 + PERIOD):
        if all(need[k] <= k for k in range(H, hi + 2)):
            H0 = H
            break
    if H0 is None:
        return None
    return {'C': C, 'i0': i0, 'period': PERIOD, 'rise': RISE, 'lim': lim,
            'table': table, 'H0': H0, 'checked_rows': hi + 1, 'nb': nb, 'nc': nc}


_CACHE = {}


def field(C, R):
    """the distance field on a board of exactly R rows, taken from the certificate when the
    certificate covers it and computed on the board itself when it does not"""
    c = get(C)
    if c is None:
        return None
    if R < c['H0']:
        return _bfs(R, C)
    lim, i0 = c['lim'], c['i0']
    out = []
    for i in range(R):
        if i < lim:
            out.append(c['table'][i][:])
        else:
            q, r = divmod(i - i0, PERIOD)
            out.append([v if v == INF else v + RISE * q for v in c['table'][i0 + r]])
    return out


def get(C):
    if C not in _CACHE:
        _CACHE[C] = certify(C)
    return _CACHE[C]


if __name__ == '__main__':
    import sys
    for C in range(3, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 13):
        c = certify(C)
        if c is None:
            print('C=%d  NO CERTIFICATE' % C)
            continue
        print('C=%-2d i0=%-3d H0=%-3d table rows=%-3d (b) checks %-6d (c) checks %-5d'
              % (C, c['i0'], c['H0'], c['lim'], c['nb'], c['nc']))
