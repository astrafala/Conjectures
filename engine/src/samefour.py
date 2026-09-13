#!/usr/bin/env python3
"""Arrays in which every 2 X 2 subblock holds the same four values.

    1/16 the number of (n+1) X 7 0..3 arrays with all 2 X 2 subblocks having the same four
      values.

"The same four values" is the same MULTISET in every block, and the condition is rigid enough
to describe in one paragraph. Two horizontally adjacent blocks share a column, so writing
m_j for the multiset {r_j, s_j} of the j-th column of a row PAIR, the condition on the pair is
m_j + m_{j+1} = V for every j, with V the common four-value multiset. Hence the m_j alternate:
m, V-m, m, V-m, .... Once V, the alternation and the top row r are fixed, the bottom row is
DETERMINED cell by cell -- s_j is whatever is left in the required multiset after removing r_j
-- and r itself is only constrained to have r_j in that multiset. So the digraph is small, its
out-degree is at most the number of 2-element sub-multisets of V, and the whole count is the
disjoint union over V of these digraphs: no array satisfies the condition for two different V,
since V is read off any one of its blocks.

The name's divisor is the square of the alphabet size, 16 over 0..3 and 9 over 0..2, and it is
divided out here so the model's terms are the entry's own.
"""
import re
from itertools import product

NAME = re.compile(
    r'(?i)^1/(\d+) the number of \(n\+1\) X (\d+) 0\.\.(\d+) arrays with all 2 X 2 subblocks '
    r'having the same four values\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\d(])', ' X ', nm)
    nm = ' '.join(nm.split())
    m = NAME.match(nm)
    if not m:
        return None
    div, cols, alpha = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if div != (alpha + 1) ** 2 or cols < 2 or cols > 12 or alpha > 5:
        return None
    return {'engine': 'samefour', 'cols': cols, 'alpha': alpha, 'div': div, 'frac': 1}


def _sub2(V):
    """the distinct 2-element sub-multisets of the 4-multiset V, with their complements"""
    out = {}
    for i in range(4):
        for j in range(i + 1, 4):
            m = tuple(sorted((V[i], V[j])))
            rest = list(V)
            rest.pop(j)
            rest.pop(i)
            out[m] = tuple(sorted(rest))
    return list(out.items())


def build(p, cap=2000000):
    cols, alpha = p['cols'], p['alpha']
    V4 = [tuple(v) for v in product(range(alpha + 1), repeat=4)
          if list(v) == sorted(v)]                    # each multiset once
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    adj = {}
    start = set()
    for V in V4:
        pats = []
        for m, c in _sub2(V):
            pats.append((m, c))
            if c != m:
                pats.append((c, m))
        for pat in pats:
            req = [pat[j % 2] for j in range(cols)]
            for r in product(*[sorted(set(q)) for q in req]):
                start.add(sid((V, r)))
        for st in list(states):
            pass
        # transitions are added lazily below
    # lazy closure
    i = 0
    order = sorted(start)
    while i < len(states):
        V, r = states[i]
        out = []
        for m, c in _sub2(V):
            for pat in ((m, c), (c, m)) if c != m else ((m, c),):
                req = [pat[j % 2] for j in range(cols)]
                s = []
                for j in range(cols):
                    q = req[j]
                    if r[j] == q[0]:
                        s.append(q[1])
                    elif r[j] == q[1]:
                        s.append(q[0])
                    else:
                        s = None
                        break
                if s is not None:
                    out.append(sid((V, tuple(s))))
        adj[i] = sorted(set(out))
        i += 1
        if len(states) > cap:
            return None
    import lumpauto
    stv = [0] * len(states)
    for j in start:
        stv[j] = 1
    wadj, wstart, wend, S = lumpauto.lump(adj, stv, [1] * len(states))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(states), 'div': p['div']}


def terms(b, N):
    """out[n] counts the (n+1) X cols arrays, divided by the name's own divisor."""
    adj, S, div = b['adj'], b['S'], b['div']
    vec = list(b['startv'])
    ev = b['endv']
    out = [sum(v * e for v, e in zip(vec, ev)) // div]
    for _ in range(N + 1):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        t = sum(v * e for v, e in zip(vec, ev))
        out.append(t // div if t % div == 0 else None)
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    if any(x is None for x in t):
        return None
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
