#!/usr/bin/env python3
"""Generalised transfer matrix for the Hardin 2 X 2-subblock array families.

Name shapes covered:
    Number of (n+1) X (K+1) 0..m arrays with every 2 X 2 subblock summing to <set>
    Number of (n+1) X  K    0..m arrays with every 2 X 2 subblock summing to <set>
optionally followed by
    and no 2 X 2 subblock having exactly two nonzero entries.

Rows of such an array are the vertices of a digraph; r -> s is an edge when every adjacent
column pair satisfies the stated conditions. An (n+1)-row array is a walk of length n, so
a(n) = 1^T M^n 1, which is C-finite. For a conjectured recurrence with characteristic
polynomial q, a(n) - sum_i c_i a(n-i) = 1^T M^(n-r) q(M) 1, so the recurrence holds for
every n >= r exactly when 1^T M^j q(M) 1 = 0 for all j >= 0 -- and Cayley-Hamilton bounds
the check at j < S. Exact integer arithmetic throughout.
"""
import re
from itertools import product

NAME = re.compile(
    r'Number of \(?n\s*\+\s*1\)?\s*X\s*\(?(\d+)(?:\s*\+\s*1)?\)?\s*'
    r'0\.\.(\d+)\s*arrays?\s*with every 2\s*X\s*2 subblock summing to\s*(.*?)\s*\.?\s*$',
    re.I)
EXTRA = re.compile(r'\s*and no 2\s*X\s*2 subblock having exactly two nonzero entries\s*$', re.I)


def parse_name(nm):
    # only a standalone x between a digit/paren and a digit/paren is the product sign;
    # replacing every x would rewrite the letter inside words such as "exactly"
    norm = re.sub(r'(?<=[\d)])\s*[xX]\s*(?=[\d(])', ' X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    m = NAME.search(norm)
    if not m:
        return None
    k = int(m.group(1))
    cols = k + 1 if re.search(r'X\s*\(\s*\d+\s*\+\s*1\s*\)', norm) else k
    alpha = int(m.group(2))
    tail = m.group(3)
    extra = bool(EXTRA.search(tail))
    tail = EXTRA.sub('', tail)
    if re.search(r'[a-zA-Z]', tail.replace(' or ', ' ').replace(',', ' ')):
        return None                       # an unrecognised extra clause: refuse
    sums = [int(v) for v in re.findall(r'\d+', tail)]
    if not sums:
        return None
    return cols, alpha, sums, extra


def build(cols, alpha, sums, extra):
    st = list(product(range(alpha + 1), repeat=cols))
    S = set(sums)
    adj = []
    for r in st:
        row = []
        for si, s in enumerate(st):
            ok = True
            for j in range(cols - 1):
                blk = (r[j], r[j + 1], s[j], s[j + 1])
                if sum(blk) not in S:
                    ok = False; break
                if extra and sum(1 for v in blk if v) == 2:
                    ok = False; break
            if ok:
                row.append(si)
        adj.append(row)
    return st, adj


def matvec(adj, v):
    return [sum(v[s] for s in row) for row in adj]


def terms(adj, S, N):
    v = [1] * S
    out = []
    for _ in range(N + 1):
        out.append(sum(v))
        v = matvec(adj, v)
    return out


def threshold(adj, S, coeffs, order):
    """Smallest t with a(n) = sum c_i a(n-i) for every n > t, or None if no such t.

    u_j = 1^T M^j q(M) 1 satisfies the monic linear recurrence given by the characteristic
    polynomial of M, of degree S. So if u_j vanishes for S consecutive j it vanishes for
    every later j, and the last nonzero u_j pins the threshold exactly.
    """
    v = [1] * S
    powers = [v]
    for _ in range(order):
        v = matvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        p = powers[order - i]
        for j in range(S):
            w[j] -= c * p[j]
    us = []
    zeros = 0
    j = 0
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(w)
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return order + last


def annihilates(adj, S, coeffs, order):
    v = [1] * S
    powers = [v]
    for _ in range(order):
        v = matvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        p = powers[order - i]
        for j in range(S):
            w[j] -= c * p[j]
    for _ in range(S + 1):
        if sum(w) != 0:
            return False
        if not any(w):
            return True
        w = matvec(adj, w)
    return True
