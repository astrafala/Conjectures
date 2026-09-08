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
    got = parse_neigh(nm)
    if got:
        return got
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return parse_name2(nm)
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
            return {'engine': 'window', 'K': K, 'base': base, 'w': w, 'pred': pred,
                    'vals': list(range(K + 1))}
    return None


# The same objects are named a second way, with the alphabet written as a range that may be
# negative and the length written as a count of elements:
#
#   Number of 0..7 arrays x(0..n+1) of n+2 elements without any interior element greater
#     than both neighbors or less than both neighbors.
#   Number of -5..5 arrays of length n with each element differing from at least one
#     neighbour by 2 or more.
#
# 164 entries are written like that, and the reader above sees none of them.
NAME2 = re.compile(
    r'^\s*Number of (-?\d+)\.\.(-?\d+) arrays?\s*'
    r'(?:x\([^)]*\)\s*)?'
    r'(?:of\s+)?(?:length\s+)?n(?:\s*([-+])\s*(\d+))?\s*(?:elements?)?\s*'
    r'with(?:out)?\s+(.*?)\s*\.?\s*$', re.I)


def _interior(body, vals):
    m = re.match(r'any interior element (greater than both neighbors)'
                 r'(?: or less than both neighbors)?$', body)
    if not m:
        return None
    both = 'less than both' in body

    def bad(v):
        if v[1] > v[0] and v[1] > v[2]:
            return True
        return both and v[1] < v[0] and v[1] < v[2]
    return 3, (lambda v: not bad(v))


def _consec(body, vals):
    if body != 'any two consecutive increases or two consecutive decreases':
        return None

    def ok(v):
        if v[0] < v[1] and v[1] < v[2]:
            return False
        if v[0] > v[1] and v[1] > v[2]:
            return False
        return True
    return 3, ok


def _prevsum(body, vals):
    m = re.match(r'each no smaller than the sum of its two previous neighbors modulo (\d+)$',
                 body)
    if not m:
        return None
    mod = int(m.group(1))
    return 3, (lambda v: v[2] >= (v[0] + v[1]) % mod)


def _threeequal(body, vals):
    m = re.match(r'no adjacent pair equal to its immediately preceding adjacent pair'
                 r'(?:, and new values introduced in [-\d.]+ order)?$', body)
    if not m:
        return None
    return 3, (lambda v: not (v[0] == v[1] == v[2]))


# _prevsum and _threeequal are NOT here. Both read a name whose meaning I could not pin
# against the entry's own data: "each no smaller than the sum of its two previous neighbors
# modulo 4" is not the sliding condition it looks like -- neither the plain reading, nor the
# cyclic one, nor treating the second element as having its first neighbour twice reproduces
# the published terms -- and "no adjacent pair equal to its immediately preceding adjacent
# pair" comes with "new values introduced in 0..k order", a canonical-form clause this engine
# does not carry. 17 entries wait on those two questions. A reader that half-works is worse
# than none: it would settle conjectures about the wrong object.
def _diffs(body, vals):
    """`with first and second differences also in -7..7', and its longer spellings."""
    m = re.match(r'(?:(adjacent element)|first(?:,| through| and)?\s*(second)?(?:,? (?:and )?)?'
                 r'(third)?(?:,? (?:and )?)?(fourth)?) differences also in '
                 r'(-?\d+)\.\.(-?\d+)$', body)
    if not m:
        return None
    if m.group(1):
        k = 1
    else:
        k = 1 + (1 if m.group(2) else 0) + (1 if m.group(3) else 0) + (1 if m.group(4) else 0)
    lo, hi = int(m.group(5)), int(m.group(6))
    if k > 5:
        return None

    def ok(v):
        # every difference of the window, not only the newest one: overlapping windows check
        # the later ones anyway, but the FIRST window of an array is the only one that ever
        # sees its own early differences, and checking only the newest let those through
        cur = list(v)
        for _ in range(k):
            cur = [cur[i + 1] - cur[i] for i in range(len(cur) - 1)]
            if any(not (lo <= x <= hi) for x in cur):
                return False
        return True

    def short(L, vals):
        # An array shorter than the window is NOT unconstrained here: a two-element array
        # still has a first difference. Counting those as free was the whole discrepancy.
        n = 0
        for v in itertools.product(vals, repeat=L):
            cur = list(v)
            good = True
            for _ in range(min(k, L - 1)):
                cur = [cur[i + 1] - cur[i] for i in range(len(cur) - 1)]
                if any(not (lo <= x <= hi) for x in cur):
                    good = False
                    break
            n += 1 if good else 0
        return n

    def prefix_ok(st):
        cur = list(st)
        for _ in range(min(k, len(st) - 1)):
            cur = [cur[i + 1] - cur[i] for i in range(len(cur) - 1)]
            if any(not (lo <= x <= hi) for x in cur):
                return False
        return True
    return k + 1, ok, short, prefix_ok


READERS2 = (_interior, _consec, _diffs)


# `each element differing from at least one neighbour' is not a sliding-window condition: the
# first and last elements have one neighbour rather than two, and whether an element is already
# satisfied has to be carried forward. 62 entries are written this way. The walk therefore needs
# its own start and end vectors -- an element is only allowed to be left behind once something
# has satisfied it, and the last element must be satisfied before the array can end.
NEIGH = re.compile(
    r'^\s*Number of (-?\d+)\.\.(-?\d+) arrays?\s*(?:x\([^)]*\)\s*)?(?:of\s+)?'
    r'(?:length\s+)?n(?:\s*\+\s*(\d+))?\s*(?:elements?)?\s*with\s+'
    r'each element (unequal to|differing from) at least one neighbou?r'
    r'(?: by (\d+) or more)?'
    r'(, starting with (-?\d+))?'
    r'(, with new values introduced in [-\d.]+ order)?\s*\.?\s*$', re.I)


def parse_neigh(nm):
    m = NEIGH.match(' '.join(nm.split()))
    if not m:
        return None
    lo, hi = int(m.group(1)), int(m.group(2))
    if hi < lo or hi - lo > 14:
        return None
    base = int(m.group(3)) if m.group(3) else 0
    d = int(m.group(5)) if m.group(5) else 1
    start0 = int(m.group(7)) if m.group(7) else None
    canon = bool(m.group(8))
    return {'engine': 'window', 'K': hi - lo, 'base': base, 'kind': 'neighbour',
            'vals': list(range(lo, hi + 1)), 'd': d, 'start0': start0, 'canon': canon}


def build_neigh(p, cap=200000):
    vals, d = p['vals'], p['d']
    states, index = [], {}

    def sid(st):
        if st not in index:
            index[st] = len(states)
            states.append(st)
        return index[st]

    start = []
    for v in vals:
        if p['start0'] is not None and v != p['start0']:
            continue
        if p['canon'] and v != vals[0]:
            continue
        start.append(sid((v, False, v) if p['canon'] else (v, False)))
    adj = {}
    i = 0
    while i < len(states):
        st = states[i]
        row = []
        p_, sat = st[0], st[1]
        mx = st[2] if p['canon'] else None
        for t in vals:
            if p['canon'] and t > mx + 1:
                continue
            far = abs(p_ - t) >= d
            if not (sat or far):
                continue          # the element about to be left behind is not satisfied
            nxt = (t, far, max(mx, t)) if p['canon'] else (t, far)
            row.append(sid(nxt))
        adj[i] = row
        i += 1
        if len(states) > cap:
            return None
    end = [1 if st[1] else 0 for st in states]
    return {'adj': [adj[j] for j in range(len(states))], 'start': start, 'end': end,
            'S': len(states), 'kind': 'neighbour'}


def terms_neigh(b, N):
    """arrays of each length from 1 up; an array ends only in a satisfied state."""
    v = [0] * b['S']
    for s in b['start']:
        v[s] += 1
    out = [sum(c for i, c in enumerate(v) if b['end'][i])]
    for _ in range(N + 2):
        w = [0] * b['S']
        for i, c in enumerate(v):
            if c:
                for j in b['adj'][i]:
                    w[j] += c
        v = w
        out.append(sum(c for i, c in enumerate(v) if b['end'][i]))
    return out


def parse_name2(nm):
    m = NAME2.match(' '.join(nm.split()))
    if not m:
        return None
    lo, hi = int(m.group(1)), int(m.group(2))
    if hi < lo or hi - lo > 12:
        return None
    sign, num = m.group(3), m.group(4)
    base = (int(num) if sign == '+' else -int(num)) if num else 0
    body = ' '.join(m.group(5).lower().split())
    if base < 0:
        return None
    vals = list(range(lo, hi + 1))
    for r in READERS2:
        got = r(body, vals)
        if got:
            w, pred = got[0], got[1]
            short = got[2] if len(got) > 2 else None
            pok = got[3] if len(got) > 3 else None
            return {'engine': 'window', 'K': hi - lo, 'base': base, 'w': w, 'pred': pred,
                    'vals': vals, 'short': short, 'prefix_ok': pok}
    return None


def build(p, cap=200000):
    if p.get('kind') == 'neighbour':
        return build_neigh(p, cap)
    w = p['w']
    vals = p.get('vals') or list(range(p['K'] + 1))
    A = len(vals)
    if A ** (w - 1) > cap:
        return None
    prev = list(itertools.product(vals, repeat=w - 1))
    short = p.get('short')
    index = {s: i for i, s in enumerate(prev)}
    adj = []
    for s in prev:
        row = []
        for t in vals:
            if p['pred'](s + (t,)):
                row.append(index[s[1:] + (t,)])
        adj.append(row)
    head = [short(L, vals) for L in range(1, w)] if short else [A ** L for L in range(1, w)]
    # A prefix shorter than the window can already break the condition -- a two-element array
    # has a first difference. Seeding the walk with every prefix would let inadmissible ones
    # through into every longer array.
    pok = p.get('prefix_ok')
    seed = [1 if (pok is None or pok(st)) else 0 for st in prev]
    return {'adj': adj, 'S': len(prev), 'A': A, 'w': w, 'head': head, 'seed': seed}


def terms(b, N):
    if b.get('kind') == 'neighbour':
        return terms_neigh(b, N)
    """the number of arrays of each length, from length 1 up.

    Windows shorter than w carry no condition, so the first w - 1 lengths are counted by
    filling the prefix freely; from length w on the walk applies the predicate at every step.
    """
    A, w, S = b['A'], b['w'], b['S']
    out = list(b.get('head') or [A ** L for L in range(1, w)])
    v = list(b.get('seed') or [1] * S)
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
