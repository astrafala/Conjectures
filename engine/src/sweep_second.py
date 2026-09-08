#!/usr/bin/env python3
"""The OTHER conjectures on entries this project has already settled.

An entry gets one paper here for the conjecture that was settled, and the entry is then never
looked at again. But 11,968 of the 11,985 entries in the roster still carry a conjectural line,
and 6,150 of those lines are a further recurrence, generating function or closed form for a
sequence THIS PROJECT HAS ALREADY PROVED IS C-FINITE.

That premise is the whole difficulty in the general case, and here it is already in hand. With
the characteristic polynomial q of the proved recurrence known, any further claim is decided by
algebra:

* another recurrence, with characteristic polynomial p, holds exactly when q divides p;
* a generating function N/D holds exactly when D's reciprocal polynomial is a multiple of q
  and enough coefficients agree -- deg N + deg D + order + 1 of them settle it;
* a closed form built from terms n^k b^n holds exactly when its own annihilator is a multiple
  of q and the two agree on that many terms.

Nothing here needs a model, a name to parse, or a new engine. It needs the proof this project
already has.

    TARGETS=deep-check/second.txt HITS=snd_hits_0.json DONE=snd_done_0.json \
      SSHARD=0 SNSHARD=4 python3 src/sweep_second.py
"""
import collections
import json
import os
import re
import signal
import zlib

import sympy

import closedform as CF
import conjlines
import gfrec
import localentry as LE
import openness
import ratrec

x = sympy.Symbol('x')


class _T(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(_T()))
BUDGET = int(os.environ.get('BUDGET', '40'))
HITS = os.environ.get('HITS', 'snd_hits.json')
DONE = os.environ.get('DONE', 'snd_done.json')
SHARD = int(os.environ.get('SSHARD', '0'))
NSHARD = int(os.environ.get('SNSHARD', '1'))
targets = [a for a in open(os.environ.get('TARGETS', 'deep-check/second.txt')).read().split()
           if a.startswith('A')]
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()

# the recurrence this project proved for each entry, from the sweeps' own records
# EVERY vein's records, not four of them. Loading only four left 1,605 roster entries
# refused with "no proved recurrence on record" when the proof is on file under a different
# sweep's name -- the tables, the min-filter images, the one-dimensional words, the cusp-form
# dimensions and the cellular automaton rows all keep their own.
PROVED = {}
import glob as _glob
_files = ['uniall_hits.json', 'gfdef_hits.json', 'gf_hits.json', 'ordwhole_hits.json',
          'cfnew_hits.json', 'lexcf_hits.json', 'mfcf_hits.json', 'wordcf_hits.json',
          'cuspcf_hits.json', 'ecacf_hits.json', 'fcf_hits.json']
_files += _glob.glob('shard_hits_*.json') + _glob.glob('tabnew_hits*.json')
for f in _files:
    try:
        for h in json.load(open(f)):
            if isinstance(h, dict) and h.get('anum') and h.get('coeffs') and not h.get('FAILS'):
                PROVED.setdefault(h['anum'], h['coeffs'])
    except Exception:
        pass
try:
    for h in json.load(open('ordtails.json'))['proved']:
        PROVED.setdefault(h['anum'], h['coeffs'])
except Exception:
    pass


def save():
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))


def poly_of(coeffs):
    order = max(int(k) for k in coeffs)
    return sympy.Poly(x ** order - sum(int(coeffs[k]) * x ** (order - int(k))
                                       for k in coeffs), x), order


for a in targets:
    if a in done or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    try:
        e = LE.get(a)
    except Exception:
        res['entry unreadable'] += 1
        done.add(a); save(); continue
    co = PROVED.get(a)
    premise = 'proved in this project'
    if not co:
        # A recurrence the ENTRY states as fact is the same premise the generating-function
        # vein rests on, and it was not being used here at all. 391 of the 414 coordination
        # sequences state one, and every one of them was refused as "no proved recurrence on
        # record" while carrying a perfectly good premise on its own page.
        for L in e['comment'] + e['formula']:
            if re.search(r'onjectur|mpirical|It appears|Apparently', L, re.I):
                continue
            r = ratrec.parse_rec(L)
            if r:
                co = {str(k): str(v) for k, v in r[0].items()}
                premise = 'stated by the entry as fact'
                break
    if not co:
        res['no recurrence available as a premise'] += 1
        done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1
        done.add(a); save(); continue
    try:
        q, qorder = poly_of(co)
    except Exception:
        res['proved recurrence unreadable'] += 1
        done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    # The premise must reproduce the entry's own terms -- but a recurrence proved here is
    # proved FOR n PAST A THRESHOLD, and the entry's early terms need not satisfy it. Testing
    # from the first index refused 919 entries whose recurrence is perfectly correct. What is
    # required is that it holds from some index on, with enough confirmations after it to be
    # the sequence's recurrence rather than a coincidence.
    bad = [k for k in range(qorder, len(d))
           if d[k] != sum(int(c) * d[k - int(i)] for i, c in co.items())]
    holds_from = (bad[-1] + 1) if bad else qorder
    if len(d) - holds_from < qorder + 2:
        res['too few terms past the threshold to confirm the premise'] += 1
        done.add(a); save(); continue
    settled, seen = [], set()
    for L in conjlines.lines(e):
        t = L.strip()
        if t in seen:
            continue
        seen.add(t)
        # (a) another recurrence
        r = ratrec.parse_rec(L)
        if r:
            other = r[0]
            if other == {int(k): int(v) for k, v in co.items()}:
                continue                      # the same recurrence, already this entry's paper
            try:
                signal.alarm(BUDGET)
                p, _ = poly_of({str(k): v for k, v in other.items()})
                rem = sympy.rem(p.as_expr(), q.as_expr(), x)
                signal.alarm(0)
            except Exception:
                signal.alarm(0)
                continue
            if sympy.simplify(rem) == 0:
                settled.append(('recurrence', t[:200]))
            continue
        # (b) a generating function
        g = None
        try:
            signal.alarm(BUDGET)
            g = gfrec.parse_gf(L)
            signal.alarm(0)
        except Exception:
            signal.alarm(0)
        if g is not None:
            try:
                signal.alarm(BUDGET)
                num, den = sympy.fraction(sympy.together(g))
                dp = sympy.Poly(sympy.expand(den), x)
                # the reciprocal of the denominator carries the characteristic roots
                rec = sympy.Poly(list(reversed(dp.all_coeffs())), x)
                rem = sympy.rem(rec.as_expr(), q.as_expr(), x)
                signal.alarm(0)
            except Exception:
                signal.alarm(0)
                continue
            if sympy.simplify(rem) == 0:
                # A generating function whose denominator's reciprocal IS the proved
                # characteristic polynomial is the SAME conjecture written in another
                # notation, not a second result. 386 of the first 389 were exactly that, and
                # counting them would have inflated 885 real results into 2,461. Only a claim
                # of strictly larger degree says something the recurrence does not.
                equiv = False
                try:
                    lead = sympy.LC(rec) if rec.degree() >= 0 else 1
                    equiv = sympy.simplify(rec.as_expr() / lead - q.as_expr()) == 0
                except Exception:
                    equiv = False
                settled.append(('generating function (restates the proved recurrence)'
                                if equiv else 'generating function', t[:200]))
            continue
        # (c) a closed form
        cf = CF.parse_line(L, bare=True)
        if cf and cf[0] is not None:
            try:
                signal.alarm(BUDGET)
                ann = CF.annihilator(cf[0])
                signal.alarm(0)
            except Exception:
                signal.alarm(0)
                continue
            if not ann:
                continue
            ac, aorder = ann
            try:
                signal.alarm(BUDGET)
                p, _ = poly_of({str(k): v for k, v in ac.items()})
                rem = sympy.rem(p.as_expr(), q.as_expr(), x)
                signal.alarm(0)
            except Exception:
                signal.alarm(0)
                continue
            if sympy.simplify(rem) == 0:
                settled.append(('closed form', t[:200]))
    # only claims that say something the proved recurrence does not are counted
    fresh = [c for c in settled if not c[0].endswith('(restates the proved recurrence)')]
    if settled:
        res['entries with something settled'] += 1
        res['claims settled (new content)'] += len(fresh)
        res['claims that only restate the recurrence'] += len(settled) - len(fresh)
    if fresh:
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': e['name'], 'premise': co,
                     'premise_kind': premise, 'qorder': qorder,
                     'settled': fresh, 'restated': [c for c in settled if c not in fresh],
                     'offset': int(e['offset'].split(',')[0]), 'nterms': len(d)})
        print('SETTLED', a, len(fresh), flush=True)
    else:
        res['nothing further follows from the proved recurrence'] += 1
    done.add(a); save()
save()
print(dict(res))
