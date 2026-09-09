#!/usr/bin/env python3
"""Arrays of FIXED length over 0..n, counted exactly as a polynomial in n.

    Number of length 6+5 0..n arrays with no six consecutive terms having the maximum of any
      two terms equal to the minimum of the remaining four terms.
    Number of length-5 0..n arrays with no repeated value equal to the previous repeated value.

These are the mirror of the transfer-matrix names: the LENGTH is fixed and the ALPHABET grows.
No walk counts them, and 292 entries of this shape carry a conjectured recurrence that nothing
had ever read.

They are still exactly countable, provided the condition is decided by the ORDER of the terms
alone -- by which are equal, which is larger -- and not by their actual values. Then an array
of length L is described completely by its weak ordering: the ordered set partition of the L
positions into m blocks of equal value, blocks listed in increasing order. Every assignment of
m distinct values from {0..n} to those blocks, in increasing order, gives one array, and there
are C(n+1, m) of them. So

    a(n) = sum_{m=1..L} N_m * C(n+1, m)

where N_m counts the admissible weak orderings with m blocks. That is an exact polynomial in n
of degree at most L -- not a fit, and with no threshold to justify -- so the conjectured
recurrence is decided by the residual test with the bound S = L + 1, since a polynomial of
degree L is annihilated by (x - 1)^(L+1).

N_m is computed by building the ordering one block at a time over subsets of the positions:
3^L work rather than the Fubini number of orderings, which for L = 11 is the difference
between 180 thousand steps and 1.3 billion. A window condition is checked the moment the last
position of that window is placed.

A condition naming an actual difference -- "differing by one", "modulo k" -- is NOT order-only
and is refused here: for those a(n) is not this polynomial and the argument does not hold.
"""
import itertools
import re
from math import comb

import repval
import window

NAME = re.compile(
    r'^\s*Number of length[- ]\(?(\d+(?:\s*\+\s*\d+)?)\)?\s+0\.\.n\s+arrays?\s+with\s+(.*?)\s*\.?\s*$',
    re.I)

# only these readers are order-only: they compare terms with =, < and >, and nothing else
ORDER_ONLY = ('_maxmin', '_median')
ORDER_REL = ('equal to', 'unequal to', 'greater than', 'greater than or equal to',
             'less than', 'less than or equal to')


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    L = sum(int(x) for x in m.group(1).split('+'))
    if not 2 <= L <= 12:
        return None
    body = ' '.join(m.group(2).lower().split())
    for r in (window._maxmin, window._median):
        got = r(body)
        if got:
            w, pred = got[0], got[1]
            return {'engine': 'ordpoly', 'kind': 'window', 'L': L, 'w': w, 'pred': pred}
    # the repeated-value conditions, but only the ones decided by order alone
    f = repval._cond(body, L)
    if f is not None and not re.search(r'mod|plus|differ', body):
        return {'engine': 'ordpoly', 'kind': 'repval', 'L': L, 'f': f}
    mm = re.match(r'no following elements (larger than|greater than or equal to) '
                  r'the first repeated value$', body)
    if mm:
        return {'engine': 'ordpoly', 'kind': 'first', 'L': L,
                'strict': mm.group(1) == 'greater than or equal to'}
    return None


def _count_window(L, w, pred, q):
    """arrays of length L over 0..q-1 with every window of w consecutive satisfying pred."""
    if L < w:
        return q ** L
    from collections import defaultdict
    cur = defaultdict(int)
    for st in itertools.product(range(q), repeat=w - 1):
        cur[st] += 1
    for _ in range(L - w + 1):
        nxt = defaultdict(int)
        for st, c in cur.items():
            for t in range(q):
                if pred(st + (t,)):
                    nxt[st[1:] + (t,)] += c
        cur = nxt
    return sum(cur.values())


def _count_repval(L, f, q):
    """arrays of length L over 0..q-1 whose repeated values satisfy f against the previous."""
    from collections import defaultdict
    cur = defaultdict(int)
    for v in range(q):
        cur[(v, None)] += 1
    for _ in range(L - 1):
        nxt = defaultdict(int)
        for (last, prev), c in cur.items():
            for t in range(q):
                if t == last:
                    if prev is not None and not f(t, prev):
                        continue
                    nxt[(t, t)] += c
                else:
                    nxt[(t, prev)] += c
        cur = nxt
    return sum(cur.values())


def _count_first(L, strict, q):
    """arrays of length L over 0..q-1 with nothing after the first repeat above it."""
    from collections import defaultdict
    cur = defaultdict(int)
    for v in range(q):
        cur[(v, None)] += 1
    for _ in range(L - 1):
        nxt = defaultdict(int)
        for (last, first), c in cur.items():
            for t in range(q):
                if first is not None and (t >= first if strict else t > first):
                    continue
                if t == last and first is None:
                    nxt[(t, t)] += c
                else:
                    nxt[(t, first)] += c
        cur = nxt
    return sum(cur.values())


def build(p, cap=200000):
    L = p['L']
    if p['kind'] == 'window':
        w = p['w']
        if (L + 1) ** (w - 1) > cap:
            return None
        vals = [_count_window(L, w, p['pred'], n + 1) for n in range(L + 1)]
    elif p['kind'] == 'repval':
        vals = [_count_repval(L, p['f'], n + 1) for n in range(L + 1)]
    else:
        vals = [_count_first(L, p['strict'], n + 1) for n in range(L + 1)]
    return {'vals': vals, 'L': L, 'S': L + 1}


def terms(b, N):
    """a(n) for n = 0, 1, 2, ... -- the entry's own index.

    a is a polynomial in n of degree at most L, so its (L+1)-st difference is zero and the
    L + 1 values computed exactly determine every later one. Extending by finite differences
    is that fact used directly; nothing is fitted and nothing is guessed.
    """
    vals = list(b['vals'])
    L = b['L']
    diffs = list(vals)
    for k in range(1, L + 1):
        diffs = [diffs[i + 1] - diffs[i] for i in range(len(diffs) - 1)]
    out = list(vals)
    while len(out) < N + 3:
        row = list(out[-(L + 1):])
        d = [row]
        for _ in range(L):
            row = [row[i + 1] - row[i] for i in range(len(row) - 1)]
            d.append(row)
        nxt = 0
        for k in range(L + 1):
            nxt += d[k][-1]
        out.append(nxt)
    return out


def threshold(b, coeffs, order):
    """the last index at which the conjectured recurrence fails, or None.

    a is a polynomial in n of degree at most L, so it satisfies the recurrence of
    (x - 1)^(L+1); S + order consecutive vanishing residuals therefore settle the claim.
    """
    S = b['S']
    t = terms(b, 2 * S + order + 20)
    last, run = None, 0
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
