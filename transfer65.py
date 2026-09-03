#!/usr/bin/env python3
"""`Number of (n+1) X W 0..m arrays with <a statistic> of each 2 X 2 subblock lexicographically
nondecreasing rowwise and columnwise.'

Each 2 X 2 subblock

        p q
        r s

is reduced to one number by a statistic the entry names --- the determinant $ps-qr$, the
permanent $ps+qr$, the sum of all four, the sum of their squares, or one of the order
statistics: writing $v_1\\le v_2\\le v_3\\le v_4$ for the four values sorted, the entries use
$v_4-v_1$, $v_4+v_1$, $v_2+v_3$, $(v_1+v_4)-(v_2+v_3)$, $v_3-v_2$ and $v_3-v_1$.  An array with
$R$ rows and $W$ columns yields a derived array $D$ with $R-1$ rows and $W-1$ columns, and the
condition is placed on $D$: its rows, read as words and compared lexicographically, are to be
nondecreasing (or nonincreasing) from top to bottom, and its columns likewise from left to
right.  The two axes may be asked for in opposite senses.

Every statistic on the list is unchanged when the subblock is transposed, so an entry that
writes the array the other way round is the same problem with the two axes exchanged.

The ROW comparison is local: row $i$ of $D$ is built from rows $i$ and $i+1$ of the array, so
comparing consecutive rows of $D$ looks at three consecutive rows of the array and no more.
The COLUMN comparison is not local --- which of two columns is the smaller is decided by the
first derived row in which they differ, and that row may be anywhere. What is bounded is the
question still outstanding: for each adjacent pair of columns the state carries one bit saying
whether the pair has been equal in every derived row so far. While the bit is set the pair is
still undecided and the next derived row must not break the order; once it is clear the pair is
settled for good and nothing further is required of it.
"""
import re
from itertools import product

import namecanon
import transfer19

FRAC = re.compile(r'^\s*(?:(Half)|One quarter|1/(\d+))\s+the number of\s+', re.I)
HEAD = re.compile(r'^\s*Number of\s+', re.I)
DIM = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
SHAPE = re.compile(r'^' + DIM + r'\s*X\s*' + DIM +
                   r'\s+(?:(0)\.\.(\d+)|(binary))\s+arrays?\s+with\s+', re.I)

DIRSPEC = (r'(?:in )?lexicographically (nondecreasing|nonincreasing)(?: order)? '
           r'(rowwise|columnwise)(?: and (?:(nondecreasing|nonincreasing) )?'
           r'(rowwise|columnwise))?\s*\.?$')

STATS = [
    (re.compile(r'^the difference between each 2 X 2 subblock maximum and minimum ' + DIRSPEC,
                re.I), 'maxmin'),
    (re.compile(r'^the sum of each 2 X 2 subblock maximum and minimum ' + DIRSPEC, re.I),
     'maxplusmin'),
    (re.compile(r'^the sum of each 2 X 2 subblock two extreme terms minus its two median '
                r'terms ' + DIRSPEC, re.I), 'extmed'),
    (re.compile(r'^the sum of each 2 X 2 subblock two median terms ' + DIRSPEC, re.I), 'med2'),
    (re.compile(r'^the difference of the upper and lower median value of each 2 X 2 subblock '
                + DIRSPEC, re.I), 'upmedlomed'),
    (re.compile(r'^the difference of the upper median and minimum value of each 2 X 2 subblock '
                + DIRSPEC, re.I), 'upmedmin'),
    (re.compile(r'^2 X 2 subblock sum of squares ' + DIRSPEC, re.I), 'squares'),
    (re.compile(r'^2 X 2 subblock sums ' + DIRSPEC, re.I), 'sum'),
]
ROWSCOLS = re.compile(r'^rows and columns of (determinants|permanents) of all 2 X 2 subblocks '
                      r'lexicographically (nondecreasing|nonincreasing)'
                      r'(, and all 2 X 2 permanents nonzero)?\s*\.?$', re.I)


def _stat(name):
    if name == 'det':
        return lambda p, q, r, s: p * s - q * r
    if name == 'per':
        return lambda p, q, r, s: p * s + q * r
    if name == 'sum':
        return lambda p, q, r, s: p + q + r + s
    if name == 'squares':
        return lambda p, q, r, s: p * p + q * q + r * r + s * s
    if name == 'maxmin':
        return lambda p, q, r, s: max(p, q, r, s) - min(p, q, r, s)
    if name == 'maxplusmin':
        return lambda p, q, r, s: max(p, q, r, s) + min(p, q, r, s)

    def order(p, q, r, s):
        return sorted((p, q, r, s))
    if name == 'med2':
        return lambda p, q, r, s: sum(order(p, q, r, s)[1:3])
    if name == 'extmed':
        return lambda p, q, r, s: (lambda v: v[0] + v[3] - v[1] - v[2])(order(p, q, r, s))
    if name == 'upmedlomed':
        return lambda p, q, r, s: (lambda v: v[2] - v[1])(order(p, q, r, s))
    if name == 'upmedmin':
        return lambda p, q, r, s: (lambda v: v[2] - v[0])(order(p, q, r, s))
    return None


STATWORD = {
    'det': (r'\det B=ps-qr', 'the determinant'),
    'per': (r'\operatorname{per}B=ps+qr', 'the permanent'),
    'sum': (r'p+q+r+s', 'the sum of the four entries'),
    'squares': (r'p^2+q^2+r^2+s^2', 'the sum of the squares of the four entries'),
    'maxmin': (r'v_4-v_1', 'the largest entry minus the smallest'),
    'maxplusmin': (r'v_4+v_1', 'the largest entry plus the smallest'),
    'med2': (r'v_2+v_3', 'the sum of the two middle entries'),
    'extmed': (r'(v_1+v_4)-(v_2+v_3)', 'the two extreme entries minus the two middle ones'),
    'upmedlomed': (r'v_3-v_2', 'the upper median minus the lower median'),
    'upmedmin': (r'v_3-v_1', 'the upper median minus the smallest entry'),
}


def parse_name(nm):
    nm = namecanon.canon(nm)
    s = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    frac = 1
    m = FRAC.match(s)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        s = s[m.end():]
    else:
        m = HEAD.match(s)
        if not m:
            return None
        s = s[m.end():]
    m = SHAPE.match(s)
    if not m:
        return None
    rows = m.group(1) or m.group(3)
    cols = m.group(4) or m.group(6)
    if rows is None or cols is None or (rows == 'n') == (cols == 'n'):
        return None
    if rows == 'n':
        W, trans = int(cols) + int(m.group(5) or 0), False
    else:
        W, trans = int(rows) + int(m.group(2) or 0), True
    alpha = 1 if m.group(9) else int(m.group(8))
    body = s[m.end():].strip()

    nonzero = False
    m = ROWSCOLS.match(body)
    if m:
        stat = 'det' if m.group(1).lower().startswith('deter') else 'per'
        up = m.group(2).lower() == 'nondecreasing'
        rowdir = coldir = up
        nonzero = bool(m.group(3))
        if nonzero and stat != 'per':
            return None
    else:
        for rx, name in STATS:
            m = rx.match(body)
            if m:
                break
        else:
            return None
        stat = name
        d1 = m.group(1).lower() == 'nondecreasing'
        ax1 = m.group(2).lower()
        ax2 = m.group(4)
        if ax2 is None:
            return None                       # a single axis is not one of the wordings seen
        d2 = d1 if m.group(3) is None else m.group(3).lower() == 'nondecreasing'
        ax2 = ax2.lower()
        if ax1 == ax2:
            return None
        rowdir = d1 if ax1 == 'rowwise' else d2
        coldir = d1 if ax1 == 'columnwise' else d2
    if trans:                       # every statistic on the list is transpose-invariant, so
        rowdir, coldir = coldir, rowdir            # transposing only exchanges the two axes
    if W < 2:
        return None
    return {'W': W, 'alpha': alpha, 'stat': stat, 'rowdir': rowdir, 'coldir': coldir,
            'nonzero': nonzero, 'trans': trans, 'frac': frac}


def build(p, cap=400000):
    W, A = p['W'], p['alpha'] + 1
    f = _stat(p['stat'])
    rowdir, coldir, nonzero = p['rowdir'], p['coldir'], p['nonzero']
    if A ** W > 40000:
        return None
    rows = list(product(range(A), repeat=W))
    nb = max(W - 2, 0)
    ones = (1,) * nb

    def derive(u, v):
        return tuple(f(u[j], u[j + 1], v[j], v[j + 1]) for j in range(W - 1))

    idx, order, adj = {}, [], []

    def push(st):
        if st not in idx:
            idx[st] = len(order)
            order.append(st)
            adj.append(None)
        return idx[st]

    push((None, None, ones))
    t = 0
    while t < len(order):
        u, dp, bits = order[t]
        out = []
        if u is None:
            for v in rows:
                out.append(push((v, None, bits)))
        else:
            for v in rows:
                D = derive(u, v)
                if nonzero and any(x == 0 for x in D):
                    continue
                if dp is not None:
                    if rowdir:
                        if list(dp) > list(D):
                            continue
                    else:
                        if list(dp) < list(D):
                            continue
                nb2 = list(bits)
                ok = True
                for j in range(nb):
                    if not bits[j]:
                        continue
                    if D[j] == D[j + 1]:
                        continue
                    if (D[j] < D[j + 1]) != coldir:
                        ok = False
                        break
                    nb2[j] = 0
                if not ok:
                    continue
                out.append(push((v, D, tuple(nb2))))
        adj[t] = out
        t += 1
        if len(order) > cap:
            return None
    n = len(order)
    st = [0] * n
    st[0] = 1
    return adj, st, [1] * n, n


matvec = transfer19.matvec
terms = transfer19.terms
threshold = transfer19.threshold
