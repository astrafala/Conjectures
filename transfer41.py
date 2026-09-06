#!/usr/bin/env python3
"""Cell conditions over a named neighbour set, decided in a three-row window.

Every condition here looks at one cell and its neighbours, and every neighbour set named lies
within the three rows $i-1,i,i+1$. So the vertices are ordered PAIRS of consecutive rows, an
edge $(p,c)\\to(c,x)$ exists when every cell of the middle row $c$ passes with $p$ above and
$x$ below, an array of $L$ rows is a walk of $L-1$ steps, the first row is tested with nothing
above (which is what makes a state a legal start) and the last with nothing below (which is
what makes a state accepting).

The predicates:

  plusminus   every element is next to itself plus one and to itself minus one, each required
              only when it lies in the alphabet --- the reading `within the range 0..m'
  noadjequal  an extra clause: no element equals a neighbour, over the SAME named set (the
              king-move reading gives 0 where the entry publishes 4)
  complement  no element x is adjacent to the value m-x
  somematch   every element equals at least one of its neighbours
  countself   each element equals the NUMBER of its neighbours equal to itself
  summod      no element equals the sum modulo k of its neighbours
  exactly     no element equals exactly k of its neighbours, for k in a stated set
  allhoriz    no element equal to all its horizontal neighbours or unequal to all its vertical
              neighbours

with the optional trailing clause `with top left element zero'.
"""
import re
from itertools import product

import namecanon
import transfer19

CLASS = {'horizontal': [(0, -1), (0, 1)],
         'vertical': [(-1, 0), (1, 0)],
         'diagonal': [(-1, -1), (1, 1)],
         'antidiagonal': [(-1, 1), (1, -1)],
         'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]}
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}

HEAD = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))?\s*(?:the number of|Number of)\s+', re.I)
SHAPE = re.compile(r'(?:\(\s*n\s*\+\s*1\s*\)|n)\s*X\s*\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?\s+'
                   r'(?:0\.\.(\d+)|(binary)|(integer))\s+arrays\s+with\s+', re.I)
# the same family is also written the other way round, with the FIXED side first:
# "(6+1) X (n+1) 0..1 arrays with ...". Transposing exchanges horizontal with vertical and
# fixes both diagonals, so it is the same problem with two words swapped -- but the shape
# pattern only read one orientation, and fifteen entries sat outside every engine for it.
SHAPE_T = re.compile(r'\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?\s*X\s*'
                     r'(?:\(\s*n\s*\+\s*1\s*\)|n)\s+'
                     r'(?:0\.\.(\d+)|(binary)|(integer))\s+arrays\s+with\s+', re.I)
SWAPWORD = {'horizontal': 'vertical', 'vertical': 'horizontal'}
_W1 = r'(?:horizontal|vertical|diagonal|antidiagonal|king-move)(?:ly)?'
NBW = r'(' + _W1 + r'(?:[, ]+(?:or |and )?' 
NBSET = _W1 + r')*)'
TAIL = re.compile(r',?\s*with (?:top|upper) left element zero\s*$', re.I)
NOADJ = re.compile(r',?\s*with no adjacent elements equal\s*$', re.I)

P_PM = re.compile(r'every element next to itself plus and minus one within the range '
                  r'0\.\.(\d+)\s+' + NBW + NBSET + r'$', re.I)
P_CP = re.compile(r'no element x\(i,j\) adjacent to value (\d+)-x\(i,j\)\s+' + NBW + NBSET
                  + r'$', re.I)
P_SM = re.compile(r'every element equal to some\s+' + NBW + NBSET + r' neighbor$', re.I)
P_CS = re.compile(r'each element equal to the number of\s+' + NBW + NBSET
                  + r' neighbors equal to itself$', re.I)
P_MD = re.compile(r'no element equal to the sum mod(?:ulo)? (\d+) of its\s+' + NBW + NBSET
                  + r' neighbors$', re.I)
P_EX = re.compile(r'no element equal to (?:exactly )?([\w ]+?) ' + NBW + NBSET
                  + r' neighbors$', re.I)
P_AH = re.compile(r'no element equal to all horizontal neighbors or unequal to all vertical '
                  r'neighbors$', re.I)


def _nbs(words):
    out = []
    for w in re.findall(r'antidiagonal|king-move|horizontal|vertical|diagonal', words.lower()):
        out += CLASS[w]
    return sorted(set(out)) or None


def _nums(s):
    out = []
    for t in re.findall(r'[a-z]+|\d+', s.lower()):
        if t in ('or', 'and', 'exactly'):
            continue
        if t.isdigit():
            out.append(int(t))
        elif t in NUM:
            out.append(NUM[t])
        else:
            return None
    return sorted(set(out)) or None


def parse_name(nm):
    nm = namecanon.canon(nm)
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    m = HEAD.match(norm)
    if not m:
        return None
    frac = 1
    if m.group(1):
        frac = 2
    elif m.group(2):
        frac = int(m.group(2))
    elif m.group(0).lower().lstrip().startswith('one quarter'):
        frac = 4
    norm = norm[m.end():]
    trans = False
    m = SHAPE.match(norm)
    if not m:
        m = SHAPE_T.match(norm)
        trans = m is not None
    if not m:
        return None
    W = int(m.group(1)) + (int(m.group(2)) if m.group(2) else 0)
    integer = bool(m.group(5))
    alpha = 1 if m.group(4) else (None if integer else int(m.group(3)))
    body = norm[m.end():].rstrip('. ')
    if trans:
        # swap only the two words transposition actually exchanges
        body = re.sub(r'\b(horizontal|vertical)(ly)?\b',
                      lambda g: SWAPWORD[g.group(1).lower()] + (g.group(2) or ''), body,
                      flags=re.I)
    tl = bool(TAIL.search(body))
    body = TAIL.sub('', body)
    noadj = bool(NOADJ.search(body))
    body = NOADJ.sub('', body).rstrip('. ')
    base = {'W': W, 'frac': frac, 'topleft': tl, 'noadj': noadj, 'trans': trans}
    c = P_PM.match(body)
    if c:
        if alpha is None or int(c.group(1)) != alpha:
            return None
        base.update(kind='plusminus', alpha=alpha, dirs=_nbs(c.group(2)))
    else:
        c = P_CP.match(body)
        if c:
            if alpha is None or int(c.group(1)) != alpha:
                return None
            base.update(kind='complement', alpha=alpha, dirs=_nbs(c.group(2)))
        else:
            c = P_SM.match(body)
            if c:
                if alpha is None:
                    return None
                base.update(kind='somematch', alpha=alpha, dirs=_nbs(c.group(1)))
            else:
                c = P_CS.match(body)
                if c:
                    d = _nbs(c.group(1))
                    if d is None:
                        return None
                    base.update(kind='countself', alpha=len(d), dirs=d)
                else:
                    c = P_MD.match(body)
                    if c:
                        if alpha is None:
                            return None
                        base.update(kind='summod', alpha=alpha, mod=int(c.group(1)),
                                    dirs=_nbs(c.group(2)))
                    else:
                        c = P_AH.match(body)
                        if c:
                            if alpha is None:
                                return None
                            base.update(kind='allhoriz', alpha=alpha,
                                        dirs=CLASS['horizontal'] + CLASS['vertical'])
                        else:
                            c = P_EX.match(body)
                            if not c or alpha is None:
                                return None
                            ks = _nums(c.group(1))
                            if ks is None:
                                return None
                            base.update(kind='exactly', alpha=alpha, ks=ks,
                                        dirs=_nbs(c.group(2)))
    if base.get('dirs') is None or W < 1 or base['alpha'] is None or base['alpha'] < 1:
        return None
    if base['kind'] != 'plusminus' and base['noadj']:
        return None
    return base


def build(p, cap=40000):
    W, A, kind = p['W'], p['alpha'] + 1, p['kind']
    D = [tuple(t) for t in p['dirs']]
    if A ** (2 * W) > 10 * cap:
        return None
    rows = list(product(range(A), repeat=W))
    m = p['alpha']

    def ok_row(above, cur, below):
        for j in range(W):
            v = cur[j]
            N = []
            for (di, dj) in D:
                k = j + dj
                if not 0 <= k < W:
                    continue
                line = above if di < 0 else (cur if di == 0 else below)
                if line is None:
                    continue
                N.append(line[k])
            if kind == 'plusminus':
                if v + 1 <= m and (v + 1) not in N:
                    return False
                if v - 1 >= 0 and (v - 1) not in N:
                    return False
                if p['noadj'] and v in N:
                    return False
            elif kind == 'complement':
                if (m - v) in N:
                    return False
            elif kind == 'somematch':
                if v not in N:
                    return False
            elif kind == 'countself':
                if v != sum(1 for x in N if x == v):
                    return False
            elif kind == 'summod':
                if v == sum(N) % p['mod']:
                    return False
            elif kind == 'exactly':
                if sum(1 for x in N if x == v) in p['ks']:
                    return False
            else:
                hor = [cur[j + d] for d in (-1, 1) if 0 <= j + d < W]
                ver = []
                for line in (above, below):
                    if line is not None:
                        ver.append(line[j])
                if all(x == v for x in hor) or all(x != v for x in ver):
                    return False
        return True

    # a state is an ordered pair (row above, current row); the row above may be absent, which
    # is what lets a walk of no steps describe a ONE-row array
    R = len(rows)
    states = [(pi, ci) for pi in range(-1, R) for ci in range(R)]
    S = len(states)
    if S > cap:
        return None
    sindex = {s: i for i, s in enumerate(states)}
    row_of = lambda i: None if i < 0 else rows[i]
    adj = [[] for _ in range(S)]
    for (pi, ci) in states:
        u = sindex[(pi, ci)]
        for xi in range(R):
            if ok_row(row_of(pi), rows[ci], rows[xi]):
                adj[u].append(sindex[(ci, xi)])
    start = [1 if (pi < 0 and (not p['topleft'] or rows[ci][0] == 0)) else 0
             for (pi, ci) in states]
    end = [1 if ok_row(row_of(pi), rows[ci], None) else 0 for (pi, ci) in states]
    return adj, start, end, S


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
