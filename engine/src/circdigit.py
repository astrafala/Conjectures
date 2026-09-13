#!/usr/bin/env python3
"""Circular digit strings whose neighbours, the wrap included, differ by at most k.

    Number of base 7 circular n-digit numbers with adjacent digits differing by 5 or less.

Let G be the graph on the digits 0..b-1 with an edge between u and v when |u-v| <= k, loops
included. A circular n-digit string is a CLOSED walk of length n in G, and closed walks of
length n from all starting points number exactly the trace of the n-th power of the adjacency
matrix. So

    a(n) = trace(M^n) = sum of the n-th powers of the eigenvalues of M     (n >= 1),

so the sequence satisfies the monic linear recurrence whose characteristic polynomial is that
of M -- of order exactly b, by Cayley-Hamilton, with no bound to estimate.

At n = 0 the entry sets a(0) = 1, the empty circular number, where the trace gives b. That is
the entry's convention and not a disagreement about the model: the two agree at every n >= 1,
on every published term of all 229 names this reads, and the threshold the annihilation test
returns simply records the transient the convention creates.

The entry counts every digit string, leading zeros included: the readings that require a
nonzero first digit give 4, 11, 25 where A124698 gives 5, 13, 29.
"""
import re

WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
        'eight': 8, 'nine': 9, 'ten': 10}

NAME = re.compile(
    r'(?i)^Number of base (\d+) circular n-digit numbers with adjacent digits differing by '
    r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten) or less\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    b = int(m.group(1))
    t = m.group(2).lower()
    k = int(t) if t.isdigit() else WORD[t]
    if b < 2 or b > 40 or k < 0:
        return None
    return {'engine': 'circdigit', 'b': b, 'k': k, 'frac': 1}


def build(p, cap=2000):
    b, k = p['b'], p['k']
    if b > cap:
        return None
    M = [[1 if abs(i - j) <= k else 0 for j in range(b)] for i in range(b)]
    return {'M': M, 'S': b, 'b': b, 'k': k}


def terms(b_, N):
    """out[n] = trace(M^n) for n >= 1, and the entry's own a(0) = 1 at the head."""
    M, b = b_['M'], b_['b']
    # powers by repeated multiplication of a b x b integer matrix: b is at most 40 here
    cur = [[1 if i == j else 0 for j in range(b)] for i in range(b)]
    out = [1]                                  # the entry's convention at n = 0
    for _ in range(N + 2):
        cur = [[sum(cur[i][t] * M[t][j] for t in range(b) if cur[i][t]) for j in range(b)]
               for i in range(b)]
        out.append(sum(cur[i][i] for i in range(b)))
    return out


def threshold(b_, coeffs, order):
    S = b_['S']
    t = terms(b_, 2 * S + order + 30)
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
