#!/usr/bin/env python3
"""The row of an elementary cellular automaton as a template of fixed and repeated blocks.

`ecarow' and `ecacount' both ask the row to grow only at its two ends,

    w(n+p) = L_r + w(n) + R_r,

and 56 of the 256 rules refuse that shape.  Looking at what they do instead settles it at
once.  Rule 133 at steps 20 and 22 is

    00101010101010101010101010101010101010100
    001010101010101010101010101010101010101010100

-- the same word with `1010' inserted in the MIDDLE, not at the ends.  Rule 141 is

    00101010101010101010101111111111111111111
    001010101010101010101010111111111111111111111

-- two periodic runs, one gaining `10' and the other `11'.  Nothing about the ends is special;
what is true of every one of these rules is that the row is a concatenation of a bounded
number of blocks, of which some are FIXED and some are REPEATED a number of times that grows
by one every p steps:

    w(n0 + r + j*p) = B_0 . Q_1^j . B_1 . Q_2^j . ... . Q_m^j . B_m,

the B's and Q's depending only on the residue r = n mod p.  The end-growth shape is the case
m = 2 with B_0 and B_2 empty, so this is a strict generalisation and nothing already certified
is lost.

The count follows immediately: |w| = 2n+1 forces sum |Q_i| = 2p, and

    on(n0 + r + j*p) = ones(B_0) + ... + ones(B_m) + j * (ones(Q_1) + ... + ones(Q_m))

is LINEAR in j, so `on' is quasi-linear in n with period p and is annihilated by (z^p - 1)^2.
OFF is 2n+1 - on and has the same annihilator; a running total adds one factor (z - 1).

**Why the template, once seen, is a theorem and not an observation.**  The rule is a local map
of radius 1, so p steps have radius p.  Let the template hold at j = K with every repeated run
at least 4p + 4|Q_i| long, and let

    F^p(T(K)) = T(K+1)   and   F^p(T(K+1)) = T(K+2)

be verified by direct simulation.  Take any j > K.  T(j) is T(K) with (j-K) further copies of
each Q_i inserted inside runs that are already longer than 2p.  A cell of F^p(T(j)) within
distance |B_0| + |Q_1|K - p of the left end sees only input cells that T(j) and T(K) share at
the same left-distance, so those output cells agree with F^p(T(K)); symmetrically at the right
end; and strictly inside a run of length > 2p the input is |Q_i|-periodic, so the output there
is |Q_i|-periodic too, with the period and phase already fixed by the two verified steps.
Hence F^p(T(j)) = T(j+1) for every j >= K, and the template -- and with it the count -- holds
for all n by induction.  Two simulations at a large K prove infinitely many.
"""
import ecarow


def _templates(rows, maxruns=3, cap=200, budget=200000):
    """every block template that renders the whole observed class, not just the first pair.

    Aligning a_0 into a_1 alone and taking the FEWEST insertion runs is the wrong question:
    rule 141 grows by `10' in one periodic run and `11' in another, and a single run of `1011'
    aligns the first pair just as well and then fails at the second.  The search below carries
    every row of the class at once -- a fixed block must match in all of them and a repeated
    block must appear j times in the j-th -- so a template is only ever built out of pieces
    that already survive the whole class.
    """
    a = rows[0]
    D = len(rows[1]) - len(a)
    out = []
    # A chaotic rule has no template and the search for one must not be allowed to cost the
    # whole run finding that out; the visit budget is what makes a refusal cheap.
    seen = [0]

    def go(i, pos, pieces, used, d):
        seen[0] += 1
        if len(out) >= cap or seen[0] > budget:
            return
        tmax = 0
        while i + tmax < len(a):
            t = tmax + 1
            if any(rows[j][pos[j]:pos[j] + t] != a[i:i + t] for j in range(len(rows))):
                break
            tmax = t
        t = len(a) - i
        if t <= tmax and all(pos[j] + t == len(rows[j]) for j in range(len(rows))):
            out.append(pieces + [('f', a[i:])])
        if used >= maxruns or d >= D:
            return
        for t in range(tmax + 1):
            if t == 0 and pieces and pieces[-1][0] == 'q':
                continue          # two adjacent runs are one run
            for L in range(1, D - d + 1):
                q = rows[1][pos[1] + t:pos[1] + t + L]
                if len(q) < L:
                    break
                np = []
                for j in range(len(rows)):
                    c = pos[j] + t
                    if rows[j][c:c + L * j] != q * j:
                        np = None
                        break
                    np.append(c + L * j)
                if np is None:
                    continue
                go(i + t, np, pieces + [('f', a[i:i + t]), ('q', q)], used + 1, d + L)

    go(0, [0] * len(rows), [], 0, 0)
    return out


def render(parts, j):
    return ''.join(s * j if k == 'q' else s for k, s in parts)


def _bg(rule, n):
    """the value the cells outside the light cone hold at step n."""
    v = 0
    for _ in range(n):
        v = (rule >> (v * 7)) & 1
    return v


def _evolve(rule, w, n, steps):
    """`steps` steps from the row `w` at time n, in its own background."""
    pad = 2 * steps + 4
    b = _bg(rule, n)
    row = [b] * pad + [int(c) for c in w] + [b] * pad
    W = len(row)
    for t in range(steps):
        # the array's own two end cells have no outside neighbour; they are given the
        # background value they would hold anyway, and the padding exceeds the number of
        # steps, so no cell the answer depends on ever sees them
        nb = _bg(rule, n + t + 1)
        nxt = [nb] * W
        for i in range(1, W - 1):
            nxt[i] = (rule >> ((row[i - 1] << 2) | (row[i] << 1) | row[i + 1])) & 1
        row = nxt
    k = pad - steps
    return ''.join(map(str, row[k:W - k]))


def shape(ws, maxp=17, maxn0=30, maxruns=3, rule=None):
    """(n0, p, {r: template}) holding for every observed row -- and PROVED, when `rule` is
    given, by the two simulations `certify' makes.

    The search is budgeted, so the list of templates it offers at one (p, n0) can be cut
    short; a shape that fits the rows but does not certify must therefore not end the search.
    It only skips that pair and goes on, and a settled rule is never lost to a truncation.
    """
    for per in range(1, maxp):
        for n0 in range(0, maxn0):
            if n0 + 3 * per + 4 >= len(ws):
                continue
            tem, ok = {}, True
            for r in range(per):
                base = n0 + r
                cls = [ws[k] for k in range(base, len(ws), per)]
                if len(cls) < 4 or any(len(cls[j + 1]) != len(cls[j]) + 2 * per
                                       for j in range(len(cls) - 1)):
                    ok = False
                    break
                cand = _templates(cls, maxruns)
                if not cand:
                    ok = False
                    break
                tem[r] = min(cand, key=lambda t: (sum(1 for k, _ in t if k == 'q'), len(t)))
            if ok and len(tem) == per and (rule is None or certify(rule, n0, per, tem)):
                return n0, per, tem
    return None


def certify(rule, n0, per, tem, ws=None):
    """simulate the p-step map at a K large enough for locality to carry it to every j."""
    for r in range(per):
        parts = tem[r]
        qs = [s for k, s in parts if k == 'q']
        if not qs:
            return False
        K = 1
        while any(len(q) * K < 4 * per + 4 * len(q) + 4 for q in qs):
            K += 1
        for j in (K, K + 1):
            n = n0 + r + j * per
            if _evolve(rule, render(parts, j), n, per) != render(parts, j + 1):
                return False
    return True
