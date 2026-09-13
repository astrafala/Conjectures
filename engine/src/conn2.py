#!/usr/bin/env python3
"""Binary n X k arrays whose 1s form one connected region, with an endpoint condition.

    Number of n X 3 binary arrays with all 1s connected and a path of 1s from upper left corner
      to lower right corner.
    Number of n X 2 binary arrays with all 1s connected, a path of 1s from left column to right
      column, and no 1 having more than two 1s adjacent.

`conn' asks EVERY value's cells to be connected; here only the 1s are asked, and the 0s are
free. The frontier carries connectivity the same way, and the endpoint conditions cost four
flags and nothing more: with all the 1s in one component, `a path of 1s from the top row to the
bottom row' says exactly that some 1 lies in the top row and some 1 in the bottom row -- the
path is then automatic. Likewise for the left and right columns, while a corner condition is a
fixed cell.

`no 1 having more than two 1s adjacent' is the neighbour count of `conn' restricted to the 1s,
and the fourth neighbour of a cell is the one BELOW it, which is not known when the row is
placed; the partial count travels in the state and is checked when the row below arrives.
"""
import re
from itertools import product

import conn

HEAD = re.compile(
    r'^\s*Number of n ?X ?(\d+) binary arrays with all 1s connected(.*?)\s*\.?\s*$', re.I)
CORNER = {'upper left': 'ul', 'upper right': 'ur', 'lower left': 'll', 'lower right': 'lr',
          'top row': 'top', 'bottom row': 'bot', 'left column': 'left',
          'right column': 'right'}


def parse_name(nm):
    m = HEAD.match(' '.join(nm.split()).replace("'", ''))
    if not m:
        return None
    k = int(m.group(1))
    rest = ' '.join(m.group(2).lower().split())
    ends = set()
    mm = re.search(r'a path of 1s from (.+?) to (.+?)(?:,|$)', rest)
    if mm:
        for w in (mm.group(1).strip(), mm.group(2).strip()):
            if w not in CORNER:
                return None
            ends.add(CORNER[w])
        rest = rest[:mm.start()] + rest[mm.end():]
    if 'all corners 1' in rest:
        ends |= {'ul', 'ur', 'll', 'lr'}
        rest = rest.replace('all corners 1', '')
    maxsame = None
    mm = re.search(r'no 1 having more than (two|three|\d+) 1s adjacent', rest)
    if mm:
        w = mm.group(1)
        maxsame = {'two': 2, 'three': 3}.get(w) or int(w)
        rest = rest[:mm.start()] + rest[mm.end():]
    if re.sub(r'[,\s]|and', '', rest):
        return None
    if not 1 <= k <= 5:
        return None
    return {'engine': 'conn2', 'k': k, 'ends': frozenset(ends), 'maxsame': maxsame, 'frac': 1}


def build(p, cap=200000):
    k, ends, maxsame = p['k'], p['ends'], p['maxsame']
    rows = list(product((0, 1), repeat=k))
    A = 2                                        # colours are 1 (a one) and 2 (a zero)

    def enc(r):
        return tuple(1 if v else 2 for v in r)

    def partial(prev, cur):
        out = []
        for i in range(k):
            if not cur[i]:
                out.append(0)
                continue
            c = 0
            if i and cur[i - 1]:
                c += 1
            if i + 1 < k and cur[i + 1]:
                c += 1
            if prev is not None and prev[i]:
                c += 1
            out.append(min(c, 4))
        return tuple(out)

    def same_ok(pend, prev, cur):
        if maxsame is None:
            return True
        if pend is not None:
            for i in range(k):
                if prev[i] and pend[i] + (1 if cur[i] else 0) > maxsame:
                    return False
        return all(v <= maxsame for v in partial(prev, cur))

    states, index = [], {}

    def sid(x):
        if x not in index:
            index[x] = len(states)
            states.append(x)
        return index[x]

    def firstok(cur):
        if 'ul' in ends and not cur[0]:
            return False
        if 'ur' in ends and not cur[-1]:
            return False
        if 'top' in ends and not any(cur):
            return False
        return True

    def flags(f, cur):
        left = f[0] or bool(cur[0])
        right = f[1] or bool(cur[-1])
        return (left, right)

    start = []
    for cur in rows:
        if not firstok(cur) or not same_ok(None, None, cur):
            continue
        s = conn._step(k, A, None, enc(cur), only={1})
        if s is None:
            continue
        start.append(sid((s, flags((False, False), cur), partial(None, cur))))
    adj = {}
    i = 0
    while i < len(states):
        s, f, pend = states[i]
        prev = tuple(1 if v == 1 else 0 for v in s[0])
        out = []
        for cur in rows:
            if not same_ok(pend, prev, cur):
                continue
            t = conn._step(k, A, s, enc(cur), only={1})
            if t is None:
                continue
            out.append(sid((t, flags(f, cur), partial(prev, cur))))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1

    def accept(x):
        s, f, pend = x
        cur = tuple(1 if v == 1 else 0 for v in s[0])
        lab, st = s[1], s[2]
        if maxsame is not None and any(pend[i] > maxsame for i in range(k)):
            return False
        if st[0] == conn.UNSEEN:
            return False                       # no 1 at all: every endpoint clause fails
        if st[0] == conn.OPEN and len({lab[i] for i in range(k) if cur[i]}) != 1:
            return False
        if 'll' in ends and not cur[0]:
            return False
        if 'lr' in ends and not cur[-1]:
            return False
        if 'bot' in ends and not any(cur):
            return False
        if 'left' in ends and not f[0]:
            return False
        if 'right' in ends and not f[1]:
            return False
        return True
    end = [i for i, x in enumerate(states) if accept(x)]
    return {'adj': adj, 'start': start, 'end': end, 'S': len(states), 'k': k}


def terms(b, N):
    return conn.terms(b, N)


def threshold(b, coeffs, order):
    return conn.threshold(b, coeffs, order)
