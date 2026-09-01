#!/usr/bin/env python3
"""Transfer matrix for cell-centred king-move conditions.

    Number of n X K 0..m arrays with no element equal to more than two of its
    king-move neighbors [, with the exception of exactly one element].

The condition is imposed on every CELL, looking at the 3 X 3 neighbourhood centred on it.
That differs from a 3 X 3 SUBBLOCK condition in one way that matters: cells on the boundary
have fewer than eight neighbours, and the count of neighbours is part of the condition (a
"strict majority" of three is two, of eight is five). Padding the array with zeros would be
wrong for anything that counts the neighbourhood; so the outside is carried explicitly as a
sentinel line and a sentinel column, and a neighbour that falls outside is simply absent.

The neighbourhood of a cell in line i needs lines i-1, i and i+1, so the state is a pair of
consecutive lines and a step evaluates the MIDDLE line of the three:

    (r, s, c) -> (s, t, c')      c' = c + (violations committed by line s)

with r = OUT for the first line and t = OUT for the last, which is why the end of the walk
carries a weight rather than being a plain indicator. The optional clause "with the exception
of exactly E elements" is the counter c, capped at E; states past the budget are dropped.
"""
import re
import namecanon
from itertools import product

OUT = None
NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
       'eight': 8, 'zero': 0}
DIM = r'\(?\s*(n\s*\+\s*\d+|n|\d+\s*\+\s*\d+|\d+)\s*\)?'
FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
SHAPE = re.compile(rf'{DIM}\s*X\s*{DIM}\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?\s+with\s+', re.I)
EXC = re.compile(r',?\s*with the exception of exactly (\w+) elements?\s*$', re.I)


def _n(t):
    t = t.strip().lower()
    if t.isdigit():
        return int(t)
    return NUM.get(t)


def _numset(s):
    out = []
    for t in re.findall(r"[a-z]+|\d+", s.lower()):
        if t in ('or', 'and', 's'):
            continue
        v = _n(t)
        if v is None:
            return None
        out.append(v)
    return sorted(set(out)) or None


def _pred(body):
    """(fn(v, eq, tot) -> ok, latex) or None. eq = neighbours equal to v, tot = neighbours."""
    low = re.sub(r'\s+', ' ', body.strip().rstrip('.').lower())

    m = re.fullmatch(r'no element (equal|unequal) to more than (\w+) of its '
                     r'king-move neighbors', low)
    if m:
        k = _n(m.group(2))
        if k is None:
            return None
        if m.group(1) == 'equal':
            return (lambda v, eq, tot, k=k: eq <= k,
                    r'\#\{\text{neighbours equal}\}\le %d' % k)
        return (lambda v, eq, tot, k=k: tot - eq <= k,
                r'\#\{\text{neighbours unequal}\}\le %d' % k)

    m = re.fullmatch(r'no element (equal|unequal) to a strict majority of its '
                     r'king-move neighbors', low)
    if m:
        if m.group(1) == 'equal':
            return (lambda v, eq, tot: not (2 * eq > tot),
                    r'2\,\#\{\text{neighbours equal}\}\le\#\{\text{neighbours}\}')
        return (lambda v, eq, tot: not (2 * (tot - eq) > tot),
                r'2\,\#\{\text{neighbours unequal}\}\le\#\{\text{neighbours}\}')

    m = re.fullmatch(r'no (\d+) (?:equal to|adjacent to) more than (\w+) of its '
                     r'king-move neighbors', low)
    if m:
        V, k = int(m.group(1)), _n(m.group(2))
        if k is None:
            return None
        return (lambda v, eq, tot, V=V, k=k: v != V or eq <= k,
                r'\text{every }%d\text{ has at most }%d\text{ neighbouring }%d\text{s}'
                % (V, k, V))

    m = re.fullmatch(r"each (\d+) adjacent to ([\w, ]+?) king-move neighboring (\d+)'?s", low)
    if m and m.group(1) == m.group(3):
        V = int(m.group(1))
        S = _numset(m.group(2))
        if not S:
            return None
        return (lambda v, eq, tot, V=V, S=set(S): v != V or eq in S,
                r'\text{every }%d\text{ has }\#\{\text{neighbouring }%d\text{s}\}\in\{%s\}'
                % (V, V, ','.join(str(x) for x in S)))

    m = re.fullmatch(r"no (\d+) adjacent to ([\w, ]+?) king-move neighboring (\d+)'?s", low)
    if m and m.group(1) == m.group(3):
        V = int(m.group(1))
        S = _numset(m.group(2))
        if not S:
            return None
        return (lambda v, eq, tot, V=V, S=set(S): v != V or eq not in S,
                r'\text{every }%d\text{ has }\#\{\text{neighbouring }%d\text{s}\}\notin\{%s\}'
                % (V, V, ','.join(str(x) for x in S)))

    m = re.fullmatch(r'every (\d+) having exactly (\w+) king-move neighbors equal to (\d+)', low)
    if m and m.group(1) == m.group(3):
        V, k = int(m.group(1)), _n(m.group(2))
        if k is None:
            return None
        return (lambda v, eq, tot, V=V, k=k: v != V or eq == k,
                r'\text{every }%d\text{ has exactly }%d\text{ neighbouring }%d\text{s}'
                % (V, k, V))
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
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
    fn, tex = got
    return {'walk': walk, 'fixed': fixed, 'base': base, 'alpha': alpha, 'frac': frac,
            'exc': exc, 'pred': fn, 'tex': tex, 'body': rest}


def _viol(p, r, s, t):
    """violations committed by the middle line s, given the lines above and below."""
    W, fn = p['fixed'], p['pred']
    bad = 0
    for j in range(W):
        v = s[j]
        eq = tot = 0
        # the row offset must be tested by POSITION, not by object identity: when the line
        # above happens to equal the current line they are the same tuple, and an identity
        # test then skipped the cell directly above as if it were the cell itself
        for di, line in ((-1, r), (0, s), (1, t)):
            if line is OUT:
                continue
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                k = j + dj
                if k < 0 or k >= W:
                    continue
                tot += 1
                if line[k] == v:
                    eq += 1
        if not fn(v, eq, tot):
            bad += 1
    return bad


def build(p, cap=40000):
    W, alpha, E = p['fixed'], p['alpha'], p['exc']
    lines = list(product(range(alpha + 1), repeat=W))
    n = len(lines)
    if n * (n + 1) * (E + 1) > cap:
        return None
    # state (r, s, c): r indexes lines or n for OUT, s indexes lines, c is the count so far
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
            for c in range(E + 1):
                u = sid(ri, si, c)
                if ri == n and c == 0:
                    start[u] = 1
                if c + vend == E:
                    end[u] = 1
                for ti in range(n):
                    v = _viol(p, r, s, lines[ti])
                    if c + v <= E:
                        adj[u].append(sid(si, ti, c + v))
    return adj, start, end, S


def matvec(adj, v):
    return [sum(v[k] for k in row) for row in adj]


def terms(adj, start, end, N):
    """terms[j] = number of admissible arrays with j+1 lines."""
    v = end[:]
    out = []
    for _ in range(N + 1):
        out.append(sum(start[i] * v[i] for i in range(len(v))))
        v = matvec(adj, v)
    return out


def threshold(adj, start, end, coeffs, order, S):
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
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(start[i] * w[i] for i in range(len(w)))
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return order + last
