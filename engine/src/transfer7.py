#!/usr/bin/env python3
"""Hardin arrays counted UP TO RELABELLING: "new values 0..k introduced in row major order".

That clause says the array is written in canonical form, so what is being counted is not
arrays but equality patterns -- set partitions of the cells into at most K = k+1 classes.
A transfer matrix over the alphabet does not see that directly, because the canonical form
is a global condition on the reading order.

The way round it. Let N_j(n) be the number of admissible patterns using exactly j classes
and L_i(n) the number of admissible arrays over a palette of i labels, counted WITHOUT the
canonical-form clause. Every condition in this family is equality-based, so it is invariant
under relabelling and

        L_i(n) = sum_j N_j(n) * i(i-1)...(i-j+1),

each pattern being labelled by an injection of its classes into the palette. Inverting the
falling factorials by finite differences, N_j = (1/j!) sum_i (-1)^(j-i) C(j,i) L_i, and the
entry's count is a(n) = sum_{j<=K} N_j(n), so

        K! * a(n) = sum_{i=0}^{K} C(K,i) * D_{K-i} * L_i(n),

with D_m the derangement numbers -- an integer combination, because
K!/(i!) * sum_{t<=K-i} (-1)^t/t! = C(K,i) D_{K-i}.

Each L_i is an ordinary transfer count over an i-letter alphabet, so a(n) is the same
walk-counting problem on the block-diagonal matrix diag(M_1,...,M_K) with the weights above
in the start vector. Everything after that is the usual annihilation test.
"""
import re
import namecanon
from itertools import product
from math import comb, factorial
import transfer6 as T6

ROWMAJOR = re.compile(r',?\s*(?:and\s+)?(?:new\s+)?values\s+\d+\.\.\d+\s+introduced\s+in\s+'
                      r'row\s+major\s+order\s*$', re.I)


def derange(m):
    d = [1, 0]
    while len(d) <= m:
        n = len(d) - 1
        d.append(n * (d[n] + d[n - 1]))
    return d[m]


def rgs(t):
    """restricted growth string of a tuple: its equality pattern, canonically labelled."""
    seen, out = {}, []
    for x in t:
        if x not in seen:
            seen[x] = len(seen)
        out.append(seen[x])
    return tuple(out)


def pattern_table(fn, alpha):
    """fn as a function of the equality pattern alone, or None if fn is not relabelling
    invariant -- which would make the whole reduction false."""
    tab = {}
    for t in product(range(alpha + 1), repeat=4):
        k = rgs(t)
        v = bool(fn(*t))
        if k in tab and tab[k] != v:
            return None
        tab[k] = v
    return tab


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
    m = ROWMAJOR.search(norm)
    if not m:
        return None
    p = T6.parse_name(norm[:m.start()].rstrip(', ') + '.')
    if not p:
        return None
    tab = pattern_table(p['pred'], p['alpha'])
    if tab is None:
        return None                      # not an equality condition: the reduction fails
    p['ptab'] = tab
    p['K'] = p['alpha'] + 1
    return p


def build(p):
    """One adjacency list for the block-diagonal matrix, plus the weighted start vector."""
    W, K, noadj = p['fixed'], p['K'], p['noadj']
    rowwalk = p['walk'] == 'rows'
    tab = p['ptab']
    adj, start, off = [], [], 0
    blocks = []
    for i in range(1, K + 1):
        vals = list(range(i))
        st = list(product(vals, repeat=W))
        idx = {s: j for j, s in enumerate(st)}
        loc = {}
        for rj in vals:
            for rj1 in vals:
                for sj in vals:
                    L = []
                    for sj1 in vals:
                        a, b, c, d = ((rj, rj1, sj, sj1) if rowwalk else (rj, sj, rj1, sj1))
                        if not tab[rgs((a, b, c, d))]:
                            continue
                        if noadj and (a == b or c == d or a == c or b == d):
                            continue
                        L.append(sj1)
                    loc[(rj, rj1, sj)] = L
        for r in st:
            if W == 1:
                adj.append([off + idx[(v,)] for v in vals if not (noadj and v == r[0])])
                continue
            out = []
            stack = [(0, (v,)) for v in reversed(vals)]
            while stack:
                j, pref = stack.pop()
                if j == W - 1:
                    out.append(off + idx[pref])
                    continue
                for nxt in reversed(loc[(r[j], r[j + 1], pref[j])]):
                    stack.append((j + 1, pref + (nxt,)))
            out.sort()
            adj.append(out)
        wt = comb(K, i) * derange(K - i)
        start += [wt] * len(st)
        blocks.append((i, len(st)))
        off += len(st)
    return adj, start, blocks


def matvec(adj, v):
    return [sum(v[s] for s in row) for row in adj]


def terms(adj, start, N):
    """K! * (number of canonical arrays with j+1 lines), for j = 0..N."""
    v = [1] * len(adj)
    out = []
    for _ in range(N + 1):
        out.append(sum(s * x for s, x in zip(start, v) if s))
        v = matvec(adj, v)
    return out


def threshold(adj, start, coeffs, order):
    S = len(adj)
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
        u = sum(s * x for s, x in zip(start, w) if s)
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


# --------------------------------------------------------------- cell-neighbourhood family
# "no element equal to more than one of its immediate leftward or upward or right-upward
# antidiagonal neighbors" and its relatives. Every neighbour offset used here points
# backwards in row major order, so a cell's condition is settled by the row above and the
# part of its own row to its left: a two-row window is enough, and the first row is the same
# condition with the row above absent.
OFFS = {'leftward': (0, -1), 'upward': (-1, 0),
        'right-upward antidiagonal': (-1, 1), 'left-upward diagonal': (-1, -1),
        'left-upward': (-1, -1), 'right-upward': (-1, 1)}

NB = re.compile(
    r'no element equal to (?:(any)|(?:more than|exactly|fewer than|at least) (\w+)) of '
    r'its immediate ([a-z \-]+?) neighbors?', re.I)
NB2 = re.compile(r'no element equal to any (horizontal or vertical) neighbou?r', re.I)


def _relword(low):
    for w in ('more than', 'exactly', 'fewer than', 'at least'):
        if w in low:
            return w
    return None


def parse_nb(nm):
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
    m = ROWMAJOR.search(norm)
    head = norm
    if m:
        head = norm[:m.start()].rstrip(', ')
    else:
        m2 = re.search(r'(?:new )?values \d+\.\.\d+ introduced in row major order\s*(?:and\s+)?',
                       norm, re.I)
        if not m2:
            return None
        head = norm[:m2.start()].rstrip(', ') + ' ' + norm[m2.end():]
        head = re.sub(r'\s+', ' ', head).strip().rstrip('.')
    m = T6.FRAC.match(head)
    frac = 1
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        head = head[m.end():]
    else:
        m = T6.HEAD.match(head)
        if not m:
            return None
        head = head[m.end():]
    m = T6.SHAPE.match(head)
    if not m:
        return None
    d1, d2 = T6._dimval(m.group(1)), T6._dimval(m.group(2))
    alpha = 1 if m.group(5) else int(m.group(4))
    rest = head[m.end():].strip().rstrip('.')
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base = 'rows', d2[1], d1[1]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base = 'cols', d1[1], d2[1]
    else:
        return None
    low = rest.lower().strip()
    if NB2.fullmatch(low):
        offs, lim, rel = [(0, -1), (-1, 0)], 0, 'more than'
    else:
        m = NB.fullmatch(low)
        if not m:
            return None
        rel = 'more than' if m.group(1) else _relword(low)
        if rel != 'more than':
            return None                        # only the "at most" form is compiled
        lim = 0 if m.group(1) else (T6._numlist(m.group(2)) or [None])[0]
        if lim is None:
            return None
        offs = []
        for w in re.split(r'\s+or\s+', m.group(3).strip()):
            w = w.strip()
            if w not in OFFS:
                return None
            offs.append(OFFS[w])
    # offsets are given in the array's own (row, column) coordinates. The walk runs along
    # rows for an (n+b) X W name and along COLUMNS for a W X (n+b) one, so in the second
    # case the two components swap: a cell's condition must be settled by the lines already
    # laid down, which means every across-walk component must be <= 0.
    offs = offs if walk == 'rows' else [(dj, di) for di, dj in offs]
    if any(dt > 0 for dt, _ in offs):
        rev = [(-dt, du) for dt, du in offs]
        if any(dt > 0 for dt, _ in rev):
            return None                        # mixed signs: needs a two-line window
        offs = rev                             # walk the other way; the count is the same
    if any(dt < -1 for dt, _ in offs):
        return None                            # would need a three-line window
    return {'walk': walk, 'fixed': fixed, 'base': base, 'alpha': alpha, 'K': alpha + 1,
            'frac': frac, 'offs': offs, 'lim': lim,
            'tex': (r'\#\{(d_1,d_2)\in\mathcal N: x_{i+d_1,j+d_2}=x_{i,j}\}\le ' + str(lim)),
            'nbtex': ',\\ '.join(f'({a},{b})' for a, b in offs)}


def _cell_ok(prev, cur, j, W, offs, lim):
    """the condition at cell (i,j); prev is the row above or None for the first row."""
    v = cur[j]
    c = 0
    for di, dj in offs:
        jj = j + dj
        if not (0 <= jj < W):
            continue
        if di == 0:
            if jj > j:
                continue                       # still undetermined: offsets point backwards
            w = cur[jj]
        else:
            if prev is None:
                continue
            w = prev[jj]
        if w == v:
            c += 1
    return c <= lim


def build_nb(p):
    W, K, offs, lim = p['fixed'], p['K'], p['offs'], p['lim']
    adj, start, first, off = [], [], [], 0
    for i in range(1, K + 1):
        vals = list(range(i))
        st = list(product(vals, repeat=W))
        idx = {s: j for j, s in enumerate(st)}
        wt = comb(K, i) * derange(K - i)
        for r in st:
            out = []
            stack = [(0, ())]
            while stack:
                j, pref = stack.pop()
                if j == W:
                    out.append(off + idx[pref])
                    continue
                for v in reversed(vals):
                    nxt = pref + (v,)
                    if _cell_ok(r, nxt + (0,) * (W - j - 1), j, W, offs, lim):
                        stack.append((j + 1, nxt))
            out.sort()
            adj.append(out)
            ok = all(_cell_ok(None, r, j, W, offs, lim) for j in range(W))
            first.append(wt if ok else 0)
            start.append(wt)
        off += len(st)
    return adj, first, start


def terms_nb(adj, first, N):
    v = [1] * len(adj)
    out = []
    for _ in range(N + 1):
        out.append(sum(s * x for s, x in zip(first, v) if s))
        v = matvec(adj, v)
    return out


def threshold_nb(adj, first, coeffs, order):
    return threshold(adj, first, coeffs, order)


# ------------------------------------------------------------------------ lumped chain
# Every condition here is relabelling-invariant, so two rows with the same equality pattern
# have, for each target pattern, the same number of successors carrying it: if r' = sigma(r)
# then s -> sigma(s) is a pattern-preserving bijection between their successor sets. The
# chain is therefore strongly lumpable over the patterns, and
#         1^T M^j 1 = sum_P e_P f_j(P),   e_P = i(i-1)...(i-|P|+1),
# where f_j is the lumped iterate. The lumped state space is the number of set partitions of
# the W columns instead of i^W: at W = 7 and i = 4 that is 350 states rather than 16384.
def patterns(W, maxb):
    out = []

    def go(pref, mx):
        if len(pref) == W:
            out.append(tuple(pref))
            return
        for v in range(min(mx + 1, maxb - 1) + 1):
            go(pref + [v], max(mx, v))
    go([], -1)
    return out


def npatterns(W, maxb):
    """number of set partitions of W cells into at most maxb blocks, WITHOUT enumerating
    them: patterns(W, i) is exponential and a name with a wide fixed dimension would hang
    the sweep before the size cap could refuse it."""
    row = [0] * (W + 1)
    row[0] = 1
    for _ in range(W):
        nxt = [0] * (W + 1)
        for b in range(W):
            if row[b]:
                nxt[b] += row[b] * b
                nxt[b + 1] += row[b]
        row = nxt
    return sum(row[1:maxb + 1])


def falling(i, b):
    r = 1
    for t in range(b):
        r *= i - t
    return r


def _succ_sub(r, vals, W, tab, rowwalk, noadj):
    loc = {}
    for rj in vals:
        for rj1 in vals:
            for sj in vals:
                L = []
                for sj1 in vals:
                    a, b, c, d = ((rj, rj1, sj, sj1) if rowwalk else (rj, sj, rj1, sj1))
                    if not tab[rgs((a, b, c, d))]:
                        continue
                    if noadj and (a == b or c == d or a == c or b == d):
                        continue
                    L.append(sj1)
                loc[(rj, rj1, sj)] = L
    if W == 1:
        return [(v,) for v in vals if not (noadj and v == r[0])]
    out, stack = [], [(0, (v,)) for v in vals]
    while stack:
        j, pref = stack.pop()
        if j == W - 1:
            out.append(pref)
            continue
        for nxt in loc[(r[j], r[j + 1], pref[j])]:
            stack.append((j + 1, pref + (nxt,)))
    return out


def _succ_nb(r, vals, W, offs, lim):
    out, stack = [], [(0, ())]
    while stack:
        j, pref = stack.pop()
        if j == W:
            out.append(pref)
            continue
        for v in vals:
            nxt = pref + (v,)
            if _cell_ok(r, nxt + (0,) * (W - j - 1), j, W, offs, lim):
                stack.append((j + 1, nxt))
    return out


def build_lumped(p, kind):
    W, K = p['fixed'], p['K']
    index, plist = {}, []
    for i in range(1, K + 1):
        for P in patterns(W, i):
            index[(i, P)] = len(plist)
            plist.append((i, P))
    adj, start = [], []
    for i, P in plist:
        vals = list(range(i))
        if kind == 'sub':
            succ = _succ_sub(P, vals, W, p['ptab'], p['walk'] == 'rows', p['noadj'])
        else:
            succ = _succ_nb(P, vals, W, p['offs'], p['lim'])
        cnt = {}
        for s in succ:
            q = rgs(s)
            cnt[q] = cnt.get(q, 0) + 1
        adj.append([(index[(i, q)], c) for q, c in cnt.items()])
        wt = comb(K, i) * derange(K - i) * falling(i, max(P) + 1)
        start.append(wt)
    return adj, start, plist


def wmatvec(adj, v):
    return [sum(c * v[t] for t, c in row) for row in adj]


def _first_weights(adj, start, p):
    """for the neighbour family the FIRST line has no line above it, so only the rows that
    already satisfy the condition on their own may start a walk."""
    W = p['fixed']
    out, k = [], 0
    for i in range(1, p['K'] + 1):
        for P in patterns(W, i):
            ok = all(_cell_ok(None, P, j, W, p['offs'], p['lim']) for j in range(W))
            out.append(start[k] if ok else 0)
            k += 1
    return out


def lterms(adj, start, N, p, kind):
    """K! * (number of canonical arrays with j+1 lines), j = 0..N."""
    sv = _first_weights(adj, start, p) if kind == 'nb' else start
    v = [1] * len(adj)
    out = []
    for _ in range(N + 1):
        out.append(sum(s * x for s, x in zip(sv, v) if s))
        v = wmatvec(adj, v)
    return out


def lthreshold(adj, start, coeffs, order, p, kind):
    S = len(adj)
    sv = _first_weights(adj, start, p) if kind == 'nb' else start
    v = [1] * S
    powers = [v]
    for _ in range(order):
        v = wmatvec(adj, v)
        powers.append(v)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(S):
            w[j] -= c * pw[j]
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= 3 * S + order + 8:
        u = sum(s * x for s, x in zip(sv, w) if s)
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        w = wmatvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return order + last
