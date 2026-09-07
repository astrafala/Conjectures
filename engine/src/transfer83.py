#!/usr/bin/env python3
"""Arrays under a condition on each element and its neighbours.

    Number of n X 3 0..1 arrays with no element equal to the same number of vertical
        neighbors as horizontal neighbors, with new values 0..1 introduced in row major order.
    Number of n X 3 0..1 arrays with no element equal to exactly one horizontal or vertical
        neighbor, with new values 0..1 introduced in row major order.
    Number of n X 2 binary arrays with every 1 having exactly one king-move neighbor equal
        to 1.
    Number of n X 4 0..1 arrays with each 1 horizontally or vertically adjacent to 0 or 2 1's.
    Number of n X 3 0..1 arrays with every one equal to some NW, E or S neighbor.

Every one of these looks at a cell and at cells one step away, so three consecutive lines
decide the whole condition on the middle one. The state is therefore two consecutive lines,
the condition on a line is tested when the line after it arrives, and the line with nothing
after it is tested by the end vector --- which is where the boundary lives: a cell in the
first line has no line before it and a cell in the last has none after it, and the entry
means exactly that, not a wrap-around.

Some of these entries also ask for new values in row major order, which is not a condition on
any window; as elsewhere it enters through one integer, the count of values introduced so
far.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8}
# (row, column) offsets, as the entry names them
DIRS = {
    'horizontal': [(0, -1), (0, 1)],
    'vertical': [(-1, 0), (1, 0)],
    'diagonal': [(-1, -1), (1, 1)],
    'antidiagonal': [(-1, 1), (1, -1)],
    'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)],
    'n': [(-1, 0)], 's': [(1, 0)], 'e': [(0, 1)], 'w': [(0, -1)],
    'nw': [(-1, -1)], 'ne': [(-1, 1)], 'sw': [(1, -1)], 'se': [(1, 1)],
}

HEAD = re.compile(
    r'^(?:Number of|number of)\s+(.+?)\s+(binary|0\.\.(\d+))\s+arrays\s+with\s+(.+?)'
    r'(,?\s*(?:and\s+)?with\s+new values 0\.\.(\d+) introduced in row major order)?\s*\.?\s*$',
    re.I)
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X \(?(\d+)\)?$', re.I), 'rows'),
    (re.compile(r'^n X \(?(\d+)\)?$', re.I), 'rows0'),
    (re.compile(r'^\(?(\d+)\)? X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^\(?(\d+)\)? X n$', re.I), 'cols0'),
]
CMP = re.compile(r'^no element equal to (the same number of|a different number of) '
                 r'(\w+) neighbors (?:as|than) (\w+) neighbors$', re.I)
NE1 = re.compile(r'^no element equal to exactly ([a-z]+|\d+) (\w+) or (\w+) neighbors?$', re.I)
KING = re.compile(r'^every (\d+) having exactly ([a-z]+|\d+) (king-?move|\w+) neighbors? '
                  r'equal to (\d+)$', re.I)
ADJ = re.compile(r"^(?:each|every) (\d+) ((?:[\w-]+(?:,\s*| or | and )?)+?) adjacent to "
                 r"([\d, or]+?) (?:neighbou?ring )?(\d+)'?s$", re.I)
SOME = re.compile(r'^every (one|\d+) equal to some ([A-Za-z, ]+?) neighbou?r$', re.I)
DIRWORD = re.compile(r'horizontally|vertically|diagonally|antidiagonally|king-?move', re.I)


def _num(t):
    t = t.strip().lower()
    return int(t) if t.isdigit() else NUM.get(t)


ADVERB = {'horizontally': 'horizontal', 'vertically': 'vertical',
          'diagonally': 'diagonal', 'antidiagonally': 'antidiagonal',
          'kingmove': 'king-move', 'kingmoves': 'king-move', 'king-moves': 'king-move'}
STOP = {'or', 'and', 'neighbor', 'neighbors', 'neighbour', 'neighbours', 'adjacent',
        'to', 'some', 'the', 'a', 'having', 'exactly'}


def _dirs(text):
    """the offsets the entry's direction words name, or None if a word is unknown

    The adverb is mapped, not stripped: "horizontally".rstrip("ly") is "horizonta", because
    rstrip removes every trailing character in the set rather than the suffix, and the whole
    family of names using adverbs silently failed to parse.
    """
    out, got = [], False
    for w in re.findall(r"[A-Za-z][A-Za-z-]*", text.lower()):
        w = ADVERB.get(w, w)
        if w in STOP:
            continue
        if w not in DIRS:
            return None
        out += DIRS[w]
        got = True
    return sorted(set(out)) if got else None


def _shape(s):
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        if kind == 'rows':
            return int(m.group(2)), int(m.group(1)), False
        if kind == 'rows0':
            return int(m.group(1)), 0, False
        if kind == 'cols':
            return int(m.group(1)), int(m.group(2)), True
        return int(m.group(1)), 0, True
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    sh = _shape(m.group(1).strip())
    if sh is None:
        return None
    L, a, tr = sh
    k = 2 if m.group(2).lower() == 'binary' else int(m.group(3)) + 1
    canon = m.group(5) is not None
    if canon and int(m.group(6)) + 1 != k:
        return None
    if not 2 <= L <= 5 or not 2 <= k <= 4:
        return None
    cond = m.group(4).strip().rstrip(',')
    spec = None
    g = CMP.match(cond)
    if g:
        d1, d2 = _dirs(g.group(2)), _dirs(g.group(3))
        if d1 and d2:
            spec = {'kind': 'cmp', 'eq': g.group(1).lower().startswith('a different'),
                    'd1': d1, 'd2': d2}
    if spec is None:
        g = NE1.match(cond)
        if g:
            v = _num(g.group(1))
            d = _dirs(g.group(2) + ' ' + g.group(3))
            if v is not None and d:
                spec = {'kind': 'countne', 'val': v, 'dirs': d}
    if spec is None:
        g = KING.match(cond)
        if g:
            cnt, d = _num(g.group(2)), _dirs(g.group(3))
            if cnt is not None and d:
                spec = {'kind': 'target', 'cell': int(g.group(1)), 'cnt': [cnt],
                        'dirs': d, 'want': int(g.group(4))}
    if spec is None:
        g = ADJ.match(cond)
        if g and DIRWORD.search(g.group(2)):
            d = _dirs(g.group(2))
            cnts = [int(x) for x in re.findall(r'\d+', g.group(3))]
            if d and cnts:
                spec = {'kind': 'target', 'cell': int(g.group(1)), 'cnt': cnts,
                        'dirs': d, 'want': int(g.group(4))}
    if spec is None:
        g = SOME.match(cond)
        if g:
            d = _dirs(g.group(2))
            if d:
                cell = 1 if g.group(1).lower() == 'one' else int(g.group(1))
                spec = {'kind': 'some', 'cell': cell, 'dirs': d}
    if spec is None:
        return None
    spec.update({'L': L, 'a': a, 'k': k, 'canon': canon, 'transposed': tr, 'frac': 1})
    return spec


def _advance(m, line, k):
    for v in line:
        if v > m:
            return None
        if v == m:
            m += 1
    return m if m <= k else None


def build(p, cap=200000):
    L, k, tr, kind = p['L'], p['k'], p.get('transposed', False), p['kind']
    lines = list(product(range(k), repeat=L))

    def off(d):
        """(step along the walk, step along the fixed axis) for a (row, column) offset"""
        return (d[1], d[0]) if tr else d

    def count(win, j, dirs, want):
        """how many neighbours of the middle line's cell j, in these directions, equal want

        win is (before, middle, after), any of which may be None at the boundary. A
        neighbour off the edge is not a neighbour: the array is finite and the entry means
        its edges, not a torus.
        """
        n = 0
        for d in dirs:
            ds, df = off(d)
            line = win[ds + 1]
            jj = j + df
            if line is None or not 0 <= jj < L:
                continue
            if line[jj] == want:
                n += 1
        return n

    def ok_line(win):
        """the middle line's cells, all of whose neighbours this window contains"""
        mid = win[1]
        for j in range(L):
            x = mid[j]
            if kind == 'cmp':
                c1 = count(win, j, p['d1'], x)
                c2 = count(win, j, p['d2'], x)
                if (c1 == c2) != p['eq']:
                    return False
            elif kind == 'countne':
                if count(win, j, p['dirs'], x) == p['val']:
                    return False
            elif kind == 'target':
                if x == p['cell'] and count(win, j, p['dirs'], p['want']) not in p['cnt']:
                    return False
            else:                                 # 'some'
                if x == p['cell'] and count(win, j, p['dirs'], x) == 0:
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

    starts = []
    for r in lines:
        m = _advance(0, r, k) if p['canon'] else 0
        if m is None:
            continue
        starts.append(sid((None, r, m)))
    if not states:
        return None
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        before, mid, m = states[u]
        for r in lines:
            m2 = _advance(m, r, k) if p['canon'] else 0
            if m2 is None:
                continue
            if not ok_line((before, mid, r)):
                continue
            v = sid((mid, r, m2))
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
    # the last line has nothing after it, and that is where its cells are decided
    end = [1 if ok_line((b, mth, None)) else 0 for b, mth, _ in states]
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
