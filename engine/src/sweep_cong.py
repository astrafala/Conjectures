#!/usr/bin/env python3
"""Congruence and divisibility conjectures on sequences whose recurrence is known.

The recurrence is a PREMISE and is only taken from a line the entry states as fact, or from a
result this project has already proved. A congruence proved from a conjectured recurrence
would be a conditional result dressed as an unconditional one, so those are refused.

    TARGETS=deep-check/cong.txt HITS=cong_hits_0.json DONE=cong_done_0.json \
      CSHARD=0 CNSHARD=4 python3 src/sweep_cong.py
"""
import collections
import json

import atomicjson
import os
import re
import signal
import zlib

import congruence as CG
import conjlines
import localentry as LE
import openness
import ratrec

CONJ = re.compile(r'onjectur|mpirical|It appears|Apparently', re.I)


class _T(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(_T()))
BUDGET = int(os.environ.get('BUDGET', '40'))
HITS = os.environ.get('HITS', 'cong_hits.json')
DONE = os.environ.get('DONE', 'cong_done.json')
SHARD = int(os.environ.get('CSHARD', '0'))
NSHARD = int(os.environ.get('CNSHARD', '1'))
targets = [a for a in open(os.environ.get('TARGETS', 'deep-check/cong.txt')).read().split()
           if a.startswith('A')]
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
# the recurrences this project has proved: their entries' recurrence is no longer a premise
PROVED = set()
for f in ('uniall_hits.json', 'gfdef_hits.json', 'gf_hits.json'):
    try:
        PROVED |= {h['anum'] for h in json.load(open(f))
                   if isinstance(h, dict) and h.get('anum') and not h.get('FAILS')}
    except Exception:
        pass


def save():
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)


for a in targets:
    if a in done or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    try:
        e = LE.get(a)
    except Exception:
        res['entry unreadable'] += 1
        done.add(a); save(); continue
    # the premise: a recurrence stated as fact, or one already proved here
    fact = None
    for L in e['comment'] + e['formula']:
        if CONJ.search(L):
            continue
        r = ratrec.parse_rec(L)
        if r:
            fact = (L.strip(), r, 'stated by the entry as fact')
            break
    if fact is None and a in PROVED:
        for L in conjlines.lines(e):
            r = ratrec.parse_rec(L)
            if r:
                fact = (L.strip(), r, 'proved in this project')
                break
    if fact is None:
        res['no recurrence available as a premise'] += 1
        done.add(a); save(); continue
    # the claim: a congruence, in a conjectural line
    found = None
    for L in conjlines.lines(e):
        cl = CG.claims(L)
        if cl:
            found = (L.strip(), cl, CG.claimed_from(L))
            break
    if not found:
        res['no congruence claim'] += 1
        done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1
        done.add(a); save(); continue
    line, cl, start = found
    # ratrec.parse_rec returns (coeffs, claimed); unpacking it as a nested pair made `coeffs`
    # an int and the premise check died on the first entry
    coeffs = fact[1][0]
    order = max(coeffs)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    if len(d) < order + 2:
        res['too few published terms to seed the recurrence'] += 1
        done.add(a); save(); continue
    # the premise must reproduce the entry's own terms, or it was misread
    chk = [k for k in range(order, len(d))
           if d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
    if chk:
        res['stated recurrence does not match DATA'] += 1
        done.add(a); save(); continue
    s0 = max(0, (start - off) if start is not None else 0)
    out = []
    for c, m in cl:
        try:
            signal.alarm(BUDGET)
            got = CG.decide(coeffs, order, d, c, m, s0)
            signal.alarm(0)
        except Exception:
            signal.alarm(0)
            got = None
        if got is None:
            out.append((c, m, 'state space too large'))
        else:
            out.append((c, m) + got)
    if all(o[2] == 'PROVED' for o in out):
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': e['name'], 'line': line, 'premise': fact[0],
                     'premise_kind': fact[2], 'claims': out, 'offset': off,
                     'start': start, 'order': order,
                     'coeffs': {str(k): str(v) for k, v in coeffs.items()}})
        print('PROVED', a, out[:2], flush=True)
    elif any(o[2] == 'FALSE' for o in out):
        res['DISPROVED'] += 1
        hits.append({'anum': a, 'name': e['name'], 'line': line, 'premise': fact[0],
                     'premise_kind': fact[2], 'claims': out, 'FAILS': True, 'offset': off,
                     'order': order,
                     'coeffs': {str(k): str(v) for k, v in coeffs.items()}})
        print('DISPROVED?', a, out[:2], flush=True)
    else:
        res['undecided at this state-space size'] += 1
    done.add(a); save()
save()
print(dict(res))
