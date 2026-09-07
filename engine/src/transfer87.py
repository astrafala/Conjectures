#!/usr/bin/env python3
"""Four more array conditions: parity prefixes, forbidden differences, distinct differences,
and quantifiers over a cell's neighbours.

    Number of n X 2 binary arrays with an element zero only if there are an even number of
        ones to its left and an even number of ones above it.
    Number of n X 3 0..2 arrays with top left element 0, horizontal differences mod 3 never 1,
        vertical differences mod 3 never -1, and antidiagonal differences never 0.
    Number of n X 2 0..4 arrays with the absolute differences of each element with its
        horizontal and antidiagonal neighbors unique.
    Number of 4 X (n+1) 0..3 arrays with no element equal to all horizontal neighbors or
        unequal to all vertical neighbors, and new values 0..3 introduced in row major order.

Three of the four are local and share a three-line window. The first is not: "an even number
of ones above it" counts the whole column above the cell, back to the top of the array. It
needs no window either, because only the PARITY of that count matters --- one bit per column,
flipped by each one that goes into that column. The parity of the ones to a cell's left is
read off the line itself as it is scanned.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

DIRS = {
    'horizontal': [(0, -1), (0, 1)], 'vertical': [(-1, 0), (1, 0)],
    'diagonal': [(-1, -1), (1, 1)], 'antidiagonal': [(-1, 1), (1, -1)],
    'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)],
}
STEP = {'horizontal': (0, 1), 'vertical': (1, 0), 'diagonal': (1, 1),
        'antidiagonal': (1, -1)}
ADVERB = {'horizontally': 'horizontal', 'vertically': 'vertical',
          'diagonally': 'diagonal', 'antidiagonally': 'antidiagonal'}

HEAD = re.compile(
    r'^(?:Number of|number of)\s+(.+?)\s+(binary|(\d+)\.\.(\d+))\s+arrays\s+with\s+(.+?)'
    r'(,?\s*(?:and\s+)?(?:with\s+)?new values \d+\.\.(\d+) introduced in row major order)?'
    r'\s*\.?\s*$', re.I)
# a fixed dimension may be written as a sum, "(3+1) X (n+1)", which is Hardin's way of
# saying the width is 4; reading only a bare digit there loses the whole family
DIM = r'(?:\((\d+)\+(\d+)\)|(\d+))'
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X ' + DIM + r'$', re.I), 'rows'),
    (re.compile(r'^n X ' + DIM + r'$', re.I), 'rows0'),
    (re.compile(r'^' + DIM + r' X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^' + DIM + r' X n$', re.I), 'cols0'),
]


def _dim(a, b, c):
    return int(c) if c else int(a) + int(b)
PARITY = re.compile(r'^an element zero only if there are an even number of ones to its left '
                    r'and an even number of ones above it$', re.I)
DIFFMOD = re.compile(r'^top left element (\d+),?\s*(.+)$', re.I)
ONEDIFF = re.compile(r'(\w+) differences (?:mod (\d+) )?never (-?\d+)', re.I)
UNIQ = re.compile(r'^the absolute differences of each element with its (?:with )?'
                  r'([A-Za-z, ]+?) neighbors unique$', re.I)
ALLUNEQ = re.compile(r'^no element equal to all (\w+) neighbors or unequal to all (\w+) '
                     r'neighbors$', re.I)


def _dirs(text):
    out, got = [], False
    for w in re.findall(r"[A-Za-z][A-Za-z-]*", text.lower()):
        w = ADVERB.get(w, w)
        if w in ('or', 'and', 'neighbors', 'neighbours'):
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
    sh = _shape(m.group(1).strip())
    if sh is None:
        return None
    L, a, tr = sh
    if m.group(2).lower() == 'binary':
        lo, hi = 0, 1
    else:
        lo, hi = int(m.group(3)), int(m.group(4))
    canon = m.group(6) is not None
    if canon and (lo != 0 or int(m.group(7)) != hi):
        return None
    cond = m.group(5).strip().rstrip(',')
    p = {'L': L, 'a': a, 'lo': lo, 'hi': hi, 'canon': canon, 'transposed': tr, 'frac': 1}
    if PARITY.match(cond):
        if (lo, hi) != (0, 1) or canon:
            return None
        p['kind'] = 'parity'
        return p if 1 <= L <= 8 else None
    g = DIFFMOD.match(cond)
    if g and 'differences' in cond:
        rules = []
        for w, mod, val in ONEDIFF.findall(g.group(2)):
            w = ADVERB.get(w.lower(), w.lower())
            if w not in STEP:
                return None
            rules.append((STEP[w], int(mod) if mod else hi - lo + 1, int(val)))
        if not rules or len(rules) != len(ONEDIFF.findall(g.group(2))):
            return None
        p.update({'kind': 'diffmod', 'corner': int(g.group(1)), 'rules': rules})
        return p if 1 <= L <= 6 and hi - lo <= 5 else None
    g = UNIQ.match(cond)
    if g:
        d = _dirs(g.group(1))
        if d is None:
            return None
        p.update({'kind': 'uniq', 'dirs': d})
        return p if 1 <= L <= 4 and hi - lo <= 5 else None
    g = ALLUNEQ.match(cond)
    if g:
        d1, d2 = _dirs(g.group(1)), _dirs(g.group(2))
        if d1 is None or d2 is None:
            return None
        p.update({'kind': 'alluneq', 'd1': d1, 'd2': d2})
        return p if 1 <= L <= 5 and hi - lo <= 4 else None
    return None


def _advance(m, line, k):
    for v in line:
        if v > m:
            return None
        if v == m:
            m += 1
    return m if m <= k else None


def build(p, cap=200000):
    L, lo, hi, kind = p['L'], p['lo'], p['hi'], p['kind']
    tr = p.get('transposed', False)
    lines = list(product(range(lo, hi + 1), repeat=L))
    if kind == 'parity':
        return _build_parity(p, lines, cap)
    k = hi + 1

    def off(d):
        return (d[1], d[0]) if tr else d

    def get(win, ds, df, j):
        line = win[ds + 1]
        jj = j + df
        return None if (line is None or not 0 <= jj < L) else line[jj]

    def ok_mid(win):
        mid = win[1]
        if kind == 'uniq':
            for j in range(L):
                ds = [abs(mid[j] - v) for v in
                      (get(win, *off(d), j) for d in p['dirs']) if v is not None]
                if len(ds) != len(set(ds)):
                    return False
            return True
        if kind == 'alluneq':
            for j in range(L):
                x = mid[j]
                h = [v for v in (get(win, *off(d), j) for d in p['d1']) if v is not None]
                v2 = [v for v in (get(win, *off(d), j) for d in p['d2']) if v is not None]
                if all(y == x for y in h) or all(y != x for y in v2):
                    return False
            return True
        # 'diffmod': every rule, applied from the middle line to where it points
        for step, mod, val in p['rules']:
            ds, df = off(step)
            for j in range(L):
                t = get(win, ds, df, j)
                if t is not None and (t - mid[j]) % mod == val % mod:
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
        if p.get('corner') is not None and r[0] != p['corner']:
            continue
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
            if not ok_mid((before, mid, r)):
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
    end = [1 if ok_mid((b, m, None)) else 0 for b, m, _ in states]
    return lumpauto.lump(adj, start, end)


def _build_parity(p, lines, cap):
    """an element may be zero only where both running counts of ones are even

    The count above a cell reaches back to the top of the array, so no window holds it; but
    only its parity is asked for, so one bit per column is enough, flipped by every one that
    lands in that column. The parity to the cell's left is read off the line being placed.
    """
    L = p['L']
    ok = {}
    for r in lines:
        good = []
        for par in range(1 << L):
            fine, left = True, 0
            for j in range(L):
                if r[j] == 0 and (left % 2 or (par >> j) & 1):
                    fine = False
                    break
                left += r[j]
            if fine:
                good.append(par)
        ok[r] = good
    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    def nxt(par, r):
        for j in range(L):
            if r[j]:
                par ^= 1 << j
        return par

    starts = [sid(nxt(0, r)) for r in lines if 0 in ok[r]]
    if not starts:
        return None
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        par = states[u]
        for r in lines:
            if par not in ok[r]:
                continue
            v = sid(nxt(par, r))
            if len(states) > cap:
                return None
            adj[u].append(v)
            if v not in seen:
                seen.add(v)
                frontier.append(v)
    S = len(states)
    start = [0] * S
    for i in starts:
        start[i] += 1
    end = [1] * S
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
