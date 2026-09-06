#!/usr/bin/env python3
"""3 X 3 subblock conditions counted up to relabelling of the alphabet.

Same inversion as `transfer20` -- the entry counts equality patterns, patterns are a fixed
rational combination of array counts over alphabets of each size, and each of those is a walk
count -- but wrapped around the 3 X 3 subblock engine instead of the cell-neighbourhood one.

Only conditions stated through EQUALITY may be treated this way, since the inversion needs the
condition to survive a permutation of the alphabet. The whitelist below is deliberately narrow:
"three equal elements in a row" and "equal diagonal or antidiagonal elements" qualify, while
sums, determinants, perimeter patterns and strict increases do not.
"""
import re
import transfer17 as T17
import transfer19 as T19
from transfer20 import falling_weights, strip_relabel, _gcd

INVARIANT = re.compile(
    r'having three equal elements in a row [a-z, \-]*(?:,? exactly \w+ ways?)?$|'
    r'having (?:three )?equal diagonal elements or (?:three )?equal antidiagonal elements$',
    re.I)


def parse_name(nm):
    plain, hit = strip_relabel(nm)
    if not hit:
        return None
    p = T17.parse_name(plain)
    if not p or not INVARIANT.fullmatch(p['body'].strip().rstrip('.')):
        return None
    m = re.search(r'0\.\.(\d+)\s*arrays?|(binary)\s*arrays?', nm, re.I)
    if not m:
        return None
    p['K'] = (1 if m.group(2) else int(m.group(1))) + 1
    p['plain'] = plain
    return p


def build(p, cap=40000):
    K = p['K']
    c = falling_weights(K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    adj, start, end = [], [], []
    base = 0
    for i, wi in zip(range(1, K + 1), w):
        q = dict(p)
        q['alpha'] = i - 1
        b = T17.build(q, cap=cap)
        if b is None:
            return None
        st, a_i = b
        S_i = len(st)
        if base + S_i > cap:
            return None
        adj.extend([[k + base for k in row] for row in a_i])
        start.extend([wi] * S_i)
        end.extend([1] * S_i)
        base += S_i
    if base == 0:
        return None
    adj, start, end, S = T19.trim(adj, start, end)
    return adj, start, end, S, den


terms = T19.terms
threshold = T19.threshold
