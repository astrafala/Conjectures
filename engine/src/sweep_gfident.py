#!/usr/bin/env python3
"""A conjectured generating function against one the entry STATES AS FACT.

    A056328  G.f.: x^4*(1 - 2*x + x^2 + 3*x^3)/(1 - 8*x + ... - 144*x^7).   [fact]
             Empirical g.f.: -x^4*(3*x^3 + x^2 - 2*x + 1) /
                             ((x-1)(2x-1)(2x+1)(3x-1)(4x-1)(3x^2-1)).       [conjecture]

When an entry asserts one generating function and conjectures another, the conjecture is true
exactly when the two are the same function. That is a rational-function identity, decided by
`cancel`, and it needs no model of the name at all.

`equate.py` is the vein for this and it has FOUR papers. Its candidate filter requires the
conjectural line to BEGIN with "Conjectur", and the corpus overwhelmingly writes this one as
`Empirical g.f.:` -- 3,593 entries against 131. That is defect 2 again, in the filter of a vein
whose own docstring estimated 353 open candidates, and it is the largest instance of it so far.

Two guards, both of which have cost something here before:

  * the asserted side is taken from `factlines.facts`, never by looking for a conjectural word
    on the line, so a generating function inside a `Conjectures: (Start)' block is not mistaken
    for a premise (it would be the same conjecture written twice);
  * the asserted side must reproduce every published term before it is used. When it does not,
    that is recorded and NOT called an error in the entry: A124869 states a g.f. for the real
    parts themselves while its terms are their numerators, and reading it as the sequence's own
    generating function is a mistake of the reader, not of the entry.
"""
import collections
import json
import os
import signal
import sys
import zlib

import sympy as sp

import algf
import conjgf
import conjlines
import factlines
import holonomic
import localentry as LE
import openness

SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
TAG = os.environ.get('TAG', '')
SFX = TAG if NSHARD == 1 else f'{TAG}_{SHARD}'
HITS, DONE, WHY = f'gfident_hits{SFX}.json', f'gfident_done{SFX}.json', f'gfident_why{SFX}.json'
ALARM = int(os.environ.get('ALARM', '90'))


class Timeout(BaseException):
    """BaseException, not Exception, and that is the whole point.

    The alarm fires INSIDE `uniform.build', whose last clause is `except Exception: return
    None' -- so a Timeout derived from Exception was swallowed there and the build returned
    None, which every caller reads as "the state space exceeded the cap". Measured: a W=9 entry
    asked with a 2-second budget and a cap of 10^12 was recorded as `state space > cap'. Every
    build timeout in this project has been filed as a cap refusal, which is why
    `uniall_caps.json' over-reports and why the 33 entries of `residue.txt' were finished with
    no record of what finished them.

    `uniform.build' already re-raises MemoryError for exactly this reason, with the comment
    that an out-of-memory "is a different fact". A timeout is a different fact by the same
    argument. Deriving from BaseException makes it one no `except Exception' can absorb --
    the idiom Python itself uses for KeyboardInterrupt.
    """
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))

pool = [a for a in open(os.environ.get('ANUMS_FILE', 'deep-check/gfident.txt')).read().split()
        if a.startswith('A')]
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
x = algf.x


def save():
    json.dump(hits, open(HITS + '.tmp', 'w'), indent=1); os.replace(HITS + '.tmp', HITS)
    json.dump(sorted(done), open(DONE + '.tmp', 'w')); os.replace(DONE + '.tmp', DONE)
    json.dump(dict(res), open(WHY + '.tmp', 'w'), indent=1, sort_keys=True)
    os.replace(WHY + '.tmp', WHY)


for a in sorted(pool):
    if a in done or a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    e = LE.get(a)
    if not e:
        res['name unknown'] += 1; done.add(a); save(); continue
    G, line = None, None
    for L in conjlines.claims(e):
        try:
            g = conjgf.parse(L)
        except Exception:
            g = None
        if g is not None:
            G, line = g, ' '.join(L.split()); break
    if G is None:
        res['no readable conjectured generating function'] += 1; done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    try:
        signal.alarm(ALARM)
        F = algf.read(e)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); F = None
    if F is None:
        res['the entry asserts no generating function to prove it from'] += 1
        done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        signal.alarm(ALARM)
        okd = holonomic.check_against_data(F, d, off)[0]
        signal.alarm(0)
    except Exception:
        signal.alarm(0)
        res['the asserted g.f. could not be expanded'] += 1; done.add(a); save(); continue
    if not okd:
        # NOT an error in the entry: the asserted line is often a g.f. for a related quantity
        res['the asserted g.f. does not generate the DATA; read it by hand'] += 1
        done.add(a); save(); continue
    try:
        signal.alarm(ALARM)
        same = sp.simplify(sp.together(F - G)) == 0
        signal.alarm(0)
    except Exception:
        signal.alarm(0)
        res['the identity could not be decided'] += 1; done.add(a); save(); continue
    if same:
        res['PROVED'] += 1
        hits.append({'anum': a, 'fact': str(F), 'conj': str(G), 'line': line,
                     'nterms': len(d), 'offset': off})
    else:
        res['the two generating functions are DIFFERENT; read it by hand'] += 1
        hits.append({'anum': a, 'FAILS': True, 'fact': str(F), 'conj': str(G), 'line': line})
    done.add(a); save()

for k, v in res.most_common():
    print(f'{v:5}  {k}')
