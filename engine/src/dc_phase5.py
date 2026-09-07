#!/usr/bin/env python3
"""Deep check, Phase 5: the mathematics, recomputed from cold.

Cached verdicts are not evidence. This rebuilds each model in a fresh process, with no reuse
of anything the original run left behind, and checks four things against what the paper
claims:

  1. the model still reproduces every term the entry publishes;
  2. the recurrence the paper states still annihilates the model, with the threshold the paper
     states -- recomputed, not read back;
  3. the threshold is EXACT: the residual at the threshold index is nonzero, so the bound
     cannot be lowered, and it vanishes from there on, so it is not one too high;
  4. the claim is not contradicted anywhere in the entry's own published data.

A disagreement here is not automatically the paper's fault --- on this project the check has
been the faulty side far more often --- so every disagreement is reported with both numbers
and settled by hand, never by trusting whichever ran last.

    python3 src/dc_phase5.py <shard> <nshards> [budget]
"""
import json
import os
import signal
import sys
import zlib
from fractions import Fraction

import localentry as LE
import repopaths
import uniform


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
BUDGET = int(sys.argv[3]) if len(sys.argv) > 3 else 120
OUT = os.path.join(repopaths.DEEPCHECK, f'phase5-{SHARD}.json')
state = json.load(open(OUT)) if os.path.exists(OUT) else {'ok': [], 'bad': [], 'skip': {}}


def save():
    json.dump(state, open(OUT, 'w'), indent=1)


def skip(a, why):
    state['skip'][why] = state['skip'].get(why, 0) + 1


seen = set(state['ok']) | {b[0] for b in state['bad']}
hits = [h for h in json.load(open('uniall_hits.json'))
        if not h.get('FAILS') and h.get('coeffs') and h.get('engine')]
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    if a in seen or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    seen.add(a)
    try:
        e = LE.get(a)
        got = uniform.read(e['name'])
    except Exception:
        skip(a, 'entry or name unreadable'); save(); continue
    if not got:
        skip(a, 'no engine reads the name now'); save(); continue
    en, p = got
    if en != h['engine']:
        # Two engines reading the same name is an OVERLAP, not a defect: engines written
        # later generalise earlier ones, and `uniform.read` returns whichever comes first in
        # its list. What the paper claims is what ITS engine computes, so the rebuild uses
        # that engine; the overlap is recorded for the duplicate-work audit.
        state.setdefault('overlap', []).append([a, h['engine'], en])
        try:
            p = uniform.M[h['engine']].parse_name(e['name'])
        except Exception:
            p = None
        if not p:
            state['bad'].append([a, f"the engine the paper used ({h['engine']}) no longer "
                                    f"parses the name"])
            save(); continue
        en = h['engine']
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, 2000000)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); skip(a, 'rebuild timed out'); save(); continue
    except Exception:
        signal.alarm(0); skip(a, 'rebuild raised'); save(); continue
    if b is None:
        skip(a, 'rebuild over the cap'); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    order = max(coeffs)
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, len(d) + off + 5)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); skip(a, 'terms timed out'); save(); continue
    except Exception:
        signal.alarm(0); skip(a, 'terms raised'); save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        state['bad'].append([a, 'the rebuilt model no longer reproduces the published DATA'])
        save(); continue
    try:
        signal.alarm(BUDGET)
        thr = uniform.threshold(en, p, b, coeffs, order)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); skip(a, 'threshold timed out'); save(); continue
    except Exception:
        signal.alarm(0); skip(a, 'threshold raised'); save(); continue
    if thr is None:
        state['bad'].append([a, 'the recurrence no longer annihilates the rebuilt model'])
        save(); continue
    nthr = thr + off - sh
    if 'nthr' in h and nthr != h['nthr']:
        state['bad'].append([a, f"threshold moved: paper says n > {h['nthr']}, "
                                f"the cold rebuild says n > {nthr}"])
        save(); continue
    bad = [off + k for k in range(len(d))
           if off + k > nthr and k - order >= 0
           and d[k] != sum(coeffs[i] * d[k - i] for i in coeffs)]
    if bad:
        state['bad'].append([a, f'claim contradicted by the entry DATA at n={bad[:3]}'])
        save(); continue
    state['ok'].append(a)
    save()
print(f"Phase 5 shard {SHARD}/{NSHARD}: {len(state['ok'])} recomputed and agreeing, "
      f"{len(state['bad'])} disagreements")
for b in state['bad'][:20]:
    print('   ', *b)
if state.get('overlap'):
    print(f"  {len(state['overlap'])} entries two engines both read (an overlap, not a "
          f"defect); the rebuild used the engine the paper used")
if state['skip']:
    print('  not recomputed:')
    for k, v in sorted(state['skip'].items(), key=lambda x: -x[1]):
        print(f'    {v:5d}  {k}')
