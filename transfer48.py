#!/usr/bin/env python3
"""`... arrays avoiding patterns 001 and 100 in rows and columns' and its relatives.

A PATTERN is a short word read along one of the four directions of the grid --- along a row,
down a column, down the nw-to-se diagonal, down the ne-to-sw antidiagonal. It is either
absolute, a literal word like `001', or relative, written with a free letter `z' as in
`z-1 z-1 z' or `z z+1 z', which forbids every triple standing in those differences whatever
the value of `z'. Each entry names one or more patterns for each of one or more directions,
and asks that no occurrence appear.

Every pattern is at most three letters long and every direction moves the row index by at most
one, so an occurrence lies inside at most three consecutive array rows. The state is the window
of the last `L-1' rows, `L' being the longest pattern named; a step appends a row and settles
every occurrence ENDING in it, together with every occurrence lying inside it. The row above
may be absent, written as a symbol, so that a walk of no steps is a one-row array and the
boundary is not assumed.
"""
import re
from itertools import product

import namecanon
import transfer19

DIRW = [(r'nw-to-se diagonals?|nw-se diagonals?', (1, 1)),
        (r'ne-to-sw antidiagonals?|ne-sw antidiagonals?', (1, -1)),
        # the longer word first: `antidiagonals?' would otherwise eat the stem of
        # `antidiagonally' and leave a `ly' for the next clause to choke on
        (r'antidiagonally|antidiagonals?', (1, -1)),
        (r'diagonally|diagonals?', (1, 1)),
        (r'horizontally|rows?', (0, 1)),
        (r'vertically|columns?', (1, 0))]
DIRRX = re.compile('|'.join('(?:%s)' % w for w, _ in DIRW), re.I)

SHAPE = re.compile(r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*'
                   r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))')
HEAD = re.compile(r'Number of\s+(.*?)\s*(binary|0\.\.(\d+))\s*arrays\s+avoiding\s+(.*?)\s*\.?\s*$',
                  re.I)


def _dirof(txt):
    for w, off in DIRW:
        if re.fullmatch(r'(?:%s)' % w, txt.strip(), re.I):
            return off
    return None


def _pat(s):
    """(kind, tuple) for one pattern word, or None"""
    s = s.strip()
    if re.fullmatch(r'\d(?:\s*\d)*', s):
        return ('abs', tuple(int(c) for c in re.findall(r'\d', s)))
    ts = s.split()
    if ts and all(re.fullmatch(r'z(?:[+-]\d+)?', t, re.I) for t in ts):
        return ('rel', tuple(int(t[1:]) if len(t) > 1 else 0 for t in ts))
    return None


def _clauses(body):
    """[(patterns, offsets)] read off the `avoiding ...' tail"""
    hits = list(DIRRX.finditer(body))
    if not hits:
        return None
    out, prev = [], 0
    for h in hits:
        txt = body[prev:h.start()]
        prev = h.end()
        off = _dirof(h.group(0))
        if off is None:
            return None
        for _ in range(6):     # the filler words come in runs: `, and the patterns ... in any'
            t2 = re.sub(r'^[\s,]*(?:and|or|in|any|the|patterns?)\b\s*', '', txt.strip(),
                        flags=re.I)
            t2 = re.sub(r'\s*\b(?:in|any)\b\s*$', '', t2.strip(), flags=re.I)
            if t2 == txt:
                break
            txt = t2
        txt = txt.strip().strip(',').strip()
        if not txt:
            if not out:
                return None
            out[-1][1].append(off)              # `... diagonally or antidiagonally'
            continue
        pats = [_pat(x) for x in re.split(r'\s+(?:and|or)\s+', txt)]
        if any(p is None for p in pats):
            return None
        out.append((pats, [off]))
    return out


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = HEAD.search(nm)
    if not m:
        return None
    sh = SHAPE.search(m.group(1).replace(' ', ''))
    if not sh:
        return None
    ra = sh.group(1) or sh.group(3)
    rb = int(sh.group(2) or 0)
    ca = sh.group(4) or sh.group(6)
    cb = int(sh.group(5) or 0)
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        W, trans, base = int(ca) + cb, False, rb
    else:
        W, trans, base = int(ra) + rb, True, cb
    alpha = 1 if m.group(2).lower() == 'binary' else int(m.group(3))
    cl = _clauses(m.group(4))
    if not cl:
        return None
    rules = []
    for pats, offs in cl:
        for off in offs:
            o = (off[1], off[0]) if trans else off
            if o[0] < 0 or (o[0] == 0 and o[1] < 0):
                o = (-o[0], -o[1])
                pats2 = [(k, tuple(reversed(t))) for k, t in pats]
            else:
                pats2 = pats
            for k, t in pats2:
                rules.append((k, t, o))
    if not rules or W < 1:
        return None
    return {'W': W, 'alpha': alpha, 'rules': rules, 'trans': trans, 'base': base, 'frac': 1}


def _match(kind, pat, vals):
    if kind == 'abs':
        return tuple(vals) == tuple(pat)
    d = [v - o for v, o in zip(vals, pat)]
    return all(x == d[0] for x in d)


def build(p, cap=40000):
    W, A = p['W'], p['alpha'] + 1
    rules = [(k, tuple(t), tuple(o)) for k, t, o in p['rules']]
    L = max(len(t) for _, t, _ in rules)
    if A ** W > 40 * cap:
        return None
    allrows = list(product(range(A), repeat=W))

    def inside(r):
        """no occurrence of a horizontal rule inside the single row r"""
        for k, t, o in rules:
            if o != (0, 1):
                continue
            for j in range(W - len(t) + 1):
                if _match(k, t, r[j:j + len(t)]):
                    return False
        return True

    rows = [r for r in allrows if inside(r)]
    if not rows:
        return [], [], [], 0

    def ending(win):
        """no occurrence ending in the last row of the window `win' (None = absent row)"""
        for k, t, o in rules:
            n = len(t)
            if o == (0, 1):
                continue
            if len(win) < n or any(win[-i] is None for i in range(1, n + 1)):
                continue
            di, dj = o
            for j in range(W):
                # j is the column of the LAST cell of the occurrence, the one in the new row;
                # the earlier cells step BACK along the direction
                cols = [j - dj * (n - 1 - s) for s in range(n)]
                if any(c < 0 or c >= W for c in cols):
                    continue
                vals = [win[-n + s][cols[s]] for s in range(n)]
                if _match(k, t, vals):
                    return False
        return True

    idx, order, adj, start = {}, [], [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
            start.append(0)
        return idx[st]

    start[push((None,) * (L - 1))] = 1
    t = 0
    while t < len(order):
        st = order[t]
        row = []
        for u in rows:
            win = st + (u,)
            if ending(win):
                row.append(push(win[1:]))
        adj[t] = row
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    return adj, start[:n], [1] * n, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
