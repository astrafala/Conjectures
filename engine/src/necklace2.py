#!/usr/bin/env python3
"""Necklaces and bracelets of k beads over -n..n with sum zero AND a cyclic condition.

    Number of 4-bead necklaces labeled with numbers -n..n not allowing reversal, with sum zero
      with no three beads in a row equal.
    Number of 5-bead necklaces labeled with numbers -n..n allowing reversal, with sum zero and
      avoiding the patterns z z+1 z+2 and z z-1 z-2.

`necklace' reads the bare `with sum zero' names and stops there; 31 entries add a condition and
no engine read one. Burnside still applies, and the condition changes only what is counted at
each group element, not the averaging.

A labelling fixed by g is constant on the orbits of g. For a ROTATION by d with c = gcd(k, d)
the fixed labellings are exactly the c-periodic words, the whole sum is (k/c) times the sum of
one period, and the cyclic condition on the k-periodic extension is the cyclic condition on the
length-c word. For a REFLECTION the fixed labellings are the palindromes, determined by
ceil((k+1)/2) values, and the condition is again local in those.

So every term is: cyclic words of length m over -n..n with a weighted sum zero and a cyclic
window condition of width at most 3. With m - 1 free values and the last solved from the sum,
the small orbits are counted by direct enumeration; the identity, where m = k, is counted by a
dynamic programme over (previous two values) carrying the running sum, with the transition
factored through the sum over the oldest value so that the cost is O(k (2n+1)^2 * k n) rather
than O(k (2n+1)^3 * k n).

Each fixed-point count is a lattice-point count over a union of relatively open rational cones,
so it is a quasi-polynomial in n; a Burnside average of quasi-polynomials is one; the degree is
at most k - 1 and the period divides the lcm of the orbit sizes, exactly as in `necklace'.
"""
import re
from itertools import product
from math import gcd

NAME = re.compile(
    r'^\s*Number of (\d+)-bead (necklace|bracelet)s?\s+labeled with numbers -n\.\.n\s+'
    r'(not allowing reversal|allowing reversal)?,?\s*with sum zero\s*(.*?)\s*\.?\s*$', re.I)

COND = {
    'with no three beads in a row equal': 'eq3',
    'and avoiding the pattern z z+1 z+2': 'up',
    'and avoiding the patterns z z+1 z+2 and z z-1 z-2': 'updown',
    'and first differences in -n..n': 'd1',
}


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    k = int(m.group(1))
    if not 3 <= k <= 8:
        return None
    tail = ' '.join((m.group(4) or '').lower().split())
    if tail not in COND:
        return None                      # `first and second differences' is not local in two
    rev = m.group(3)
    reversal = (rev is None and m.group(2).lower() == 'bracelet') or \
               (rev is not None and rev.lower() == 'allowing reversal')
    return {'engine': 'necklace2', 'k': k, 'reversal': reversal, 'cond': COND[tail], 'frac': 1}


def _ok3(cond, a, b, t, n):
    """whether the three consecutive beads a, b, t are allowed."""
    if cond == 'eq3':
        return not (a == b == t)
    if cond == 'up':
        return not (b == a + 1 and t == a + 2)
    if cond == 'updown':
        return not (b == a + 1 and t == a + 2) and not (b == a - 1 and t == a - 2)
    if cond == 'd1':
        return abs(t - b) <= n
    raise KeyError(cond)


def _words_ok(cond, w, n):
    """the cyclic word w, as a tuple, satisfies the condition."""
    k = len(w)
    return all(_ok3(cond, w[i], w[(i + 1) % k], w[(i + 2) % k], n) for i in range(k))


def _small(m, weights, cond, n, rep):
    """count by enumeration: m orbit values, the last solved from the weighted sum."""
    V = range(-n, n + 1)
    tot = 0
    for head in product(V, repeat=m - 1):
        s = sum(w * y for w, y in zip(weights, head))
        last = weights[m - 1]
        if s % last:
            continue
        y = -s // last
        if not -n <= y <= n:
            continue
        vals = head + (y,)
        if _words_ok(cond, rep(vals), n):
            tot += 1
    return tot


def _events(k, cond):
    """the forbidden windows, each as the offsets it ties the three positions to."""
    if cond == 'eq3':
        return [((i, 0), ((i + 1) % k, 0), ((i + 2) % k, 0)) for i in range(k)]
    if cond == 'up':
        return [((i, 0), ((i + 1) % k, 1), ((i + 2) % k, 2)) for i in range(k)]
    if cond == 'updown':
        return ([((i, 0), ((i + 1) % k, 1), ((i + 2) % k, 2)) for i in range(k)] +
                [((i, 0), ((i + 1) % k, -1), ((i + 2) % k, -2)) for i in range(k)])
    raise KeyError(cond)


def _merge(k, chosen):
    """union-find with offsets: x_p = y_(root of p) + off_p, or None if inconsistent."""
    par = list(range(k))
    off = [0] * k

    def find(p):
        if par[p] == p:
            return p, 0
        r, d = find(par[p])
        par[p] = r
        off[p] += d
        return r, off[p]

    for ev in chosen:
        base, b0 = ev[0]
        for q, c in ev[1:]:
            ra, da = find(base)
            rb, db = find(q)
            # x_base = y_ra + da (with offset b0 = 0), x_q = y_rb + db, and x_q = x_base + c
            if ra == rb:
                if db - da != c:
                    return None
                continue
            par[rb] = ra
            off[rb] = da + c - db
    groups = {}
    for p in range(k):
        r, d = find(p)
        groups.setdefault(r, []).append((p, d))
    return list(groups.values())


def _count_affine(groups, n):
    """integer points with x_p = y_g + off_p in [-n, n] and sum_p x_p = 0."""
    ivs, wts, const = [], [], 0
    for g in groups:
        lo = max(-n - d for _p, d in g)
        hi = min(n - d for _p, d in g)
        if lo > hi:
            return 0
        ivs.append((lo, hi))
        wts.append(len(g))
        const += sum(d for _p, d in g)
    target = -const
    span = sum(w * max(abs(lo), abs(hi)) for w, (lo, hi) in zip(wts, ivs))
    if abs(target) > span:
        return 0
    off = span
    cur = [0] * (2 * span + 1)
    cur[off] = 1
    for w, (lo, hi) in zip(wts, ivs):
        nxt = [0] * (2 * span + 1)
        for s, c in enumerate(cur):
            if not c:
                continue
            for y in range(lo, hi + 1):
                t = s + w * y
                if 0 <= t <= 2 * span:
                    nxt[t] += c
        cur = nxt
    return cur[off + target] if 0 <= off + target <= 2 * span else 0


def _cyclic_window3(k, cond, n):
    """cyclic words of length k over -n..n, sum zero, avoiding every forbidden window.

    The forbidden windows are defined by EQUALITIES (with offsets), so inclusion-exclusion over
    them turns each term into a count of integer points under a set of affine identifications --
    a single convolution. That replaces a dynamic programme over pairs of consecutive values,
    whose cost is (2n+1)^4 times the sum range because the cycle has to be closed by fixing two
    values, and which took fourteen minutes on one four-bead entry.
    """
    ev = _events(k, cond)
    tot = 0
    for mask in range(1 << len(ev)):
        chosen = [ev[i] for i in range(len(ev)) if mask >> i & 1]
        g = _merge(k, chosen)
        if g is None:
            continue
        c = _count_affine(g, n)
        tot += -c if bin(mask).count('1') % 2 else c
    return tot


def _cyclic_chain(k, cond, n):
    """the width-2 condition |x_(i+1) - x_i| <= n, on the cycle, with sum zero."""
    assert cond == 'd1'
    off = k * n
    SR = 2 * off + 1
    tot = 0
    for a0 in range(-n, n + 1):
        cur = [None] * (2 * n + 1)
        row = [0] * SR
        row[a0 + off] = 1
        cur[a0 + n] = row
        for _ in range(k - 1):
            nxt = [None] * (2 * n + 1)
            for bi, r in enumerate(cur):
                if r is None:
                    continue
                b = bi - n
                for t in range(max(-n, b - n), min(n, b + n) + 1):
                    tgt = nxt[t + n]
                    if tgt is None:
                        tgt = nxt[t + n] = [0] * SR
                    if t >= 0:
                        for q in range(SR - t):
                            c = r[q]
                            if c:
                                tgt[q + t] += c
                    else:
                        for q in range(-t, SR):
                            c = r[q]
                            if c:
                                tgt[q + t] += c
            cur = nxt
        for bi, r in enumerate(cur):
            if r is not None and abs(bi - n - a0) <= n:
                tot += r[off]
    return tot


def _cyclic(k, cond, n):
    return _cyclic_chain(k, cond, n) if cond == 'd1' else _cyclic_window3(k, cond, n)



def _elements(k, reversal):
    """the group, as permutations perm[i] = image of position i."""
    out = [tuple((i + d) % k for i in range(k)) for d in range(k)]
    if reversal:
        out += [tuple((r - i) % k for i in range(k)) for r in range(k)]
    return out


def _orbits(perm):
    k = len(perm)
    seen = [False] * k
    orb = []
    for i in range(k):
        if seen[i]:
            continue
        cyc = []
        j = i
        while not seen[j]:
            seen[j] = True
            cyc.append(j)
            j = perm[j]
        orb.append(cyc)
    return orb


def fixed_count(k, perm, cond, n):
    """labellings fixed by perm, with sum zero and the condition."""
    orb = _orbits(perm)
    m = len(orb)
    if m == k:
        return _cyclic(k, cond, n)
    weights = [len(o) for o in orb]
    where = [0] * k
    for j, o in enumerate(orb):
        for i in o:
            where[i] = j

    def rep(vals):
        return tuple(vals[where[i]] for i in range(k))
    if m == 1:
        return sum(1 for y in range(-n, n + 1)
                   if weights[0] * y == 0 and _words_ok(cond, rep((y,)), n))
    return _small(m, weights, cond, n, rep)


def count(k, reversal, cond, n):
    G = _elements(k, reversal)
    tot = sum(fixed_count(k, g, cond, n) for g in G)
    assert tot % len(G) == 0
    return tot // len(G)


def _forms(k, perm, cond):
    """the x-part forms of the arrangement, in the orbit variables of `perm`."""
    orb = _orbits(perm)
    m = len(orb)
    where = [0] * k
    for j, o in enumerate(orb):
        for i in o:
            where[i] = j
    # each form carries the coefficient of n it appears with. `|y_i - y_j| <= n' is a pair of
    # hyperplanes that MOVE with the parameter, and treating them as fixed ones through the
    # origin gave an annihilator that failed at every index -- which the extrapolation guard
    # caught, and which is why the guard is run on a derived bound at all.
    F = set()
    for j in range(m):
        f = tuple(1 if q == j else 0 for q in range(m))
        F.add((f, -1))
        F.add((f, 1))
    F.add((tuple(len(o) for o in orb), 0))                       # the weighted sum
    for i in range(k):
        a, b, c = where[i], where[(i + 1) % k], where[(i + 2) % k]
        for u, v in ((a, b), (a, c), (b, c)) if cond != 'd1' else ((a, b),):
            if u == v:
                continue
            f = [0] * m
            f[u] += 1
            f[v] -= 1
            f = tuple(f)
            if cond == 'd1':
                F.add((f, -1))
                F.add((f, 1))
            else:
                F.add((f, 0))
    return m, sorted(F)


def _divisors(t):
    d = set()
    i = 1
    while i * i <= t:
        if t % i == 0:
            d.add(i)
            d.add(t // i)
        i += 1
    return d


def bound(k, reversal, cond):
    """(A, n_0): a monic annihilator of the necklace count and the transient before it holds.

    Each fixed-point count is a lattice-point count over a union of relatively open rational
    cones in the orbit variables, so it is a quasi-polynomial whose period divides the
    determinants of the arrangement; the Burnside average of quasi-polynomials is one, and an
    annihilator of the sum is the least common multiple of the annihilators of the terms, taken
    here as the maximum multiplicity of each cyclotomic factor.

    A ray that leaves the box or the sum-zero plane bounds no cell of the region and is
    dropped: `latpoly._rays' does that, and it is what keeps the period small -- for four beads
    with no three equal it is 3 rather than the twelve values the determinants alone offer, and
    the difference is S = 13 against S = 25, which is the difference between a model that can
    be evaluated and one that cannot.

    The patterns `z z+1 z+2' put constants into the arrangement, so the shape settles only past
    an n_0. Every constraint is on a difference of two bead values and fixes it to a value of
    absolute size at most 2, so the total forced amount is at most 2k and n_0 = 3k covers it.
    """
    import itertools

    import latpoly
    cnt = {}
    for g in _elements(k, reversal):
        m, F = _forms(k, g, cond)
        if len(F) < m:
            continue
        boxes = [(f, -1, 1) for f, _t in F if sum(abs(x) for x in f) == 1]
        eqs = [tuple(len(o) for o in _orbits(g))]
        H = [tuple(list(f) + [t]) for f, t in F]
        tot = 1
        for i in range(m):
            tot = tot * (len(H) - i) // (i + 1)
        if tot <= 600000:
            T = latpoly._rays(H, m, boxes, eqs)
            # the multiplicity of Phi_d is bounded by the number of DISTINCT rays whose height
            # d divides, and by the dimension of the cone -- which the sum-zero plane drops to
            # m - 1. Taking m for every divisor gave degree 126 at seven beads, where the true
            # bound is a fraction of that, and a model that cannot be evaluated is a refusal.
            # the cone lives in {sum w y = 0} x (the n axis), so its dimension is m: the
            # m - 1 free bead values and the parameter. Taking m - 1 refused every entry, and
            # the extrapolation guard is what said so.
            dim = m
            per = {}
            for t, gens in T.items():
                c = None if gens is None or None in gens else len(gens)
                for d in _divisors(t):
                    if per.get(d) is None and d in per:
                        continue
                    if c is None:
                        per[d] = None
                    else:
                        per[d] = None if per.get(d, 0) is None else per.get(d, 0) + c
            for d, avail in per.items():
                mult = dim if avail is None else min(dim, max(1, avail))
                cnt[d] = max(cnt.get(d, 0), mult)
            continue
        nf = len({f for f, _t in F})
        tot = 1
        for i in range(m):
            tot = tot * (nf - i) // (i + 1)
        if tot > 3_000_000:
            return None, None
        for S in itertools.combinations(sorted({f for f, _t in F}), m):
            d = latpoly._det([list(v) for v in S])
            if d:
                for q in _divisors(abs(d)):
                    cnt[q] = max(cnt.get(q, 0), m)
    if not cnt:
        return None, None
    cache = {}
    A = [1]
    for d in sorted(cnt):
        phi = latpoly._cyclotomic(d, cache)
        for _ in range(cnt[d]):
            A = latpoly._polymul(A, phi)
    n0 = 0 if cond in ('eq3', 'd1') else 3 * k
    return A, n0


def build(p, cap=200000):
    k, rev, cond = p['k'], p['reversal'], p['cond']
    if cond == 'd1' and k > 5:
        # the width-2 condition has no equality form, so it is counted by a dynamic programme
        # rather than by inclusion-exclusion, and past five beads that costs more than the
        # bound is worth. Refused with the reason rather than left to run.
        return None
    A, n0 = bound(k, rev, cond)
    if A is None:
        return None
    A = [0] * (n0 + 1) + A
    S = len(A) - 1
    if S > 90:
        return None
    vals = [count(k, rev, cond, n) for n in range(S + 6)]
    for mm in range(S, len(vals)):          # the bound, on terms it did not supply
        if vals[mm] != -sum(A[j] * vals[mm - S + j] for j in range(S)):
            return None
    return {'k': k, 'reversal': rev, 'cond': cond, 'A': A, 'S': S, 'vals': vals}


def terms(b, N):
    v = list(b['vals'])
    while len(v) <= N:
        v.append(count(b['k'], b['reversal'], b['cond'], len(v)))
    return v[:N + 1]


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
