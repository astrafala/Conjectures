#!/usr/bin/env python3
"""Transfer matrix for the Hardin K X K-subblock MATRIX families.

Name shapes covered:
    Number of (n+K-1) X W 0..m matrices with each K X K subblock idempotent
    Number of (n+K-1) X W 0..m matrices with each K X K subblock having the same population
    Number of (n+K-1) X W 0..m matrices with each K X K permanent equal

The condition couples K consecutive rows and K consecutive columns at once, so a row of the
array is not a state on its own: the state is the strip of the last K-1 rows, and one step of
the walk appends a new row, the step being legal exactly when the K X W band it completes has
every one of its K X K windows admissible.  An array with n+K-1 rows is then a walk of n steps
from any state to any state, so a(n) = 1^T M^n 1 and the sequence is C-finite.

Enumerating the legal (K-1) X W strips directly is hopeless -- there are (m+1)^((K-1)W) of them
-- but they need not be enumerated.  Consecutive windows of one band overlap in K X (K-1), so a
legal band is a walk in the overlap graph on the admissible K X K windows, and the states that
matter are exactly the tops and bottoms of legal bands.  That turns a search over strips into a
search over windows, of which there are few.

For the two conditions that only say some quantity is the SAME across all windows, the count
splits by the common value: the arrays whose windows all have population v are a walk count of
their own, the values of v give disjoint sets of arrays, and a disjoint union of the graphs adds
the counts.

Admissible windows for `idempotent` are not found by trying all 2^(K*K) matrices, which is out
of reach by K = 6.  Writing M^2 = M row by row, row r_i must equal the sum of the rows indexed
by its own support; comparing supports gives a closed description -- pick the zero rows Z, pick
a set B of indices with r_b = {b} u Z_b for Z_b contained in Z, and let every other nonzero row
be a disjoint union of those -- which generates each idempotent exactly once.  The counts it
gives for K = 2, 3, 4 (8, 50, 452) agree with exhaustion over all 2^(K*K) matrices.
"""
import re
import collections
from itertools import combinations, product

import namecanon
import transfer17

NAME = re.compile(
    r'Number of \(?n\s*\+\s*(\d+)\)?\s*X\s*(\d+)\s*'
    r'0\.\.(\d+)\s*matrices\s+with\s+each\s+(\d+)\s*X\s*(\d+)\s*'
    r'(?:subblock\s+)?(idempotent|having the same population|permanent equal)\s*\.?\s*$',
    re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)
    norm = re.sub(r'(?<=[\d)])\s*[xX]\s*(?=[\d(])', ' X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    m = NAME.search(norm)
    if not m:
        return None
    d, W, alpha, k1, k2 = (int(m.group(i)) for i in (1, 2, 3, 4, 5))
    if k1 != k2 or k1 < 2 or d != k1 - 1 or W < k1:
        return None
    pred = m.group(6).lower()
    pred = {'idempotent': 'idem', 'having the same population': 'pop',
            'permanent equal': 'perm'}[pred]
    if pred == 'perm' and k1 != 2:
        return None
    return {'K': k1, 'W': W, 'alpha': alpha, 'pred': pred, 'frac': 1}


# ---------------------------------------------------------------- admissible windows

def idempotents(k):
    """every 0-1 k X k matrix with M^2 = M, each exactly once, as tuples of row tuples."""
    out = []
    for zmask in range(1 << k):
        Z = [i for i in range(k) if (zmask >> i) & 1]
        rest = [i for i in range(k) if not (zmask >> i) & 1]
        zopts = []
        for s in range(1 << len(Z)):
            mask = 0
            for t in range(len(Z)):
                if (s >> t) & 1:
                    mask |= 1 << Z[t]
            zopts.append(mask)
        for bsel in range(1 << len(rest)):
            B = [rest[t] for t in range(len(rest)) if (bsel >> t) & 1]
            other = [rest[t] for t in range(len(rest)) if not (bsel >> t) & 1]
            for zb in product(zopts, repeat=len(B)):
                prim = [(1 << B[t]) | zb[t] for t in range(len(B))]
                subs = []
                for r in range(1, len(B) + 1):
                    for c in combinations(range(len(B)), r):
                        mask, ok = 0, True
                        for t in c:
                            if mask & prim[t]:
                                ok = False
                                break
                            mask |= prim[t]
                        if ok:
                            subs.append(mask)
                if other and not subs:
                    continue
                base = [0] * k
                for t in range(len(B)):
                    base[B[t]] = prim[t]
                for rows in product(subs, repeat=len(other)):
                    M = list(base)
                    for t, i in enumerate(other):
                        M[i] = rows[t]
                    out.append(tuple(tuple((M[i] >> j) & 1 for j in range(k))
                                     for i in range(k)))
    return out


def windows(p, cap):
    """list of window groups; the count is the sum over groups."""
    K, al, pred = p['K'], p['alpha'], p['pred']
    if pred == 'idem':
        if al != 1:
            return None
        w = idempotents(K)
        return None if len(w) > 40 * cap else [w]
    tot = (al + 1) ** (K * K)
    if tot > 400000:
        return None
    g = collections.defaultdict(list)
    for cells in product(range(al + 1), repeat=K * K):
        M = tuple(tuple(cells[i * K:(i + 1) * K]) for i in range(K))
        key = (sum(cells) if pred == 'pop'
               else M[0][0] * M[1][1] + M[0][1] * M[1][0])
        g[key].append(M)
    return [g[k] for k in sorted(g)]


# ---------------------------------------------------------------- the walk

def build(p, cap=4000):
    K, W = p['K'], p['W']
    groups = windows(p, cap)
    if groups is None:
        return None
    steps = W - K + 1
    states, index, adj = [], {}, []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    for gi, G in enumerate(groups):
        if not G:
            continue
        byleft = collections.defaultdict(list)
        for B in G:
            byleft[tuple(r[:K - 1] for r in B)].append(B)
        succ = {A: byleft.get(tuple(r[1:] for r in A), []) for A in G}
        stack = [(A, [list(r) for r in A], 1) for A in G]
        nband = 0
        while stack:
            cur, rows, d = stack.pop()
            if d == steps:
                nband += 1
                if nband > 60 * cap:
                    return None
                top = (gi,) + tuple(tuple(r) for r in rows[:K - 1])
                bot = (gi,) + tuple(tuple(r) for r in rows[1:])
                a, b = sid(top), sid(bot)
                if len(states) > cap:
                    return None
                adj[a].append(b)
                continue
            for B in succ[cur]:
                nr = [rows[i] + [B[i][K - 1]] for i in range(K)]
                stack.append((B, nr, d + 1))
    if not states:
        return None
    return states, adj


def terms(adj, S, N):
    return transfer17.terms(adj, S, N)


def threshold(adj, S, coeffs, order):
    return transfer17.threshold(adj, S, coeffs, order)
