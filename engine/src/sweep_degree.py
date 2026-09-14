#!/usr/bin/env python3
"""The sweep for "a(n) is a polynomial of degree d for n>k".

See `degclaim`. Two thresholds decide the whole claim:

    (z-1)^(d+1)  must annihilate, and its last failure fixes the first n from which a IS a
                 polynomial of degree at most d: a is polynomial on n >= nthr - d;
    (z-1)^d      must NOT annihilate, or the degree is smaller than the entry says.

The entry's own "for n>k" predicts nthr = k+d+1 exactly, so the bound is not merely sufficient
and the sweep records whether it is tight, short of the claim, or beyond it. A claim the model
proves only from LATER than the entry says is not a proof of the entry's sentence and is
recorded as a contradiction to be read by hand, never installed.

    ANUMS_FILE=deep-check/degree.txt python3 src/sweep_degree.py 200000 0 1
"""
import collections
import json
import os
import resource
import signal
import sys
import zlib

import atomicjson
import conjlines
import degclaim
import localentry as LE
import openness
import uniform

CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
SHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 0
NSHARD = int(sys.argv[3]) if len(sys.argv) > 3 else 1
TAG = os.environ.get('TAG', '')
SFX = f'{TAG}' if NSHARD == 1 else f'{TAG}_{SHARD}'
HITS, DONE, WHY = f'degree_hits{SFX}.json', f'degree_done{SFX}.json', f'degree_why{SFX}.json'
BUDGET = int(os.environ.get('BUDGET', '300'))
MEMGB = float(os.environ.get('MEMGB', '6'))
resource.setrlimit(resource.RLIMIT_AS, (int(MEMGB * 2 ** 30), resource.RLIM_INFINITY))

pool = [a for a in open(os.environ.get('ANUMS_FILE', 'deep-check/degree.txt')).read().split()
        if a.startswith('A')]
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))


def save():
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)
    atomicjson.dump(dict(res), WHY, indent=1, sort_keys=True)


import atexit
atexit.register(save)

for a in sorted(pool):
    if a in done or a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    e = LE.get(a)
    if not e:
        res['name unknown'] += 1; done.add(a); save(); continue
    got = None
    for L in conjlines.claims(e):
        r = degclaim.read(L)
        if r:
            got = (r, ' '.join(L.split()))
            break
    if not got:
        res['no degree claim'] += 1; done.add(a); save(); continue
    (deg, first), line = got
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    rd = uniform.read(e['name'])
    if not rd:
        res['name no longer read'] += 1; done.add(a); save(); continue
    en, p = rd
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['build timed out'] += 1; done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['build failed'] += 1; done.add(a); save(); continue
    if b is None:
        res['state space > cap'] += 1; done.add(a); save(); continue
    S = uniform.size(en, p, b)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, len(d) + off + 5)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['terms failed or timed out'] += 1; done.add(a); save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; done.add(a); save(); continue
    try:
        signal.alarm(BUDGET * 8)
        hi = uniform.threshold(en, p, b, degclaim.coeffs(deg), deg + 1)
        lo = uniform.threshold(en, p, b, degclaim.coeffs(deg - 1), deg) if deg else 0
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['annihilation timed out'] += 1; done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['threshold failed'] += 1; done.add(a); save(); continue
    if hi is None:
        res['UNRESOLVED: no polynomial of that degree'] += 1; done.add(a); save(); continue
    if lo is not None:
        # (z-1)^deg annihilates too, so the degree is SMALLER than the entry says
        res['degree is smaller than claimed'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': e['name'], 'line': line,
                     'deg': deg, 'smaller_from': lo})
        done.add(a); save(); continue
    nthr = hi + off - sh
    poly_from = nthr - deg
    if first is not None and poly_from > first:
        res['claim contradicted: polynomial only from later'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': e['name'], 'line': line,
                     'deg': deg, 'claimed_from': first, 'proved_from': poly_from})
        done.add(a); save(); continue
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': e['name'], 'engine': en, 'S': S, 'order': deg + 1,
                 'degree': deg, 'offset': off, 'shift': sh, 'nthr': nthr,
                 'poly_from': poly_from, 'claimed_from': first, 'nterms': len(d),
                 'line': line, 'tight': first is not None and poly_from == first,
                 'coeffs': {int(k): str(v) for k, v in degclaim.coeffs(deg).items()}})
    done.add(a); save()
    print('done', a, res['PROVED'], flush=True)
save()
print(dict(res))
