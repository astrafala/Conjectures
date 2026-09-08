#!/usr/bin/env python3
"""Active-cell counts of a two-dimensional cellular automaton.

    Number of active (ON, black) cells in n-th stage of growth of the two-dimensional cellular
    automaton defined by "Rule 342", based on the 5-celled von Neumann neighborhood.
    Partial sums of the number of active cells ... / First differences of ... / at stage 2^n-1.

168 entries, none readable before. The automaton is the same outer-totalistic rule `ca2d`
uses; what is counted is the whole configuration rather than one axis.

**The window is the SQUARE |i|,|j| <= n, not the light cone |i|+|j| <= n.** The diamond fits
every entry whose background stays off and fails all 103 whose background flips, because at a
stage where the background is ON the cells the diamond excludes are ON too and the entry counts
them. What gave that away was the even-indexed terms agreeing exactly while only the odd ones
differed: a discrepancy that alternates with the background is a background problem.

Four indexings appear and the name says which: the plain count, its partial sums, its first
differences, and the count at stage 2^n-1.
"""
import re

HEAD = re.compile(
    r'^\s*(Partial sums of the number of active|First differences of number of active|'
    r'Number of active)\s*\(?(?:ON, black\)?)?\s*cells?\s*(.*?)'
    r'"?Rule (\d+)"?', re.I | re.S)


def parse_name(nm):
    m = HEAD.match(re.sub(r'\s+', ' ', nm).strip())
    if not m:
        return None
    rule = int(m.group(3))
    if not 0 <= rule <= 1023:
        return None
    head, mid = m.group(1).lower(), m.group(2) or ''
    if 'partial sums' in head:
        kind = 'sums'
    elif 'first differences' in head:
        kind = 'diffs'
    elif '2^n-1' in mid:
        kind = 'pow'
    else:
        kind = 'plain'
    return {'rule': rule, 'kind': kind, 'frac': 1}


def raw(rule, steps):
    """cells ON inside the square |i|,|j| <= n at each stage"""
    R = 2 * steps + 3
    N = 2 * R + 1
    C = R
    g = [[0] * N for _ in range(N)]
    g[C][C] = 1
    out = []
    for n in range(steps + 1):
        out.append(sum(g[C + i][C + j] for i in range(-n, n + 1) for j in range(-n, n + 1)))
        ng = [[0] * N for _ in range(N)]
        for i in range(1, N - 1):
            gi, gu, gd = g[i], g[i - 1], g[i + 1]
            ngi = ng[i]
            for j in range(1, N - 1):
                t = gu[j] + gd[j] + gi[j - 1] + gi[j + 1]
                ngi[j] = (rule >> (t * 2 + gi[j])) & 1
        g = ng
    return out


def build(p, cap=200000):
    # stage 2^n-1 needs the automaton run to 2^K, and a 2000-square grid for 512 steps is
    # hopeless; K = 6 reaches every published prefix these entries have
    steps = (2 ** 6) if p['kind'] == 'pow' else 60
    return {'rule': p['rule'], 'kind': p['kind'], 'raw': raw(p['rule'], steps), 'S': 24}


def terms(b, N):
    c = b['raw']
    if b['kind'] == 'sums':
        s = 0
        return [(s := s + v) for v in c][:N + 1]
    if b['kind'] == 'diffs':
        return [c[i + 1] - c[i] for i in range(len(c) - 1)][:N + 1]
    if b['kind'] == 'pow':
        return [c[2 ** n - 1] for n in range(0, min(7, N + 1))]
    return c[:N + 1]


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
