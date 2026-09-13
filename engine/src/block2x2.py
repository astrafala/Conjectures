#!/usr/bin/env python3
"""Arrays of fixed width whose every 2 X 2 subblock satisfies one condition.

    Number of (n+1) X (7+1) 0..2 arrays with the minimum plus the upper median equal to the
      lower median plus the maximum in every 2 X 2 subblock.

The width is fixed and the height grows, so a row is a state and the condition, spanning two
consecutive rows, is exactly the edge relation: a walk in the row digraph is an admissible
array. Nothing here is new machinery -- what was missing was a reading of the condition.

For a 2 X 2 block with entries sorted v1 <= v2 <= v3 <= v4 the minimum is v1, the lower median
v2, the upper median v3 and the maximum v4, so the entry asks for v1 + v3 = v2 + v4. Since
v1 <= v2 and v3 <= v4 the left side never exceeds the right, and equality forces BOTH v1 = v2
and v3 = v4: the four entries of every 2 X 2 subblock form two equal pairs. Its sibling family
asks only that the two medians agree, v2 = v3, which is the same shape with a weaker edge
relation. That is what makes
the digraph sparse -- 65,536 rows and 67,072 edges at width 8 over 0..3 -- and it is a
statement about the condition, not an optimisation applied to it.

The digraph is built one column at a time rather than by trying every pair of rows, because
(alpha+1)^(2*width) pairs is 4 x 10^9 at that size and the edge set is 67,072 of them.
"""
import re
from itertools import product

SHAPE = re.compile(
    r'(?i)^Number of \(n\s*\+\s*1\)\s*X\s*\((\d+)\s*\+\s*1\)\s*0\.\.(\d+)\s*arrays with '
    r'(.+?)\s*\.?\s*$')

COND = {
    'the minimum plus the upper median equal to the lower median plus the maximum in '
    'every 2 x 2 subblock': 'medpair',
    'the upper median equal to the lower median in every 2 x 2 subblock': 'medeq',
}


def _ok(kind, a, b, c, d):
    v = sorted((a, b, c, d))
    if kind == 'medpair':
        return v[0] == v[1] and v[2] == v[3]
    if kind == 'medeq':
        return v[1] == v[2]
    raise ValueError(kind)


def parse_name(nm):
    nm = ' '.join(nm.split())
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\d(])', ' X ', nm)
    nm = ' '.join(nm.split())
    m = SHAPE.match(nm)
    if not m:
        return None
    kind = COND.get(re.sub(r'2 X 2', '2 x 2', m.group(3)).lower())
    if kind is None:
        return None
    cols, alpha = int(m.group(1)) + 1, int(m.group(2))
    if cols < 2 or (alpha + 1) ** cols > 2000000:
        return None
    return {'engine': 'block2x2', 'cols': cols, 'alpha': alpha, 'kind': kind, 'frac': 1}


def build(p, cap=2000000):
    cols, alpha, kind = p['cols'], p['alpha'], p['kind']
    V = range(alpha + 1)
    rows = list(product(V, repeat=cols))
    if len(rows) > cap:
        return None
    idx = {r: i for i, r in enumerate(rows)}
    adj = {}
    for i, r in enumerate(rows):
        parts = [()]
        for j in range(cols):
            nxt = []
            for q in parts:
                for v in V:
                    if j and not _ok(kind, r[j - 1], r[j], q[-1], v):
                        continue
                    nxt.append(q + (v,))
            parts = nxt
            if not parts:
                break
        adj[i] = [idx[s] for s in parts]
    import lumpauto
    st = [1] * len(rows)
    wadj, wstart, wend, S = lumpauto.lump(adj, st, [1] * len(rows))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(rows)}


def terms(b, N):
    """out[n] counts the (n+1) X cols arrays: n edges of the row digraph."""
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
