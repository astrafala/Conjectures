#!/usr/bin/env python3
"""Transfer-matrix proof for the "every 2 X 2 subblock sums to c" array families.

An (n+1) x K array over {0,...,m} whose every 2 x 2 subblock sums to c is exactly a walk
of length n in the digraph whose vertices are the rows (tuples in {0,...,m}^K) and whose
edges r -> s are the pairs with r[j]+r[j+1]+s[j]+s[j+1] = c for every j. Hence

    a(n) = 1^T M^n 1

for the adjacency matrix M, which is C-finite. For a conjectured recurrence with
characteristic polynomial q,

    a(n) - sum_i c_i a(n-i)  =  1^T M^(n-r) q(M) 1 ,

so the recurrence holds for EVERY n >= r if and only if 1^T M^j q(M) 1 = 0 for all j >= 0,
and by Cayley-Hamilton it is enough to check j = 0, ..., S-1 with S the number of states.
That is a finite exact computation in integer arithmetic.
"""
from itertools import product
from fractions import Fraction as Fr


def states(K, m):
    return list(product(range(m + 1), repeat=K))


def edges(K, m, c):
    st = states(K, m)
    idx = {s: i for i, s in enumerate(st)}
    adj = [[] for _ in st]
    for r in st:
        for s in st:
            if all(r[j] + r[j + 1] + s[j] + s[j + 1] == c for j in range(K - 1)):
                adj[idx[r]].append(idx[s])
    return st, adj


def matvec(adj, v):
    """(M v)[r] = sum_{r->s} v[s]"""
    return [sum(v[s] for s in row) for row in adj]


def terms(K, m, c, N):
    """a(n) = 1^T M^n 1 for n = 0..N."""
    st, adj = edges(K, m, c)
    v = [1] * len(st)
    out = []
    for _ in range(N + 1):
        out.append(sum(v))
        v = matvec(adj, v)
    return out, st, adj


def qM_one(adj, S, coeffs, order):
    """w = q(M) 1 where q(t) = t^order - sum_i c_i t^(order-i)."""
    v = [1] * S
    powers = [v]
    for _ in range(order):
        v = matvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        for j in range(S):
            w[j] -= c * powers[order - i][j]
    return w


def annihilates(adj, S, coeffs, order, cap=None):
    """True iff 1^T M^j q(M) 1 = 0 for every j >= 0 (checked to the Cayley-Hamilton bound)."""
    w = qM_one(adj, S, coeffs, order)
    lim = S if cap is None else min(S, cap)
    for _ in range(lim + 1):
        if sum(w) != 0:
            return False
        if not any(w):
            return True                      # w is the zero vector: nothing left to check
        w = matvec(adj, w)
    return True
