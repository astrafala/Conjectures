#!/usr/bin/env python3
"""Cell conditions over an explicit alphabet, two-line window, no relabelling.

Three name shapes, all saying the same kind of thing about every cell of the array:

  * "each element equal to the number of its horizontal and vertical neighbors unequal to
    itself"                                        -- the cell's VALUE is the neighbour count
  * "every element equal to 0, 1 or 4 horizontally, vertically or antidiagonally adjacent
    elements, with upper left element zero"        -- the count lies in a stated set
  * "each 1 adjacent to 0 or 2 king-move neighboring 1s"
    "every 1 horizontally, diagonally or antidiagonally adjacent to 1 neighboring 1"
                                                   -- the same, imposed only on the cells
                                                      carrying a stated value

Every neighbour set here reaches one line up and one line down, so the vertices are ordered
pairs of consecutive lines, (p,c) -> (c,x) is an edge when every cell of c passes with p
above and x below, and the first and last lines are tested with one neighbour line missing.
"""
import re
from itertools import product
import transfer6 as T6

H = [(0, -1), (0, 1)]
V = [(-1, 0), (1, 0)]
D = [(-1, -1), (1, 1)]
A = [(-1, 1), (1, -1)]
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8, 'no': 0}


def _nums(s):
    out = []
    for t in re.findall(r'[a-z]+|\d+', s.lower()):
        if t in ('or', 'and', ','):
            continue
        if t in NUM:
            out.append(NUM[t])
        elif t.isdigit():
            out.append(int(t))
        else:
            return None
    return sorted(set(out)) or None


DIRS = {'horizontal': H, 'vertical': V, 'diagonal': D, 'antidiagonal': A,
        'horizontally': H, 'vertically': V, 'diagonally': D, 'antidiagonally': A}


def _nbset(txt):
    """'horizontally, vertically or antidiagonally' / 'king-move' -> offsets."""
    t = txt.strip().lower()
    if t in ('king-move', 'king move'):
        return H + V + D + A
    words = [w for w in re.split(r'[,\s]+|\bor\b|\band\b', t) if w]
    offs = []
    for w in words:
        if w not in DIRS:
            return None
        for o in DIRS[w]:
            if o not in offs:
                offs.append(o)
    return offs or None


DIRWORDS = r'(?:king-move|(?:horizontal|vertical|diagonal|antidiagonal)(?:ly)?' \
           r'(?:[,\s]+(?:or\s+|and\s+)?(?:horizontal|vertical|diagonal|antidiagonal)(?:ly)?)*)'

SELF = re.compile(r'(?:each|every) element equal to the number (?:of )?its (' + DIRWORDS +
                  r') neighbou?rs (equal|unequal) to itself', re.I)
COUNT = re.compile(r'(?:each|every) element (equal|unequal) to ([\w,\s]+?) (' + DIRWORDS +
                   r') adjacent elements(, with upper left element zero)?', re.I)
VALUE = re.compile(r'(?:each|every) (\d+) (?:(' + DIRWORDS + r') )?adjacent to ([\w,\s]+?) '
                   r'(?:(' + DIRWORDS + r') )?neighbou?ring (\d+)s?', re.I)


def _cond(rest):
    low = rest.strip().rstrip('.').lower()
    m = SELF.fullmatch(low)
    if m:
        offs = _nbset(m.group(1))
        if not offs:
            return None
        uneq = m.group(2) == 'unequal'
        return {'mode': 'self', 'offs': offs, 'uneq': uneq, 'ul0': False,
                'tex': (r'x_{t,u}=\#\{\text{neighbours with a value }'
                        + ('different from' if uneq else 'equal to') + r'\ x_{t,u}\}')}
    m = COUNT.fullmatch(low)
    if m:
        sense, nums, dirs, ul0 = m.groups()
        offs = _nbset(dirs)
        v = _nums(nums)
        if not offs or not v:
            return None
        return {'mode': 'count', 'offs': offs, 'uneq': sense == 'unequal',
                'set': v, 'ul0': bool(ul0),
                'tex': (r'\#\{\text{neighbours with a value }'
                        + ('different from' if sense == 'unequal' else 'equal to')
                        + r'\ x_{t,u}\}\in\{' + ','.join(map(str, v)) + r'\}')}
    m = VALUE.fullmatch(low)
    if m:
        val, d1, nums, d2, val2 = m.groups()
        if val != val2:
            return None
        offs = _nbset(d1 or d2 or 'king-move')
        v = _nums(nums)
        if not offs or not v or (d1 and d2):
            return None
        return {'mode': 'value', 'offs': offs, 'val': int(val), 'set': v, 'ul0': False,
                'tex': (r'x_{t,u}=' + val + r'\ \Rightarrow\ \#\{\text{neighbours equal to }'
                        + val + r'\}\in\{' + ','.join(map(str, v)) + r'\}')}
    return None


def parse_name(nm):
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
    frac = 1
    m = T6.FRAC.match(norm)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        norm = norm[m.end():]
    else:
        m = T6.HEAD.match(norm)
        if not m:
            return None
        norm = norm[m.end():]
    from transfer8 import SHAPE2, _dim
    m = SHAPE2.match(norm)
    if not m:
        return None
    d1, d2 = _dim(m.group(1)), _dim(m.group(2))
    alpha = 1 if m.group(5) else int(m.group(4))
    rest = norm[m.end():].strip().rstrip('.')
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base, mult = 'rows', d2[1], d1[1], d1[2]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base, mult = 'cols', d1[1], d2[1], d2[2]
    else:
        return None
    c = _cond(rest)
    if not c:
        return None
    if walk == 'cols':
        c = dict(c, offs=[(du, dt) for dt, du in c['offs']])
    c.update({'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
              'frac': frac, 'rest': rest})
    return c


def cell_ok(above, cur, below, u, W, p):
    v = cur[u]
    if p['mode'] == 'value' and v != p['val']:
        return True
    eq = 0
    for dt, du in p['offs']:
        uu = u + du
        if not (0 <= uu < W):
            continue
        L = cur if dt == 0 else (above if dt < 0 else below)
        if L is None:
            continue
        if p['mode'] == 'value':
            if L[uu] == p['val']:
                eq += 1
        elif L[uu] == v:
            eq += 1
        elif p.get('uneq'):
            eq += 0
    if p['mode'] in ('self', 'count') and p.get('uneq'):
        tot = 0
        for dt, du in p['offs']:
            uu = u + du
            if not (0 <= uu < W):
                continue
            L = cur if dt == 0 else (above if dt < 0 else below)
            if L is None:
                continue
            tot += 1
        eq = tot - eq
    if p['mode'] == 'self':
        return v == eq
    return eq in p['set']


def line_ok(above, cur, below, W, p):
    return all(cell_ok(above, cur, below, u, W, p) for u in range(W))


def build(p, cap=200000):
    W, al = p['fixed'], p['alpha']
    lines = list(product(range(al + 1), repeat=W))
    if len(lines) ** 2 > cap:
        return None
    idx = {}
    st = []
    for a in lines:
        for b in lines:
            idx[(a, b)] = len(st)
            st.append((a, b))
    adj, start, end = [], [], []
    for (a, b) in st:
        row = []
        for x in lines:
            if line_ok(a, b, x, W, p):
                row.append(idx[(b, x)])
        adj.append(row)
        s = line_ok(None, a, b, W, p) and (not p['ul0'] or a[0] == 0)
        start.append(1 if s else 0)
        end.append(1 if line_ok(a, b, None, W, p) else 0)
    return adj, start, end, st


def matvec(adj, v):
    return [sum(v[t] for t in row) for row in adj]


def singles(p):
    W, al = p['fixed'], p['alpha']
    n = 0
    for r in product(range(al + 1), repeat=W):
        if line_ok(None, r, None, W, p) and (not p['ul0'] or r[0] == 0):
            n += 1
    return n


def avals(adj, start, end, p, nmax):
    mult, base = p['mult'], p['base']
    Lmax = mult * nmax + base
    # an array with no lines: the empty array, counted once, which is what the entries with
    # offset 0 record as a(0)
    vals = {0: p['frac'], 1: singles(p)}
    g = end[:]
    L = 2
    while L <= Lmax:
        vals[L] = sum(s * x for s, x in zip(start, g) if s)
        g = matvec(adj, g)
        L += 1
    return [vals.get(mult * n + base) if mult * n + base >= 0 else None
            for n in range(nmax + 1)]


def threshold(adj, start, end, coeffs, order, p):
    import time as _t
    mult, base = p['mult'], p['base']
    S = len(adj)
    n_lo = 0
    while mult * n_lo + base < 2:
        n_lo += 1
    o = mult * n_lo + base - 2
    h = end[:]
    for _ in range(o):
        h = matvec(adj, h)
    powers = [h]
    for _ in range(order):
        for _ in range(mult):
            h = matvec(adj, h)
        powers.append(h)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(S):
            w[j] -= c * pw[j]
    t0 = _t.time()
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= 2 * S + order + 8:
        if _t.time() - t0 > 420:
            return None
        u = sum(s * x for s, x in zip(start, w) if s)
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        for _ in range(mult):
            w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return n_lo + order + last
