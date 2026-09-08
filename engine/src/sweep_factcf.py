#!/usr/bin/env python3
"""Conjectured recurrences that follow from a CLOSED FORM the entry records as fact.

The generating-function vein settles a conjectured recurrence from a g.f. the entry states as
fact. The same argument runs from a closed form, and 1,190 entries carry one:

    %F Axxxxxx a(n) = 2^n - n - 2.
    %F Axxxxxx Conjectures from _Colin Barker_, ...: (Start)
    %F Axxxxxx a(n) = 4*a(n-1) - 5*a(n-2) + 2*a(n-3).

A closed form that is a combination of terms n^k b^n is annihilated by a known monic integer
polynomial q -- the product of (x-b)^(k+1) over its bases. The sequence therefore satisfies
EVERY recurrence whose characteristic polynomial is a multiple of q, and no other. So the
conjecture is decided by one polynomial division, with no model of the sequence at all.

Two things are checked beyond the division, because a stated formula is a premise and premises
can be misread:

* the closed form must reproduce the entry's own published terms, in exact arithmetic, over
  the whole range it publishes -- if it does not, the line was misparsed and nothing is claimed;
* the conjectured recurrence must hold on those same published terms wherever the entry gives
  enough of them.

    TARGETS=deep-check/factcf.txt HITS=fcf_hits_0.json DONE=fcf_done_0.json \
      FSHARD=0 FNSHARD=4 python3 src/sweep_factcf.py
"""
import collections
import json

import atomicjson
import os
import re
import signal
import zlib

import sympy

import closedform as CF
import conjlines
import localentry as LE
import openness
import ratrec

x = sympy.Symbol('x')
n = sympy.Symbol('n')


class _T(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(_T()))
BUDGET = int(os.environ.get('BUDGET', '40'))
HITS = os.environ.get('HITS', 'fcf_hits.json')
DONE = os.environ.get('DONE', 'fcf_done.json')
SHARD = int(os.environ.get('FSHARD', '0'))
NSHARD = int(os.environ.get('FNSHARD', '1'))
targets = [a for a in open(os.environ.get('TARGETS', 'deep-check/factcf.txt')).read().split()
           if a.startswith('A')]
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
res = collections.Counter()
CONJ = re.compile(r'onjectur|mpirical|It appears|Apparently', re.I)


def save():
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)


def charpoly(coeffs, order):
    """x^r - c_1 x^(r-1) - ... - c_r"""
    return sympy.Poly(x ** order - sum(int(coeffs[i]) * x ** (order - i)
                                       for i in coeffs), x)


for a in targets:
    if a in done or a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    try:
        e = LE.get(a)
    except Exception:
        res['entry unreadable'] += 1
        done.add(a)
        save()
        continue
    # the closed form must be stated as FACT: not inside a conjecture block, no hedge word
    _conjset = {L.strip() for L in conjlines.lines(e)}
    fact = None
    for L in e['comment'] + e['formula']:
        if CONJ.search(L) or L.strip() in _conjset:
            continue
        q = CF.parse_line(L, bare=True)
        if q and q[0] is not None:
            fact = (L.strip(), q[0])
            break
    if fact is None:
        res['no closed form stated as fact'] += 1
        done.add(a)
        save()
        continue
    conj = [r for r in (ratrec.parse_rec(L) for L in conjlines.lines(e)) if r]
    if not conj:
        res['no conjectured recurrence'] += 1
        done.add(a)
        save()
        continue
    if not openness.status(a)[0]:
        res['not open'] += 1
        done.add(a)
        save()
        continue
    try:
        signal.alarm(BUDGET)
        ann = CF.annihilator(fact[1])
        signal.alarm(0)
    except Exception:
        signal.alarm(0)
        res['closed form has no integer annihilator'] += 1
        done.add(a)
        save()
        continue
    if ann is None:
        res['closed form has no integer annihilator'] += 1
        done.add(a)
        save()
        continue
    qc, qorder = ann
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    # the stated formula must reproduce the entry's own terms, or it was misread
    try:
        signal.alarm(BUDGET)
        vals = [sympy.nsimplify(fact[1].subs(n, off + k)) for k in range(len(d))]
        signal.alarm(0)
    except Exception:
        signal.alarm(0)
        res['closed form would not evaluate'] += 1
        done.add(a)
        save()
        continue
    bad = [off + k for k, v in enumerate(vals)
           if not (v.is_Integer and int(v) == d[k])]
    if bad:
        res['stated closed form does not match DATA'] += 1
        done.add(a)
        save()
        continue
    coeffs, dd = conj[0]
    order = max(coeffs)
    try:
        signal.alarm(BUDGET)
        p = charpoly(coeffs, order)
        rem = sympy.rem(p.as_expr(), charpoly(qc, qorder).as_expr(), x)
        signal.alarm(0)
    except Exception:
        signal.alarm(0)
        res['division failed'] += 1
        done.add(a)
        save()
        continue
    if sympy.simplify(rem) != 0:
        res['the stated closed form does not imply the conjecture'] += 1
        done.add(a)
        save()
        continue
    # and the conjecture must hold on the published terms wherever they reach
    wrong = [off + k for k in range(len(d))
             if k - order >= 0 and d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())
             and off + k > (dd if dd is not None else off + order)]
    if wrong:
        res['conjecture contradicted by DATA'] += 1
        done.add(a)
        save()
        continue
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': e['name'], 'factline': fact[0],
                 'expr': str(fact[1]), 'qorder': qorder,
                 'qcoeffs': {str(k): str(v) for k, v in qc.items()},
                 'order': order, 'claimed': dd, 'offset': off, 'nterms': len(d),
                 'coeffs': {str(k): str(v) for k, v in coeffs.items()}})
    done.add(a)
    save()
    print('done', a, res['PROVED'], flush=True)
save()
print(dict(res))
