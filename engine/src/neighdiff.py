#!/usr/bin/env python3
"""Arrays in which every element differs from at least one NEIGHBOUR in a stated way.

    Number of 0..6 arrays of length n with each element differing from at least one neighbor
      by 1 or less, starting with 0.

"At least one neighbour" is an obligation, not a window test: the element's left neighbour is
known when it is read and its right neighbour is not, so whether the condition is met cannot be
decided in place. One bit carries it -- whether the element just read is still waiting for a
partner. The vertex is (that element, that bit); reading the next element either discharges the
debt, in which case the new element is itself already partnered, or leaves it standing, in which
case the array is dead if the debt was already outstanding. An array is admissible exactly when
it ends with no debt.

The first element has only a right neighbour, so it starts in debt; "starting with 0" fixes it.
A length-1 array is therefore never admissible, and every entry of this family publishes
a(1) = 0.
"""
import re

REL = {
    '1 or less': lambda a, b: abs(a - b) <= 1,
    'something other than 1': lambda a, b: abs(a - b) != 1,
    '2 or more': lambda a, b: abs(a - b) >= 2,
    '2 or less': lambda a, b: abs(a - b) <= 2,
    '3 or more': lambda a, b: abs(a - b) >= 3,
    'more than 1': lambda a, b: abs(a - b) > 1,
    'exactly 1': lambda a, b: abs(a - b) == 1,
}

NAME = re.compile(
    r'(?i)^Number of 0\.\.(\d+) arrays of length n with each element differing from at least '
    r'one neighbor by (.+?)(, starting with 0)?\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    K = int(m.group(1))
    rel = ' '.join(m.group(2).lower().split())
    if rel not in REL or K < 1 or K > 30:
        return None
    return {'engine': 'neighdiff', 'K': K, 'rel': rel, 'zero': bool(m.group(3)), 'frac': 1}


def build(p, cap=200000):
    K, f, zero = p['K'], REL[p['rel']], p['zero']
    V = range(K + 1)
    # vertex (v, debt): the last element and whether it still needs a partner to its right
    states = [(v, d) for v in V for d in (0, 1)]
    idx = {s: i for i, s in enumerate(states)}
    adj = {}
    for i, (v, d) in enumerate(states):
        out = []
        for w in V:
            ok = f(v, w)
            if d and not ok:
                continue                 # v's debt can never be paid now
            out.append(idx[(w, 0 if ok else 1)])
        adj[i] = out
    start = [0] * len(states)
    for v in V:
        if zero and v != 0:
            continue
        start[idx[(v, 1)]] = 1           # the first element owes a partner on its right
    end = [1 if d == 0 else 0 for (_v, d) in states]
    import lumpauto
    wadj, wstart, wend, S = lumpauto.lump(adj, start, end)
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(states), 'zero': zero, 'K': K}


def terms(b, N):
    """out[j] counts the arrays of length j+1.

    out[0] is the length-1 count and it is 0: a single element has no neighbour at all, so its
    debt can never be paid. Every entry of this family publishes a(1) = 0, which is the
    walk saying it rather than a convention imposed on it.
    """
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    out = [sum(v * e for v, e in zip(vec, ev))]
    for _ in range(N + 1):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v * e for v, e in zip(vec, ev)))
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
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
