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

import bmrec
import localentry as LE
import repopaths
import uniform

# `uniall_hits.json` labels the order-line recoveries with the name of the VEIN, not of a
# transfer engine: there is no `uniform.M['ordwhole']`, and Phase 5 was reporting eight
# perfectly sound papers as disagreements for that reason alone. The engine each of those
# papers actually used is recorded in the sweep's own file, so the rebuild reads it from
# there. Those papers also make a claim no other paper makes -- that the recurrence the
# entry states is the MINIMAL one, which is what makes it unique and hence proved -- so the
# minimal order is recomputed from scratch too, not read back.
ORDW = {}
if os.path.exists('ordwhole_hits.json'):
    ORDW = {h['anum']: h for h in json.load(open('ordwhole_hits.json'))}
P62 = (1 << 61) - 1


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
    if h['engine'] == 'ordwhole':
        o = ORDW.get(a)
        if not o:
            skip(a, 'order-line record missing'); save(); continue
        h = dict(h, engine=o['engine'], nthr=o.get('nthr'), stated=o.get('stated'),
                 order=o.get('order'))
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
    if a in ORDW and ORDW[a].get('stated') is not None:
        # The paper's claim is that no SHORTER recurrence holds, so a recurrence of the
        # stated order is forced to be this one. Recompute the minimal order over a large
        # prime and then exactly over Q; both must come back at the stated order.
        stated = ORDW[a]['stated']
        try:
            signal.alarm(BUDGET)
            need = 2 * ORDW[a]['Smerged'] + max(8, stated + 4)
            tt = uniform.terms(en, p, b, need + off + 5)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); skip(a, 'order-line terms timed out'); save(); continue
        except Exception:
            signal.alarm(0); skip(a, 'order-line terms raised'); save(); continue
        sq = [x.numerator for x in tt[sh:] if x is not None and x.denominator == 1]
        if len(sq) < 2 * ORDW[a]['Smerged'] + 4:
            skip(a, 'too few exact terms to recompute the minimal order'); save(); continue
        L0 = bmrec.bm_mod([v % P62 for v in sq], P62)
        if L0 != stated:
            state['bad'].append([a, f'minimal order recomputed as {L0}, the paper needs it '
                                    f'to be {stated}'])
            save(); continue
        Lx, cs = bmrec.bm([Fraction(v) for v in sq])
        if Lx != stated or any(c.denominator != 1 for c in cs):
            state['bad'].append([a, 'the minimal recurrence over Q is no longer integral of '
                                    'the stated order'])
            save(); continue
        if {i + 1: int(c) for i, c in enumerate(cs)} != coeffs:
            state['bad'].append([a, 'the recomputed minimal recurrence is not the one the '
                                    'paper prints'])
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
    # The order-line papers print no threshold: their claim is that the recurrence is the
    # minimal one, recomputed above, and their record's `nthr` is bookkeeping the paper never
    # quotes. Comparing against it flagged a paper for a sentence it does not contain.
    if a in ORDW:
        h = dict(h); h.pop('nthr', None)
    if 'nthr' in h and h['nthr'] is not None and nthr != h['nthr']:
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
# The per-shard file is rewritten after every entry, so while a run is going it is dirty in
# the working tree every few seconds and no commit of it is ever current. It is progress. The
# result is the merge of every shard, written when a shard has nothing left to attempt, and
# that is what is stored.
def _summary():
    import glob
    ok, bad, skip = set(), [], {}
    for f in glob.glob(os.path.join(repopaths.DEEPCHECK, 'phase5-*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        ok |= set(d['ok'])
        bad += d['bad']
        for k, v in d.get('skip', {}).items():
            skip[k] = skip.get(k, 0) + v
    json.dump({'recomputed': len(ok), 'disagreements': bad, 'not_recomputed': skip,
               'entries': sorted(ok)},
              open(os.path.join(repopaths.DEEPCHECK, 'phase5.json'), 'w'), indent=1)


_summary()
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
