#!/usr/bin/env python3
"""Necklaces and bracelets of k beads labelled from -n..n with sum zero.

    Number of 4-bead necklaces labeled with numbers -n..n not allowing reversal, with sum zero.
    Number of 7-bead necklaces labeled with numbers -n..n allowing reversal, with sum zero.

The bead count is fixed and the alphabet grows, so no walk counts these. Burnside does, exactly.

Write G for the cyclic group of rotations when reversal is not allowed and the dihedral group
when it is. A labelling fixed by an element of G is constant on each orbit of that element, so
it is a choice of one value per orbit; and the sum of the whole labelling is then the sum over
orbits of (orbit size) * (that value). The number of labellings fixed by an element is
therefore the number of integer solutions of

    sum_i w_i x_i = 0,   x_i in [-n, n],

with w_i the orbit sizes -- counted here by a small convolution rather than by enumeration.
Burnside's lemma averages those counts over the group and gives the number of necklaces
exactly, for every n, with nothing fitted.

Each fixed-point count is a polynomial in n (a bounded lattice-point count with a homogeneous
constraint), so the necklace count is too, of degree at most k - 1: the residual test runs with
S = k.
"""
import re

NAME = re.compile(
    r'^\s*Number of (\d+)-bead (necklace|bracelet)s?\s+labeled with numbers -n\.\.n\s+'
    r'(not allowing reversal|allowing reversal)?,?\s*with sum zero\s*\.?\s*$', re.I)


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    k = int(m.group(1))
    if not 2 <= k <= 12:
        return None
    rev = m.group(3)
    reversal = (rev is None and m.group(2).lower() == 'bracelet') or \
               (rev is not None and rev.lower() == 'allowing reversal')
    return {'engine': 'necklace', 'k': k, 'reversal': reversal}


def _orbit_sizes(perm):
    """the cycle lengths of a permutation given as a tuple perm[i] = image of i."""
    k = len(perm)
    seen = [False] * k
    out = []
    for i in range(k):
        if seen[i]:
            continue
        n_ = 0
        j = i
        while not seen[j]:
            seen[j] = True
            j = perm[j]
            n_ += 1
        out.append(n_)
    return out


def _solutions(weights, n):
    """how many integer x_i in [-n, n] have sum_i w_i x_i = 0."""
    lo = -sum(abs(w) for w in weights) * n
    span = -2 * lo + 1
    cur = [0] * span
    cur[-lo] = 1
    for w in weights:
        nxt = [0] * span
        for s, c in enumerate(cur):
            if not c:
                continue
            for x in range(-n, n + 1):
                t = s + w * x
                if 0 <= t < span:
                    nxt[t] += c
        cur = nxt
    return cur[-lo]


def _group(k, reversal):
    """every element of the group, as a permutation of the bead positions."""
    els = [tuple((i + j) % k for i in range(k)) for j in range(k)]
    if reversal:
        els += [tuple((j - i) % k for i in range(k)) for j in range(k)]
    return els


def _bound(orbits):
    """S, derived from the orbit weights rather than assumed.

    A group element with orbits of sizes w_1..w_m contributes the number of integer points at
    height n of the cone {|x_i| <= t, sum w_i x_i = 0} in R^(m+1). Every ray of that cone is
    cut out by m of the defining hyperplanes, so its height divides the determinant of their
    x-parts, and those determinants are the w_i (replace one e_i by w) together with 1. Each
    simplicial cone in a triangulation has at most m+1 rays, so

        A(z) = prod_{d | some w_i} Phi_d(z)^(m+1)

    annihilates that term, and the lcm over the group's elements annihilates a.

    A ROTATION has all its orbits the same size, so the equation reduces to sum x_i = 0 and
    every determinant is 1: the term is a polynomial of degree below m, and S = k is right.
    A REFLECTION of an odd-length bracelet fixes one bead and pairs the rest, so its weights
    are 1 and 2, x_0 = -2(x_1 + ... ) is forced even, and the term has PERIOD TWO. S = k was
    assumed for both and is false for the bracelets: the fifth difference of A208826 is
    -36, 48, -60, ... and never vanishes. The bound is computed here instead.
    """
    from math import gcd
    D = set()
    for ws in orbits:
        for w in ws:
            d = 1
            while d <= w:
                if w % d == 0:
                    D.add(d)
                d += 1
    deg = 0
    for d in sorted(D):
        t, kk, mm = d, 2, d
        while kk * kk <= mm:
            if mm % kk == 0:
                while mm % kk == 0:
                    mm //= kk
                t -= t // kk
            kk += 1
        if mm > 1:
            t -= t // mm
        deg += t
    # One more than that. Each Burnside term is a cone containing the origin, and the origin
    # is a cell of the arrangement with no ray: its series is the constant 1, whose numerator
    # over the common denominator has degree exactly the denominator's. Every cell that HAS a
    # ray keeps the numerator below it. Same correction as latpoly's, for the same reason.
    return deg * (max(len(ws) for ws in orbits) + 1) + 1


def build(p, cap=200000):
    k = p['k']
    els = [_orbit_sizes(e) for e in _group(k, p['reversal'])]
    return {'k': k, 'orbits': els, 'S': _bound(els)}


def terms(b, N):
    """the number of necklaces for n = 0, 1, 2, ... -- the entry's own index."""
    g = len(b['orbits'])
    out = []
    for n in range(N + 3):
        tot = sum(_solutions(w, n) for w in b['orbits'])
        assert tot % g == 0, 'Burnside sum not divisible by the group order'
        out.append(tot // g)
    return out


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
