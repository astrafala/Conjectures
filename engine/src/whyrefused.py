#!/usr/bin/env python3
"""Why was each of these refused? Cap, or time, or neither.

"State space > cap" and "build timed out" both come back from the sweep as a refusal, and
they need opposite responses: the first wants a bigger cap, the second wants a longer budget.
Re-running everything at both is how an afternoon disappears. This asks the cheap question
first --- give each entry a short, fixed slice and record which wall it hit --- so the next
pass can be aimed.

    python3 src/whyrefused.py <file of A-numbers> [seconds] [cap]
"""
import signal
import sys
import time

import localentry as LE
import openness
import uniform


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))

names = [a for a in open(sys.argv[1]).read().replace(',', ' ').split() if a]
SLICE = int(sys.argv[2]) if len(sys.argv) > 2 else 20
CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 2000000

tally = {}
for a in names:
    try:
        e = LE.get(a)
        got = uniform.read(e['name'])
    except Exception:
        tally[a] = ('unreadable', 0.0, None)
        continue
    if not got:
        tally[a] = ('no engine', 0.0, None)
        continue
    en, p = got
    if not openness.status(a)[0]:
        tally[a] = ('not open', 0.0, en)
        continue
    t0 = time.time()
    try:
        signal.alarm(SLICE)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0)
        tally[a] = ('TIME: build did not finish in %ds' % SLICE, time.time() - t0, en)
        continue
    except Exception as exc:
        signal.alarm(0)
        tally[a] = ('build raised %s' % type(exc).__name__, time.time() - t0, en)
        continue
    dt = time.time() - t0
    if b is None:
        tally[a] = ('CAP: refused at %d' % CAP, dt, en)
    else:
        tally[a] = ('builds, S=%d' % uniform.size(en, p, b), dt, en)
    print(f'{a}  {en:12s}  {tally[a][0]}  ({dt:.1f}s)', flush=True)

import collections
kind = collections.Counter(v[0].split(':')[0].split(',')[0] for v in tally.values())
print('\n' + ', '.join(f'{v} {k}' for k, v in kind.most_common()))
