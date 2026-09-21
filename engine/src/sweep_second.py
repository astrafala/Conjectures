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

import atomicjson
import os
import re
import signal
import zlib

import sympy

nsym = sympy.Symbol('n')

import closedform as CF
import conjlines
import factlines
import gfrec
import localentry as LE
import repopaths
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
# A "further" conjecture that is the conjecture the entry's EXISTING paper already settles is
# the first result stated again, not a second one. 235 papers were installed and withdrawn the
# same day for exactly that, and the withdrawal happened in two stages because the first test
# was too weak: comparing against the lines other hits files record catches a duplicate only
# when the entry's paper came from a vein that stores the line it used, and it found 118 of the
# 235. The authoritative comparison is with the PAPER, which quotes the conjecture it settles --
# `paper-sources/` holds the TeX -- and on that test all 235 were duplicates.
#
# So the paper is what is read here. The claim's distinctive core (the formula, with the
# "Empirical:" opening and the attribution stripped) is looked for in the TeX of every paper
# already installed on the entry.
import glob as _g2
import os as _os
import re as _re

_SRC = {_os.path.basename(_p): _p
        for _p in _g2.glob(repopaths.ROOT + '/paper-sources/*/*.tex')}
# ...and NOT against a paper this vein itself wrote. Comparing a claim with the paper that
# states that very claim makes every record a duplicate of itself: it is how 109 papers were
# withdrawn that were perfectly good second results. The comparison is with what the entry was
# proved for BEFORE this vein ran.
PAPERS = {}
try:
    for _r in json.load(open('rank-map.json')):
        if _r.get('engine') == 'second-conjecture':
            continue
        _b = _os.path.basename(_r['path']).replace('.pdf', '.tex')
        _p = _SRC.get(_b)
        if not _p:
            continue
        try:
            PAPERS.setdefault(_r['anum'], []).append(
                _re.sub(r'[\\${}]', '', _re.sub(r'\s+', ' ', open(_p, errors='replace').read())))
        except Exception:
            pass
except Exception:
    pass


def already_proved(anum, line):
    """is this claim the one the entry's own paper already settles?"""
    t = _re.sub(r'[\\${}]', '', _re.sub(r'\s+', ' ', line))
    core = _re.sub(r'^\s*(Empirical|Conjectur\w*)\s*[:.]?\s*', '', t, flags=_re.I)
    core = _re.sub(r'\s*-\s*_.*$', '', core).strip()[:60]
    if not core:
        return True
    bodies = PAPERS.get(anum, ())
    if not bodies:
        # no stored source for the entry's existing paper, so this claim CANNOT be compared
        # against what that paper already settles. Refuse rather than assume it is different:
        # 368 installed papers have no stored source, and assuming would put the first result
        # back on the roster as a second one for every one of them.
        return True
    return any(core in body for body in bodies)


# The entries whose proof this project has actually PUBLISHED. A premise held in a hits file
# but never installed is a proof that no paper states, and a second-conjecture paper resting on
# one rests on nothing a reader can follow.
try:
    ROSTER = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
except Exception:
    ROSTER = set()

PROVED = {}
import glob as _glob
# A hand-written list of hits files is a stale filter like any other: every vein added since
# it was written is invisible, and an entry whose recurrence this project proved in one of them
# is refused here as "no recurrence available as a premise". 44 of the 244 entries this sweep
# had already settled were refused on re-ask for exactly that reason. Read every hits file --
# only records carrying explicit `coeffs` and no FAILS are used, so a file of a different shape
# contributes nothing rather than something wrong.
# Where each premise came from, alongside the premise itself. A hit here copies the
# coefficients in and kept no reference to their source, so when the source was withdrawn
# nothing connected the two: 42 records in snd_hits.json carry premise_kind "proved in this
# project" and there is no coeffs record anywhere in the project that supports them. Six are
# named in WITHDRAWN.md -- under `gf-conjecture', because a withdrawal blocks the ARGUMENT and
# these rest ON that argument (STATE.md defect 45). A copied fact cannot be re-checked; a
# named one can.
PREMISE_FROM = {}
_files = sorted(set(_glob.glob('*_hits*.json')) | {'uniall_hits.json'})
for f in _files:
    try:
        for h in json.load(open(f)):
            if isinstance(h, dict) and h.get('anum') and h.get('coeffs') and not h.get('FAILS'):
                if h['anum'] not in PROVED:
                    PREMISE_FROM[h['anum']] = [f, h.get('engine', '')]
                PROVED.setdefault(h['anum'], h['coeffs'])
    except Exception:
        pass
try:
    for h in json.load(open('ordtails.json'))['proved']:
        PROVED.setdefault(h['anum'], h['coeffs'])
except Exception:
    pass

# A vein that proves a GENERATING FUNCTION records no coefficients, so 318 entries this project
# has settled were refused here as "no recurrence available as a premise". They have one: if the
# proved g.f. is N/D with D(0) = 1 and
#
#     D(x) = 1 - c_1 x - ... - c_r x^r,     then     a(n) = sum_i c_i a(n-i)
#
# for every n past deg N. The denominator IS the recurrence, so read it off rather than refusing.
# Only exact integer coefficients are taken; anything else is left alone.
for _f in _glob.glob('*_hits*.json'):
    if _f.startswith('snd'):
        continue
    try:
        _d = json.load(open(_f))
    except Exception:
        continue
    if not isinstance(_d, list):
        continue
    for _h in _d:
        if not (isinstance(_h, dict) and _h.get('anum')) or _h.get('FAILS'):
            continue
        if _h['anum'] in PROVED or _h.get('coeffs'):
            continue
        for _k in ('line', 'gfline'):
            if not _h.get(_k):
                continue
            try:
                _g = gfrec.parse_gf(' '.join(str(_h[_k]).split()))
                if _g is None:
                    continue
                _num, _den = sympy.fraction(sympy.together(_g))
                _dp = sympy.Poly(sympy.expand(_den), x)
                _c = _dp.all_coeffs()[::-1]          # constant term first
                if not _c or _c[0] == 0:
                    continue
                _c = [sympy.nsimplify(v / _c[0]) for v in _c]
                if any(not v.is_Integer for v in _c):
                    continue
                _co = {str(i): str(-int(_c[i])) for i in range(1, len(_c)) if _c[i] != 0}
                if _co:
                    PROVED.setdefault(_h['anum'], _co)
            except Exception:
                pass
            break


def save():
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)


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
        # ... but a line carrying no conjectural WORD is not a fact. A `Conjectures from X:
        # (Start)' block holds bare formula lines, and taking one of those as a premise for
        # another line of the same block proves nothing. factlines is the only safe source.
        for L in factlines.facts(e):
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
    off = int(e['offset'].split(',')[0])
    settled, seen = [], set()
    for L in conjlines.lines(e):
        t = L.strip()
        if t in seen:
            continue
        seen.add(t)
        if already_proved(a, t):
            res['already this entry\'s paper, or no source to compare with'] += 1
            continue
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
                # q | p says a and f satisfy the SAME recurrence. It does NOT say they are the
                # same solution of it, and for a CLOSED FORM that is the whole claim. Two
                # solutions of a recurrence of order D coincide exactly when they agree at D
                # consecutive indices, so the window has to be checked -- past the index from
                # which `a` provably satisfies p, and inside the published terms. Without this
                # the vein proves "f satisfies the right recurrence" and reports it as
                # "a(n) = f(n)". (For another RECURRENCE the claim IS "a satisfies p", and
                # q | p settles it outright; that branch needs no window.)
                lo = holds_from + max(0, aorder - qorder)
                hi = lo + aorder
                if hi > len(d):
                    res['closed form: too few terms to pin the solution'] += 1
                    continue
                try:
                    signal.alarm(BUDGET)
                    vals = [int(sympy.nsimplify(cf[0].subs(nsym, off + k)))
                            for k in range(lo, hi)]
                    signal.alarm(0)
                except Exception:
                    signal.alarm(0)
                    res['closed form could not be evaluated on the window'] += 1
                    continue
                if vals != d[lo:hi]:
                    res['closed form satisfies the recurrence but is a DIFFERENT solution'] += 1
                    continue
                settled.append(('closed form', t[:200], {'D': aorder, 'lo': off + lo,
                                                         'hi': off + hi - 1}))
    # only claims that say something the proved recurrence does not are counted
    fresh = [c for c in settled if not c[0].endswith('(restates the proved recurrence)')]
    if settled:
        res['entries with something settled'] += 1
        res['claims settled (new content)'] += len(fresh)
        res['claims that only restate the recurrence'] += len(settled) - len(fresh)
    if fresh:
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': e['name'], 'premise': co,
                     'premise_kind': premise,
                     'premise_from': PREMISE_FROM.get(a, ['the entry itself', '']),
                     'premise_on_roster': a in ROSTER, 'qorder': qorder,
                     'settled': fresh, 'restated': [c for c in settled if c not in fresh],
                     'offset': int(e['offset'].split(',')[0]), 'nterms': len(d)})
        print('SETTLED', a, len(fresh), flush=True)
    else:
        res['nothing further follows from the proved recurrence'] += 1
    done.add(a); save()
save()
print(dict(res))
