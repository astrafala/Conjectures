#!/usr/bin/env python3
"""Nondecreasing arrangements over a fixed alphabet, counted by capped multiplicity profile.

    Number of nondecreasing arrangements of n+2 numbers in 0..5 with each number being the
      sum mod 6 of two others.

A nondecreasing arrangement IS its multiset, so what is being counted is multisets of size
n + B drawn from 0..M-1. The condition asks, of each element x, that two OTHER elements sum to
x modulo M. Whether that is possible depends on the multiset only through each value's
multiplicity CAPPED AT r + 1, where r is how many others are summed: an element of value v can
use two further copies of v only if v occurs at least three times, and nothing is gained by a
fourth. So the condition is a property of the capped profile, of which there are (r+2)^M --
65,536 at the largest size here -- and each profile is checked once on a representative.

The count then follows exactly. Write F for the total multiplicity the profile fixes outright
and t for how many values are capped, meaning "this many or more". The multisets with that
profile are the solutions of a sum over the t capped values, each at least r + 1, so there are
C(L - F - (r+1)t + t - 1, t - 1) of them and the total is a sum of binomials in L. That is an
exact polynomial in n of degree at most M - 1 once L is past the point where every profile can
be realised, so the residual test runs with S = M.

Nothing is fitted and no threshold is assumed: the profile enumeration is complete and the
binomial is zero exactly when the profile cannot be realised at that length.
"""
import itertools
import re
from math import comb

NAME = re.compile(
    r'^\s*Number of nondecreasing arrangements of n\s*\+\s*(\d+) numbers in 0\.\.(\d+) '
    r'with each number being the sum mod (\d+) of (two|three|four) others\s*\.?\s*$', re.I)
COUNT = {'two': 2, 'three': 3, 'four': 4}


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    B, top, mod, word = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4).lower()
    if top + 1 != mod or mod > 9:
        return None
    return {'engine': 'multiset', 'B': B, 'M': mod, 'r': COUNT[word.lower()]}


def _ok(profile, M, r):
    """does every value present have r others summing to it modulo M?"""
    arr = []
    for v, c in enumerate(profile):
        arr.extend([v] * c)
    if len(arr) < r + 1:
        return False
    for i, x in enumerate(arr):
        rest = arr[:i] + arr[i + 1:]
        if not any(sum(c) % M == x for c in itertools.combinations(rest, r)):
            return False
    return True


def build(p, cap=200000):
    M, r = p['M'], p['r']
    lim = r + 1
    if (lim + 1) ** M > 4 * cap:
        return None
    good = []
    for prof in itertools.product(range(lim + 1), repeat=M):
        if not _ok(prof, M, r):
            continue
        F = sum(c for c in prof if c < lim)
        t = sum(1 for c in prof if c == lim)
        good.append((F, t))
    return {'profiles': good, 'M': M, 'B': p['B'], 'r': r, 'S': M}


def terms(b, N):
    """the number of arrangements for n = 0, 1, 2, ... -- the entry's own index."""
    lim = b['r'] + 1
    out = []
    for n in range(N + 3):
        L = n + b['B']
        tot = 0
        for F, t in b['profiles']:
            if t == 0:
                tot += 1 if F == L else 0
                continue
            slack = L - F - lim * t
            if slack < 0:
                continue
            tot += comb(slack + t - 1, t - 1)
        out.append(tot)
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 8 * S + order + 30)
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
