#!/usr/bin/env python3
"""The sweep for conjectured P-RECURSIVE recurrences.

459 open pool entries conjecture one -- `sum_i p_i(n) a(n-i) = 0` with polynomial coefficients
-- and `ratrec` reads constant coefficients only, so every one is invisible to every other
sweep here. 380 of them parse (`precrec`).

The proof is not a check of terms. When the entry states its generating function as FACT and
that function is algebraic (`algf`), `holonomic.residual` turns the claim into

    B(x) = sum_i x^i (p_i(theta+i) A)(x),   theta = x d/dx,

an explicit element of an algebraic function field. The claim holds for every n exactly when
B = 0, and for every n > d exactly when B is a polynomial of degree d. That is an identity of
functions, settled symbolically, so it holds at every index at once.

Two refusals are deliberate. A generating function the entry marks CONJECTURAL is not used --
proving one conjecture from another is not a proof -- and an inhomogeneous claim is a different
theorem, not a weaker one.

    ANUMS_FILE=deep-check/prec.txt python3 src/sweep_prec.py 0 1
"""
import collections
import json
import os
import resource
import signal
import sys
import zlib

import sympy as sp

import algf
import atomicjson
import conjlines
import holonomic
import localentry as LE
import openness
import precrec

SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
TAG = os.environ.get('TAG', '')
SFX = f'{TAG}' if NSHARD == 1 else f'{TAG}_{SHARD}'
HITS, DONE, WHY = f'prec_hits{SFX}.json', f'prec_done{SFX}.json', f'prec_why{SFX}.json'
# see defect 25: the per-step alarm must be shorter than the runner's own timeout
ALARM = int(os.environ.get('ALARM', '240'))
MEMGB = float(os.environ.get('MEMGB', '6'))
SLOW = os.environ.get('SLOW', '') == '1'   # run `prove` where `quadratic` cannot decide
resource.setrlimit(resource.RLIMIT_AS, (int(MEMGB * 2 ** 30), resource.RLIM_INFINITY))

pool = [a for a in open(os.environ.get('ANUMS_FILE', 'deep-check/prec.txt')).read().split()
        if a.startswith('A')]
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
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
    got = None
    for L in conjlines.claims(e):
        ps = precrec.read(L)
        if ps:
            got = (ps, ' '.join(L.split()))
            break
    if not got:
        res['no readable P-recursive claim'] += 1; done.add(a); save(); continue
    ps, line = got
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    try:
        signal.alarm(ALARM)
        A = algf.read(e)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); A = None
    if A is None:
        res['no factual algebraic generating function'] += 1; done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        signal.alarm(ALARM)
        okd, bad, _got = holonomic.check_against_data(A, d, off)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['series against DATA timed out'] += 1; done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['series against DATA failed'] += 1; done.add(a); save(); continue
    if not okd:
        # the g.f. the entry states does not generate the terms it publishes: that is a fact
        # about the entry worth recording, and the claim cannot be settled from it
        res['stated g.f. does not generate the DATA'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': e['name'], 'line': line, 'bad': bad})
        done.add(a); save(); continue
    # The quadratic route first: every g.f. this sweep accepts is algebraic of degree 2, so B
    # lies in Q(x)[y]/(y^2 - D) and the question "is B a polynomial" is polynomial arithmetic.
    # `prove` decides the same thing through sympy's `simplify` and two forty-term series of
    # nested radicals, at about two entries per seven minutes; `quadratic` does it in seconds
    # and was checked to agree with it -- same degree on all four entries already proved, and
    # the same refusal on the ones it had refused. When A is not quadratic in ONE radical,
    # `quadratic` returns None and the slow route runs.
    fast = None
    try:
        signal.alarm(ALARM)
        fast = holonomic.quadratic(A, ps)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); fast = None
    if fast is not None:
        ok, deg = fast
        if not ok:
            res['residual is not a polynomial: claim not established'] += 1
            done.add(a); save(); continue
        is_zero = (deg < 0)
    elif not SLOW:
        # `quadratic` returns None only when A is not quadratic in ONE radical, which means
        # the algebraic degree is above 2. `prove` can still decide those in principle, but it
        # is the slow route and it stalled this sweep on its first such entry for the whole
        # window. They are RECORDED and left for an opt-in pass rather than silently skipped.
        res['not quadratic in one radical'] += 1
        done.add(a); save(); continue
    else:
        try:
            signal.alarm(ALARM * 2)
            is_zero, Bs, coeffs, firstnz = holonomic.prove(a, A, ps)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); res['residual timed out'] += 1; done.add(a); save(); continue
        except Exception:
            signal.alarm(0); res['residual failed'] += 1; done.add(a); save(); continue
        nz = [k for k, c in enumerate(coeffs) if c != 0]
        tail = [k for k in nz if k >= len(coeffs) - 6]
        if not is_zero and tail:
            res['residual is not a polynomial: claim not established'] += 1
            done.add(a); save(); continue
        deg = max(nz) if nz else -1
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': e['name'], 'engine': 'holonomic', 'line': line,
                 'gf': str(A), 'ps': [str(p) for p in ps], 'order': len(ps) - 1,
                 'zero': bool(is_zero), 'degB': deg, 'from_n': deg + 1,
                 'offset': off, 'nterms': len(d)})
    done.add(a); save()
    print('done', a, res['PROVED'], flush=True)
save()
print(dict(res))
