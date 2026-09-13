#!/usr/bin/env python3
"""The whole configuration of a two-dimensional automaton, and when its axis certificate is a
theorem rather than an observation.

`ca2d' reads an axis or a diagonal of the automaton as a numeral and certifies

    w(n+p) = L_r + w(n) + R_r

by running the automaton and checking the identity over every stage it computed. For the
ONE-dimensional automata that check is a proof: a row of an elementary automaton is a function
of the row before it, so the identity holding at two consecutive n fixes every window at both
boundaries and induction carries it forward. **In two dimensions it is not.** The cell at
(x, 0) at stage n+1 reads (x, 0), (x+-1, 0) and (x, +-1), so the axis is not a function of the
axis before it; determining the axis at stage n+p needs every row within distance p, and those
need theirs. The induction the one-dimensional papers use is simply unavailable here, and a
paper that states a theorem for all n on the strength of the identity holding to stage 64 is
claiming more than it has shown.

What does prove it, for the rules that have it, is periodicity of the CONFIGURATION:

    C(n+p) = C(n) as configurations of the whole plane, for one n past a settling point.

The automaton is deterministic, so that single equality gives C(n+kp) = C(n) for every k with
no locality argument at all, and every reading of every axis and diagonal follows. Rule 3, for
instance, is a single live cell at even stages and an entirely live plane minus a small figure
at odd ones: the configuration has period two exactly, and the axis word grows only because
the window |x| <= n widens around a configuration that is not changing.

Getting the background right is the whole of the check. A rule taking an empty von Neumann
neighbourhood to a live cell flips the ENTIRE plane, so comparing two stages by padding the
smaller one with zeros compares two different things and reports no periodicity where the
configurations are identical. `bg' is the orbit of the all-zero plane and is what the padding
uses.
"""


def bg(rule, n):
    """the value the cells that never met the initial one hold at stage n"""
    v = 0
    for _ in range(n):
        v = (rule >> (9 * v)) & 1        # four neighbours and the cell itself all v
    return v


def grids(rule, steps):
    """the configuration at each stage, cropped to the box |x|,|y| <= n+1"""
    R = 2 * steps + 3                    # the padding must exceed the steps: see `ca2d'
    N = 2 * R + 1
    C = R
    g = [[0] * N for _ in range(N)]
    g[C][C] = 1
    out = []
    for n in range(steps + 1):
        out.append(tuple(tuple(row[C - n - 1:C + n + 2]) for row in g[C - n - 1:C + n + 2]))
        ng = [[0] * N for _ in range(N)]
        for i in range(1, N - 1):
            gi, gu, gd = g[i], g[i - 1], g[i + 1]
            ngi = ng[i]
            for j in range(1, N - 1):
                t = gu[j] + gd[j] + gi[j - 1] + gi[j + 1]
                ngi[j] = (rule >> (t * 2 + gi[j])) & 1
        g = ng
    return out


def _pad(g, k, b):
    m = len(g) + 2 * k
    z = tuple([b] * m)
    return tuple([z] * k + [tuple([b] * k + list(r) + [b] * k) for r in g] + [z] * k)


def timeperiod(rule, steps=30, maxp=9, maxn0=14, gs=None):
    """(n0, p) with C(n+p) = C(n) for every computed n >= n0, or None"""
    gs = gs or grids(rule, steps)
    for p in range(1, maxp):
        for n0 in range(0, maxn0):
            if n0 + 3 * p + 4 >= len(gs):
                continue
            if all(_pad(gs[n], p, bg(rule, n)) == gs[n + p]
                   for n in range(n0, len(gs) - p)):
                return n0, p
    return None
