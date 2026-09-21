#!/usr/bin/env python3
"""The sweep for `hyperrec`: a P-recursive conjecture against a hypergeometric closed form.

    ANUMS_FILE=deep-check/prec.txt python3 src/sweep_hyper.py 0 1
"""
import collections
import json
import os
import signal
import sys
import zlib

import conjlines
import factlines
import hyperrec
import localentry as LE
import openness
import precrec
import sympy as sp

SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
TAG = os.environ.get('TAG', '')
SFX = TAG if NSHARD == 1 else f'{TAG}_{SHARD}'
HITS, DONE, WHY = f'hyper_hits{SFX}.json', f'hyper_done{SFX}.json', f'hyper_why{SFX}.json'
ALARM = int(os.environ.get('ALARM', '60'))


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
n = hyperrec.n
pool = [a for a in open(os.environ.get('ANUMS_FILE', 'deep-check/prec.txt')).read().split()
        if a.startswith('A')]
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
roster |= {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()


def save():
    json.dump(hits, open(HITS + '.t', 'w'), indent=1); os.replace(HITS + '.t', HITS)
    json.dump(sorted(done), open(DONE + '.t', 'w')); os.replace(DONE + '.t', DONE)
    json.dump(dict(res), open(WHY + '.t', 'w'), indent=1, sort_keys=True)
    os.replace(WHY + '.t', WHY)


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
            got = (ps, ' '.join(L.split())); break
    if not got:
        res['no readable P-recursive claim'] += 1; done.add(a); save(); continue
    ps, line = got
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    f, factline = None, None
    for L in factlines.facts(e):
        t = ' '.join(L.split())
        c = hyperrec.closed(t)
        if c is not None:
            f, factline = c, t; break
    if f is None:
        res['no hypergeometric closed form stated as fact'] += 1; done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        signal.alarm(ALARM)
        bad = [i + off for i, v in enumerate(d)
               if sp.nsimplify(f.subs(n, i + off)) != v]
        signal.alarm(0)
    except Exception:
        signal.alarm(0)
        res['closed form could not be evaluated'] += 1; done.add(a); save(); continue
    # A closed form is routinely stated for n past the first index or two: A060774's
    # 6*C(3n,n) - 6*C(2n,n) gives 0 at n = 0 where the entry has 1, the empty path, and matches
    # every term after it. Demanding agreement from the offset made that an accusation against
    # the entry -- the eighth such verdict this month that was the reader's. What is required is
    # agreement from SOME index on, with enough terms after it to mean anything, and the
    # conjecture is then proved from that index rather than from the offset.
    first = (bad[-1] + 1) if bad else off
    if len(d) - (first - off) < len(ps) + 2:
        res['closed form agrees too late to be worth using'] += 1; done.add(a); save(); continue
    if bad and bad[-1] - off > 3:
        # not a late start but a disagreement in the body of the data: a fact about the entry,
        # recorded and never installed, and read by hand before it is called anything
        res['stated closed form does not generate the DATA'] += 1
        hits.append({'anum': a, 'FAILS': True, 'closed': str(f), 'factline': factline,
                     'line': line, 'bad': bad[:6]})
        done.add(a); save(); continue
    try:
        signal.alarm(ALARM)
        r = hyperrec.ratio(f)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); r = None
    if r is None:
        res['closed form is not hypergeometric'] += 1; done.add(a); save(); continue
    try:
        signal.alarm(ALARM * 3)
        ok = hyperrec.settles({i: p for i, p in enumerate(ps)}, r)
        signal.alarm(0)
    except Exception:
        signal.alarm(0)
        res['the reduction did not finish'] += 1; done.add(a); save(); continue
    if ok:
        res['PROVED'] += 1
        hits.append({'anum': a, 'closed': str(f), 'factline': factline, 'line': line,
                     'offset': off, 'nterms': len(d), 'from_n': first})
    else:
        res['the ratio does not imply the conjectured recurrence'] += 1
    done.add(a); save()

for k, v in res.most_common():
    print(f'{v:5}  {k}')
