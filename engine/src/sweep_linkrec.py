#!/usr/bin/env python3
"""The sweep for conjectures that live in a linked a-file rather than in the entry.

    Empirical recurrence of order 42 (see link above).

is the whole of what 192 entries say, and every one of them has a name an engine here already
reads. `linkrec` fetches the file; from there this is the ordinary annihilation test, with one
extra refusal: the entry's own sentence states an ORDER, and if the fetched file's order is
not that order then the two are not the same statement and the pair is refused rather than
reconciled.

    ANUMS_FILE=deep-check/linkrec.txt BUDGET=300 python3 src/sweep_linkrec.py 200000 0 3
"""
import collections
import json
import os
import signal
import sys
import zlib

import atomicjson
import conjlines
import linkrec
import localentry as LE
import openness
import uniform

CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
SHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 0
NSHARD = int(sys.argv[3]) if len(sys.argv) > 3 else 1
SFX = '' if NSHARD == 1 else f'_{SHARD}'
HITS, DONE = f'linkrec_hits{SFX}.json', f'linkrec_done{SFX}.json'
WHY = f'linkrec_why{SFX}.json'
BUDGET = int(os.environ.get('BUDGET', '300'))
FETCH = os.environ.get('LRFETCH', '') == '1'

pool = [a for a in open(os.environ.get('ANUMS_FILE', 'deep-check/linkrec.txt')).read().split()
        if a.startswith('A')]
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
# A shard's `done` is its own file, so a run at a different NSHARD repartitions the pool and
# asks the same entries again -- two of the first six proofs were computed twice that way, at
# several minutes each. What any shard has already settled is settled.
import glob as _glob
for _f in _glob.glob('linkrec_hits_*.json') + ['linkrec_hits.json']:
    try:
        done |= {h['anum'] for h in json.load(open(_f)) if isinstance(h, dict) and h.get('anum')}
    except Exception:
        pass
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
    line = next((L for L in conjlines.claims(e) if linkrec.points_at_link(L)), None)
    if line is None:
        res['no line defers to a link'] += 1; done.add(a); save(); continue
    st = linkrec.stated(line)
    if not st:
        res['line names no order'] += 1; done.add(a); save(); continue
    if st[0] != 'recurrence':
        res['claim is a polynomial, not a recurrence'] += 1; done.add(a); save(); continue
    rec = linkrec.recurrence(a, FETCH)
    if not rec:
        res['a-file absent or unparsed'] += 1; continue      # NOT done: a fetch may fix it
    if max(rec[0]) != st[1]:
        res['a-file order differs from the entry'] += 1; done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    got = uniform.read(e['name'])
    if not got:
        res['name no longer read'] += 1; done.add(a); save(); continue
    en, p = got
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
    coeffs, claimed = rec
    order = max(coeffs)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        signal.alarm(BUDGET * 4)
        t = uniform.terms(en, p, b, len(d) + off + 5)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['terms timed out'] += 1; done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['terms failed'] += 1; done.add(a); save(); continue
    tv = [None if (v is None or v.denominator != 1) else v.numerator for v in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; done.add(a); save(); continue
    try:
        signal.alarm(BUDGET * 8)
        thr = uniform.threshold(en, p, b, coeffs, order)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['annihilation timed out'] += 1; done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['threshold failed'] += 1; done.add(a); save(); continue
    if thr is None:
        res['UNRESOLVED'] += 1; done.add(a); save(); continue
    nthr = thr + off - sh
    bad = [off + k for k in range(len(d))
           if off + k > nthr and k - order >= 0 and
           d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
    if bad:
        res['claim contradicted by DATA'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': e['name'], 'bad': bad[:3]})
    else:
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': e['name'], 'engine': en, 'S': S, 'order': order,
                     'offset': off, 'shift': sh, 'nthr': nthr, 'nterms': len(d),
                     'claimed': claimed, 'stated_order': st[1],
                     'line': ' '.join(line.split()),
                     'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    done.add(a); save()
    print('done', a, res['PROVED'], flush=True)
save()
print(dict(res))
