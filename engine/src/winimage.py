#!/usr/bin/env python3
"""How many distinct arrays a sliding-window statistic can produce.

    Number of second differences of arrays of length n+2 of numbers in 0..5.
    Number of arrays of median of three adjacent elements of some length n+2 0..2 array, with
      no adjacent equal elements in the latter.
    Number of arrays of maxima of three adjacent elements of some length n+2 0..3 array.

The entry counts the DISTINCT images, not the arrays: two inputs giving the same output word are
one. That is the image of a sliding-window map, so the output words form a regular language and
the count is a walk in its subset construction -- a state is the set of input windows consistent
with the output emitted so far. Nothing about the statistic matters beyond its being a function
of a fixed window, so medians, maxima, minima and k-th differences are one engine.
"""
import re
from itertools import product

WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
        'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5}

DIFF = re.compile(
    r'^\s*Number of (first|second|third|fourth|fifth) differences of arrays of length '
    r'n\+(\d+) of numbers in (-?\d+)\.\.(-?\d+)\s*\.?\s*$', re.I)
STAT = re.compile(
    r'^\s*Number of arrays of (median|maxima|minima|maximum|minimum) of '
    r'(two|three|four) adjacent elements of some length n\+(\d+) (-?\d+)\.\.(-?\d+) array'
    r'(.*?)\s*\.?\s*$', re.I)


# The same map written the other way round: the entry names the OUTPUT length first and calls
# the input "a random ... array of n+k-1 elements". 25 entries are written that way and no
# sweep could read one of them.
FILT = re.compile(
    r'(?i)^Number of n[- ]element (-?\d+)\.\.(-?\d+) arrays with each element the '
    r'(minimum|maximum|median) of (\d+) adjacent elements of a random (-?\d+)\.\.(-?\d+) '
    r'array of n\+(\d+) elements\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = FILT.match(nm)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        if (int(m.group(5)), int(m.group(6))) != (lo, hi):
            return None                       # the two alphabets must be the same one
        w, off = int(m.group(4)), int(m.group(7))
        if off != w - 1 or hi - lo > 8 or w < 2 or w > 8:
            return None
        st = {'minimum': 'minima', 'maximum': 'maxima', 'median': 'median'}[m.group(3).lower()]
        if st == 'median' and w % 2 == 0:
            return None                       # no median of an even window is named here
        return {'engine': 'winimage', 'kind': st, 'k': w - 1, 'off': off,
                'lo': lo, 'hi': hi, 'cond': None, 'frac': 1}
    m = DIFF.match(nm)
    if m:
        k = WORD[m.group(1).lower()]
        lo, hi = int(m.group(3)), int(m.group(4))
        if hi - lo > 8 or k > 4:
            return None
        return {'engine': 'winimage', 'kind': 'diff', 'k': k, 'off': int(m.group(2)),
                'lo': lo, 'hi': hi, 'cond': None, 'frac': 1}
    m = STAT.match(nm)
    if m:
        st = m.group(1).lower()
        st = {'maximum': 'maxima', 'minimum': 'minima'}[st] if st in ('maximum', 'minimum') else st
        w = WORD[m.group(2).lower()]
        lo, hi = int(m.group(4)), int(m.group(5))
        tail = ' '.join(m.group(6).lower().split()).strip(' ,')
        cond = None
        if tail:
            if tail == 'with no adjacent equal elements in the latter':
                cond = 'noadj'
            else:
                return None
        if hi - lo > 8 or w > 4:
            return None
        return {'engine': 'winimage', 'kind': st, 'k': w - 1, 'off': int(m.group(3)),
                'lo': lo, 'hi': hi, 'cond': cond, 'frac': 1}
    return None


def _out(p, win):
    kind = p['kind']
    if kind == 'diff':
        k = p['k']
        cur = list(win)
        for _ in range(k):
            cur = [cur[i + 1] - cur[i] for i in range(len(cur) - 1)]
        return cur[0]
    if kind == 'median':
        return sorted(win)[len(win) // 2]
    if kind == 'maxima':
        return max(win)
    return min(win)


def build(p, cap=200000):
    lo, hi, k, cond = p['lo'], p['hi'], p['k'], p['cond']
    V = list(range(lo, hi + 1))
    W = k + 1

    def okwin(win):
        if cond == 'noadj':
            return all(win[i] != win[i + 1] for i in range(len(win) - 1))
        return True

    starts = frozenset(w for w in product(V, repeat=W - 1) if okwin(w))
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    s0 = sid(starts)
    adj = {}
    i = 0
    while i < len(states):
        S = states[i]
        by = {}
        for w in S:
            for v in V:
                win = w + (v,)
                if not okwin(win):
                    continue
                by.setdefault(_out(p, win), set()).add(win[1:])
        adj[i] = [sid(frozenset(t)) for t in by.values()]
        i += 1
        if len(states) > cap:
            return None
    # the subset automaton is highly redundant -- a third difference over 0..5 has 7,917
    # states and 21 behaviours -- and the residual test runs until S consecutive residuals
    # vanish, so the state count is the whole cost. Merging states with the same FUTURE
    # changes no count.
    import lumpauto
    st = [0] * len(states)
    st[s0] = 1
    wadj, wstart, wend, K = lumpauto.lump(adj, st, [1] * len(states))
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': K, 'raw': len(states), 'off': p['off']}


def terms(b, N):
    """a(n): the array has length n + off, so it gives n + off - k outputs."""
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    out = [sum(v * e for v, e in zip(vec, ev))]
    for _ in range(N + b['off']):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v * e for v, e in zip(vec, ev)))
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
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
