#!/usr/bin/env python3
"""How many distinct marker patterns a sliding-window map can produce.

**NOT REGISTERED. The reading is not pinned down and nothing here is installed.** The model
below reproduces every published term of A221992, the 0..1 case, and is one too many at n = 10
for A221993, the 0..2 case: 85 against the entry's 84, confirmed by brute force over all 3^10
arrays, so the automaton is faithful to the reading and the READING is what is wrong. Three
tie-breaking rules for a trailing edge maximum (y_i > y_{i+1} with y_i >= y_{i-1}, with
y_i > y_{i-1}, and y_i >= y_{i+1} with y_i > y_{i-1}), four choices of which positions carry a
mark, two padding lengths on each side and the reversed kernel were all tried; every one that
matches the first eight terms gives 85. Left here with the measurement rather than deleted,
because the machinery is right and only the sentence is not.

    Number of binary arrays indicating the locations of trailing edge maxima of a random
      length-n 0..3 array extended with zeros and convolved with 1,4,6,4,1.

34 entries, none read. The array x is padded with zeros, convolved with a fixed kernel to give
y, and each position is marked when y has a trailing edge maximum there: y_i > y_{i+1} and
y_i >= y_{i-1}. The entry counts the DISTINCT marker words, not the arrays -- two different x
that mark the same positions are one.

That is the image of a sliding-window map, so the marker words form a regular language and the
count is a walk count in its minimal automaton. y_i needs the last len(ker) inputs and the mark
at i needs y_{i-1}, y_i and y_{i+1}, so a window of len(ker)+2 inputs decides one mark: the
transducer's state is that window, and the language of marker words is what it emits. Counting
DISTINCT outputs is then the subset construction -- a state of the determinised automaton is
the set of windows consistent with the marks emitted so far -- and the walks of the result are
the distinct marker words.
"""
import re

NAME = re.compile(
    r'^\s*Number of binary arrays indicating the locations of trailing edge maxima of a '
    r'random length-n 0\.\.(\d+) array extended with zeros and convolved with '
    r'([\d,]+)\s*\.?\s*$', re.I)


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    A = int(m.group(1))
    ker = [int(v) for v in m.group(2).split(',') if v.strip()]
    if not 1 <= A <= 6 or not 2 <= len(ker) <= 6:
        return None
    return {'engine': 'edgemark', 'A': A, 'ker': tuple(ker), 'frac': 1}


def _mark(win, ker):
    """the mark at the middle of a window of len(ker)+2 consecutive inputs."""
    K = len(ker)
    y = []
    for s in range(3):                      # y_{i-1}, y_i, y_{i+1}
        y.append(sum(ker[j] * win[s + K - 1 - j] for j in range(K)))
    return 1 if (y[1] > y[2] and y[1] >= y[0]) else 0


def build(p, cap=200000):
    A, ker = p['A'], p['ker']
    K = len(ker)
    W = K + 2                                # the window that decides one mark
    V = range(A + 1)
    zero = tuple([0] * W)

    def step(win, v):
        return win[1:] + (v,)

    # The padded input is K zeros, the array, K zeros; the marks run over every position with
    # a full window, so the walk is: K-1 forced zero reads to fill the window, then n free
    # reads, then K forced zero reads, each read emitting one mark.
    def det(free, tailonly=False):
        """one subset-construction step set"""
        return free

    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    def advance(S, vals):
        """from a subset S, the possible (mark, new subset) pairs reading one symbol."""
        out = {}
        for win in S:
            for v in vals:
                nw = step(win, v)
                out.setdefault(_mark(nw, ker), set()).add(nw)
        return {m: frozenset(s) for m, s in out.items()}

    # fill the window with the leading zeros
    S0 = frozenset([zero])
    pre = 0
    for _ in range(W - 1):
        S0 = frozenset(step(w, 0) for w in S0)
        pre += 0
    start = sid(('f', S0))
    adj, emit = {}, {}
    i = 0
    while i < len(states):
        kind, S = states[i]
        out = []
        vals = V if kind == 'f' else (0,)
        for m, T in advance(S, vals).items():
            out.append(sid((kind, T)))
        adj[i] = out
        i += 1
        if len(states) > cap:
            return None
    # the tail: the array is padded with K zeros, and those reads emit marks too, so the
    # end vector is the number of distinct mark words the forced zero tail can still produce
    # from each state -- a walk count with a weighted end vector, not a plain accept set.
    def tail_count(S):
        cur = {S: 1}
        for _ in range(K):
            nxt = {}
            for T, c in cur.items():
                for _m, U in advance(T, (0,)).items():
                    nxt[U] = nxt.get(U, 0) + c
            cur = nxt
        return sum(cur.values())

    endv = [tail_count(S) for _k, S in states]
    return {'adj': adj, 'start': start, 'endv': endv, 'S': len(states), 'K': K,
            'ker': ker, 'A': A}


def terms(b, N):
    adj, S, endv = b['adj'], b['S'], b['endv']
    vec = [0] * S
    vec[b['start']] = 1
    out = [None]
    for _ in range(N):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v * e for v, e in zip(vec, endv)))
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    last, run = None, 0
    for j in range(order, len(t)):
        if t[j] is None or t[j - order] is None:
            continue
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
