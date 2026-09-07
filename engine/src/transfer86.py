#!/usr/bin/env python3
"""Five more conditions on arrays, each decided by a window of consecutive lines.

    Number of n X 3 binary matrices with no two 1's adjacent diagonally or antidiagonally.
    One quarter the number of n X 3 1..4 arrays with no two neighbors of any element equal
        to each other.
    Number of (n+2) X 3 binary arrays with no more than one of any consecutive three bits set
        in any row or column.
    Number of n X 3 0..3 arrays with entries increasing mod 4 by 0, 1 or 2 rightwards and
        downwards, starting with upper left zero.
    Number of n X 3 binary arrays with row sums nondecreasing and columns lexicographically
        nondecreasing.

The first four are local: every cell they mention lies within one or two lines of the cell
being judged, so a window of three consecutive lines decides everything anchored at the
middle one, and the line with nothing after it is judged by the end vector.

The last is not local in either direction and is here because it needs no window at all. A
row sum has to be at least the one before it, so carry the previous row sum. Two columns are
compared at the first line where they differ, so carry one flag per adjacent pair saying
whether they are still equal so far; a pair that has separated the right way never has to be
looked at again, and a pair that separates the wrong way ends the walk. Both are bounded, and
together they are the whole state.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
DIRS = {
    'horizontal': [(0, -1), (0, 1)], 'vertical': [(-1, 0), (1, 0)],
    'diagonal': [(-1, -1), (1, 1)], 'antidiagonal': [(-1, 1), (1, -1)],
    'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)],
}
ADVERB = {'horizontally': 'horizontal', 'vertically': 'vertical',
          'diagonally': 'diagonal', 'antidiagonally': 'antidiagonal'}

HEAD = re.compile(
    r'^(?:(One quarter|One half|1/(\d+)) the number of|Number of|number of)\s+(.+?)\s+'
    r'(?:(binary|(\d+)\.\.(\d+))\s+)?(?:arrays|matrices)\s+with\s+(.+?)\s*\.?\s*$', re.I)
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X \(?(\d+)\)?$', re.I), 'rows'),
    (re.compile(r'^n X \(?(\d+)\)?$', re.I), 'rows0'),
    (re.compile(r'^\(?(\d+)\)? X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^\(?(\d+)\)? X n$', re.I), 'cols0'),
]
NOADJ = re.compile(r"^(?:top left value (\d+) and )?no two (\d+)'?s adjacent "
                   r"([A-Za-z, ]+?)$", re.I)
DISTINCT = re.compile(r'^no two neighbors of any element equal to each other$', re.I)
RUNBITS = re.compile(r'^no more than ([a-z]+|\d+) of any consecutive ([a-z]+|\d+) bits set '
                     r'in any row or column$', re.I)
INCMOD = re.compile(r'^entries increasing mod (\d+) by ([\d, or]+?) rightwards and '
                    r'downwards,? starting with upper left ([a-z]+|\d+)$', re.I)
SUMLEX = re.compile(r'^row sums nondecreasing and columns lexicographically nondecreasing$',
                    re.I)


def _num(t):
    t = t.strip().lower()
    return int(t) if t.isdigit() else NUM.get(t)


def _dirs(text):
    out, got = [], False
    for w in re.findall(r"[A-Za-z][A-Za-z-]*", text.lower()):
        w = ADVERB.get(w, w)
        if w in ('or', 'and'):
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
    frac = 1
    if m.group(1):
        frac = {'one quarter': 4, 'one half': 2}.get(m.group(1).lower()) or int(m.group(2))
    sh = _shape(m.group(3).strip())
    if sh is None:
        return None
    L, a, tr = sh
    lo, hi = 0, None
    if m.group(4) is None:
        hi = None
    elif m.group(4).lower() == 'binary':
        lo, hi = 0, 1
    else:
        lo, hi = int(m.group(5)), int(m.group(6))
    cond = m.group(7).strip()
    p = {'L': L, 'a': a, 'lo': lo, 'hi': hi, 'transposed': tr, 'frac': frac}
    g = NOADJ.match(cond)
    if g:
        d = _dirs(g.group(3))
        if d is None or hi is None:
            return None
        p.update({'kind': 'noadj', 'val': int(g.group(2)), 'dirs': d,
                  'corner': None if g.group(1) is None else int(g.group(1))})
    elif DISTINCT.match(cond):
        if hi is None:
            return None
        p.update({'kind': 'distinct', 'dirs': DIRS['horizontal'] + DIRS['vertical']})
    elif RUNBITS.match(cond):
        g = RUNBITS.match(cond)
        most, run = _num(g.group(1)), _num(g.group(2))
        if most is None or run is None or not 2 <= run <= 4:
            return None
        p.update({'kind': 'runbits', 'most': most, 'run': run, 'lo': 0, 'hi': 1})
    elif INCMOD.match(cond):
        g = INCMOD.match(cond)
        z = _num(g.group(3))
        steps = [int(x) for x in re.findall(r'\d+', g.group(2))]
        if z is None or not steps:
            return None
        p.update({'kind': 'incmod', 'mod': int(g.group(1)), 'steps': steps, 'corner': z,
                  'lo': 0, 'hi': int(g.group(1)) - 1})
    elif SUMLEX.match(cond):
        if hi is None:
            return None
        p.update({'kind': 'sumlex'})
    else:
        return None
    if p['hi'] is None or not 1 <= p['hi'] - p['lo'] + 1 <= 6 or not 1 <= L <= 7:
        return None
    return p


def build(p, cap=200000):
    L, lo, hi, kind = p['L'], p['lo'], p['hi'], p['kind']
    tr = p.get('transposed', False)
    lines = list(product(range(lo, hi + 1), repeat=L))
    if kind == 'sumlex':
        return _build_sumlex(p, lines, cap)

    def off(d):
        return (d[1], d[0]) if tr else d

    def get(win, ds, df, j):
        line = win[ds + 1]
        jj = j + df
        return None if (line is None or not 0 <= jj < L) else line[jj]

    def ok_mid(win):
        """everything anchored at the middle line of this three-line window"""
        mid = win[1]
        if kind == 'noadj':
            for j in range(L):
                if mid[j] != p['val']:
                    continue
                for d in p['dirs']:
                    ds, df = off(d)
                    if get(win, ds, df, j) == p['val']:
                        return False
            return True
        if kind == 'distinct':
            for j in range(L):
                vals = [get(win, *off(d), j) for d in p['dirs']]
                vals = [v for v in vals if v is not None]
                if len(vals) != len(set(vals)):
                    return False
            return True
        if kind == 'runbits':
            r, most = p['run'], p['most']
            for j in range(L - r + 1):           # a run inside the middle line
                if sum(mid[j:j + r]) > most:
                    return False
            if r == 3:                           # a run across the window, centred here
                for j in range(L):
                    col = [get(win, t, 0, j) for t in (-1, 0, 1)]
                    if None not in col and sum(col) > most:
                        return False
            return True
        # 'incmod': steps rightwards inside the line, and downwards from the line before
        mod, steps = p['mod'], p['steps']
        for j in range(L - 1):
            if (mid[j + 1] - mid[j]) % mod not in steps:
                return False
        before = win[0]
        if before is not None:
            for j in range(L):
                lo_, hi_ = (before[j], mid[j]) if not tr else (before[j], mid[j])
                if (hi_ - lo_) % mod not in steps:
                    return False
        return True

    def start_ok(line):
        c = p.get('corner')
        return c is None or line[0] == c

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    starts = [sid((None, r)) for r in lines if start_ok(r)]
    if not starts:
        return None
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        before, mid = states[u]
        for r in lines:
            if not ok_mid((before, mid, r)):
                continue
            v = sid((mid, r))
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
    end = [1 if ok_mid((b, m, None)) else 0 for b, m in states]
    return lumpauto.lump(adj, start, end)


def _build_sumlex(p, lines, cap):
    """row sums nondecreasing, columns lexicographically nondecreasing

    No window is involved. The state is the previous row's sum together with one flag per
    adjacent column pair saying whether the two columns have been equal in every row so far;
    once a pair separates it never has to be looked at again, and separating the wrong way
    ends the walk.
    """
    L = p['L']
    full = (1 << (L - 1)) - 1

    def step(tie, line):
        """the new tie mask, or None if a pair separates the wrong way"""
        out = tie
        for j in range(L - 1):
            if not (tie >> j) & 1:
                continue
            if line[j] < line[j + 1]:
                out &= ~(1 << j)                 # settled, and settled correctly
            elif line[j] > line[j + 1]:
                return None
        return out

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
        t = step(full, r)
        if t is not None:
            starts.append(sid((sum(r), t)))
    if not starts:
        return None
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        psum, tie = states[u]
        for r in lines:
            if sum(r) < psum:
                continue
            t = step(tie, r)
            if t is None:
                continue
            v = sid((sum(r), t))
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
