#!/usr/bin/env python3
"""Arrays over a fixed alphabet whose every PAIR or TRIPLE of positions must be compatible.

    Number of -3..3 arrays x(i) of n+1 elements i=1..n+1 with x(i)+x(j), x(i+1)+x(j+1),
      -(x(i)+x(j+1)), and -(x(i+1)+x(j)) having two, three or four distinct values for every
      i<=n and j<=n.
    Number of -2..2 arrays x(i) of n+1 elements i=1..n+1 with
      set{t,u,v in 0,1}((x[i+t]+x[j+u]+x[k+v])*(-1)^(t+u+v)) having three, four, five or six
      distinct values for every i,j,k<=n.

65 entries, none read. The condition quantifies over ALL pairs or triples of positions, so no
bounded window decides it -- but it depends on those positions only through the ADJACENT PAIRS
(x_i, x_{i+1}) they sit at. Writing D for the set of distinct adjacent pairs an array uses, the
condition says exactly that every two (or three) members of D are compatible: D must be a
clique of a fixed graph on the (2A+1)^2 pairs, or a clique of a fixed 3-uniform hypergraph.

That makes the state (last value, the set of adjacent pairs used so far). Admissibility is
subset-closed, so appending a value only has to test the new pair against what is already
there, and the reachable states are the cliques -- a finite digraph whose walks are the arrays,
which is what every transfer-matrix paper here already settles.
"""
import re
from itertools import product

WORDS = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
         'one': 1, 'nine': 9, 'ten': 10}

PAIR = re.compile(
    r'^\s*Number of (-?\d+)\.\.(-?\d+) arrays x\(i\) of n\+1 elements i=1\.\.n\+1 with '
    r'x\(i\)\+x\(j\), x\(i\+1\)\+x\(j\+1\), -\(x\(i\)\+x\(j\+1\)\), and -\(x\(i\+1\)\+x\(j\)\) '
    r'having (.*?) distinct values for every i<=n and j<=n\s*\.?\s*$', re.I)
TRIP = re.compile(
    r'^\s*Number of (-?\d+)\.\.(-?\d+) arrays x\(i\) of n\+1 elements i=1\.\.n\+1 with '
    r'set\{t,u,v in 0,1\}\(\(x\[i\+t\]\+x\[j\+u\]\+x\[k\+v\]\)\*\(-1\)\^\(t\+u\+v\)\) '
    r'having (.*?) distinct values for every i,j,k<=n\s*\.?\s*$', re.I)


def _counts(text):
    out = set()
    for w in re.split(r',| or |and', text):
        w = w.strip()
        if not w:
            continue
        if w in WORDS:
            out.add(WORDS[w])
        elif w.isdigit():
            out.add(int(w))
        else:
            return None
    return out or None


def parse_name(nm):
    nm = ' '.join(nm.split())
    for rx, kind in ((PAIR, 'pair'), (TRIP, 'triple')):
        m = rx.match(nm)
        if not m:
            continue
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo != -hi or not 1 <= hi <= 4:
            return None
        cs = _counts(m.group(3))
        if cs is None:
            return None
        return {'engine': 'pairclique', 'A': hi, 'kind': kind, 'counts': frozenset(cs),
                'frac': 1}
    return None


def _ok_pair(p, q, cs):
    (a, b), (c, d) = p, q
    return len({a + c, b + d, -(a + d), -(b + c)}) in cs


def _ok_triple(p, q, r, cs):
    (a, b), (c, d), (e, f) = p, q, r
    vals = set()
    for t in (0, 1):
        for u in (0, 1):
            for v in (0, 1):
                s = (a if t == 0 else b) + (c if u == 0 else d) + (e if v == 0 else f)
                vals.add(s * (-1) ** (t + u + v))
    return len(vals) in cs


def _walk_allowed(V, pairs, nbrs, selfok, cap, A, kind):
    """the walk whose state is (last value, the pairs still allowed)."""
    import lumpauto
    pid = {q: i for i, q in enumerate(pairs)}
    ALL = frozenset(i for i in range(len(pairs)) if i in selfok)
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    start = [sid((v, ALL)) for v in V]
    adj = {}
    i = 0
    while i < len(states):
        last, allow = states[i]
        out = []
        for nxt in V:
            q = pid[(last, nxt)]
            if q not in allow:
                continue
            out.append(sid((nxt, allow & nbrs[q])))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1
    st = [0] * len(states)
    for u in start:
        st[u] += 1
    wadj, wstart, wend, K = lumpauto.lump(adj, st, [1] * len(states))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': K, 'raw': len(states), 'A': A, 'kind': kind}


def build(p, cap=200000):
    A, kind, cs = p['A'], p['kind'], p['counts']
    if kind == 'triple' and A > 2:
        # a TRIPLE condition is not pairwise, so the state has to carry the set of pairs
        # already used rather than the set still allowed, and at 49 pairs that set space is
        # past any budget. Refused with the reason rather than left to explore it.
        return None
    V = list(range(-A, A + 1))
    pairs = [(a, b) for a in V for b in V]
    if kind == 'pair':
        # For a PAIRWISE condition the future depends only on which pairs are still allowed,
        # not on which were used: allowed is the intersection of the neighbourhoods of the used
        # ones. Carrying the used set instead put the raw state count past three hundred
        # thousand; carrying the allowed set keeps it in the hundreds, and it is the same walk.
        nbrs = []
        for i, pi in enumerate(pairs):
            nbrs.append(frozenset(j for j, pj in enumerate(pairs)
                                  if _ok_pair(pi, pj, cs) and _ok_pair(pj, pi, cs)))
        selfok = frozenset(i for i, pi in enumerate(pairs) if _ok_pair(pi, pi, cs))
        return _walk_allowed(V, pairs, nbrs, selfok, cap, A, kind)
    else:
        def fits(new, S):
            T = list(S) + [new]
            for q in T:
                for r in T:
                    if not _ok_triple(pairs[new], pairs[q], pairs[r], cs):
                        return False
                    if not _ok_triple(pairs[q], pairs[new], pairs[r], cs):
                        return False
                    if not _ok_triple(pairs[q], pairs[r], pairs[new], cs):
                        return False
            return True

    pid = {q: i for i, q in enumerate(pairs)}
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    start = [sid((v, frozenset())) for v in V]
    adj = {}
    i = 0
    while i < len(states):
        last, S = states[i]
        out = []
        for nxt in V:
            q = pid[(last, nxt)]
            if q in S:
                out.append(sid((nxt, S)))
                continue
            if not fits(q, S):
                continue
            out.append(sid((nxt, S | {q})))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1
    # The set a state carries is bookkeeping for a condition already settled; two states whose
    # FUTURE behaviour agrees contribute identically to every walk count and may be merged.
    # Without this the state count is nine thousand and the residual test, which runs until S
    # consecutive residuals vanish, is hopeless -- the same reason the 3 x 3 subblock family
    # needed it.
    import lumpauto
    st = [0] * len(states)
    for u in start:
        st[u] += 1
    wadj, wstart, wend, K = lumpauto.lump(adj, st, [1] * len(states))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': K, 'raw': len(states), 'A': A, 'kind': kind}


def terms(b, N):
    """a(n) = arrays of n+1 elements, i.e. walks of n steps."""
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    out = [sum(v * e for v, e in zip(vec, ev))]
    for _ in range(N):
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
