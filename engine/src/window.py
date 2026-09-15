#!/usr/bin/env python3
"""Image counts of a sliding-window statistic over a growing alphabet.

    A228462  Number of arrays of maxima of three adjacent elements of some length 7 0..n array.
    A228741  Number of arrays of the median of three adjacent elements of some length-6 0..n array.
    A229013  ... of some length-5 0..n array, with no adjacent equal elements in the latter.

Every transfer-matrix engine in this project models a FIXED alphabet with n as the LENGTH. These
entries invert that: the length k is a small constant and the alphabet {0..n} grows with n. No
transfer matrix applies, which is why all of them refuse as "no engine reads the name".

THE ARGUMENT. Write w for the window width and L = k - w + 1 for the length of the image array
b. Whether a given b lies in the image depends only on b's ORDER TYPE -- the weak ordering of
its entries -- and not on n or on the actual values:

  * set a_i = min{ b_j : window j covers i }. Every entry of a is then one of b's own values, so
    a lies in {0..n}^k whenever b does; and a is componentwise the LARGEST candidate, since any
    witness a' must satisfy a'_i <= b_j for each window j covering i. So max over window j of a
    is at least b_j (as it is at least the same max over a') and at most b_j (by construction),
    which makes the greedy witness exact: b is achievable exactly when it reproduces b;
  * that construction and that test are comparisons among b's entries alone, so relabelling the
    values by any increasing map {0..n} -> {0..n'} carries witnesses to witnesses.

THIS ARGUMENT IS FOR MAX AND MIN ONLY, and the reason is worth stating because it looked as
though it covered the median and does not. A median window can require a witness entry STRICTLY
BETWEEN two values of b -- a value whose rank among b's entries is all that matters, so any
integer in that open interval will do, but SOME integer must be there. Whether one is depends on
the gaps between b's values, which the order type does not record: b = (0,1) and b = (0,5) have
the same order type and different gaps. Achievability is therefore not order-type invariant for
the median, the sum below is not the count, and the four median entries this file could
otherwise settle are left refused. (The count is still a polynomial -- classifying by order type
AND gap pattern, the number of value sets with a prescribed pattern P of non-empty gaps is
C(n-m, |P|-1), so a(n) is a sum of binomials in n -- but the census is then over (type, pattern)
pairs, 2^(m+1) times larger, and that is a different build.)

The number of tuples in {0..n}^L whose order type uses exactly m distinct values is C(n+1, m) --
choose which m of the n+1 alphabet letters are used; the order type then says how. Hence, with
A_m the number of ACHIEVABLE order types on m distinct values,

    a(n) = sum_{m=1..L} A_m * C(n+1, m),

exactly, for every n >= 0. That is a polynomial in n of degree at most L with no fitting and no
asymptotics, and the entry's conjectured closed form is then either equal to it as an element of
Q[n] or it is not.

The cost is the enumeration of the weak orderings of L elements -- the ordered Bell numbers,
4,683 at L = 6 and 47,293 at L = 7 -- each tested once. The census depends only on
(k, w, statistic, side condition), never on the entry, so entries of the same shape share it.
"""
import itertools
from math import comb

import sympy as sp

n = sp.Symbol('n')


def set_partitions(L):
    """restricted growth strings: every set partition of {0..L-1}, blocks by first occurrence"""
    a = [0] * L

    def rec(i, mx):
        if i == L:
            yield tuple(a)
            return
        for v in range(mx + 2):
            a[i] = v
            yield from rec(i + 1, max(mx, v))
    yield from rec(0, -1)


def weak_orders(L):
    """every weak ordering of L elements, as a tuple of dense ranks 0..m-1"""
    for rgs in set_partitions(L):
        m = max(rgs) + 1
        for perm in itertools.permutations(range(m)):
            yield tuple(perm[v] for v in rgs), m


def _windows(k, w):
    return [tuple(range(j, j + w)) for j in range(k - w + 1)]


def achievable_max(b, k, w, extreme=None):
    """is b the windowed MAXIMUM of some length-k array? (the greedy witness is exact)"""
    wins = _windows(k, w)
    big = max(b) + 1
    a = []
    for i in range(k):
        cover = [b[j] for j, win in enumerate(wins) if i in win]
        a.append(min(cover) if cover else big)
    return all(max(a[j] for j in win) == b[i] for i, win in enumerate(wins))


def _median(vals):
    return sorted(vals)[len(vals) // 2]


def achievable_search(b, k, w, fn, cond=None):
    """is b the windowed `fn` of some length-k array? decided by a reachability DP.

    The witness's entries may be taken from b's values together with one letter below them all
    and one above -- for a median window every b_j is literally one of the entries it is the
    median of, and for min/max the extremes are the only other useful letters. The state is the
    last w-1 entries, so the DP is O(k * V^w) with V at most L + 2.
    """
    vals = sorted(set(b))
    alpha = [-1] + vals + [max(vals) + 1]
    wins = k - w + 1
    if wins != len(b):
        return False
    states = {t: None for t in itertools.product(alpha, repeat=w - 1)}
    live = set(states)
    if cond is not None:
        live = {t for t in live if cond(t)}
    for i in range(w - 1, k):
        nxt = set()
        for st in live:
            for v in alpha:
                full = st + (v,)
                if cond is not None and not cond(full):
                    continue
                if fn(full) != b[i - w + 1]:
                    continue
                nxt.add(full[1:])
        live = nxt
        if not live:
            return False
    return True


def census(k, w, stat, cond=None):
    """[A_1, ..., A_L]: achievable order types by number of distinct values"""
    L = k - w + 1
    A = [0] * (L + 1)
    fn = {'max': max, 'min': min, 'median': _median}[stat]
    for b, m in weak_orders(L):
        if stat == 'max' and cond is None:
            ok = achievable_max(b, k, w, None)
        else:
            ok = achievable_search(b, k, w, fn, cond)
        if ok:
            A[m] += 1
    return A[1:]


def polynomial(A):
    """sum_m A_m * C(n+1, m), expanded in Q[n]"""
    expr = 0
    for m, a in enumerate(A, start=1):
        if a:
            expr += a * sp.binomial(n + 1, m)
    return sp.expand(sp.simplify(sp.expand_func(expr)))


NO_ADJACENT_EQUAL = lambda t: all(t[i] != t[i + 1] for i in range(len(t) - 1))
