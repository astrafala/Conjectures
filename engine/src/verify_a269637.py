#!/usr/bin/env python3
"""Every claim in the A269637 disproof, re-derived from scratch in exact integer arithmetic.

    python3 src/verify_a269637.py

The paper says five things and this checks all five:

  1. the published order-10 line fails at all ten indices the entry's own DATA can test it,
     using nothing but the entry's twenty published integers;
  2. the reading of the name is the right one -- brute force over all 6^n tuples, n <= 7;
  3. the 42-state transfer model reproduces the DATA and all 210 b-file terms;
  4. order 13 is the least that admits a constant-coefficient recurrence, and it is integral;
  5. p(M)u is the zero vector, which proves the order-13 line outright -- no Cayley-Hamilton
     appeal needed -- and the weaker Krylov test m < 42 is run as well.

The point of keeping this is the first item. A disproof that needs a model is only as good as
the model; this one does not. Ten multiply-adds on numbers the entry prints settle it, and
everything after item 1 is about the CORRECTION, not about the refutation.
"""
import itertools
import json
import os
from fractions import Fraction

K = 6
PUB = [6, 36, 210, 1209, 6876, 38738, 216528, 1202353, 6639294, 36486190,
       199677806, 1088813760, 5918190122, 32077034918, 173421804818, 935474530883,
       5035906367464, 27059901888584, 145161762258568, 777537033208493]
CONJ = [29, -330, 1730, -2815, -9981, 36088, 31192, -161403, -158561, 291970]
TRUE = CONJ + [583350, 364874, 80630]
BFILE = os.path.join(os.path.dirname(__file__), '..', '..', 'bcache', 'b269637.txt')

ok = True


def say(flag, msg):
    global ok
    ok = ok and flag
    print(('  ok  ' if flag else ' FAIL ') + msg)


# 1. the disproof, on the entry's own integers and nothing else ------------------------
print('1. the published order-10 line against the published DATA')
fails = []
for n in range(11, 21):
    rhs = sum(CONJ[i] * PUB[n - 2 - i] for i in range(10))
    fails.append((n, PUB[n - 1], rhs, PUB[n - 1] - rhs))
for n, t, r, d in fails:
    print('     n=%-3d true %-16d line %-16d diff %d' % (n, t, r, d))
say(all(d != 0 for _, _, _, d in fails), 'fails at all %d testable indices' % len(fails))
say(fails[0][3] == 643714, 'first failure n=11, difference 643714')


# 2. the reading of the name ------------------------------------------------------------
def admissible(t):
    prev = None
    for i in range(1, len(t)):
        if t[i] == t[i - 1]:
            if prev is not None and (t[i] - prev) not in (2, -1):
                return False
            prev = t[i]
    return True


print('2. brute force over all 6^n tuples')
bf = [sum(1 for t in itertools.product(range(K), repeat=n) if admissible(t))
      for n in range(1, 8)]
say(bf == PUB[:7], 'n=1..7 give %s' % (bf,))


# 3. the transfer model -----------------------------------------------------------------
STATES = [(L, P) for L in range(K) for P in list(range(K)) + [K]]   # K means "no repeat yet"
IDX = {s: i for i, s in enumerate(STATES)}
D = len(STATES)
M = [[0] * D for _ in range(D)]          # M[new][old]
for (L, P) in STATES:
    j = IDX[(L, P)]
    for x in range(K):
        if x != L:
            k = (x, P)
        else:
            if P != K and (x - P) not in (2, -1):
                continue
            k = (x, x)
        M[IDX[k]][j] += 1
U = [0] * D
for t in range(K):
    U[IDX[(t, K)]] = 1
ONE = [1] * D


def mv(u):
    return [sum(M[i][j] * u[j] for j in range(D) if M[i][j]) for i in range(D)]


N = 260
terms, u = [], U[:]
for _ in range(N):
    terms.append(sum(ONE[i] * u[i] for i in range(D)))
    u = mv(u)
print('3. the %d-state transfer model' % D)
say(terms[:20] == PUB, 'reproduces all 20 published DATA terms')
say(terms[:7] == bf, 'agrees with brute force at n=1..7')
try:
    b = {}
    for line in open(BFILE):
        line = line.strip()
        if line and not line.startswith('#'):
            p = line.split()
            if len(p) >= 2:
                b[int(p[0])] = int(p[1])
    say(all(b[i] == terms[i - 1] for i in b), 'reproduces all %d b-file terms' % len(b))
except OSError:
    print('  --   b-file not cached, skipped')


# 4. the least order that admits a recurrence -------------------------------------------
def solve(d):
    A = [[Fraction(terms[n - 1 - i]) for i in range(d)] for n in range(d, 2 * d)]
    rhs = [Fraction(terms[n]) for n in range(d, 2 * d)]
    for c in range(d):
        p = next((r for r in range(c, d) if A[r][c]), None)
        if p is None:
            return None
        A[c], A[p] = A[p], A[c]
        rhs[c], rhs[p] = rhs[p], rhs[c]
        pv = A[c][c]
        A[c] = [v / pv for v in A[c]]
        rhs[c] /= pv
        for r in range(d):
            if r != c and A[r][c]:
                f = A[r][c]
                A[r] = [A[r][k] - f * A[c][k] for k in range(d)]
                rhs[r] -= f * rhs[c]
    return rhs


def holds(co):
    d = len(co)
    return all(sum(co[i] * terms[n - 1 - i] for i in range(d)) == terms[n]
               for n in range(d, len(terms)))


print('4. the least order that admits a constant-coefficient recurrence')
least = None
for d in range(1, 20):
    co = solve(d)
    if co is not None and holds(co):
        least = (d, co)
        break
say(least is not None and least[0] == 13, 'least order is %s' % (least and least[0]))
say(least is not None and all(c.denominator == 1 for c in least[1]), 'coefficients integral')
say(least is not None and [int(c) for c in least[1]] == TRUE, 'they are the paper\'s')
say(TRUE[:10] == CONJ, 'the published 10 are its first 10, term for term')
say(holds(TRUE), 'order-13 line holds at all %d testable model indices' % (len(terms) - 13))


# 5. annihilation ------------------------------------------------------------------------
print('5. annihilation')
pows = [U[:]]
for _ in range(13):
    pows.append(mv(pows[-1]))
pc = [1] + [-c for c in TRUE]
w = [sum(pc[i] * pows[13 - i][j] for i in range(14)) for j in range(D)]
say(all(v == 0 for v in w), 'p(M)u is the zero vector -- the recurrence holds for every n >= 14')
u, krylov = w[:], True
for _ in range(D):
    if sum(ONE[i] * u[i] for i in range(D)) != 0:
        krylov = False
        break
    u = mv(u)
say(krylov, 'the weaker Krylov test vanishes for every m < %d as well' % D)

print()
print('ALL CHECKS PASSED' if ok else 'SOMETHING FAILED')
raise SystemExit(0 if ok else 1)
