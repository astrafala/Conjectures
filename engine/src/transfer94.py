#!/usr/bin/env python3
r"""Monotone height arrays: values rising by 0 or 1 with every step, pinned to a distance.

The family, forty entries none of which any engine read:

    Number of n X W nonnegative integer arrays with upper left 0
      [and lower right its <king-move|city block> distance away minus D]
      [and every value within K of its <city block|king move> distance from the upper left]
      and every value increasing by 0 or 1 with every step <right or down
                                                            |right, diagonally se or down>.

Write v(i,j) for the entry and put u(j) = v(i,j) - i, the row read relative to its own index.
Every condition becomes local in u:

  * a step RIGHT asks v(i,j+1) - v(i,j) in {0,1}, so u(j+1) - u(j) in {0,1}: a row is a
    staircase, non-decreasing and rising by at most one at a time;
  * a step DOWN asks v(i+1,j) - v(i,j) in {0,1}, so u'(j) - u(j) in {-1,0}: the relative row
    never rises and falls by at most one;
  * a step DIAGONALLY SE asks v(i+1,j+1) - v(i,j) in {0,1}, so u'(j+1) - u(j) in {-1,0};
  * "within K of its city block distance" is |v(i,j) - (i+j)| <= K, so |u(j) - j| <= K ---
    free of i, which is exactly why this coordinate is the right one;
  * "within K of its king move distance" is |v(i,j) - max(i,j)| <= K. For i >= j that is
    |u(j)| <= K, again free of i; for i < j it is |u(j) + i - j| <= K, which does depend on
    i. Only the first W rows can have i < j, so the state carries a phase min(i, W) and the
    graph is still finite.

Without a "within K" clause the state space is bounded by the OTHER clause instead. The
lower-right cell is pinned to its distance minus D; u never rises with i and never falls by
more than one along a row, so u(j) lies in [j - D, j] throughout. Both bounds are used when
both clauses are present.

The last cell's requirement is a constant in this coordinate, which is what makes a single
accepting vector correct for every n: for city block distance the lower right must be
n + W - 2 - D, so u(W-1) = W - 1 - D; for king move distance and n >= W it must be n - 1 - D,
so u(W-1) = -D.
"""
import re

import namecanon

SHAPE = re.compile(r'(?i)^\s*Number of\s+n\s*X\s*(\d+)\s+nonnegative integer arrays\s+with\s+'
                   r'upper left(?:\s+entry)?\s+0\s*,?\s*(.*?)\s*\.?\s*$')
LOWER = re.compile(r'(?i)^and\s+lower right(?:\s+entry)?\s+its\s+(king[- ]move|city block)\s+'
                   r'distance away minus\s+(\d+)\b')
LOWER_N = re.compile(r'(?i)^and\s+lower right(?:\s+entry)?\s+n\s*\+\s*(\d+)\s*-\s*(\d+)\b')
WITHIN = re.compile(r'(?i)^and\s+(?:every\s+)?value\s+within\s+(\d+)\s+of\s+its\s+'
                    r'(city block|king[- ]move)\s+distance\s+from\s+the\s+upper\s+left\b')
STEPS = re.compile(r'(?i)^and\s+(?:every\s+)?value\s+increasing\s+by\s+0\s+or\s+1\s+with\s+'
                   r'every\s+step\s+(.+?)\s*$')


def _dist(word):
    return 'king' if 'king' in word.lower() else 'cb'


def parse_name(nm):
    m = SHAPE.match(namecanon.canon(' '.join(nm.split())))
    if not m:
        return None
    W, rest = int(m.group(1)), m.group(2)
    if W < 2 or W > 8:
        return None
    D = Ddist = K = Kdist = None
    steps = None
    # the clauses arrive in a fixed order but not all are present; take them off the front
    for _ in range(4):
        rest = rest.strip()
        mm = LOWER.match(rest)
        if mm:
            Ddist, D = _dist(mm.group(1)), int(mm.group(2))
            rest = rest[mm.end():]
            continue
        mm = LOWER_N.match(rest)
        if mm:
            # "lower right n+2-4" for width 2 is n + W - 4, and the lower right cell's city
            # block distance is n + W - 2, so this is that distance minus 2. The form is only
            # accepted when the first number really is W, since otherwise it says something
            # this program has not been shown.
            if int(mm.group(1)) != W:
                return None
            Ddist, D = 'cb', int(mm.group(2)) - 2
            if D < 0:
                return None
            rest = rest[mm.end():]
            continue
        mm = WITHIN.match(rest)
        if mm:
            K, Kdist = int(mm.group(1)), _dist(mm.group(2))
            rest = rest[mm.end():]
            continue
        mm = STEPS.match(rest)
        if mm:
            s = mm.group(1).lower().replace(',', ' ')
            s = ' '.join(s.split())
            if s in ('right or down',):
                steps = 'rd'
            elif s in ('right diagonally se or down', 'right diagonally southeast or down'):
                steps = 'rsd'
            else:
                return None
            rest = rest[mm.end():]
            continue
        break
    if steps is None or rest.strip():
        return None
    if K is None and D is None:
        return None                      # nothing bounds the state space
    return {'W': W, 'steps': steps, 'K': K, 'Kdist': Kdist, 'D': D, 'Ddist': Ddist,
            'frac': 1}


def _rows(p, phase):
    """the admissible u-vectors for a row whose index is `phase` (W meaning W or more)"""
    W, K, D = p['W'], p['K'], p['D']

    lo, hi = [], []
    for j in range(W):
        a, b = -10 ** 6, 10 ** 6
        if K is not None:
            if p['Kdist'] == 'cb':
                a, b = max(a, j - K), min(b, j + K)
            else:
                # |u(j) + i - max(i, j)| <= K with i = phase, and i >= j once phase >= W
                i = phase
                d = max(i, j) if i < W else i
                shift = d - i               # 0 once the row index is past the width
                a, b = max(a, shift - K), min(b, shift + K)
        if D is not None:
            # u never rises with i and rises by at most one along a row, so every u(j) lies
            # between the last row's value and the first row's. The last row is pinned by the
            # lower-right clause, and where that pin sits depends on which distance is meant:
            # city block puts u(W-1) at W-1-D, king move at -D. Using the city-block bound for
            # both cut the accepting states out of the king-move models and returned zero.
            floor = (j - D) if p['Ddist'] == 'cb' else (j - (W - 1) - D)
            a, b = max(a, floor), min(b, j)
        lo.append(a)
        hi.append(b)

    out = []

    def go(j, cur):
        if j == W:
            out.append(tuple(cur))
            return
        rng = range(lo[j], hi[j] + 1) if j == 0 else (cur[j - 1], cur[j - 1] + 1)
        for v in rng:
            if lo[j] <= v <= hi[j]:
                go(j + 1, cur + [v])

    go(0, [])
    return out


def build(p, cap=2000000):
    W, steps = p['W'], p['steps']
    phases = list(range(W + 1))
    index, states = {}, []

    def sid(s):
        i = index.get(s)
        if i is None:
            i = index[s] = len(states)
            states.append(s)
        return i

    per = {ph: _rows(p, ph) for ph in phases}
    if sum(len(v) for v in per.values()) > cap:
        return None
    for ph in phases:
        for u in per[ph]:
            sid((ph, u))
    if len(states) > cap:
        return None

    def ok_step(u, v):
        for j in range(W):
            if v[j] - u[j] not in (-1, 0):
                return False
        if steps == 'rsd':
            for j in range(W - 1):
                if v[j + 1] - u[j] not in (-1, 0):
                    return False
        return True

    adj = [[] for _ in states]
    for si, (ph, u) in enumerate(states):
        nph = min(ph + 1, W)
        for v in per[nph]:
            if ok_step(u, v):
                adj[si].append(sid((nph, v)))

    # row 0: u(0) = v(0,0) = 0
    start = [0] * len(states)
    for si, (ph, u) in enumerate(states):
        if ph == 0 and u[0] == 0:
            start[si] = 1

    if p['D'] is None:
        end = [1] * len(states)
    elif p['Ddist'] == 'cb':
        # city block: the lower right cell of an n X W array is at distance (n-1)+(W-1), so
        # the pinned value is n+W-2-D and u(W-1) = W-1-D whatever n is
        want = W - 1 - p['D']
        end = [1 if u[W - 1] == want else 0 for _, u in states]
    else:
        # king move: the distance is max(n-1, W-1), which is n-1 only once the array is at
        # least as tall as it is wide. For the first few rows it is W-1 instead, and the
        # pinned u depends on the row --- which the phase already carries. Using the tall-array
        # formula everywhere made the model start 0, 0 where the entry starts 1, 1.
        end = [1 if u[W - 1] == max(W - 1 - ph, 0) - p['D'] else 0 for ph, u in states]
    return adj, start, end, len(states)


# The walk count and the annihilation test are transfer19's; this engine differs only in what
# its states are, so re-exporting them keeps one implementation of the arithmetic rather than
# a second copy to drift out of step.
from transfer19 import terms, threshold, matvec  # noqa: E402,F401
