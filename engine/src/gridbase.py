#!/usr/bin/env python3
"""The cross-BASE identity on the bounded-difference square arrays, and its proof.

    Number of n X n arrays with entries in 1..5 in which adjacent entries differ by 3 or less
    (adjacent means in x or y directions).
      [Empirical] a(base+1,n,diff) = a(base,n,diff) + F(n,diff) for base >= 2.diff.(n-1) and
      F(n,diff) = (n=2, A063496(diff+1)) (n=3, A068744(diff+1)) (n=4, A068745(diff+1)) ...

This is the same shape as the circular-digit family `circbase` settles, one dimension up, and
the same four lines prove it. Write T(b, d, n) for the number of n X n arrays with entries in
1..b whose orthogonally adjacent entries differ by at most d.

  1. T(b+1, d, n) - T(b, d, n) counts exactly the admissible arrays over {1,...,b+1} that USE
     the value b+1, since the others are precisely the arrays over {1,...,b}.

  2. Every admissible array has max - min <= 2*d*(n-1). Take a cell attaining the maximum and
     one attaining the minimum; the grid graph on n X n cells with orthogonal adjacency has
     diameter 2(n-1), so some path between them has length at most 2(n-1), and along a path of
     length L the value changes by at most d*L.

  3. An array using b+1 has maximum b+1, so by 2 all its values lie in
     [b+1-2*d*(n-1), b+1]. When b >= 2*d*(n-1) that whole window lies inside {1,...,b+1}, so
     the count in 1 is the number of admissible arrays over Z with maximum 0 -- a number that
     does not depend on b at all. That is F(n, d), and it is what the entry's named reference
     sequences tabulate.

So the threshold in the entry's own line is exactly the diameter bound, and it is sharp: the
identity is checked here at the threshold and one above it, and it FAILS below it (at
base = 5, diff = 3, n = 3 the difference is 964,755 where F is 1,253,329).

One reading detail that matters. The line names its reference as "A063496(diff+1)", and those
sequences do not share an offset -- A063496 has offset 1, A068744 offset 0. The index is
POSITIONAL: the (diff+1)-th term as listed. Both readings agree for n = 2 and only the
positional one is right for n = 3, where F(3,2) = 87825 is the third term of A068744 and
A068744(3) under its own offset is 1253329. The paper states it positionally.
"""
import re

import conjlines
import localentry as LE

NAME = re.compile(
    r'^Number of n\s*X\s*n arrays with entries in 1\.\.(\d+) in which adjacent entries '
    r'differ by (\d+) or less', re.I)

LINE = re.compile(r'a\(base\s*\+\s*1\s*,\s*n\s*,\s*diff\)\s*=\s*a\(base\s*,\s*n\s*,\s*diff\)'
                  r'\s*\+\s*F\(\s*n\s*,\s*diff\s*\)', re.I)
RANGE = re.compile(r'for\s+base\s*>=\s*2[.\s*]*diff[.\s*]*\(\s*n\s*-\s*1\s*\)', re.I)
REFS = re.compile(r'\(\s*n\s*=\s*(\d+)\s*,\s*(A\d{6})\s*\(\s*diff\s*\+\s*1\s*\)\s*\)', re.I)


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    return {'engine': 'gridbase', 'b': int(m.group(1)), 'd': int(m.group(2))}


def claim(anum, e=None):
    e = e or LE.get(anum)
    for L in conjlines.lines(e):
        t = ' '.join(L.split())
        if LINE.search(t):
            return {'line': t, 'range_ok': bool(RANGE.search(t)),
                    'refs': {int(a): b for a, b in REFS.findall(t)}}
    return None


def _rows(b, d, n):
    from itertools import product
    return [r for r in product(range(b), repeat=n)
            if all(abs(r[j] - r[j + 1]) <= d for j in range(n - 1))]


def T(b, d, n):
    """arrays n X n over an alphabet of size b, orthogonal neighbours differing by <= d"""
    rows = _rows(b, d, n)
    cur = {r: 1 for r in rows}
    for _ in range(n - 1):
        nxt = {}
        for prev, w in cur.items():
            for r in rows:
                if all(abs(prev[j] - r[j]) <= d for j in range(n)):
                    nxt[r] = nxt.get(r, 0) + w
        cur = nxt
    return sum(cur.values())


def F(d, n):
    """admissible n X n arrays over Z with maximum 0: the translation classes"""
    span = 2 * d * (n - 1)
    from itertools import product
    rows = [r for r in product(range(-span, 1), repeat=n)
            if all(abs(r[j] - r[j + 1]) <= d for j in range(n - 1))]

    def upto(mx):
        cur = {r: 1 for r in rows if max(r) <= mx}
        for _ in range(n - 1):
            nxt = {}
            for prev, w in cur.items():
                for r in rows:
                    if max(r) <= mx and all(abs(prev[j] - r[j]) <= d for j in range(n)):
                        nxt[r] = nxt.get(r, 0) + w
            cur = nxt
        return sum(cur.values())
    return upto(0) - upto(-1)


def nmax(b, d):
    """the largest n for which the entry's own threshold 2*d*(n-1) <= b holds"""
    return b // (2 * d) + 1


def depth(b, d, budget=3_000_000):
    """how many rows of the array the direct count can afford.

    T(b, d, n) is a row-pair dynamic program over the admissible rows, so it costs about
    |rows|^2 per step and |rows| grows like b*(2d+1)^(n-1) until the alphabet saturates. At
    b = 12, d = 9 every one of the 20,736 rows of length 4 is admissible and the pair loop is
    four hundred million steps, which is why an unbounded depth stalled the scan. The depth is
    chosen from the cost rather than fixed, and what was actually verified is recorded on the
    hit so the paper can say so.
    """
    n = 1
    while n < 6:
        rows = 1
        for _ in range(n - 1):
            rows = min(rows * (2 * d + 1), b ** n)
        rows = min(b * rows, b ** n)
        if rows * rows * max(1, n - 1) > budget:
            return max(n - 1, 2)
        n += 1
    return 5


def check(anum, ncap=None):
    """verify the model against DATA and the identity over the range the entry claims it"""
    e = LE.get(anum)
    p = parse_name(e['name'])
    if p is None:
        return None
    cl = claim(anum, e)
    if cl is None:
        return None
    b, d = p['b'], p['d']
    if ncap is None:
        ncap = depth(b, d)
    if not cl['range_ok']:
        return {'anum': anum, 'FAILS': True,
                'why': 'the range clause is not the "base >= 2.diff.(n-1)" form this proves'}
    data = [int(x) for x in e['data'].split(',') if x.strip()]
    off = int(e['offset'].split(',')[0])
    ncheck = min(len(data) + off - 1, ncap)
    model = [T(b, d, n) for n in range(off, ncheck + 1)]
    if model != data[:len(model)]:
        return {'anum': anum, 'FAILS': True, 'why': 'model does not match DATA'}
    # the identity, at and above the entry's own threshold, for every n it covers
    bad = []
    for n in range(2, min(nmax(b, d), ncap) + 1):
        if T(b + 1, d, n) - T(b, d, n) != F(d, n):
            bad.append(n)
    # and below it, the identity must FAIL -- the threshold is claimed sharp
    sharp = None
    n0 = nmax(b, d) + 1
    if n0 <= ncap and 2 * d * (n0 - 1) > b:
        sharp = T(b + 1, d, n0) - T(b, d, n0) != F(d, n0)
    # the named reference sequences, read POSITIONALLY, must be the F this proves
    refbad = []
    for n, ref in sorted(cl['refs'].items()):
        if n > ncap:
            continue
        r = LE.get(ref)
        if not r:
            continue
        vals = [int(x) for x in r['data'].split(',') if x.strip()]
        if d + 1 <= len(vals) and vals[d] != F(d, n):
            refbad.append(ref)
    return {'anum': anum, 'b': b, 'd': d, 'nmax': nmax(b, d), 'checked': min(nmax(b, d), ncap),
            'bad': bad, 'sharp': sharp, 'refbad': refbad, 'line': cl['line'],
            'refs': cl['refs'], 'nterms': len(data), 'offset': off, 'terms_checked': len(model)}
