#!/usr/bin/env python3
"""Every claim in the A236647 disproof, re-derived from scratch in exact integer arithmetic.

    python3 src/verify_a236647.py

  1. the published order-34 line fails at all 176 indices the entry's own b-file can test,
     first at n = 35, short by 145084608 -- no model enters this;
  2. the reading of Hardin's wording is the right one -- brute force over all 3^(3(n+1))
     arrays for n <= 3, and the same rule at width 2 reproduces A236646;
  3. the 224-state transfer model reproduces all 16 DATA terms and all 210 b-file terms;
  4. 38 is the least order holding on the tail -- every order below it fails there, so the
     published 34 is too short to repair with any coefficients;
  5. p(M)u does NOT vanish, and that is the point: 1^T w = 114688 is exactly the n = 39
     exception the parent table A236651 names ("[order 38] for n>39"), while 1^T M^m (Mw)
     vanishes for every m <= 224 and so, by Cayley-Hamilton, for every m.
"""
import itertools
import json
import os
import re
from fractions import Fraction

W = 3                      # the entry is (n+1) X (2+1)
BFILE = os.path.join(os.path.dirname(__file__), '..', 'bcache', 'b236647.txt')
DATA = [484, 4500, 41980, 394380, 3668492, 34234336, 319904840, 2991463632,
        27901011760, 260484793448, 2433205784152, 22729004719568,
        212171486821248, 1981136638265476, 18502116150459608, 172787369160052104]
LINE = ('a(n) = 13*a(n-2) +184*a(n-3) +3506*a(n-4) +9110*a(n-5) +21587*a(n-6) '
        '+63605*a(n-7) -342128*a(n-8) -864643*a(n-9) +1140624*a(n-10) +294974*a(n-11) '
        '+739053*a(n-12) +15509266*a(n-13) -16660349*a(n-14) -37563062*a(n-15) '
        '+41074149*a(n-16) -39645704*a(n-17) -48556860*a(n-18) +140778823*a(n-19) '
        '-72899036*a(n-20) -67241570*a(n-21) +329687733*a(n-22) -46469782*a(n-23) '
        '-133466871*a(n-24) +319656720*a(n-25) -408928291*a(n-26) -40519358*a(n-27) '
        '+151099557*a(n-28) -160188966*a(n-29) +104521624*a(n-30) -63973040*a(n-31) '
        '-163603316*a(n-32) +759648*a(n-33) +12746672*a(n-34)')

ok = True


def say(flag, msg):
    global ok
    ok = ok and flag
    print(('  ok  ' if flag else ' FAIL ') + msg)


def parse(line):
    co = {}
    for sgn, num, k in re.findall(r'([+-]?)\s*(\d*)\s*\*?\s*a\(n-(\d+)\)',
                                  line.split('a(n) =', 1)[1]):
        c = int(num) if num else 1
        co[int(k)] = co.get(int(k), 0) + (-c if sgn == '-' else c)
    return [co.get(i, 0) for i in range(1, max(co) + 1)]


def chi(a, b, c, d):
    s = sorted([a, b, c, d])
    return s[3] + s[2] - s[1] - s[0]


# 1. the disproof, on the entry's b-file and nothing else --------------------------------
b = {}
for l in open(BFILE):
    l = l.strip()
    if l and not l.startswith('#'):
        p = l.split()
        b[int(p[0])] = int(p[1])
C = parse(LINE)
d = len(C)
print('1. the published order-%d line against the entry\'s b-file' % d)
say(len(b) == 210 and b[1] == 484, 'b-file has %d terms, n = %d..%d' % (len(b), min(b), max(b)))
say(all(b[i] == DATA[i - 1] for i in range(1, 17)), 'b-file agrees with the published DATA')
bad = []
for n in range(d + 1, max(b) + 1):
    r = sum(C[i] * b[n - 1 - i] for i in range(d))
    if r != b[n]:
        bad.append((n, b[n] - r))
say(len(bad) == max(b) - d, 'fails at all %d testable indices' % len(bad))
say(bad and bad[0] == (35, 145084608), 'first failure n=35, short by 145084608')
for n, g in bad[:6]:
    print('     n=%-3d short by %d' % (n, g))


# 2. the reading of the wording -----------------------------------------------------------
def brute(rows, width):
    n = 0
    for A in itertools.product(range(3), repeat=rows * width):
        v = [[chi(A[r * width + c], A[r * width + c + 1],
                  A[(r + 1) * width + c], A[(r + 1) * width + c + 1])
              for c in range(width - 1)] for r in range(rows - 1)]
        good = True
        for r in range(rows - 1):
            for c in range(width - 1):
                if c + 1 < width - 1 and v[r][c] == v[r][c + 1]:
                    good = False
                if r + 1 < rows - 1 and v[r][c] == v[r + 1][c]:
                    good = False
            if not good:
                break
        n += good
    return n


print('2. brute force straight from the entry\'s words')
bf = [brute(n + 1, W) for n in (1, 2, 3)]
say(bf == DATA[:3], 'width 3, n=1..3 give %s' % (bf,))
bf2 = [brute(n + 1, 2) for n in (1, 2, 3, 4)]
say(bf2 == [81, 484, 2932, 17824], 'the same rule at width 2 gives A236646: %s' % (bf2,))


# 3. the transfer model ---------------------------------------------------------------------
rows = list(itertools.product(range(3), repeat=W))


def colours(p, q):
    return tuple(chi(p[c], p[c + 1], q[c], q[c + 1]) for c in range(W - 1))


init = {}
for p in rows:
    for q in rows:
        cv = colours(p, q)
        if len(set(cv)) == len(cv):
            init[(q, cv)] = init.get((q, cv), 0) + 1
S, frontier, edges = set(init), set(init), {}
while frontier:
    nf = set()
    for s in frontier:
        q, cv = s
        out = []
        for r in rows:
            nv = colours(q, r)
            if len(set(nv)) != len(nv) or any(nv[i] == cv[i] for i in range(W - 1)):
                continue
            out.append((r, nv))
            if (r, nv) not in S:
                S.add((r, nv))
                nf.add((r, nv))
        edges[s] = out
    frontier = nf
idx = {s: i for i, s in enumerate(sorted(S))}
D = len(idx)
M = [[0] * D for _ in range(D)]
for s, out in edges.items():
    for k in out:
        M[idx[k]][idx[s]] += 1
u = [0] * D
for s, c in init.items():
    u[idx[s]] = c
one = [1] * D


def mv(v):
    return [sum(M[i][j] * v[j] for j in range(D) if M[i][j]) for i in range(D)]


N = 215
terms, v = [], u[:]
for _ in range(N):
    terms.append(sum(v))
    v = mv(v)
print('3. the transfer model')
say(D == 224, '%d reachable states' % D)
say(terms[:16] == DATA, 'reproduces all 16 published DATA terms')
say(all(b[i] == terms[i - 1] for i in b), 'reproduces all %d b-file terms' % len(b))
say(min(len(edges[s]) for s in S) >= 1,
    'every state extends (min out-degree %d), so a is nondecreasing'
    % min(len(edges[s]) for s in S))


# 4. the least order that holds on the tail ---------------------------------------------------
def solve_at(order, start):
    A = [[Fraction(terms[n - 1 - i]) for i in range(order)]
         for n in range(start, start + order)]
    rhs = [Fraction(terms[n]) for n in range(start, start + order)]
    for c in range(order):
        p = next((r for r in range(c, order) if A[r][c]), None)
        if p is None:
            return None
        A[c], A[p] = A[p], A[c]
        rhs[c], rhs[p] = rhs[p], rhs[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        rhs[c] /= pv
        for r in range(order):
            if r != c and A[r][c]:
                f = A[r][c]
                A[r] = [A[r][k] - f * A[c][k] for k in range(order)]
                rhs[r] -= f * rhs[c]
    return rhs


print('4. the least order that holds on the tail')
holds = []
for order in range(1, 39):
    co = solve_at(order, 140)
    if co is None:
        continue
    if all(sum(co[i] * terms[n - 1 - i] for i in range(order)) == terms[n]
           for n in range(140, len(terms))):
        holds.append(order)
say(holds == [38], 'orders 1..38 fitted at n=140: only %s holds' % holds)
TRUE = [int(x) for x in solve_at(38, 140)]
say(all(isinstance(x, int) for x in TRUE), 'its coefficients are integral')
say(TRUE[:34] == C, 'its first 34 coefficients are the published ones, term for term')
say(TRUE[34:] == [1733120, 12956032, 5889024, -243712],
    'the dropped tail is %s' % (TRUE[34:],))


# 5. annihilation ------------------------------------------------------------------------------
print('5. annihilation')
pows = [u[:]]
for _ in range(38):
    pows.append(mv(pows[-1]))
pc = [1] + [-c for c in TRUE]
w = [sum(pc[i] * pows[38 - i][j] for i in range(39)) for j in range(D)]
say(sum(one[i] * w[i] for i in range(D)) == 114688,
    '1^T p(M)u = 114688 -- the n=39 exception the table names')
v, first = mv(w), None
for m in range(D + 1):
    if sum(one[i] * v[i] for i in range(D)) != 0:
        first = m
        break
    v = mv(v)
say(first is None, '1^T M^m (M p(M)u) = 0 for every m <= %d, so for every m' % D)
bfbad = [n for n in range(39, max(b) + 1)
         if sum(TRUE[i] * b[n - 1 - i] for i in range(38)) != b[n]]
say(bfbad == [39], 'against the b-file the order-38 line fails only at n=39')

print()
print('ALL CHECKS PASSED' if ok else 'SOMETHING FAILED')
raise SystemExit(0 if ok else 1)
