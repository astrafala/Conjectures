#!/usr/bin/env python3
"""Settle conjectured generating functions from a recurrence the entry states as fact.

The mirror image of the project's largest vein; see recgf.py for the argument.

    RGPOOL=deep-check/recgf.txt HITS=rg_hits_0.json DONE=rg_done_0.json \
      RGSHARD=0 RGNSHARD=4 BUDGET=40 python3 src/sweep_recgf.py
"""
import collections
import json

import atomicjson
import os
import re
import signal
import zlib

import sympy

import conjgf
import conjlines
import gfrec
import localentry as LE
import openness
import ratrec
import recgf

import closedform as CF

x = sympy.Symbol('x')


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
BUDGET = int(os.environ.get('BUDGET', '40'))
HITS = os.environ.get('HITS', 'rg_hits.json')
DONE = os.environ.get('DONE', 'rg_done.json')
SHARD = int(os.environ.get('RGSHARD', '0'))
NSHARD = int(os.environ.get('RGNSHARD', '1'))
POOL = os.environ.get('RGPOOL', 'deep-check/recgf.txt')
# `rec': the premise is a recurrence the entry states as fact. `cf': a closed form stated as
# fact, which annihilates the sequence just as strongly and needs no other change.
PREMISE = os.environ.get('PREMISE', 'rec')
targets = [a for a in open(POOL).read().split() if a.startswith('A')]
hits = atomicjson.load(HITS, [])
done = set(atomicjson.load(DONE, []))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
res = collections.Counter()
CONJW = re.compile(r'onjectur|mpirical|It appears|Apparently', re.I)


def save():
    atomicjson.dump(hits, HITS)
    atomicjson.dump(sorted(done), DONE)


for a in targets:
    if a in done or a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    try:
        e = LE.get(a)
    except Exception:
        res['unreadable'] += 1; done.add(a); save(); continue
    conj = [(L, g) for L, g in ((L, conjgf.parse(L)) for L in conjlines.lines(e))
            if g is not None]
    if not conj:
        res['no conjectured generating function'] += 1; done.add(a); save(); continue
    # the premise: a formula line that is not conjectural. Carrying no conjectural WORD is
    # not enough -- an entry writes `Conjectures from X: (Start)' and then several bare
    # formula lines, none of which says `conjecture', and reading one of those as a fact
    # would turn a conjecture into a premise. conjlines names every line the entry means
    # conjecturally, block members included, and those are excluded here.
    conjset = {id(L) for L in conjlines.lines(e)}
    conjtext = {L.strip() for L in conjlines.lines(e)}
    prem = None
    for L in e['formula'] + e['comment']:
        if CONJW.search(L) or id(L) in conjset or L.strip() in conjtext:
            continue
        if PREMISE == 'rec':
            r = ratrec.parse_rec(L)
            if r:
                prem = (L, r[0], r[1]); break
        else:
            f = CF.parse_line(L, bare=True)
            if f is None:
                continue
            try:
                q = CF.annihilator(f if not isinstance(f, tuple) else f[0])
                co = recgf.coeffs_from_annihilator(q)
            except Exception:
                co = None
            if co:
                prem = (L, co, f[1] if isinstance(f, tuple) and len(f) > 1
                        and isinstance(f[1], int) else None)
                break
    if prem is None:
        res['no premise stated as fact'] += 1; done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    fline, coeffs, thr = prem
    order = max(int(i) for i in coeffs)
    # the recurrence holds for n > thr, so from index K of the published terms; with no
    # threshold written down the entry means it from the first index where it can be asked
    K = max(order, (thr + 1 - off) if thr is not None else order)
    hit = None
    for L, g in conj:
        try:
            signal.alarm(BUDGET)
            s = gfrec.series(g, len(d) + off + 2)
            signal.alarm(0)
        except Exception:
            signal.alarm(0); continue
        if s is None:
            continue
        # the shift that lines the conjectured series up with the published terms. A
        # mismatch is NOT reported as a disproof: the corpus writes generating functions
        # under several offset conventions, and a shift this loop does not try would make a
        # true conjecture look false. Unmatched lines are set aside to be read, not counted.
        sh = None
        for cand in range(0, max(off, 0) + 3):
            if cand + len(d) <= len(s) and all(s[cand + k] == d[k] for k in range(len(d))):
                sh = cand; break
        if sh is None:
            res['no shift lines the conjecture up with the data'] += 1
            continue
        try:
            signal.alarm(BUDGET)
            ok = recgf.implies(g, sh, coeffs, d, K)
            signal.alarm(0)
        except Exception:
            signal.alarm(0); continue
        if ok is None:
            continue
        if ok is False:
            continue
        hit = {'anum': a, 'name': e['name'], 'gfline': L.strip(),
               'gf': sympy.srepr(g), 'gftex': sympy.latex(g),
               'factline': fline.strip(), 'coeffs': {int(k): str(v) for k, v in coeffs.items()},
               'thr': thr, 'K': K, 'offset': off, 'shift': sh, 'order': order,
               'nterms': len(d), 'modified': e['modified'], 'revision': e['revision']}
        break
    if hit is None:
        res['the stated recurrence does not force it'] += 1
    elif hit != 'bad':
        res['PROVED'] += 1
        hits.append(hit)
    done.add(a); save()
    print('done', a, len(done), flush=True)

print(dict(res))
