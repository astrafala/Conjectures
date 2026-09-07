#!/usr/bin/env python3
"""Element-and-neighbour conditions that reach further than one line.

    Number of n X 2 0..3 arrays with new values 0..3 introduced in row major order and no
        element equal to any knight-move neighbor.
    Number of n X 2 0..1 arrays with no element equal to more than two horizontal or vertical
        neighbors, with new values 0..1 introduced in row major order.
    Half the number of n X 3 binary arrays with each element equal to at least two neighbors.
    Number of n X 2 0..2 arrays with each element equal to either the maximum or the minimum
        of its horizontal and vertical neighbors.
    Number of n X 3 0..2 arrays with every element equal to some element at offset (-1,-1)
        (-1,0) (-1,1) (0,-1) (0,1) or (1,0) both plus 1 mod 3 and minus 1 mod 3, with new
        values introduced in order 0..2.

The earlier neighbour engine assumed every cell named lay one line away, which a knight move
does not: it reaches two. So the window here is 2R+1 lines wide, R being the furthest the
condition reaches, and the state carries 2R of them. A line is judged when the line R beyond
it arrives, and the last R lines --- the ones with nothing far enough beyond them --- are
judged by the end vector. A neighbour off the edge is not a neighbour, which is what makes
the first terms of these sequences small.

One reading was genuinely ambiguous and the data settled it. "Each element equal to at least
two neighbors" does not say which neighbours; taking the four horizontal and vertical ones
gives A180752's published 0, 1, 1, 2, while taking all eight king-move neighbours gives
0, 3, 9, 37.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
DIRS = {
    'horizontal': [(0, -1), (0, 1)], 'vertical': [(-1, 0), (1, 0)],
    'diagonal': [(-1, -1), (1, 1)], 'antidiagonal': [(-1, 1), (1, -1)],
    'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)],
    'knight-move': [(a, b) for a in (-2, -1, 1, 2) for b in (-2, -1, 1, 2)
                    if abs(a) + abs(b) == 3],
}
ADVERB = {'horizontally': 'horizontal', 'vertically': 'vertical',
          'diagonally': 'diagonal', 'antidiagonally': 'antidiagonal',
          'kingmove': 'king-move', 'knightmove': 'knight-move'}
BARE = DIRS['horizontal'] + DIRS['vertical']       # "neighbors" with nothing said: pinned

DIM = r'(?:\((\d+)\+(\d+)\)|(\d+))'
HEAD = re.compile(
    r'^(?:(Half|One quarter|1/(\d+)) the number of|Number of|number of)\s+(.+?)\s+'
    r'(binary|(\d+)\.\.(\d+))\s+arrays\s+with\s+(.+?)\s*\.?\s*$', re.I)
CANON = re.compile(r'^(.*?),?\s*(?:and\s+)?with new values (?:\d+\.\.(\d+) )?introduced in '
                   r'(?:row major order|order 0\.\.(\d+))'
                   r'(?:\s*\(colorings ignoring permutations of colors\))?$', re.I)
CANON2 = re.compile(r'^new values \d+\.\.(\d+) introduced in row major order and (.+?)'
                    r'(?:\s*\(colorings ignoring permutations of colors\))?$', re.I)
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X ' + DIM + r'$', re.I), 'rows'),
    (re.compile(r'^n X ' + DIM + r'$', re.I), 'rows0'),
    (re.compile(r'^' + DIM + r' X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^' + DIM + r' X n$', re.I), 'cols0'),
]
NOANY = re.compile(r'^no element equal to any ([\w-]+) neighbou?r$', re.I)
CMP = re.compile(r'^(?:no|each|every) element equal to (more than|at least|at most|fewer '
                 r'than) ([a-z]+|\d+) ?([\w -]*?) ?neighbou?rs$', re.I)
MAXMIN = re.compile(r'^each element equal to either the maximum or the minimum of its '
                    r'([\w and-]+?) neighbou?rs$', re.I)
OFFS = re.compile(r'^every element equal to some element at offset (.+?) both plus (\d+) '
                  r'mod (\d+) and minus (\d+) mod (\d+)$', re.I)


def _num(t):
    t = t.strip().lower()
    return int(t) if t.isdigit() else NUM.get(t)


def _dim(a, b, c):
    return int(c) if c else int(a) + int(b)


def _dirs(text):
    if not text.strip():
        return list(BARE)
    out, got = [], False
    for w in re.findall(r"[A-Za-z][A-Za-z-]*", text.lower()):
        w = ADVERB.get(w, w)
        if w in ('or', 'and', 'its', 'neighbor', 'neighbors', 'neighbour', 'neighbours'):
            continue
        if w not in DIRS:
            return None
        out += DIRS[w]
        got = True
    return sorted(set(out)) if got else list(BARE)


def _shape(s):
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        g = m.groups()
        if kind == 'rows':
            return _dim(g[1], g[2], g[3]), int(g[0]), False
        if kind == 'rows0':
            return _dim(g[0], g[1], g[2]), 0, False
        if kind == 'cols':
            return _dim(g[0], g[1], g[2]), int(g[3]), True
        return _dim(g[0], g[1], g[2]), 0, True
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    frac = 1
    if m.group(1):
        frac = {'half': 2, 'one quarter': 4}.get(m.group(1).lower()) or int(m.group(2))
    sh = _shape(m.group(3).strip())
    if sh is None:
        return None
    L, a, tr = sh
    k = 2 if m.group(4).lower() == 'binary' else int(m.group(6)) + 1
    cond = m.group(7).strip()
    canon = False
    g = CANON.match(cond)
    if g:
        hi = g.group(2) or g.group(3)
        if hi is not None and int(hi) + 1 != k:
            return None
        canon, cond = True, g.group(1).strip().rstrip(',')
    else:
        g = CANON2.match(cond)
        if g:
            if int(g.group(1)) + 1 != k:
                return None
            canon, cond = True, g.group(2).strip().rstrip(',')
    p = {'L': L, 'a': a, 'k': k, 'canon': canon, 'transposed': tr, 'frac': frac}
    g = NOANY.match(cond)
    if g:
        d = _dirs(g.group(1))
        if d is None:
            return None
        p.update({'kind': 'noany', 'dirs': d})
    elif CMP.match(cond):
        g = CMP.match(cond)
        v = _num(g.group(2))
        d = _dirs(g.group(3))
        if v is None or d is None:
            return None
        p.update({'kind': 'cmp', 'rel': g.group(1).lower(), 'val': v, 'dirs': d})
    elif MAXMIN.match(cond):
        d = _dirs(MAXMIN.match(cond).group(1))
        if d is None:
            return None
        p.update({'kind': 'maxmin', 'dirs': d})
    elif OFFS.match(cond):
        g = OFFS.match(cond)
        offs = [(int(x), int(y)) for x, y in re.findall(r'\((-?\d+),\s*(-?\d+)\)', g.group(1))]
        if not offs or int(g.group(3)) != k or int(g.group(5)) != k:
            return None
        p.update({'kind': 'offs', 'dirs': offs, 'up': int(g.group(2)), 'dn': int(g.group(4))})
    else:
        return None
    if not 1 <= L <= 5 or not 2 <= k <= 4:
        return None
    reach = max(max(abs(d[1] if tr else d[0]) for d in p['dirs']), 1)
    if reach > 2:
        return None
    p['reach'] = reach
    return p


def _advance(m, line, k):
    for v in line:
        if v > m:
            return None
        if v == m:
            m += 1
    return m if m <= k else None


def build(p, cap=200000):
    L, k, R = p['L'], p['k'], p['reach']
    tr = p.get('transposed', False)
    kind = p['kind']
    lines = list(product(range(k), repeat=L))
    W = 2 * R                                   # lines carried in the state

    def off(d):
        return (d[1], d[0]) if tr else d

    def judge(win, mid):
        """the cells of win[mid], all of whose neighbours this window contains"""
        row = win[mid]
        if row is None:
            return True
        for j in range(L):
            x = row[j]
            vals = []
            for d in p['dirs']:
                ds, df = off(d)
                t, jj = mid + ds, j + df
                if not 0 <= t < len(win) or not 0 <= jj < L or win[t] is None:
                    continue
                vals.append(win[t][jj])
            if kind == 'noany':
                if x in vals:
                    return False
            elif kind == 'cmp':
                c, rel, v = vals.count(x), p['rel'], p['val']
                bad = ((rel == 'more than' and c > v) or (rel == 'at least' and c < v)
                       or (rel == 'at most' and c > v) or (rel == 'fewer than' and c >= v))
                if bad:
                    return False
            elif kind == 'maxmin':
                if not vals or x not in (max(vals), min(vals)):
                    return False
            else:                                # 'offs'
                if (x + p['up']) % k not in vals or (x - p['dn']) % k not in vals:
                    return False
        return True

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    empty = (None,) * W
    starts = []
    for r in lines:
        m = _advance(0, r, k) if p['canon'] else 0
        if m is None:
            continue
        starts.append(sid(((empty + (r,))[1:], m)))
    if not states:
        return None
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        st, m = states[u]
        for r in lines:
            m2 = _advance(m, r, k) if p['canon'] else 0
            if m2 is None:
                continue
            win = st + (r,)                     # 2R+1 lines; the middle one is now decided
            if not judge(win, R):
                continue
            v = sid((win[1:], m2))
            if len(states) > cap:
                return None
            adj[u].append(v)
            if v not in seen:
                seen.add(v)
                frontier.append(v)
    S = len(states)
    start = [0] * S
    for i in set(starts):
        start[i] = 1
    # the last R lines have nothing far enough beyond them, and are judged here
    end = []
    for st, m in states:
        win = st + (None,) * R
        end.append(1 if all(judge(win, i) for i in range(R, W)) else 0)
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
