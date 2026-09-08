#!/usr/bin/env python3
"""Min-filter images of lexicographically sorted arrays.

    Number of n X 4 arrays of the minimum value of corresponding elements and their horizontal
    or vertical neighbors in a random, but sorted with lexicographically nondecreasing rows and
    nonincreasing columns, 0..1 n X 4 array.

Two things make this different from an ordinary walk count.

**It counts an image.** What varies is the underlying sorted array; what is counted is how many
DIFFERENT filtered arrays come out. Two underlying arrays with the same filtered image count
once, so the obvious graph overcounts. The cure is the subset construction: the filtered row i
is decided by underlying rows i-1, i and i+1, so a pair of consecutive underlying rows is a
state of a nondeterministic machine whose OUTPUT is the filtered array, and the distinct
outputs are the paths of its determinisation, whose states are the sets of pairs still
consistent with the output emitted so far.

**The domain is constrained, and one of the constraints is not row-local.** "Rows in
lexicographically nondecreasing order" compares consecutive rows and needs only the previous
row. "Columns in lexicographically nonincreasing order" compares whole columns read downwards,
left to right -- which looks global, but decomposes: a column pair is either still equal in
every row read so far, or it has already been decided at some earlier row and is never
constrained again. So the state carries one bit per adjacent column pair, and the constraint
becomes local after all.

The reading was pinned against the entry rather than assumed. For A219498 the underlying
arrays with one row are the nonincreasing 4-bit words, their filtered images are 1111, 1100,
1000 and 0000, and the entry's a(1) is 4.
"""
import re
from itertools import product

import namecanon

DIRS = {'horizontal': [(0, -1), (0, 1)], 'vertical': [(-1, 0), (1, 0)],
        'diagonal': [(-1, -1), (1, 1)], 'antidiagonal': [(-1, 1), (1, -1)]}

DIM = r'\(?\s*(?:n\s*\+\s*\d+|n|\d+)\s*\)?'
HEAD = re.compile(
    r'^\s*Number of\s+(' + DIM + r')\s*X\s*(' + DIM + r')\s+arrays of the minimum value of '
    r'corresponding elements and their (.+?) neighbors in a random,? but sorted with '
    r'lexicographically (nondecreasing|nonincreasing) rows and '
    # "nondecreasing rows and columns" states the ordering once and means it for both; 61 of
    # the family are written that way and every one was refused as unreadable
    r'(?:(nondecreasing|nonincreasing) )?columns,\s*(\d+)\.\.(\d+)\s*'
    r'(?:' + DIM + r')\s*X\s*(?:' + DIM + r')\s+array\s*\.?\s*$', re.I)


def _dirs(t):
    """the neighbour set, and whether the entry's own name is defective.

    Two entries read "horizontal, diagonal, diagonal or antidiagonal": a direction word
    written twice, which names no set at all -- four slots with only three distinct words in
    them. There is no literal reading to take. The candidate repairs were each run against the
    entry's own published terms and exactly one reproduced them (the repeat is a slip for
    "vertical"), so the reading is settled by the entry rather than chosen by me. A paper built
    from such a name has to say so, which is what the `repaired` flag is for.
    """
    t = t.lower().replace(' or ', ' ').replace(',', ' ')
    words = re.findall(r'[a-z]+', t)
    if set(words) - set(DIRS):
        return None, False
    got = [d for d in DIRS if d in words]
    if not got:
        return None, False
    if len(words) > len(got):
        # a word is repeated: the entry names one more slot than it has distinct words, and
        # the missing one can only be the direction it does not mention
        missing = [d for d in DIRS if d not in got]
        if len(words) - len(got) != 1 or len(missing) != 1:
            return None, False
        return tuple(sorted(got + missing)), True
    return tuple(sorted(got)), False


def _dv(s):
    s = s.replace(' ', '')
    if 'n' in s:
        return ('n', int(s.split('+')[1]) if '+' in s else 0)
    return ('c', int(s))


def parse_name(nm):
    m = HEAD.match(namecanon.canon(re.sub(r'\s+', ' ', nm).strip()))
    if not m:
        return None
    d1, d2 = _dv(m.group(1)), _dv(m.group(2))
    dirs, repaired = _dirs(m.group(3))
    if not dirs:
        return None
    lo, hi = int(m.group(6)), int(m.group(7))
    if lo != 0 or hi < 1:
        return None
    if d1[0] == 'n' and d2[0] == 'c':
        walk, W, base, tr = 'rows', d2[1], d1[1], False
    elif d2[0] == 'n' and d1[0] == 'c':
        # written W X n: the array is the transpose, so the walk still runs along the growing
        # side and every offset is transposed with it
        walk, W, base, tr = 'cols', d1[1], d2[1], True
    else:
        return None
    if W < 1 or W > 8:
        return None
    roword = m.group(4).lower()
    colord = (m.group(5) or m.group(4)).lower()
    if tr:
        # A name written W X n is the transpose of what this engine walks, and transposing
        # exchanges the two orderings as well as the offsets: the entry's ROWS become this
        # engine's columns. Transposing only the offsets made every one of the 30 such names
        # disagree with its own published terms -- which is exactly what a data check is for.
        roword, colord = colord, roword
    return {'W': W, 'alpha': hi + 1, 'base': base, 'walk': walk, 'transposed': tr,
            'dirs': tuple(dirs), 'roword': roword, 'colord': colord, 'frac': 1,
            'named_dirs': m.group(3).strip(), 'repaired': repaired}


def _offsets(p):
    off = []
    for d in p['dirs']:
        for (a, b) in DIRS[d]:
            off.append((b, a) if p['transposed'] else (a, b))
    return tuple(sorted(set(off)))


def _mf(prev, cur, nxt, W, off):
    """the filtered row for `cur`, with `prev` and `nxt` above and below (None = edge)"""
    out = []
    for j in range(W):
        v = cur[j]
        for (di, dj) in off:
            jj = j + dj
            if not (0 <= jj < W):
                continue
            r = cur if di == 0 else (prev if di < 0 else nxt)
            if r is not None:
                v = min(v, r[jj])
        out.append(v)
    return tuple(out)


def _step_ties(r, ties, colord):
    """the tie vector after appending row r, or None if r breaks the column order"""
    out = []
    for j, tied in enumerate(ties):
        if not tied:
            out.append(False)
            continue
        if r[j] == r[j + 1]:
            out.append(True)
            continue
        if (r[j] < r[j + 1]) if colord == 'nondecreasing' else (r[j] > r[j + 1]):
            out.append(False)
        else:
            return None
    return tuple(out)


def build(p, cap=200000):
    W, A = p['W'], p['alpha']
    if A ** (2 * W) > cap:
        return None
    off = _offsets(p)
    rows = list(product(range(A), repeat=W))
    nd = p['roword'] == 'nondecreasing'
    t0 = (True,) * (W - 1)

    # the nondeterministic states: (previous row, current row, tie vector after current row)
    start = {}                               # first emitted symbol -> set of NFA states
    for r1 in rows:
        s1 = _step_ties(r1, t0, p['colord'])
        if s1 is None:
            continue
        for r2 in rows:
            if (r1 > r2) if nd else (r1 < r2):
                continue
            s2 = _step_ties(r2, s1, p['colord'])
            if s2 is None:
                continue
            start.setdefault(_mf(None, r1, r2, W, off), set()).add((r1, r2, s2))

    # succ is asked for the same NFA state once per DFA state that contains it, and a state
    # sits in many of them: without this the determinisation re-walked every row of the
    # alphabet thousands of times and eight entries was a whole window's work.
    _memo = {}

    def succ(state):
        """emitted symbol -> set of successor NFA states"""
        got = _memo.get(state)
        if got is not None:
            return got
        pr, cu, ts = state
        out = {}
        for nx in rows:
            if (cu > nx) if nd else (cu < nx):
                continue
            tn = _step_ties(nx, ts, p['colord'])
            if tn is None:
                continue
            out.setdefault(_mf(pr, cu, nx, W, off), set()).add((cu, nx, tn))
        _memo[state] = out
        return out

    # determinise: a DFA state is a frozenset of NFA states, and the walk count in the DFA is
    # the count of DISTINCT outputs, which is the whole point
    ini = [frozenset(v) for v in start.values()]
    index = {}
    order = []
    queue = []
    for d in ini:
        if d not in index:
            index[d] = len(order)
            order.append(d)
            queue.append(d)
    adj = {}
    # A determinisation can grow far past anything worth waiting for, and an alarm cannot
    # always interrupt it. The DFA-state cap is checked on every step and is a SETTING, not a
    # wall: the refusal names it so a later run at a higher cap can be seen to be worth making.
    dfacap = int(cap ** 0.5) + 64
    while queue:
        if len(order) > dfacap:
            return None
        d = queue.pop()
        agg = {}
        for st in d:
            for o, s in succ(st).items():
                agg.setdefault(o, set()).update(s)
        row = []
        for o, s in agg.items():
            f = frozenset(s)
            if f not in index:
                index[f] = len(order)
                order.append(f)
                queue.append(f)
            row.append(index[f])
        adj[index[d]] = row
    S = len(order)
    ivec = [0] * S
    for d in ini:
        ivec[index[d]] += 1
    # the last filtered row is emitted with nothing below it, so it is not a step of the walk
    # but a count attached to the state the walk stops in
    tau = [0] * S
    for d, i in index.items():
        tau[i] = len({_mf(pr, cu, None, W, off) for (pr, cu, _) in d})
    # one row is not a walk at all: it has no row below to constrain it
    one = set()
    for r1 in rows:
        if _step_ties(r1, t0, p['colord']) is not None:
            one.add(_mf(None, r1, None, W, off))
    return {'adj': [adj.get(i, []) for i in range(S)], 'ivec': ivec, 'tau': tau,
            'S': S, 'one': len(one)}


def terms(b, N):
    """a(1), a(2), ... by walk step: a(k) = ivec . M^(k-1) . tau, with a(1) counted directly"""
    S = b['S']
    out = [0, b['one']]
    v = list(b['ivec'])
    for k in range(2, N + 1):
        out.append(sum(v[i] * b['tau'][i] for i in range(S)))
        nv = [0] * S
        for i, row in enumerate(b['adj']):
            if v[i]:
                for j in row:
                    nv[j] += v[i]
        v = nv
    return out


def threshold(b, coeffs, order):
    """the last index at which the conjectured recurrence fails, or None if it never holds.

    For n >= 2 the sequence is the walk count ivec . M^(n-2) . tau on S states, so a residual
    of a fixed recurrence is a linear functional of a vector living in an S-dimensional space.
    S consecutive vanishing residuals therefore force every later one to vanish, and that is
    what makes the search finite rather than a sample. a(1) is counted on its own board and is
    included in the residuals, which is why a threshold of 1 or 2 is common in this family.
    """
    S = b['S']
    need = 2 * S + order + 8
    t = terms(b, need)
    last, run = None, 0
    for j in range(order + 1, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S:
        return None                      # not enough vanishing residuals to certify
    return last if last is not None else 0
