#!/usr/bin/env python3
"""Transfer matrix for cell-centred conditions over a NAMED neighbour set.

    Number of n X K 0..m arrays with no element less than a strict majority of its
    horizontal, vertical, diagonal and antidiagonal neighbors.

The condition is imposed on every cell and looks at a set of neighbours the entry names:
horizontal is left and right, vertical is up and down, diagonal is nw-se, antidiagonal is
ne-sw, king-move is all eight. Every such set lies within the three lines i-1, i, i+1, so the
state is a pair of consecutive lines and a step settles the middle one, exactly as for the
king-move engine -- and, as there, the number of neighbours is part of the condition, so the
outside is carried explicitly rather than padded.
"""
import os
import re
import namecanon
from itertools import product

OUT = None
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8}
SETS = {
    'horizontal': [(0, -1), (0, 1)],
    'vertical': [(-1, 0), (1, 0)],
    'diagonal': [(-1, -1), (1, 1)],
    'antidiagonal': [(-1, 1), (1, -1)],
    'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)],
    # the "immediate ..." phrases name a DIRECTED set: only the neighbours already seen in
    # row-major order, which is why they appear alongside the relabelling clause
    'immediate leftward or upward or right-upward antidiagonal': [(0, -1), (-1, 0), (-1, 1)],
    'immediate leftward or upward or left-upward diagonal': [(0, -1), (-1, 0), (-1, -1)],
    'immediate leftward or upward': [(0, -1), (-1, 0)],
}
IMM = sorted((k for k in SETS if k.startswith('immediate')), key=len, reverse=True)
DIM = r'\(?\s*(n\s*\+\s*\d+|n|\d+\s*\+\s*\d+|\d+)\s*\)?'
FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
SHAPE = re.compile(rf'{DIM}\s*X\s*{DIM}\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?\s+with\s+', re.I)
EXC = re.compile(r',?\s*with the exception of exactly (\w+) elements?\s*$', re.I)
_W = r'(?:immediate leftward or upward or right-upward antidiagonal|' \
     r'immediate leftward or upward or left-upward diagonal|immediate leftward or upward|' \
     r'horizontal|vertical|antidiagonal|diagonal|king-move)'
NB = r'(' + _W + r'(?:[, ]+(?:and |or )?' + _W + r')*)'
# a relabelling clause changes what is counted (equality patterns, not arrays) and is not
# handled here; such names are refused rather than silently read as ordinary counts
RELABEL = re.compile(r'new values|values 0\.\.\d+ introduced|introduced in row major', re.I)


def _n(t):
    t = t.strip().lower()
    return int(t) if t.isdigit() else NUM.get(t)


def _offsets(phrase):
    low = phrase.lower()
    for k in IMM:
        if k in low:
            return list(SETS[k])
    # "antidiagonal" contains "diagonal", so the longer word has to come first in the
    # alternation or every antidiagonal would be read as a diagonal
    words = re.findall(r'antidiagonal|king-move|horizontal|vertical|diagonal', low)
    if not words:
        return None
    offs = []
    for w in words:
        for o in SETS[w]:
            if o not in offs:
                offs.append(o)
    return offs


def _tex(phrase):
    return re.sub(r'\s+', ' ', phrase.strip())


def _pred(body):
    """(fn, latex, set phrase, second set phrase or None, invariant) or None.

    ns is the list of neighbour values actually present (the outside contributes nothing).
    `invariant` records whether the condition survives a permutation of the alphabet, which
    is what decides whether the relabelling engine may use it: a condition stated through
    equality alone does, one that names a literal value or compares sizes does not.
    """
    low = re.sub(r'\s+', ' ', body.strip().rstrip('.').lower())

    # "unequal TO a strict majority" but "less THAN a strict majority": the connecting word
    # differs, and leaving it out of the pattern made the equal/unequal forms -- the common
    # ones -- silently unreadable while the less/greater forms parsed.
    m = re.fullmatch(r'no element (equal to|unequal to|less than|greater than) '
                     r'a strict majority of its ' + NB + r' neighbors', low)
    if m:
        kind = m.group(1)
        if kind == 'equal to':
            f = lambda v, ns: sum(1 for u in ns if u == v)
        elif kind == 'unequal to':
            f = lambda v, ns: sum(1 for u in ns if u != v)
        elif kind == 'less than':
            f = lambda v, ns: sum(1 for u in ns if u > v)
        else:
            f = lambda v, ns: sum(1 for u in ns if u < v)
        return ((lambda v, ns, f=f: not (2 * f(v, ns) > len(ns))),
                r'\text{no cell is %s a strict majority of its %s neighbours}'
                % (kind, _tex(m.group(2))), m.group(2), None,
                kind in ('equal to', 'unequal to'))

    m = re.fullmatch(r'no element having a strict majority of its ' + NB +
                     r' neighbors equal to (\w+)', low)
    if m:
        w = _n(m.group(2))
        if w is None:
            return None
        return ((lambda v, ns, w=w: not (2 * sum(1 for u in ns if u == w) > len(ns))),
                r'\text{no cell has a strict majority of its %s neighbours equal to %d}'
                % (_tex(m.group(1)), w), m.group(1), None, False)

    m = re.fullmatch(r'no element (equal|unequal) to more than (\w+) of its ' + NB +
                     r' neighbors', low)
    if m:
        k = _n(m.group(2))
        if k is None:
            return None
        if m.group(1) == 'equal':
            f = lambda v, ns: sum(1 for u in ns if u == v)
        else:
            f = lambda v, ns: sum(1 for u in ns if u != v)
        return ((lambda v, ns, f=f, k=k: f(v, ns) <= k),
                r'\text{no cell is %s to more than %d of its %s neighbours}'
                % (m.group(1), k, _tex(m.group(3))), m.group(3), None, True)

    m = re.fullmatch(r'no (\d+) (?:equal|adjacent) to more than (\w+) of its ' + NB +
                     r' neighbors', low)
    if m:
        V, k = int(m.group(1)), _n(m.group(2))
        if k is None:
            return None
        return ((lambda v, ns, V=V, k=k:
                 v != V or sum(1 for u in ns if u == v) <= k),
                r'\text{every %d has at most %d neighbouring %ds}' % (V, k, V),
                m.group(3), None, False)

    m = re.fullmatch(r'every element equal to exactly ([\w, ]+?) of its ' + NB +
                     r' neighbors', low)
    if m:
        S = [_n(t) for t in re.findall(r'[a-z]+|\d+', m.group(1)) if t not in ('or', 'and')]
        if any(x is None for x in S) or not S:
            return None
        return ((lambda v, ns, S=set(S): sum(1 for u in ns if u == v) in S),
                r'\text{every cell equals exactly }\{%s\}\text{ of its %s neighbours}'
                % (','.join(str(x) for x in sorted(S)), _tex(m.group(2))), m.group(2), None,
                True)

    m = re.fullmatch(r'each element x equal to the number(?: of)? its ' + NB +
                     r' neighbors equal to ([\d,]+) for x=([\d,]+)', low)
    if m:
        vals = [int(t) for t in m.group(2).split(',')]
        xs = [int(t) for t in m.group(3).split(',')]
        if len(vals) != len(xs):
            return None
        table = dict(zip(xs, vals))
        return ((lambda v, ns, table=table: v in table and
                 sum(1 for u in ns if u == table[v]) == v),
                r'\text{a cell of value }x\text{ has exactly }x\text{ neighbours of the '
                r'value paired with }x', m.group(1), None, False)

    m = re.fullmatch(r'no element x\(i,j\) adjacent to value (\d+)-x\(i,j\) ' + NB +
                     r'(?:, and top left element zero)?', low)
    if m:
        K = int(m.group(1))
        return ((lambda v, ns, K=K: all(u != K - v for u in ns)),
                r'\text{no cell }v\text{ has a neighbour equal to }%d-v' % K,
                m.group(2), None, False)

    m = re.fullmatch(r'each element equal to the number (?:of )?its ' + NB +
                     r' neighbors within one of itself', low)
    if m:
        return ((lambda v, ns: v == sum(1 for u in ns if abs(u - v) <= 1)),
                r'\text{each cell }v\text{ equals the number of its neighbours }u'
                r'\text{ with }|u-v|\le1', m.group(1), None, False)

    m = re.fullmatch(r'every nonzero element less than or equal to at least (\w+) ' + NB +
                     r' neighbors', low)
    if m:
        k = _n(m.group(1))
        if k is None:
            return None
        return ((lambda v, ns, k=k: v == 0 or sum(1 for u in ns if v <= u) >= k),
                r'\text{every nonzero }v\text{ has at least %d neighbours }\ge v' % k,
                m.group(2), None, False)

    m = re.fullmatch(r'no element equal to all ' + NB + r' neighbors', low)
    if m:
        return ((lambda v, ns: not (len(ns) > 0 and all(u == v for u in ns))),
                r'\text{no cell equals all its %s neighbours}' % _tex(m.group(1)),
                m.group(1), None, True)

    m = re.fullmatch(r'no element equal to (fewer|more) ' + NB + r' neighbors than ' + NB +
                     r' neighbors', low)
    if m:
        less = m.group(1) == 'fewer'
        return ((lambda v, ns, ns2, less=less:
                 not ((sum(1 for u in ns if u == v) < sum(1 for u in ns2 if u == v)) if less
                      else (sum(1 for u in ns if u == v) > sum(1 for u in ns2 if u == v)))),
                r'\text{no cell equals %s of its %s neighbours than of its %s}'
                % (m.group(1), _tex(m.group(2)), _tex(m.group(3))),
                m.group(2), m.group(3), True)

    m = re.fullmatch(r'no element (greater than|less than|equal to) all ' + NB +
                     r' neighbors or (greater than|less than|equal to) all ' + NB +
                     r' neighbors', low)
    if m:
        k1, k2 = m.group(1), m.group(3)

        def side(kind):
            if kind == 'greater than':
                return lambda v, ns: len(ns) > 0 and all(u < v for u in ns)
            if kind == 'less than':
                return lambda v, ns: len(ns) > 0 and all(u > v for u in ns)
            return lambda v, ns: len(ns) > 0 and all(u == v for u in ns)
        f1, f2 = side(k1), side(k2)
        return ((lambda v, ns, ns2, f1=f1, f2=f2: not (f1(v, ns) or f2(v, ns2))),
                r'\text{no cell is %s all its %s neighbours or %s all its %s neighbours}'
                % (k1, _tex(m.group(2)), k2, _tex(m.group(4))), m.group(2), m.group(4),
                k1 == 'equal to' and k2 == 'equal to')
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
    if RELABEL.search(nm):
        return None
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    frac = 1
    m = FRAC.match(norm)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        norm = norm[m.end():]
    else:
        m = HEAD.match(norm)
        if not m:
            return None
        norm = norm[m.end():]
    m = SHAPE.match(norm)
    if not m:
        return None

    def dv(s):
        s = s.replace(' ', '')
        if 'n' in s:
            return ('n', int(s.split('+')[1]) if '+' in s else 0)
        if '+' in s:
            return ('c', sum(int(x) for x in s.split('+')))
        return ('c', int(s))
    d1, d2 = dv(m.group(1)), dv(m.group(2))
    alpha = 1 if m.group(5) else int(m.group(4))
    rest = norm[m.end():].strip().rstrip('.')
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base = 'rows', d2[1], d1[1]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base = 'cols', d1[1], d2[1]
    else:
        return None
    tl0 = bool(re.search(r'top left element zero', rest, re.I))
    exc = 0
    m = EXC.search(rest)
    if m:
        e = _n(m.group(1))
        if e is None:
            return None
        exc = e
        rest = rest[:m.start()].strip().rstrip(',')
    got = _pred(rest)
    if not got:
        return None
    fn, tex, ph1, ph2, inv = got
    o1 = _offsets(ph1)
    o2 = _offsets(ph2) if ph2 else None
    if o1 is None or (ph2 and o2 is None):
        return None
    # the offsets are named in the ARRAY's frame (horizontal means along a row). When the
    # entry fixes the first dimension -- "2 X n" -- the walk runs along COLUMNS, so the
    # engine's lines are columns and the two components swap. Sets like king-move or
    # horizontal+vertical are invariant under that and hide the error; "horizontal,
    # diagonal and antidiagonal" is not, and it was the DATA check that showed it.
    if walk == 'cols':
        o1 = [(b, a) for (a, b) in o1]
        if o2 is not None:
            o2 = [(b, a) for (a, b) in o2]
    return {'walk': walk, 'fixed': fixed, 'base': base, 'alpha': alpha, 'frac': frac,
            'exc': exc, 'pred': fn, 'tex': tex, 'body': rest,
            'offs': o1, 'offs2': o2, 'two': o2 is not None, 'inv': inv, 'tl0': tl0}


def _gather(p, r, s, t, j, offs):
    W = p['fixed']
    rows = {-1: r, 0: s, 1: t}
    out = []
    for di, dj in offs:
        line = rows[di]
        if line is OUT:
            continue
        k = j + dj
        if 0 <= k < W:
            out.append(line[k])
    return out


def _viol(p, r, s, t):
    W = p['fixed']
    fn = p['pred']
    bad = 0
    for j in range(W):
        v = s[j]
        ns = _gather(p, r, s, t, j, p['offs'])
        if p['two']:
            ok = fn(v, ns, _gather(p, r, s, t, j, p['offs2']))
        else:
            ok = fn(v, ns)
        if not ok:
            bad += 1
    return bad


def build(p, cap=40000):
    W, alpha, E = p['fixed'], p['alpha'], p['exc']
    lines = list(product(range(alpha + 1), repeat=W))
    n = len(lines)
    # Two things can put this build out of reach and the pair-free one within it. The vertex
    # count (alpha+1)^(2W)*(E+1) is the obvious one; the loop below also runs over TRIPLES of
    # lines, which no vertex guard sees, so an entry could pass the guard and then never
    # finish. Either way the pair-free build returns the same counts from far fewer states,
    # and it applies its own cap to the states it actually reaches.
    if n * (n + 1) * (E + 1) > cap or n * n * (n + 1) > 20000000:
        return build_pairfree(p, cap=cap)

    def sid(ri, si, c):
        return (ri * n + si) * (E + 1) + c
    S = (n + 1) * n * (E + 1)
    adj = [[] for _ in range(S)]
    start = [0] * S
    end = [0] * S
    getline = lambda i: OUT if i == n else lines[i]
    for ri in range(n + 1):
        r = getline(ri)
        for si in range(n):
            s = lines[si]
            vend = _viol(p, r, s, OUT)
            row = []
            for ti in range(n):
                row.append(_viol(p, r, s, lines[ti]))
            for c in range(E + 1):
                u = sid(ri, si, c)
                if ri == n and c == 0 and not (p.get('tl0') and s[0] != 0):
                    start[u] = 1
                if c + vend == E:
                    end[u] = 1
                for ti, v in enumerate(row):
                    if c + v <= E:
                        adj[u].append(sid(si, ti, c + v))
    return trim(adj, start, end)


def trim(adj, start, end):
    """Drop every state that no start->accept walk passes through.

    A state not reachable from the starting set, or from which no accepting state can be
    reached, contributes nothing to any walk count, so removing it leaves every value
    iota^T M^j tau unchanged. It is pure bookkeeping, but the annihilation test costs one
    matrix-vector product per iteration and there can be thousands of iterations, so the
    size of the graph is the whole running time.
    """
    S = len(adj)
    fwd = [False] * S
    stack = [i for i in range(S) if start[i]]
    for i in stack:
        fwd[i] = True
    while stack:
        u = stack.pop()
        for k in adj[u]:
            if not fwd[k]:
                fwd[k] = True
                stack.append(k)
    rev = [[] for _ in range(S)]
    for u in range(S):
        for k in adj[u]:
            rev[k].append(u)
    bwd = [False] * S
    stack = [i for i in range(S) if end[i]]
    for i in stack:
        bwd[i] = True
    while stack:
        u = stack.pop()
        for k in rev[u]:
            if not bwd[k]:
                bwd[k] = True
                stack.append(k)
    keep = [i for i in range(S) if fwd[i] and bwd[i]]
    if len(keep) == S:
        return adj, start, end, S
    idx = {v: i for i, v in enumerate(keep)}
    adj2 = [[idx[k] for k in adj[v] if k in idx] for v in keep]
    return adj2, [start[v] for v in keep], [end[v] for v in keep], len(keep)


def matvec(adj, v):
    return [sum(v[k] for k in row) for row in adj]


def terms(adj, start, end, N):
    v = end[:]
    out = []
    for _ in range(N + 1):
        out.append(sum(start[i] * v[i] for i in range(len(v))))
        v = matvec(adj, v)
    return out


def matvec_mod(adj, v, p):
    return [sum(v[k] for k in row) % p for row in adj]


P62 = (1 << 61) - 1          # a Mersenne prime: arithmetic stays in machine-word ints


def threshold(adj, start, end, coeffs, order, S, mod=None):
    """Smallest t with the recurrence holding for every n > t, or None.

    With `mod` set the whole computation runs in Z/mod, which keeps every intermediate a
    machine-sized integer instead of a growing big one. That is a FILTER, not a proof: a
    residual can vanish mod p without vanishing, so a run that succeeds mod p is repeated
    exactly. A run that fails mod p cannot succeed exactly, so the rejection is sound.
    """
    if mod:
        return _threshold_mod(adj, start, end, coeffs, order, S, mod)
    v = end[:]
    powers = [v]
    for _ in range(order):
        v = matvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(len(w)):
            w[j] -= c * pw[j]
    # An entry whose recurrence does NOT hold costs the full 3S iterations before the test
    # can say so, and that is where nearly all the time in a sweep goes. If the recurrence
    # held from index t then the residual would be zero from t-order on, and no threshold
    # anywhere in this roster is past 70; so once the residual is still producing nonzeros
    # after GIVEUP iterations the entry is abandoned as UNRESOLVED. That is a statement
    # about the search, not about the conjecture: nothing is certified on this path.
    GIVEUP = int(os.environ.get('THRGIVEUP', '400'))
    us, zeros, j, last_nz = [], 0, 0, -1
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(start[i] * w[i] for i in range(len(w)))
        us.append(u)
        if u != 0:
            last_nz = j
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        if j > GIVEUP and last_nz > j - 4:
            return None
        w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return order + last


def _threshold_mod(adj, start, end, coeffs, order, S, p):
    v = [x % p for x in end]
    powers = [v]
    for _ in range(order):
        v = matvec_mod(adj, v, p)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        ci = c % p
        for j in range(len(w)):
            w[j] = (w[j] - ci * pw[j]) % p
    GIVEUP = int(os.environ.get('THRGIVEUP', '400'))
    us, zeros, j, last_nz = [], 0, 0, -1
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(start[i] * w[i] for i in range(len(w))) % p
        us.append(u)
        if u != 0:
            last_nz = j
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        if j > GIVEUP and last_nz > j - 4:
            return None
        w = matvec_mod(adj, w, p)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return order + last


# ---------------------------------------------------------------------------
# The pair of lines is more state than the condition can tell apart
#
# `build` above indexes its vertices by (r, s, c): an ordered pair of lines and the count of
# violations so far. That is (alpha+1)^(2W)*(E+1) vertices, and the loop that fills the edges
# runs over triples of lines, so the wider members of this family were never built at all --
# not refused on the cap, simply never finished.
#
# Every offset the entry names has |dj| <= 1, so whether the cell at column j of the middle
# line is violated depends on the three lines only through their windows at j-1, j, j+1.
# Collect, for each j, the indicator over the third line's window; call that tuple P(r, s).
# Then the violation count of any t is read off P, the count at the bottom edge is read off P,
# and the successor (s, t) carries P(s, t), which does not mention r. So two pairs (r, s) and
# (r', s) with the same P are indistinguishable, and the vertex is (s, P, c).
#
# The profile of one column depends only on a pair of windows, so it is computed once per
# such pair -- (alpha+2)^6 of them at worst -- and P is then W lookups.
# ---------------------------------------------------------------------------

def _cell_ok(p, r, s, t, j):
    fn = p['pred']
    v = s[j]
    ns = _gather(p, r, s, t, j, p['offs'])
    if p['two']:
        return fn(v, ns, _gather(p, r, s, t, j, p['offs2']))
    return fn(v, ns)


def build_pairfree(p, cap=200000):
    W, alpha, E = p['fixed'], p['alpha'], p['exc']
    A = alpha + 1
    vals = list(range(A))
    lines = list(product(vals, repeat=W))

    def wins(line):
        """the window (j-1, j, j+1) of a line at each column, None outside the line"""
        if line is OUT:
            return [None] * W
        return [tuple(line[k] if 0 <= k < W else None for k in (j - 1, j, j + 1))
                for j in range(W)]

    # every window that can occur, plus the all-None window a line off the edge presents
    wset = set()
    for line in lines:
        for w in wins(line):
            wset.add(w)
    wset.add(None)
    twins = sorted(wset, key=lambda w: (w is None,
                                        tuple(-1 if v is None else v for v in w) if w else ()))
    tw_ix = {w: i for i, w in enumerate(twins)}

    def mkline(w, j):
        """some line whose window at column j is w; None means the line is off the edge"""
        if w is None:
            return OUT
        base = [0] * W
        for d, v in zip((-1, 0, 1), w):
            k = j + d
            if 0 <= k < W and v is not None:
                base[k] = v
        return tuple(base)

    prof_cache = {}

    def col_profile(rw, sw, j):
        """for column j, which third-line windows leave the middle cell unviolated"""
        key = (rw, sw, j if (j == 0 or j == W - 1) else 1)
        got = prof_cache.get(key)
        if got is None:
            r = mkline(rw, j)
            s = mkline(sw, j)
            got = tuple(0 if _cell_ok(p, r, s, mkline(tw, j), j) else 1 for tw in twins)
            prof_cache[key] = got
        return got

    def profile(r, s):
        rw, sw = wins(r), wins(s)
        return tuple(col_profile(rw[j], sw[j], j) for j in range(W))

    def viol_from(P, t):
        tw = wins(t)
        return sum(P[j][tw_ix[tw[j]]] for j in range(W))

    def vend_from(P):
        return sum(P[j][tw_ix[None]] for j in range(W))

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append(None)
        return i

    starts = []
    for s in lines:
        if p.get('tl0') and s[0] != 0:
            continue
        starts.append(sid((s, profile(OUT, s), 0)))
        if len(states) > cap:
            return None
    if not states:
        return None
    qi = 0
    while qi < len(states):
        s, P, c = states[qi]
        row = []
        for t in lines:
            v = viol_from(P, t)
            if c + v <= E:
                row.append(sid((t, profile(s, t), c + v)))
                if len(states) > cap:
                    return None
        adj[qi] = row
        qi += 1
    S = len(states)
    start = [0] * S
    for i in starts:
        start[i] = 1
    end = [1 if c + vend_from(P) == E else 0 for (s, P, c) in states]
    return adj, start, end, S
