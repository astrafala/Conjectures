#!/usr/bin/env python3
"""Every claim in the A196074 disproof, re-derived in exact integer arithmetic.

    python3 src/verify_a196074.py

  1. the published order-37 line fails at all 163 indices the entry's own b-file can test,
     first at n = 38 where it exceeds the true value by 393 -- no model enters this;
  2. an independent enumeration, written from the entry's wording and sharing no code with
     the engine, gives the entry's first seven terms;
  3. the transfer model reproduces all 30 DATA terms and all 200 b-file terms;
  4. 43 is the least order that fits, its coefficients are integral, and its first 37 are the
     published ones term for term;
  5. the project's own annihilation test certifies the order-43 line from n = 44 and returns
     NO threshold for the published one.

A196074 carried a row in uniall_caps.json at a cap of 2,000,000. It builds in under four
seconds at 1,461 states, which merge to 58 -- one more false cap row (defect 61), and this
one was hiding a disproof.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conjlines
import localentry as LE
import lumpauto
import ratrec
import uniform

A = 'A196074'
W, K = 4, 5
F = {0: 0, 1: 3, 2: 2, 3: 1, 4: 4}
BFILE = os.path.join(os.path.dirname(__file__), '..', '..', 'bcache', 'b196074.txt')
TRUE = [0, 13, 184, 3506]        # placeholder, replaced below from the fit
ok = True


def say(flag, msg):
    global ok
    ok = ok and flag
    print(('  ok  ' if flag else ' FAIL ') + msg)


e = LE.get(A)
data = [int(v) for v in e['data'].split(',') if v.strip()]
b = {}
for line in open(BFILE):
    line = line.strip()
    if line and not line.startswith('#'):
        p = line.split()
        b[int(p[0])] = int(p[1])

recs = [r for r in (ratrec.parse_rec(L) for L in conjlines.claims(e)) if r]
pub = recs[0][0]
d = max(pub)
C = [pub.get(i, 0) for i in range(1, d + 1)]

print('1. the published order-%d line against the entry\'s b-file' % d)
say(len(b) == 200, 'b-file has %d terms, n = %d..%d' % (len(b), min(b), max(b)))
say(all(b[i] == data[i - 1] for i in range(1, len(data) + 1)),
    'b-file agrees with all %d published DATA terms' % len(data))
bad = [(n, b[n] - sum(C[i] * b[n - 1 - i] for i in range(d)))
       for n in range(d + 1, max(b) + 1)
       if sum(C[i] * b[n - 1 - i] for i in range(d)) != b[n]]
say(len(bad) == max(b) - d, 'fails at all %d testable indices' % len(bad))
say(bad and bad[0] == (38, -393), 'first failure n=38, the line exceeding a(38) by 393')
for n, g in bad[:5]:
    print('     n=%-3d off by %+d' % (n, -g))


# 2. independent enumeration ---------------------------------------------------------------
rows = list(itertools.product(range(K), repeat=W))


def row_ok(p, c, x):
    for j in range(W):
        v = c[j]
        n = 0
        if j > 0 and c[j - 1] == F[v]:
            n += 1
        if j < W - 1 and c[j + 1] == F[v]:
            n += 1
        if p is not None and p[j] == F[v]:
            n += 1
        if x is not None and x[j] == F[v]:
            n += 1
        if n != v:
            return False
    return True


def brute(n):
    if n == 1:
        return sum(1 for r in rows if row_ok(None, r, None))
    st = {(p, c): 1 for p in rows for c in rows if row_ok(None, p, c)}
    for _ in range(n - 2):
        nx = {}
        for (p, c), v in st.items():
            for x in rows:
                if row_ok(p, c, x):
                    nx[(c, x)] = nx.get((c, x), 0) + v
        st = nx
    return sum(v for (p, c), v in st.items() if row_ok(p, c, None))


print('2. an independent enumeration from the entry\'s wording')
bf = [brute(n) for n in range(1, 8)]
say(bf == data[:7], 'n=1..7 give %s' % (bf,))


# 3. the transfer model ----------------------------------------------------------------------
en, p = uniform.read(e['name'])
model = uniform.build(en, p, 40000000)
S = uniform.size(en, p, model)
adj, start, end = uniform.lumpable(en, model)
_, _, _, S2 = lumpauto.lump(adj, start, end)
T = [int(x) for x in uniform.terms(en, p, model, max(b) + 5)]
print('3. the transfer model (%s)' % en)
say(model is not None, '%d reachable states of the %d ordered row pairs, merging to %d'
    % (S, K ** (2 * W), S2))
say(T[:len(data)] == data, 'reproduces all %d published DATA terms' % len(data))
say(all(b[i] == T[i - 1] for i in b), 'reproduces all %d b-file terms' % len(b))
say(T[:7] == bf, 'agrees with the independent enumeration at n=1..7')


# 4. the least order that fits ----------------------------------------------------------------
from fractions import Fraction


def solve(order):
    M = [[Fraction(T[n - 1 - i]) for i in range(order)]
         for n in range(order, 2 * order)]
    r = [Fraction(T[n]) for n in range(order, 2 * order)]
    for c in range(order):
        q = next((x for x in range(c, order) if M[x][c]), None)
        if q is None:
            return None
        M[c], M[q] = M[q], M[c]
        r[c], r[q] = r[q], r[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        r[c] /= pv
        for x in range(order):
            if x != c and M[x][c]:
                f = M[x][c]
                M[x] = [M[x][k] - f * M[c][k] for k in range(order)]
                r[x] -= f * r[c]
    return r


print('4. the least order that fits')
least = None
for order in range(1, 50):
    co = solve(order)
    if co is not None and all(sum(co[i] * T[n - 1 - i] for i in range(order)) == T[n]
                              for n in range(order, len(T))):
        least = (order, [int(x) for x in co] if all(x.denominator == 1 for x in co) else None)
        break
say(least and least[0] == 43, 'least order is %s' % (least and least[0]))
say(least and least[1] is not None, 'its coefficients are integral')
say(least and least[1][:37] == C, 'its first 37 are the published ones, term for term')
say(least and least[1][37:] == [274, 112, 84, -56, 8, -8],
    'the dropped tail is %s' % (least and least[1][37:],))
TRUE = least[1]
say(all(sum(TRUE[i] * b[n - 1 - i] for i in range(43)) == b[n]
        for n in range(44, max(b) + 1)),
    'the order-43 line holds at all %d b-file indices it asserts' % (max(b) - 43))


# 5. annihilation, through the project's own test ---------------------------------------------
print('5. the annihilation test, on both lines through the same code')
tc = {i + 1: TRUE[i] for i in range(43) if TRUE[i]}
thr_true = uniform.threshold(en, p, model, tc, 43)
thr_pub = uniform.threshold(en, p, model, pub, d)
say(thr_true == 42, 'the order-43 line is certified from threshold %s' % (thr_true,))
say(thr_pub is None, 'the published order-37 line returns NO threshold (%s)' % (thr_pub,))

print()
print('ALL CHECKS PASSED' if ok else 'SOMETHING FAILED')
raise SystemExit(0 if ok else 1)
