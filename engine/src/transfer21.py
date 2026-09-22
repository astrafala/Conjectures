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



def build_pairfree(p, cap=200000):
    """`build' over `T17.build_pairfree' instead of `T17.build'.

    `T17.build' refuses a priori on `(alpha+1)^(2W) > cap' because its vertices are ordered
    PAIRS of lines. `T17.build_pairfree' has no such refusal: it merges the predecessor line
    into its effect on the future before the states exist, so the pair never gets built. Every
    other caller of `transfer17' already goes through `uniform', which dispatches to the
    pair-free build; this file was the one place still asking for the pair state, and that
    a-priori test is the whole of what refuses all 15 capped `transfer21' entries that carry a
    conjecture.

    The one thing that does not carry over unchanged is the start vector. `build' gives weight
    `wi' to every pair, so `[wi] * S_i' is right there. The pair-free build has already summed
    the predecessors away, and its own start weight at a merged state is how many pairs
    collapsed onto it -- so the same thing here is `wi' TIMES that weight, not `wi'.
    """
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
        # SWITCHED to `T17.build_lineset' (22 September). This is where the switch belongs:
        # `build_lineset' is transfer17's function, not this module's, and transfer21 reaches
        # transfer17 only through here. Changing `uniform`'s dispatch to `M[en].build_lineset'
        # instead asked THIS module for a function it does not have, and `uniform.build' ends
        # in `except Exception: return None' -- so every transfer21 build returned None in
        # 0.0 seconds and read as "state space > cap". Defect 46's shape once more, in the one
        # place already documented as having it.
        b = T17.build_lineset(q, cap=cap)
        if b is None:
            # `build_pairfree' also returns None on `W < 3', where the pair build works fine.
            # Falling back keeps this strictly an improvement: it can open entries the pair
            # build refuses and cannot lose one the pair build accepts.
            b2 = T17.build(q, cap=cap)
            if b2 is None:
                return None
            st, a_i = b2
            S_i = len(st)
            s_i, e_i = [wi] * S_i, [1] * S_i
        else:
            a_i, sw, e_i, S_i = b
            s_i = [wi * x for x in sw]
        if base + S_i > cap:
            return None
        adj.extend([[k + base for k in row] for row in a_i])
        start.extend(s_i)
        end.extend(e_i)
        base += S_i
    if base == 0:
        return None
    adj, start, end, S = T19.trim(adj, start, end)
    return adj, start, end, S, den

terms = T19.terms
threshold = T19.threshold
