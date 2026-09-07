#!/usr/bin/env python3
"""Entries that state only the ORDER of their empirical recurrence, for the whole sequence.

    Empirical recurrence of order 33 (see link above)

432 unsettled entries say that and nothing more; the recurrence itself lives in a file the
local copy does not carry. Every sweep here filters on a recurrence it can PARSE, so all 432
were skipped in silence -- not refused, never looked at. An engine already models 414 of them.

The recurrence cannot be read, and does not need to be. The entry is a fixed-width array
count, hence a walk count on S vertices, hence satisfies some monic recurrence of order at
most S by Cayley--Hamilton. Berlekamp--Massey on 2S exact terms returns the MINIMAL one. If
that minimal order equals the order the entry states, then any recurrence of that order the
sequence satisfies has a characteristic polynomial that is a multiple of the minimal
polynomial and of the same degree, hence equal to it: the entry's recurrence is the one
computed here, whatever its file says.

If the stated order is larger than the minimal one, no such uniqueness holds -- the entry's
polynomial is some multiple of the minimal one and which multiple cannot be recovered without
reading it -- and the entry is left alone rather than guessed at.

    ANUMS_FILE=... BUDGET=120 python3 src/sweep_ordwhole.py 2000000 0 3
"""
import json
import os
import re
import signal
import sys
import zlib
from fractions import Fraction

import bmrec
import localentry as LE
import lumpauto
import openness
import uniform


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
BUDGET = int(os.environ.get('BUDGET', '120'))
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 2000000
SHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 0
NSHARD = int(sys.argv[3]) if len(sys.argv) > 3 else 1
P62 = (1 << 61) - 1
SC = ('/tmp/claude-0/-home-user-Conjectures/'
      'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/')
names = json.load(open(SC + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
HITS = f'ordwhole_hits_{SHARD}.json'
DONE = f'ordwhole_done_{SHARD}.json'
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
ORDER = re.compile(r'[Ee]mpirical recurrence of order (\d+)')
res = {}


def save():
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))


def note(k):
    res[k] = res.get(k, 0) + 1


targets = [a for a in open(os.environ['ANUMS_FILE']).read().replace(',', ' ').split() if a]
for a in sorted(targets):
    if a in done or a in roster:
        continue
    if zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    try:
        e = LE.get(a)
    except Exception:
        note('entry unreadable'); done.add(a); save(); continue
    m = ORDER.search(' '.join(e['comment'] + e['formula']))
    if not m:
        note('no order line'); done.add(a); save(); continue
    stated = int(m.group(1))
    got = uniform.read(names[a])
    if not got:
        note('no engine'); done.add(a); save(); continue
    en, p = got
    if not openness.status(a)[0]:
        note('not open'); done.add(a); save(); continue
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); note('build timed out'); done.add(a); save(); continue
    except Exception:
        signal.alarm(0); note('build failed'); done.add(a); save(); continue
    if b is None:
        note(f'state space > cap {CAP}'); done.add(a); save(); continue
    S = uniform.size(en, p, b)
    # The bound that matters is the merged one: the minimal recurrence has order at most the
    # number of states with distinct futures, and merging first is what makes 2S terms
    # affordable at all.
    try:
        if isinstance(b, tuple) and len(b) == 4 and isinstance(b[1], list):
            _, _, _, Sm = lumpauto.lump(b[0], b[1], b[2])
            S = min(S, Sm)
    except Exception:
        pass
    if S > 4000:
        note('merged state count too large for 2S terms'); done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    need = 2 * S + max(8, stated + 4)
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, need + off + 5)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); note('terms timed out'); done.add(a); save(); continue
    except Exception:
        signal.alarm(0); note('terms failed'); done.add(a); save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        note('model does not match DATA'); done.add(a); save(); continue
    seq = [v for v in tv[sh:] if v is not None]
    if len(seq) < 2 * S + 4:
        note('too few exact terms for the bound'); done.add(a); save(); continue
    L0 = bmrec.bm_mod([v % P62 for v in seq], P62)
    if L0 != stated:
        note(f'minimal order {L0} is not the stated order'); done.add(a); save(); continue
    Lx, cs = bmrec.bm([Fraction(v) for v in seq])
    if Lx != stated or any(c.denominator != 1 for c in cs):
        note('minimal recurrence not integral or order disagrees over Q')
        done.add(a); save(); continue
    coeffs = {i + 1: int(c) for i, c in enumerate(cs)}
    bad = [off + k for k in range(len(d))
           if k - Lx >= 0 and d[k] != sum(coeffs[i] * d[k - i] for i in coeffs)]
    if bad:
        note('recovered recurrence contradicted by DATA'); done.add(a); save(); continue
    note('PROVED')
    # ordbuild quotes the entry's own sentence, so the record carries it
    line = next((' '.join(L.split()) for L in e['comment'] + e['formula']
                 if ORDER.search(L)), 'Empirical recurrence of order %d' % stated)
    hits.append({'anum': a, 'name': names[a], 'engine': en, 'line': line,
                 'S': uniform.size(en, p, b),
                 'Smerged': S, 'order': Lx, 'stated': stated, 'offset': off, 'shift': sh,
                 'nterms': len(d), 'nthr': off + Lx - 1,
                 'coeffs': {str(k): str(v) for k, v in coeffs.items()}})
    done.add(a); save()
    print('done', a, 'order', Lx, flush=True)
save()
print(res)
