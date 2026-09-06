#!/usr/bin/env python3
"""Lump a walk automaton by identical FUTURE behaviour.

a(n) = iota^T M^n tau, and (M^n tau)_u is the number of walks of n steps from u weighted by
tau at the end.  Two states whose future functions agree for every n may be merged: the merged
digraph carries edge multiplicities, and the count is unchanged.

The partition is the coarsest one refining {tau = c} and stable under "same number of edges
into each block", found by ordinary refinement.  What it buys is ITERATIONS: the annihilation
test runs until S consecutive residuals vanish, so the cost is governed by the state count, and
the states this family produces are highly redundant --- the bookkeeping a state carries for
the ORDER clause is invisible to the future once the rows it names are settled.
"""
import collections


def lump(adj, start, end):
    S = len(adj)
    block = list(end)
    # normalise the initial labels to 0..k-1
    remap = {v: i for i, v in enumerate(sorted(set(block)))}
    block = [remap[v] for v in block]
    while True:
        sig = []
        for u in range(S):
            c = collections.Counter(block[v] for v in adj[u])
            sig.append((block[u], tuple(sorted(c.items()))))
        order = {s: i for i, s in enumerate(sorted(set(sig)))}
        nb = [order[s] for s in sig]
        if nb == block:
            break
        block = nb
    K = max(block) + 1 if block else 0
    members = [[] for _ in range(K)]
    for u in range(S):
        members[block[u]].append(u)
    wadj = []
    for b in range(K):
        u = members[b][0]
        row = []
        for v in adj[u]:
            row.append(block[v])
        wadj.append(row)
    wstart = [0] * K
    for u in range(S):
        wstart[block[u]] += start[u]
    wend = [end[members[b][0]] for b in range(K)]
    return wadj, wstart, wend, K
