#!/usr/bin/env python3
"""Arrays over a fixed alphabet under a condition on every window of consecutive terms.

    Number of length n+4 0..7 arrays with no pair in any consecutive five terms totalling
      exactly 7.
    Number of length n+3 0..4 arrays with no disjoint pairs in any consecutive four terms
      having the same sum.
    Number of length n+2 0..5 arrays with the medians of every three consecutive terms
      nondecreasing.
    Number of length n+7 0..1 arrays with at most one downstep in every 7 consecutive
      neighbor pairs.
    Number of length n+3 0..7 arrays with every four consecutive terms having the sum of some
      three elements equal to three times the fourth.

Every one of these is the same object: an alphabet 0..K, a window width w, and a predicate on
a w-tuple that must hold at every window (or must fail at every window). The count of arrays of
each length is then a walk count on the (K+1)^(w-1) states that remember the last w-1 symbols,
and det(I - xM) has degree at most that, which is what the residual test needs.

145 entries of this shape carry a conjectured recurrence and no engine read any of them. The
conditions differ only in the predicate, so they are written here as predicates and share
everything else.
"""
import itertools
import re

WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
        'eight': 8, 'nine': 9, 'ten': 10, 'a': 1, 'an': 1}
ORD = {'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6, 'seventh': 7}
MULT = {'twice': 2, 'two times': 2, 'three times': 3, 'four times': 4, 'five times': 5, 'six times': 6,
        'twin': 2}

NAME = re.compile(
    r'^\s*Number of length[- ]\(?n(?:\s*\+\s*(\d+))?\)?\s+0\.\.(\d+)\s+arrays?\s+with\s+(.*?)\s*\.?\s*$',
    re.I)


def _num(s):
    s = s.strip().lower()
    if s.isdigit():
        return int(s)
    return WORD.get(s)


def _pairsum(body):
    m = re.match(r'(no|some) pairs? in (any|every) consecutive (\w+) terms totalling exactly '
                 r'(\d+)$', body)
    if not m:
        return None
    w = _num(m.group(3))
    t = int(m.group(4))
    if not w:
        return None
    want = m.group(1) == 'some'

    def pred(v):
        return any(v[i] + v[j] == t for i in range(len(v)) for j in range(i + 1, len(v)))
    return w, (pred if want else (lambda v: not pred(v)))


def _maxmin(body):
    m = re.match(r'(no|every) (\w+) consecutive terms having the maximum of (any|some) (\w+) '
                 r'terms equal to the minimum of the remaining (\w+)(?: terms)?$', body)
    if not m:
        return None
    w, j, r = _num(m.group(2)), _num(m.group(4)), _num(m.group(5))
    if not (w and j and r) or j + r != w:
        return None
    want = m.group(1) == 'every'

    def pred(v):
        idx = range(len(v))
        for s in itertools.combinations(idx, j):
            rest = [v[i] for i in idx if i not in s]
            if max(v[i] for i in s) == min(rest):
                return True
        return False
    return w, (pred if want else (lambda v: not pred(v)))


def _sumtimes(body):
    m = re.match(r'(no|every) (\w+) consecutive terms having the sum of (any|some) (\w+) '
                 r'elements equal to (twice|three times|four times|five times|six times) the '
                 r'(\w+)$', body)
    if not m:
        return None
    w, j = _num(m.group(2)), _num(m.group(4))
    c = MULT[m.group(5)]
    if not (w and j) or j + 1 != w:
        return None
    want = m.group(1) == 'every'

    def pred(v):
        idx = range(len(v))
        for s in itertools.combinations(idx, j):
            rest = [v[i] for i in idx if i not in s]
            if sum(v[i] for i in s) == c * rest[0]:
                return True
        return False
    return w, (pred if want else (lambda v: not pred(v)))


def _disjoint(body):
    m = re.match(r'(no|some) disjoint pairs in (any|every) consecutive (\w+) terms having the '
                 r'same sum$', body)
    if not m:
        return None
    w = _num(m.group(3))
    if not w or w < 4:
        return None
    want = m.group(1) == 'some'

    def pred(v):
        idx = range(len(v))
        for a, b in itertools.combinations(idx, 2):
            for c, d in itertools.combinations(idx, 2):
                if len({a, b, c, d}) == 4 and v[a] + v[b] == v[c] + v[d]:
                    return True
        return False
    return w, (pred if want else (lambda v: not pred(v)))


def _median(body):
    if body != 'the medians of every three consecutive terms nondecreasing':
        return None

    def med(a, b, c):
        return sorted((a, b, c))[1]
    return 4, (lambda v: med(v[0], v[1], v[2]) <= med(v[1], v[2], v[3]))


def _downstep(body):
    m = re.match(r'at most (\w+) (?:downstep|downsteps) in every (\w+) consecutive neighbor '
                 r'pairs$', body)
    if not m:
        return None
    k, w = _num(m.group(1)), _num(m.group(2))
    if k is None or not w:
        return None
    return w + 1, (lambda v: sum(1 for i in range(len(v) - 1) if v[i] > v[i + 1]) <= k)


def _linear(body):
    """`c times the sum of some J elements equal to d times the sum of the remaining M'.

    The `sum of any two elements equal to twice the third' reader above is the case d = 1 with
    a single element on the right; the corpus also writes both sides as sums and puts a
    multiplier on each. One reader covers every spelling.
    """
    m = re.match(r'(no|every) (\w+) consecutive terms having '
                 r'(?:(twice|two times|three times|four times|five times|six times) )?'
                 r'the sum of (any|some) (\w+) elements equal to '
                 r'(?:(twice|two times|three times|four times|five times|six times) )?'
                 r'the sum of the remaining (\w+)$', body)
    if not m:
        return None
    w, j, r = _num(m.group(2)), _num(m.group(5)), _num(m.group(7))
    if not (w and j and r) or j + r != w:
        return None
    c1 = MULT.get(m.group(3), 1) if m.group(3) else 1
    c2 = MULT.get(m.group(6), 1) if m.group(6) else 1
    want = m.group(1) == 'every'

    def pred(v):
        idx = range(len(v))
        tot = sum(v)
        for s_ in itertools.combinations(idx, j):
            a = sum(v[i] for i in s_)
            if c1 * a == c2 * (tot - a):
                return True
        return False
    return w, (pred if want else (lambda v: not pred(v)))


def _samesum(body):
    """`no|some disjoint triples in any|every consecutive W terms having the same sum', and
    the three-disjoint-pairs spelling of the same thing."""
    m = re.match(r'(no|some) (?:(\w+) )?disjoint (pairs|triples) in (any|every|each) '
                 r'consecutive (\w+) terms having the same sum$', body)
    if not m:
        return None
    howmany = _num(m.group(2)) if m.group(2) else 2
    size = 2 if m.group(3) == 'pairs' else 3
    w = _num(m.group(5))
    if not w or not howmany or howmany * size > w:
        return None
    want = m.group(1) == 'some'

    def pred(v):
        idx = list(range(len(v)))
        for pick in itertools.combinations(idx, howmany * size):
            for grouping in _partitions(list(pick), size):
                sums = {sum(v[i] for i in g) for g in grouping}
                if len(sums) == 1:
                    return True
        return False
    return w, (pred if want else (lambda v: not pred(v)))


def _partitions(items, size):
    """the ways to split `items` into blocks of `size`, each block once."""
    if not items:
        yield []
        return
    first = items[0]
    for rest in itertools.combinations(items[1:], size - 1):
        block = (first,) + rest
        left = [i for i in items[1:] if i not in rest]
        for tail in _partitions(left, size):
            yield [block] + tail


READERS = (_pairsum, _maxmin, _sumtimes, _linear, _samesum, _disjoint, _median, _downstep)


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    base = int(m.group(1)) if m.group(1) else 0
    K = int(m.group(2))
    body = ' '.join(m.group(3).lower().split())
    if K > 9:
        return None
    for r in READERS:
        got = r(body)
        if got:
            w, pred = got
            if w > 8:
                return None
            return {'engine': 'window', 'K': K, 'base': base, 'w': w, 'pred': pred}
    return None


def build(p, cap=200000):
    K, w = p['K'], p['w']
    if (K + 1) ** (w - 1) > cap:
        return None
    A = K + 1
    prev = list(itertools.product(range(A), repeat=w - 1))
    index = {s: i for i, s in enumerate(prev)}
    adj = []
    for s in prev:
        row = []
        for t in range(A):
            if p['pred'](s + (t,)):
                row.append(index[s[1:] + (t,)])
        adj.append(row)
    return {'adj': adj, 'S': len(prev), 'A': A, 'w': w}


def terms(b, N):
    """the number of arrays of each length, from length 1 up.

    Windows shorter than w carry no condition, so the first w - 1 lengths are counted by
    filling the prefix freely; from length w on the walk applies the predicate at every step.
    """
    A, w, S = b['A'], b['w'], b['S']
    out = [A ** L for L in range(1, w)]
    v = [0] * S
    for i in range(S):
        v[i] = 1
    # length w - 1 is the state itself; step once for each further symbol
    cur = list(v)
    for L in range(w - 1, N + 3):
        nx = [0] * S
        tot = 0
        for i, c in enumerate(cur):
            if c:
                for j in b['adj'][i]:
                    nx[j] += c
                    tot += c
        out.append(tot)
        cur = nx
        if len(out) > N + 2:
            break
    return out[:N + 3]


def threshold(b, coeffs, order):
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
