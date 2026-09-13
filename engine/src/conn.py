#!/usr/bin/env python3
"""n X k arrays in which every value's cells form one connected region.

    Number of n X 3 1..2 arrays containing at least one of each value, and all equal values
      connected.
    Number of n X 3 1..4 arrays with all 1s connected, all 2s connected, all 3s connected, all
      4s connected, 1 in the upper left corner, 2 in the upper right corner, 3 in the lower left
      corner, and 4 in the lower right corner.

40 entries turn on connectivity and no engine read one, because connectivity is not decided by
any bounded window: two cells of the same colour may be joined through a path that leaves the
window and comes back. The frontier carries it. Reading the array row by row, the state is

  * the colours of the current row,
  * which of its cells are in the same component of the region seen so far -- a partition of
    the k positions, refining the colouring, canonically labelled,
  * and for each colour whether it is unseen, open, or CLOSED.

A component closes when the new row has no cell in it. A closed component can never be reached
again, so at that moment the colour must have no other open component and no later cell, and
that is the whole of the condition: at the end every colour that appeared has exactly one
component. The count is then a walk in a finite digraph, which is what every transfer-matrix
paper here already settles.

The corner clauses are fixed cells in the first and last rows; `at least one of each value' is
the requirement that no colour is unseen at the end; `no element having more than two neighbours
with the same value' is local to two consecutive rows and is checked as the row is placed.
"""
import re
from itertools import product

HEAD = re.compile(
    r'^\s*Number of n ?X ?(\d+) (?:1\.\.(\d+)|(binary)) arrays (?:with|containing) (.*?)\s*\.?\s*$',
    re.I)
UNSEEN, OPEN, CLOSED = 0, 1, 2


def parse_name(nm):
    m = HEAD.match(' '.join(nm.split()))
    if not m:
        return None
    k = int(m.group(1))
    A = int(m.group(2)) if m.group(2) else 2
    body = ' '.join(m.group(4).lower().split()).replace("'", '')
    rest = body
    allconn = False
    if 'all equal values connected' in rest:
        allconn = True
        rest = rest.replace('all equal values connected', '')
    got = re.findall(r'all (\d+)s connected', rest)
    if got:
        if sorted(int(g) for g in got) != list(range(1, A + 1)):
            return None
        allconn = True
        rest = re.sub(r'all \d+s connected', '', rest)
    if not allconn:
        return None
    need_all = 'at least one of each value' in rest
    rest = rest.replace('at least one of each value', '')
    corners = {}
    for v, c in re.findall(r'(\d+) in the (upper left|upper right|lower left|lower right) corner',
                           rest):
        corners[c] = int(v)
    rest = re.sub(r'\d+ in the (?:upper left|upper right|lower left|lower right) corner', '',
                  rest)
    maxsame = None
    mm = re.search(r'no element having more than (\d+) neighbors with the same value', rest)
    if mm:
        maxsame = int(mm.group(1))
        rest = rest[:mm.start()] + rest[mm.end():]
    if re.sub(r'[,\s]|and|with', '', rest):
        return None                       # an unread clause: refuse rather than ignore it
    if not 1 <= k <= 4 or not 2 <= A <= 4 or (A ** k) * 20 > 40000:
        return None
    return {'engine': 'conn', 'k': k, 'A': A, 'need_all': need_all, 'corners': corners,
            'maxsame': maxsame, 'frac': 1}


def _canon(colour, parent):
    """canonical component labels of the k frontier cells."""
    k = len(colour)
    lab, seen = [0] * k, {}
    for i in range(k):
        r = parent[i]
        if r not in seen:
            seen[r] = len(seen)
        lab[i] = seen[r]
    return tuple(lab)


def _step(k, A, prev, cur):
    """(colours, labels, status) for the next row, or None if the array is already dead.

    A union-find over the old frontier cells and the new ones: old cells that shared a label
    are the same component, new neighbours of equal colour join, and a new cell joins the cell
    above it when their colours agree. A class with no new cell in it has CLOSED -- nothing can
    reach it again -- so the colour must have had exactly that one component and must not
    appear again.
    """
    par = list(range(2 * k))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    def uni(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            par[max(ra, rb)] = min(ra, rb)

    if prev is None:
        pc = pl = None
        st = [UNSEEN] * A
    else:
        pc, pl, status = prev
        st = list(status)
        for c in set(cur):
            if st[c - 1] == CLOSED:
                return None
        for a in range(k):
            for b in range(a + 1, k):
                if pl[a] == pl[b]:
                    uni(a, b)
        for a in range(k):
            if pc[a] == cur[a]:
                uni(a, k + a)
    for a in range(k - 1):
        if cur[a] == cur[a + 1]:
            uni(k + a, k + a + 1)
    if prev is not None:
        oldc = {}
        for a in range(k):
            oldc.setdefault((pc[a], pl[a]), []).append(a)
        for (col, _lab), cells in oldc.items():
            root = find(cells[0])
            alive = any(find(k + b) == root for b in range(k))
            if alive:
                continue
            # this component has closed: the colour must have no other component anywhere
            others = sum(1 for (c2, _l2) in oldc if c2 == col) > 1
            if others or any(cc == col for cc in cur):
                return None
            st[col - 1] = CLOSED
    lab, seen = [0] * k, {}
    for a in range(k):
        r = find(k + a)
        if r not in seen:
            seen[r] = len(seen)
        lab[a] = seen[r]
    for c in set(cur):
        if st[c - 1] == UNSEEN:
            st[c - 1] = OPEN
    return (tuple(cur), tuple(lab), tuple(st))


def build(p, cap=200000):
    k, A = p['k'], p['A']
    cols = list(product(range(1, A + 1), repeat=k))
    maxsame, corners, need_all = p['maxsame'], p['corners'], p['need_all']

    # A cell's same-valued neighbours are its left, its right, the cell above and the cell
    # BELOW, and the last of those is not known when the row is placed. Checking only the
    # first three counted A164760 as though the clause were not there at all. The partial
    # count travels in the state, one small number per position, and the check happens when
    # the row below arrives -- or, for the last row, at the end.
    def partial(prev, cur):
        out = []
        for i in range(k):
            c = 0
            if i and cur[i - 1] == cur[i]:
                c += 1
            if i + 1 < k and cur[i + 1] == cur[i]:
                c += 1
            if prev is not None and prev[i] == cur[i]:
                c += 1
            out.append(min(c, 4))
        return tuple(out)

    def same_ok(pend, prev, cur):
        if maxsame is None:
            return True
        if pend is not None:
            for i in range(k):
                if pend[i] + (1 if prev[i] == cur[i] else 0) > maxsame:
                    return False
        return all(v <= maxsame for v in partial(prev, cur))

    states, index = [], {}

    def sid(x):
        if x not in index:
            index[x] = len(states)
            states.append(x)
        return index[x]

    # first rows
    start = []
    for cur in cols:
        if corners.get('upper left') and cur[0] != corners['upper left']:
            continue
        if corners.get('upper right') and cur[-1] != corners['upper right']:
            continue
        if not same_ok(None, None, cur):
            continue
        s = _step(k, A, None, cur)
        if s is not None:
            start.append(sid(s + (partial(None, cur),) if maxsame is not None else s))
    adj = {}
    i = 0
    while i < len(states):
        full = states[i]
        prev = full[:3]
        pend = full[3] if maxsame is not None else None
        out = []
        for cur in cols:
            if not same_ok(pend, prev[0], cur):
                continue
            s = _step(k, A, prev, cur)
            if s is None:
                continue
            out.append(sid(s + (partial(prev[0], cur),) if maxsame is not None else s))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1

    def accept(s):
        cur, lab, st = s[:3]
        if maxsame is not None and any(v > maxsame for v in s[3]):
            return False
        if corners.get('lower left') and cur[0] != corners['lower left']:
            return False
        if corners.get('lower right') and cur[-1] != corners['lower right']:
            return False
        for c in range(1, A + 1):
            if st[c - 1] == UNSEEN:
                if need_all or corners:
                    return False
                continue
            if st[c - 1] == OPEN:
                if len({lab[i] for i in range(k) if cur[i] == c}) != 1:
                    return False
        return True
    end = [i for i, s in enumerate(states) if accept(s)]
    return {'adj': adj, 'start': start, 'end': end, 'S': len(states), 'k': k, 'A': A}


def terms(b, N):
    adj, S = b['adj'], b['S']
    es = set(b['end'])
    vec = [0] * S
    for s in b['start']:
        vec[s] += 1
    out = [0, sum(v for i, v in enumerate(vec) if i in es)]
    for _ in range(N - 1):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v for i, v in enumerate(vec) if i in es))
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
