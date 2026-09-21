#!/usr/bin/env python3
"""Ask ONE engine (or a few) about every name in the clone, and prove what it reads.

    python3 src/sweep_engine.py lexsub edgemark boardwalk block2x2

`sweep_uni` is the standing sweep and it reads `uni_cands.json`, a cache of which engine reads
which name. The cache is right and it is also slow to rebuild -- a quarter of an hour of asking
a hundred and twenty parsers about twenty-nine thousand names -- and a newly written engine is
invisible to every sweep until that rebuild lands. Three engines were written in one afternoon
and each one restarted the rebuild, which is a silent refusal waiting to happen.

So this asks the named engines directly, with no cache in between, and writes into exactly the
same hits file under the same lock. It is the same pipeline as `sweep_uni` from `uniform.read`
onwards: build, match the model against the entry's OWN published data, find the shift, then
test the conjectured recurrence's residual against the model's derived bound.
"""
import collections
import json
import os
import re
import resource
import signal
import sys

import conjlines
import localentry as LE
import openness
import ratrec
import uniform


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
BUDGET = int(os.environ.get('BUDGET', '600'))
CAP = int(os.environ.get('CAP', '400000'))

# A state-space cap is a promise about the number of STATES, and several engines allocate
# toward it before they can count them -- `uniform.build` in particular. Twice today this
# sweep was killed outright by the kernel at 13.9 GB, at the same entry both times, and a
# process that dies takes its tally and its place in the list with it. An address-space limit
# turns that into a MemoryError, which the per-entry `except Exception` below already treats
# as "build failed": the entry is skipped and the sweep goes on. STATE.md records the same
# kill happening to `sweep_shard` at the standing cap; this is the general guard for it.
MEMGB = float(os.environ.get('MEMGB', '6'))
try:
    _lim = int(MEMGB * (1 << 30))
    resource.setrlimit(resource.RLIMIT_AS, (_lim, _lim))
except (ValueError, OSError):
    pass
P = ('/tmp/claude-0/-home-user-Conjectures/'
     'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/')
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
roster |= {v['anum'] for v in json.load(open('paper-engines.json')).values()}
HITS, DONE = 'uniall_hits.json', 'uniall_done.json'
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
_tick = [0]

want = sys.argv[1:]
if not want:
    raise SystemExit('name at least one engine')
# a narrow re-ask: when a PARSER is widened rather than an engine written, the entries that
# changed are known by name and sweeping every one of an engine's names to reach fifteen of
# them is hours of work for nothing.
ONLY_ANUMS = set(os.environ.get('ONLY_ANUMS', '').replace(',', ' ').split())
for en in want:
    if en not in uniform.M:
        raise SystemExit(f'{en} is not a registered engine')
# ask them in the order `uniform.read' would, not the order they were typed: ENG is a priority
# list, and a name two engines can read should go to the same one here as in the standing sweep.
want = [en for en in uniform.ENG if en in set(want)]

LOCK = HITS + '.lock'
if os.path.exists(LOCK):
    try:
        other = int(open(LOCK).read().strip())
    except Exception:
        other = None
    if other is not None and os.path.exists(f'/proc/{other}'):
        raise SystemExit(f'another sweep (pid {other}) is writing {HITS}; refusing to run')
open(LOCK, 'w').write(str(os.getpid()))


def save():
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))


# an entry already in `done' was asked by the standing sweep, possibly through a DIFFERENT
# engine and possibly before this one existed; being asked once is not being asked about this
# argument, so the mark is not a reason to skip here.
seen = {h['anum'] for h in hits if h.get('anum')}
for a in sorted(names):
    if a in roster or a in seen:
        continue
    if ONLY_ANUMS and a not in ONLY_ANUMS:
        continue
    nm = names[a]
    got = None
    for en in want:
        try:
            p = uniform.M[en].parse_name(nm)
        except Exception:
            continue
        if p:
            got = (en, p)
            break
    if not got:
        continue
    en, p = got
    _tick[0] += 1
    if _tick[0] % 25 == 0:
        print('  ... %d asked, %s so far: %s' % (_tick[0], a, dict(res)), flush=True)
    e = LE.get(a)
    # NOT a word test on the line: a conjecture is very often a block, and then its formula
    # lines carry no conjectural word at all. `sweep_uni` still tests the word, and on the
    # first run of this sweep that refused 170 of 205 entries -- every one of the nineteen
    # lexsub names and every one of the boardwalk names -- as "no parsable recurrence", with
    # the recurrence sitting in plain sight inside a "Conjectures from X: (Start)" block.
    recs = [r for r in (ratrec.parse_rec(L) for L in conjlines.claims(e)) if r]
    if not recs:
        res['no parsable recurrence'] += 1; continue
    if not openness.status(a)[0]:
        res['not open'] += 1; continue
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['build timed out'] += 1; continue
    except Exception:
        signal.alarm(0); res['build failed'] += 1; continue
    if b is None:
        res['state space > cap'] += 1; continue
    S = uniform.size(en, p, b)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, len(d) + off + 5)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['terms timed out'] += 1; continue
    except Exception:
        signal.alarm(0); res['terms failed'] += 1; continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    try:
        signal.alarm(BUDGET)
        thr = uniform.threshold(en, p, b, coeffs, order)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['annihilation timed out'] += 1; continue
    except Exception:
        signal.alarm(0); res['threshold failed'] += 1; continue
    if thr is None:
        res['UNRESOLVED'] += 1; continue
    nthr = thr + off - sh
    bad = [off + k for k in range(len(d))
           if off + k > nthr and k - order >= 0 and
           d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
    if bad:
        res['claim contradicted by DATA'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm, 'bad': bad[:3]})
    else:
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': nm, 'engine': en, 'S': S, 'order': order,
                     'offset': off, 'shift': sh, 'nthr': nthr, 'nterms': len(d),
                     'claimed': dd,
                     'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    seen.add(a)
    save()
    print('done', a, en, res['PROVED'], flush=True)
    _tick[0] = 0
save()
try:
    os.remove(LOCK)
except OSError:
    pass
print(dict(res))
