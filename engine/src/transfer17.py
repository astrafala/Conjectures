#!/usr/bin/env python3
"""Generic transfer matrix for Hardin arrays whose condition is local to each 3 X 3 block.

    Number of (n+2) X (K+2) 0..m arrays with every 3 X 3 subblock <P>

A 3 X 3 block spans three consecutive lines, so the state is a PAIR of consecutive lines and
the step (r,s) -> (s,t) tests <P> on every window of three consecutive columns of the three
lines r, s, t. An array with L lines is then a walk of length L-2 on the pair state, so with
V the set of lines and M the adjacency matrix,

    a(L) = 1^T M^(L-2) 1     for L >= 2.

Line entries of a block are written g[i][j] with i the line index within the block and j the
column index, so g[0] is the top line of the block.
"""
import re
import namecanon
from itertools import product

DIM = r'\(?\s*(n\s*\+\s*\d+|n|\d+\s*\+\s*\d+|\d+)\s*\)?'
FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
SHAPE = re.compile(rf'{DIM}\s*X\s*{DIM}\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?\s+with\s+', re.I)
QUANT = re.compile(r'^(every|each|no|all)\s+3\s*X\s*3\s+subblock\s+', re.I)
# the second clause often drops the "3X3 subblock": "... row and column sum nonprime and
# every diagonal and antidiagonal sum prime". Requiring the repeat left those unread.
SPLIT = re.compile(r'\s+and\s+(?:every|each|no|all)\s+(?:3\s*X\s*3\s+)?(?:subblock\s+)?'
                   r'(?=(?:row|column|diagonal|antidiagonal))', re.I)


def _isprime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def _numlist(s):
    out = [int(t) for t in re.findall(r'\d+', s)]
    return sorted(set(out)) if out else None


def rows_of(g):
    return [g[0], g[1], g[2]]


def cols_of(g):
    return [(g[0][j], g[1][j], g[2][j]) for j in range(3)]


def diag_of(g):
    return (g[0][0], g[1][1], g[2][2])


def anti_of(g):
    return (g[0][2], g[1][1], g[2][0])


LINES = {'row': rows_of, 'column': cols_of,
         'diagonal': lambda g: [diag_of(g)], 'antidiagonal': lambda g: [anti_of(g)]}
PERIM = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]


DIRS = {'horizontally': rows_of, 'vertically': cols_of,
        'diagonally': lambda g: [diag_of(g)],
        'nw-to-se diagonally': lambda g: [diag_of(g)],
        'antidiagonally': lambda g: [anti_of(g)],
        'ne-to-sw antidiagonally': lambda g: [anti_of(g)]}
_D = r'(?:nw-to-se diagonally|ne-to-sw antidiagonally|horizontally|vertically|' \
     r'antidiagonally|diagonally)'
DIRLIST = r'(' + _D + r'(?:[, ]+(?:and |or )?' + _D + r')*)'
WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
        'eight': 8, 'nine': 9}


def _tex(phrase):
    return re.sub(r'\s+', ' ', phrase.strip())


def _dirs(phrase):
    out = []
    for w in re.findall(_D, phrase.lower()):
        f = DIRS[w]
        if f not in out:
            out.append(f)
    return out


def _clause(t):
    """one clause of the condition: (fn(g)->bool, latex) or None."""
    t = t.strip().rstrip('.').strip()
    low = re.sub(r'\s+', ' ', t.lower())

    # "each 3X3 subblock having rows and columns in lexicographically nondecreasing order":
    # the three rows of the block, read left to right as 3-tuples, are nondecreasing under the
    # lexicographic order, and so are the three columns read top to bottom. 37 entries state
    # this and no engine read any of them -- the shape, the quantifier and the block size all
    # parsed, and only this predicate was missing from the vocabulary.
    m = re.fullmatch(r'having (rows|columns|rows and columns|columns and rows) in '
                     r'lexicographically (nondecreasing|nonincreasing|increasing|decreasing) '
                     r'order', low)
    if m:
        want, how = m.group(1), m.group(2)
        rows = 'row' in want
        cols = 'column' in want

        def fn(g, rows=rows, cols=cols, how=how):
            seqs = []
            if rows:
                seqs += [tuple(g[i]) for i in range(3)]
            if cols:
                if rows:
                    seqs.append(None)                      # rows and columns are separate lists
                seqs += [tuple(g[i][j] for i in range(3)) for j in range(3)]
            groups, cur = [], []
            for x in seqs:
                if x is None:
                    groups.append(cur); cur = []
                else:
                    cur.append(x)
            groups.append(cur)
            for grp in groups:
                for a, b in zip(grp, grp[1:]):
                    if how == 'nondecreasing' and not a <= b:
                        return False
                    if how == 'nonincreasing' and not a >= b:
                        return False
                    if how == 'increasing' and not a < b:
                        return False
                    if how == 'decreasing' and not a > b:
                        return False
            return True
        which = {'rows': r'\text{rows}', 'columns': r'\text{columns}'}.get(
            want, r'\text{rows and the columns}')
        return fn, (r'\text{the %s of }g\text{ are in lexicographically %s order}'
                    % (which.replace(r'\text{', '').replace('}', ''), how))

    m = re.fullmatch(r'(?:having )?clockwise perimeter pattern ((?:[01]{8}[ ,]*|or )+)', low)
    if m:
        pats = re.findall(r'[01]{8}', m.group(1))
        if not pats:
            return None
        # the perimeter is a CYCLE: the entry names one representative and the pattern is
        # matched wherever the clockwise reading starts, so every rotation counts. Reading
        # the representative literally gives a count far below the entry's own first term
        # (6 against 48 on A259994), which is how this was caught.
        S = set()
        for p in pats:
            w = tuple(int(ch) for ch in p)
            for r in range(8):
                S.add(w[r:] + w[:r])

        def fn(g, S=S):
            return tuple(g[i][j] for i, j in PERIM) in S
        tex = (r'\text{the clockwise perimeter word of }g\text{ is a rotation of one of }\{' +
               ',\\ '.join(p for p in pats) + r'\}')
        return fn, tex

    m = re.fullmatch(r'having three (equal|strictly increasing) elements in a row '
                     + DIRLIST + r'(?:,? exactly (\w+) ways?)?', low)
    if m:
        eq = m.group(1) == 'equal'
        fs = _dirs(m.group(2))
        want = WORD.get(m.group(3)) if m.group(3) else None
        if m.group(3) and want is None:
            return None

        def fn(g, fs=tuple(fs), eq=eq, want=want):
            k = 0
            for f in fs:
                for ln in f(g):
                    if (ln[0] == ln[1] == ln[2]) if eq else (ln[0] < ln[1] < ln[2]):
                        k += 1
            return k == want if want is not None else k >= 1
        howmany = (r'\text{exactly }%d' % want) if want is not None else r'\text{at least one}'
        return fn, (r'%s\text{ of the %s lines of }g\text{ %s}'
                    % (howmany, _tex(m.group(2)),
                       r'\text{is constant}' if eq else r'\text{is strictly increasing}'))

    m = re.fullmatch(r'having (?:three )?equal diagonal elements or (?:three )?equal '
                     r'antidiagonal elements', low)
    if m:
        def fn(g):
            d, a = diag_of(g), anti_of(g)
            return d[0] == d[1] == d[2] or a[0] == a[1] == a[2]
        return fn, r'\text{the diagonal or the antidiagonal of }g\text{ is constant}'

    m = re.fullmatch(r'((?:row|column|diagonal|antidiagonal)(?:[, ]+(?:and )?'
                     r'(?:row|column|diagonal|antidiagonal))*) sum (non)?prime', low)
    if m:
        kinds = re.findall(r'row|column|diagonal|antidiagonal', m.group(1))
        want = m.group(2) is None

        def fn(g, kinds=tuple(kinds), want=want):
            for k in kinds:
                for ln in LINES[k](g):
                    if _isprime(sum(ln)) != want:
                        return False
            return True
        return fn, (r'\text{every %s sum is %sprime}'
                    % (', '.join(kinds), '' if want else 'non'))

    if low in ('having a positive determinant', 'having a negative determinant'):
        pos = low.endswith('positive determinant')

        def fn(g, pos=pos):
            det = (g[0][0]*(g[1][1]*g[2][2]-g[1][2]*g[2][1])
                   - g[0][1]*(g[1][0]*g[2][2]-g[1][2]*g[2][0])
                   + g[0][2]*(g[1][0]*g[2][1]-g[1][1]*g[2][0]))
            return det > 0 if pos else det < 0
        return fn, (r'\det g > 0' if pos else r'\det g < 0')

    if low in ('singular', 'nonsingular'):
        want = (low == 'singular')

        def fn(g, want=want):
            det = (g[0][0]*(g[1][1]*g[2][2]-g[1][2]*g[2][1])
                   - g[0][1]*(g[1][0]*g[2][2]-g[1][2]*g[2][0])
                   + g[0][2]*(g[1][0]*g[2][1]-g[1][1]*g[2][0]))
            return (det == 0) == want
        return fn, (r'\det g = 0' if want else r'\det g \ne 0')

    # "<lines> sum [not] equal to <list>", the lines being any of row/column/diagonal/
    # antidiagonal joined by commas and "and"
    m = re.fullmatch(r'((?:row|column|diagonal|antidiagonal)(?:[, ]+(?:and )?'
                     r'(?:row|column|diagonal|antidiagonal))*) sum (not )?equal to ([\d ,or]+)',
                     low)
    if m:
        kinds = re.findall(r'row|column|diagonal|antidiagonal', m.group(1))
        neg = bool(m.group(2))
        vals = _numlist(m.group(3))
        if not vals or not kinds:
            return None
        S = set(vals)

        def fn(g, kinds=tuple(kinds), S=S, neg=neg):
            for k in kinds:
                for ln in LINES[k](g):
                    if (sum(ln) in S) == neg:
                        return False
            return True
        rel = r'\notin' if neg else r'\in'
        tex = (r'\text{every %s sum} %s \{%s\}' %
               (', '.join(kinds), rel, ','.join(str(v) for v in vals)))
        return fn, tex

    # "<kind> sum <v>" / "no <kind> sum <v>" -- a bare equality or disequality
    m = re.fullmatch(r'(no )?(row|column|diagonal|antidiagonal) sum ([\d ,or]+)', low)
    if m:
        neg = bool(m.group(1))
        kind = m.group(2)
        vals = _numlist(m.group(3))
        if not vals:
            return None
        S = set(vals)

        def fn(g, kind=kind, S=S, neg=neg):
            for ln in LINES[kind](g):
                if (sum(ln) in S) == neg:
                    return False
            return True
        rel = r'\notin' if neg else r'\in'
        tex = r'\text{every %s sum} %s \{%s\}' % (kind, rel, ','.join(str(v) for v in vals))
        return fn, tex
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
    rest = norm[m.end():].strip()
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base = 'rows', d2[1], d1[1]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base = 'cols', d1[1], d2[1]
    else:
        return None
    m = QUANT.match(rest)
    if not m:
        return None
    quant = m.group(1).lower()
    body = rest[m.end():].strip().rstrip('.').strip()
    # ``no 3X3 subblock diagonal sum 1 and no antidiagonal sum 1 and no row sum 0'' is a
    # conjunction of separate prohibitions, not the negation of a conjunction: each ``no''
    # binds its own clause. Negating the whole thing would count arrays in which SOME block
    # violates one of the four, which is a different and much larger set.
    percl = quant == 'no' and re.search(r'\s+and\s+no\s+', body, re.I)
    if percl:
        parts = ['no ' + q.strip() for q in re.split(r'\s+and\s+no\s+', body, flags=re.I)]
    else:
        parts = SPLIT.split(body)
    cls = []
    for i, part in enumerate(parts):
        part = re.sub(r'^subblock\s+', '', part.strip(), flags=re.I)
        got = _clause(part)
        if not got:
            return None
        cls.append(got)
    fns = [c[0] for c in cls]

    def pred(g, fns=tuple(fns)):
        return all(f(g) for f in fns)
    if quant == 'no' and not percl:
        inner = pred

        def pred(g, inner=inner):
            return not inner(g)
    tex = r'\ \text{ and }\ '.join(c[1] for c in cls)
    if quant == 'no' and not percl:
        tex = r'\text{not }\bigl(' + tex + r'\bigr)'
    return {'walk': walk, 'fixed': fixed, 'base': base, 'alpha': alpha, 'frac': frac,
            'quant': quant, 'pred': pred, 'tex': tex, 'body': body}


def build(p, cap=40000):
    """Pair-of-lines digraph. Vertices are ordered pairs (r, s) of admissible lines."""
    W, alpha, fn = p['fixed'], p['alpha'], p['pred']
    rowwalk = p['walk'] == 'rows'
    vals = list(range(alpha + 1))
    if (alpha + 1) ** (2 * W) > cap:
        return None
    lines = list(product(vals, repeat=W))
    st = [(r, s) for r in lines for s in lines]
    idx = {v: i for i, v in enumerate(st)}

    def ok(r, s, t):
        for j in range(W - 2):
            if rowwalk:
                g = ((r[j], r[j + 1], r[j + 2]),
                     (s[j], s[j + 1], s[j + 2]),
                     (t[j], t[j + 1], t[j + 2]))
            else:                       # the walk runs along columns: transpose the block
                g = ((r[j], s[j], t[j]),
                     (r[j + 1], s[j + 1], t[j + 1]),
                     (r[j + 2], s[j + 2], t[j + 2]))
            if not fn(g):
                return False
        return True
    def valid(r, s):
        """the lines t that may follow (r, s), found by growing t one column at a time

        Testing every t against every block costs |lines| * (W-2) per pair, and with sixty
        thousand pairs that is where the whole family stalled. Each block is decided the
        moment its last column arrives, and a prefix the condition already rules out rules
        out every t extending it, so the search prunes instead of enumerating.
        """
        out, pre = [], []

        def rec(j):
            if j == W:
                out.append(tuple(pre))
                return
            for v in vals:
                pre.append(v)
                if j < 2 or blk(r, s, pre, j - 2):
                    rec(j + 1)
                pre.pop()

        rec(0)
        return out

    def blk(r, s, t, j):
        if rowwalk:
            g = ((r[j], r[j + 1], r[j + 2]),
                 (s[j], s[j + 1], s[j + 2]),
                 (t[j], t[j + 1], t[j + 2]))
        else:
            g = ((r[j], s[j], t[j]),
                 (r[j + 1], s[j + 1], t[j + 1]),
                 (r[j + 2], s[j + 2], t[j + 2]))
        return fn(g)

    adj = []
    for (r, s) in st:
        adj.append([idx[(s, t)] for t in valid(r, s)])
    return st, adj


def matvec(adj, v):
    return [sum(v[k] for k in row) for row in adj]


def terms(adj, S, N):
    """terms[j] = number of admissible arrays with j+2 lines."""
    v = [1] * S
    out = []
    for _ in range(N + 1):
        out.append(sum(v))
        v = matvec(adj, v)
    return out


def threshold(adj, S, coeffs, order):
    v = [1] * S
    powers = [v]
    for _ in range(order):
        v = matvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(S):
            w[j] -= c * pw[j]
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(w)
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


# ---------------------------------------------------------------------------
# A build that never materialises the pair state
#
# The vertices above are ordered pairs of lines, so the state count is
# (alpha+1)^(2W): sixteen million at width 6 over four values, which is why the wider
# members of this family were never settled. Almost all of that is redundant, and the
# redundancy has an exact description.
#
# For a pair (r, s) and a window j, whether a line t is admissible at that window depends
# on r and s only through their own j-th windows. Collect, for each j, the set of triples
# (t_j, t_{j+1}, t_{j+2}) the pair allows; call that tuple of sets C(r, s). Then:
#
#   * the lines t that may follow (r, s) are exactly those consistent with every C_j, and
#   * the successor is (s, t), whose own constraint C(s, t) does not mention r at all.
#
# So two pairs (r, s) and (r', s) with the same C are indistinguishable --- same outgoing
# lines, same successors --- and the state may be taken to be (s, C). That is the same
# merge `lumpauto` performs, done before the states exist rather than after.
#
# The start weight of (s, C) is the number of r with C(r, s) = C, and r enters C column by
# column, so those counts come from a small dynamic programme rather than from enumerating
# every r.
# ---------------------------------------------------------------------------

def _windows(line, K):
    return [(line[j], line[j + 1], line[j + 2]) for j in range(K)]


def build_pairfree(p, cap=200000):
    W, alpha, fn = p['fixed'], p['alpha'], p['pred']
    rowwalk = p['walk'] == 'rows'
    A = alpha + 1
    K = W - 2
    if K < 1:
        return None
    vals = list(range(A))
    tris = list(product(vals, repeat=3))
    tri_bit = {t: 1 << i for i, t in enumerate(tris)}

    mask_cache = {}

    def mask(rw, sw):
        """which third windows the pair of windows (rw, sw) allows"""
        m = mask_cache.get((rw, sw))
        if m is None:
            m = 0
            for tw in tris:
                g = (rw, sw, tw) if rowwalk else ((rw[0], sw[0], tw[0]),
                                                  (rw[1], sw[1], tw[1]),
                                                  (rw[2], sw[2], tw[2]))
                if fn(g):
                    m |= tri_bit[tw]
            mask_cache[(rw, sw)] = m
        return m

    def constraint(r, s):
        rw, sw = _windows(r, K), _windows(s, K)
        return tuple(mask(rw[j], sw[j]) for j in range(K))

    def follows(C):
        """the lines consistent with every window constraint, grown column by column"""
        out, pre = [], []

        def rec(i):
            if i == W:
                out.append(tuple(pre))
                return
            for v in vals:
                pre.append(v)
                j = i - 2
                if j < 0 or (C[j] >> (tri_bit[(pre[j], pre[j + 1], pre[j + 2])].bit_length() - 1)) & 1:
                    rec(i + 1)
                pre.pop()

        rec(0)
        return out

    rows = list(product(vals, repeat=W))

    # start weights: for each s, how many r give each constraint, r grown column by column
    startw = {}
    for s in rows:
        sw = _windows(s, K)
        layer = {}
        for a in vals:
            for b in vals:
                layer[((a, b), ())] = layer.get(((a, b), ()), 0) + 1
        for j in range(K):
            nxt = {}
            for (last2, done), cnt in layer.items():
                x, y = last2
                for z in vals:
                    key = ((y, z), done + (mask((x, y, z), sw[j]),))
                    nxt[key] = nxt.get(key, 0) + cnt
            layer = nxt
        for (_, C), cnt in layer.items():
            k = (s, C)
            startw[k] = startw.get(k, 0) + cnt
        if len(startw) > cap:
            return None

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append(None)
        return i

    for k in startw:
        sid(k)
    qi = 0
    while qi < len(states):
        s, C = states[qi]
        row = []
        for t in follows(C):
            row.append(sid((t, constraint(s, t))))
            if len(states) > cap:
                return None
        adj[qi] = row
        qi += 1
    S = len(states)
    start = [startw.get(k, 0) for k in states]
    end = [1] * S
    return adj, start, end, S
