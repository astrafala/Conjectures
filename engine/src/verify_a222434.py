#!/usr/bin/env python3
"""Every claim in the A222434 disproof, re-derived in exact integer arithmetic.

    python3 src/verify_a222434.py

  1. the published order-25 line fails at all 185 indices the b-file can test (13 of them
     visible in the DATA alone), first at n = 26 where it falls short by 3;
  2. the edgemark model, 62 states, reproduces all 210 b-file terms;
  3. the annihilation test certifies the published line PLUS -a(n-26) from n = 55, and
     certifies the published line for no n at all;
  4. the range is not decoration: the corrected line fails at exactly eight indices below 55
     and holds at all 156 from 55 to 210.

The fourth entry of this shape in one day, and the variant worth separating: in A269637,
A236647 and A196074 the correction is a pure truncation, valid wherever the line asserts
anything. Here what is missing is a term AND a range, and appending the term without the
range gives another false statement.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conjlines
import localentry as LE
import lumpauto
import ratrec
import uniform

A = 'A222434'
BFILE = os.path.join(os.path.dirname(__file__), '..', '..', 'bcache', 'b222434.txt')
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

print('1. the published order-%d line' % d)
say(len(b) == 210 and all(b[i] == data[i - 1] for i in range(1, len(data) + 1)),
    'b-file has %d terms and agrees with all %d DATA terms' % (len(b), len(data)))
bad = [n for n in range(d + 1, max(b) + 1)
       if sum(C[i] * b[n - 1 - i] for i in range(d)) != b[n]]
say(len(bad) == max(b) - d, 'fails at all %d indices the b-file can test' % len(bad))
say(bad and bad[0] == 26 and b[26] - sum(C[i] * b[25 - i] for i in range(d)) == 3,
    'first failure n=26: a(26)=%d, the line gives %d' % (b[26], sum(C[i] * b[25 - i] for i in range(d))))
say(sum(1 for n in bad if n <= len(data)) == 13,
    '%d of the failures are visible in the DATA alone' % sum(1 for n in bad if n <= len(data)))

print('2. the model')
en, p = uniform.read(e['name'])
model = uniform.build(en, p, 40000000)
S = uniform.size(en, p, model)
T = [int(x) for x in uniform.terms(en, p, model, max(b) + 5)]
shift = next((s for s in range(4) if all(b[i] == T[i - 1 + s] for i in range(1, 40))), None)
say(model is not None, 'engine %s builds at %d states' % (en, S))
say(shift is not None and all(b[i] == T[i - 1 + shift] for i in b),
    'reproduces all %d b-file terms (index shift %s)' % (len(b), shift))

print('3. the annihilation test, both lines through the same code')
co = dict(pub)
co[26] = co.get(26, 0) - 1
thr_true = uniform.threshold(en, p, model, co, max(co))
thr_pub = uniform.threshold(en, p, model, pub, d)
say(thr_true == 54, 'published + (-a(n-26)) is certified from threshold %s' % (thr_true,))
say(thr_pub is None, 'the published line is certified for NO n (%s)' % (thr_pub,))

print('4. the range is not decoration')
CAND = [co.get(i, 0) for i in range(1, 27)]
cbad = [n for n in range(27, max(b) + 1)
        if sum(CAND[i] * b[n - 1 - i] for i in range(26)) != b[n]]
say(cbad == [29, 35, 38, 41, 45, 48, 51, 54],
    'the corrected line fails at %s below 55' % (cbad,))
say(all(n <= 54 for n in cbad), 'and holds at all %d indices from 55 to 210'
    % (max(b) - 54))

print()
print('ALL CHECKS PASSED' if ok else 'SOMETHING FAILED')
raise SystemExit(0 if ok else 1)
