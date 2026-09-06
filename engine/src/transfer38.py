#!/usr/bin/env python3
"""The edge-count families counted UP TO RELABELLING of the alphabet.

    ... and new values 0..m introduced in row major order

is the clause that turns an array count into a count of EQUALITY PATTERNS, and `transfer20'
records the reduction: with `N_j` the patterns using exactly `j` letters and `L_i` the arrays
over an alphabet of size `i`,

    L_i  =  sum_j N_j * i(i-1)...(i-j+1),

a triangular system with unit diagonal, so the entry's count `N_1 + ... + N_K` is a fixed
rational combination of the `L_i`, each of which is a walk count of its own.

The reduction is legitimate only when the condition is invariant under permuting the alphabet,
and here that is a real restriction rather than a formality. `Equal edges' counts perimeter
edges whose two cells AGREE, which survives any relabelling. `Clockwise edge increases' does
not: it compares cells by SIZE, and permuting the alphabet changes the count. So this wrapper
accepts the equal-edges conditions and refuses the increase-counting ones, which is why the
family splits the way it does.
"""
from fractions import Fraction

import transfer36
import transfer37
import transfer19
from transfer20 import falling_weights, strip_relabel

MODS = (transfer36, transfer37)
OKKIND = {'same', 'fixed', 'nbequal', 'nbdiffer', 'mixed', 'eq'}


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def parse_name(nm):
    plain, hit = strip_relabel(nm)
    if not hit:
        return None
    for k, mod in enumerate(MODS):
        try:
            p = mod.parse_name(plain)
        except Exception:
            p = None
        if p:
            break
    else:
        return None
    if p['kind'] not in OKKIND:
        return None
    stats = {p.get('stat'), p.get('stat2')} - {None}
    if any(s != 'equal edges' for s in stats):
        return None
    if mod is transfer37 and p['kind'] != 'eq':
        return None
    if mod is transfer36 and p['kind'] == 'fixed':
        return None                     # `equal to k' is about the count, but see stats above
    return {'which': k, 'p': p, 'K': p['alpha'] + 1, 'frac': 1}


def build(q, cap=40000):
    mod = MODS[q['which']]
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
        # A None from the component engine means EITHER `no admissible state' OR `refused as
        # too large', and the two must not be confused: silently dropping a refused component
        # would leave a model that undercounts. So the component engine's own size guard is
        # tested here first, and a component it would refuse fails the whole build.
        if (i ** p['W'] > 4 * cap) if mod is transfer36 else (i ** (2 * p['W']) > 10 * cap):
            return None
        b = mod.build(p, cap=cap)
        if b is None:
            continue                   # genuinely empty over so small an alphabet
        st, a_i = b
        if base + len(st) > cap:
            return None
        adj.extend([[t + base for t in row] for row in a_i])
        start.extend([w[i - 1]] * len(st))
        end.extend([1] * len(st))
        base += len(st)
    if base == 0:
        return None
    return adj, start, end, base, den


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
