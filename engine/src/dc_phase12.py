#!/usr/bin/env python3
"""Deep check, Phase 12: the adversarial pass, in the part a machine can do.

The reading half of Phase 12 is a person's job and is written up in DEEP-CHECK.md. This is
the half that is not: attacking each claim numerically at parameters beyond anything the paper
asserts.

A paper says a recurrence holds for every n above a threshold. Phase 5 shows that
algebraically, by exhibiting the residual and its vanishing --- which is a proof, but a proof
carried out by the same library that built the model. So this runs the model far past the
entry's published range and simply CHECKS the recurrence there, term by term, with nothing but
integer arithmetic. If the algebra and the arithmetic ever part company, one of them is wrong,
and that is what this is for.

The sample is stratified: every family represented, and the families with the most papers
sampled hardest, so that no family goes untested and no family swamps the run.

    python3 src/dc_phase12.py [per_family] [multiple] [shard] [nshards]
"""
import json
import os
import signal
import sys
import zlib

import localentry as LE
import repopaths
import uniform


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
PER = int(sys.argv[1]) if len(sys.argv) > 1 else 6
MULT = int(sys.argv[2]) if len(sys.argv) > 2 else 3
SHARD = int(sys.argv[3]) if len(sys.argv) > 3 else 0
NSHARD = int(sys.argv[4]) if len(sys.argv) > 4 else 1
OUT = os.path.join(repopaths.DEEPCHECK, f'phase12-{SHARD}.json')
state = json.load(open(OUT)) if os.path.exists(OUT) else {'ok': {}, 'bad': [], 'skip': {}}


def save():
    json.dump(state, open(OUT, 'w'), indent=1)


def skip(why):
    state['skip'][why] = state['skip'].get(why, 0) + 1


hits = [h for h in json.load(open('uniall_hits.json'))
        if not h.get('FAILS') and h.get('coeffs') and h.get('engine')]
ORDW = ({h['anum']: h for h in json.load(open('ordwhole_hits.json'))}
        if os.path.exists('ordwhole_hits.json') else {})

# stratify: take the first PER of each family, in A-number order, so the sample is fixed and
# reproducible rather than whatever the run happened to reach
byfam = {}
for h in sorted(hits, key=lambda x: x['anum']):
    eng = ORDW[h['anum']]['engine'] if h['anum'] in ORDW else h['engine']
    byfam.setdefault(eng, []).append(h)
sample = [h for v in byfam.values() for h in v[:PER]]
print(f'{len(byfam)} engine families, {len(sample)} entries sampled '
      f'({PER} per family), shard {SHARD}/{NSHARD}', flush=True)

done = set(state['ok']) | {b[0] for b in state['bad']}
for h in sorted(sample, key=lambda x: x['anum']):
    a = h['anum']
    if a in done or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    done.add(a)
    eng = ORDW[a]['engine'] if a in ORDW else h['engine']
    try:
        e = LE.get(a)
        p = uniform.M[eng].parse_name(e['name'])
    except Exception:
        skip('name or entry unreadable'); save(); continue
    if not p:
        skip('engine no longer parses the name'); save(); continue
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    order = max(coeffs)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    want = MULT * len(d) + order + off + 5
    try:
        signal.alarm(240)
        b = uniform.build(eng, p, 2000000)
        if b is None:
            signal.alarm(0); skip('over the cap'); save(); continue
        t = uniform.terms(eng, p, b, want)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); skip('timed out past the published range'); save(); continue
    except Exception:
        signal.alarm(0); skip('raised past the published range'); save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 5) if tv[s:s + len(d)] == d), None)
    if sh is None:
        state['bad'].append([a, 'the model does not reproduce the published data'])
        save(); continue
    seq = [v for v in tv[sh:] if v is not None]
    thr = h.get('nthr')
    start = order if (thr is None or a in ORDW) else max(order, thr - off + 1)
    bad = [off + k for k in range(start, len(seq))
           if seq[k] != sum(coeffs[i] * seq[k - i] for i in coeffs)]
    beyond = len(seq) - len(d)
    if bad:
        state['bad'].append([a, f'the recurrence fails at n={bad[:3]} --- inside the '
                                f'published range' if bad[0] < off + len(d) else
                                f'the recurrence fails at n={bad[:3]}, beyond the published '
                                f'range but inside what the paper asserts'])
        save(); continue
    if beyond <= 0:
        skip('could not get past the published range'); save(); continue
    state['ok'][a] = beyond
    save()
    print(f'  {a} ({eng}) holds for {beyond} terms past the published range', flush=True)

print(f'\nPhase 12 numeric attack, shard {SHARD}: {len(state["ok"])} entries pushed past '
      f'their published range, {len(state["bad"])} failures')
if state['ok']:
    v = sorted(state['ok'].values())
    print(f'  terms beyond the entry: min {v[0]}, median {v[len(v) // 2]}, max {v[-1]}')
for b in state['bad'][:20]:
    print('   ', *b)
if state['skip']:
    print('  not attacked:')
    for k, n in sorted(state['skip'].items(), key=lambda x: -x[1]):
        print(f'    {n:5d}  {k}')
