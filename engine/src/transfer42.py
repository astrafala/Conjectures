#!/usr/bin/env python3
"""The cell-condition families of `transfer41' counted UP TO RELABELLING.

Only the conditions stated through EQUALITY survive a permutation of the alphabet, and here
that excludes most of the family: `next to itself plus and minus one', `adjacent to the value
m-x' and `equal to the sum mod k of its neighbours' all compare or combine letters
arithmetically. What remains --- `equal to some neighbour', `equal to exactly k neighbours',
and `equal to all its horizontal neighbours or unequal to all its vertical ones' --- is about
agreement alone, and for those the pattern reduction of `transfer20' applies unchanged.
"""
import transfer19
import transfer41
from transfer20 import falling_weights, strip_relabel

INV = {'somematch', 'exactly', 'allhoriz'}


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def parse_name(nm):
    plain, hit = strip_relabel(nm)
    if not hit:
        return None
    p = transfer41.parse_name(plain)
    if not p or p['kind'] not in INV:
        return None
    return {'p': p, 'K': p['alpha'] + 1, 'frac': p['frac']}


def build(q, cap=40000):
    K = q['K']
    c = falling_weights(K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    adj, start, end = [], [], []
    base = 0
    for i in range(1, K + 1):
        p = dict(q['p'])
        p['alpha'] = i - 1
        if i ** (2 * p['W']) > 10 * cap:
            return None                  # a component the engine would refuse, not an empty one
        b = transfer41.build(p, cap=cap)
        if b is None:
            return None
        a_i, s_i, e_i, S_i = b
        if base + S_i > cap:
            return None
        adj.extend([[t + base for t in row] for row in a_i])
        start.extend([w[i - 1] * x for x in s_i])
        end.extend(e_i)
        base += S_i
    if base == 0:
        return None
    return adj, start, end, base, den


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
