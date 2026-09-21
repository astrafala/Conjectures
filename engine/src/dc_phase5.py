#!/usr/bin/env python3
"""Deep check, Phase 5: the mathematics, recomputed from cold.

Cached verdicts are not evidence. This rebuilds each model in a fresh process, with no reuse
of anything the original run left behind, and checks four things against what the paper
claims:

  1. the model still reproduces every term the entry publishes;
  2. the recurrence the paper states still annihilates the model, with the threshold the paper
     states -- recomputed, not read back;
  3. the threshold is EXACT: the residual at the threshold index is nonzero, so the bound
     cannot be lowered, and it vanishes from there on, so it is not one too high;
  4. the claim is not contradicted anywhere in the entry's own published data.

A disagreement here is not automatically the paper's fault --- on this project the check has
been the faulty side far more often --- so every disagreement is reported with both numbers
and settled by hand, never by trusting whichever ran last.

    python3 src/dc_phase5.py <shard> <nshards> [budget]
"""
import glob
import json
import os
import signal
import sys
import zlib
from fractions import Fraction

import bmrec
import localentry as LE
import atomicjson
import repopaths
import uniform

# `uniall_hits.json` labels the order-line recoveries with the name of the VEIN, not of a
# transfer engine: there is no `uniform.M['ordwhole']`, and Phase 5 was reporting eight
# perfectly sound papers as disagreements for that reason alone. The engine each of those
# papers actually used is recorded in the sweep's own file, so the rebuild reads it from
# there. Those papers also make a claim no other paper makes -- that the recurrence the
# entry states is the MINIMAL one, which is what makes it unique and hence proved -- so the
# minimal order is recomputed from scratch too, not read back.
ORDW = {}
if os.path.exists('ordwhole_hits.json'):
    ORDW = {h['anum']: h for h in json.load(open('ordwhole_hits.json'))}
P62 = (1 << 61) - 1


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
SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
BUDGET = int(sys.argv[3]) if len(sys.argv) > 3 else 120
# 73 entries could not be rebuilt at 2,000,000 -- and every one of them records a state count
# BELOW that, the largest 1,849,046. The engines refuse on an estimate made before the states
# are built, not on the count itself, so the cap has to clear the estimate rather than the
# answer. It is settable so those 73 can be re-reached without re-running the other 3,790.
CAP = int(os.environ.get('P5CAP', '2000000'))
OUT = os.path.join(repopaths.DEEPCHECK, f'phase5-{SHARD}.json')
state = json.load(open(OUT)) if os.path.exists(OUT) else {'ok': [], 'bad': [], 'skip': {}}


def save():
    # atomicjson, not `json.dump(open(OUT, "w"))'. This runs after every entry and the file is
    # truncated for the whole of the write, so a reader that arrives inside that window sees a
    # half-written object -- `status.py' died on `KeyError: "ok"' reading exactly that, three
    # minutes after this check was restarted, and the file was perfectly well-formed a second
    # later. A torn read of a progress file is worse than a crash: it reads as data loss.
    atomicjson.dump(state, OUT, indent=1)
    try:
        inflight()
    except NameError:
        pass


def skip(a, why):
    # Two things were wrong here. A count is not enough: a check that cannot say WHICH entries
    # it could not reach cannot be re-aimed at them. And `seen` was built from the ok and bad
    # lists only, so a skipped entry was retried on every round and counted again each time --
    # "179 rebuild over the cap" was 179 skip EVENTS across rounds, not 179 entries. The set
    # below is the entry list, and the counter is derived from it, so a rerun cannot inflate
    # either.
    d = state.setdefault('skipped', {}).setdefault(why, [])
    if a not in d:
        d.append(a)
    state['skip'] = {k: len(v) for k, v in state['skipped'].items()}
    # stamp the state with the engines this verdict was reached under, so a machine-reason skip
    # can be told apart from one reached under today's code
    state['stamp'] = _stamp


# A skip whose reason is about the MACHINE expires when the engines change; a skip about the
# MATHEMATICS does not. The `seen` set below is what stops a skipped entry being retried, and
# without this the two kinds were kept forever alike: 31 entries recorded "rebuild over the cap"
# on 8 September were still excluded tonight, four of them results installed TODAY, and
# A184710 -- which needs 353 states against a cap of eight million -- was among them. The engine
# that could not build them was replaced this morning (STATE.md defect 43).
#
# The expiry is the engine sources themselves. If any of them is newer than the stamp written
# when a machine-reason skip was recorded, those skips are dropped and the entries asked again.
MACHINE_REASON = ('over the cap', 'timed out', 'raised', 'out of memory', 'unreadable')


def _engine_stamp():
    """Newest mtime across the engine sources, to the second."""
    newest = 0.0
    for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '*.py')):
        try:
            newest = max(newest, os.path.getmtime(f))
        except OSError:
            pass
    return int(newest)


_stamp = _engine_stamp()
if state.get('stamp') != _stamp:
    _dropped = 0
    for _why in [w for w in state.get('skipped', {})
                 if any(m in w for m in MACHINE_REASON)]:
        _dropped += len(state['skipped'].pop(_why))
    if _dropped:
        state['skip'] = {k: len(v) for k, v in state.get('skipped', {}).items()}
        print(f'  engines changed since the last run: {_dropped} machine-reason skips retired',
              flush=True)
    state['stamp'] = _stamp
    save()

seen = (set(state['ok']) | {b[0] for b in state['bad']}
        | {a for v in state.get('skipped', {}).values() for a in v})
hits = [h for h in json.load(open('uniall_hits.json'))
        if not h.get('FAILS') and h.get('coeffs') and h.get('engine')]
# NEWEST FIRST, not by A-number. `uniall_hits.json` is appended in the order results are found,
# so the tail is the most recent and the head is what has been verified for weeks. Iterating by
# anum spends the expensive end of this check re-verifying A000045 while the results installed
# today -- the ones that have never been checked at all, and the ones that exercise whatever
# build was changed most recently -- wait behind 4,000 others.
#
# The remaining entries cost about seven minutes each to rebuild and re-verify from cold, so the
# backlog is roughly 237 hours at three shards. The order is therefore most of what this check
# can control: it decides which results are verified in the first day rather than the tenth.
# NOT `phase5-inflight-<shard>.json'. Two readers glob `phase5-*.json' for the shard states --
# `status.py' and this file's own `_summary', which is how a shard learns what the other two
# have settled -- and a marker named to match is picked up as a fourth shard state. status.py
# died on `KeyError: "ok"' within a minute of the marker first being written. A new file
# placed beside an existing glob is a change to every reader of that glob.
INFLIGHT = os.path.join(repopaths.DEEPCHECK, f'p5-inflight-{SHARD}.json')


def inflight(a=None, phase=''):
    """Name the entry being verified, BEFORE the work starts.

    Every record this check writes is written after a verdict, which is exactly the case a
    process that dies cannot reach -- and this one dies every hour, because the container
    restarts. Without this there is no way to tell a shard grinding on one expensive rebuild
    from a shard that is not running: both look like an `ok` count that does not move, which is
    what "4,064, unchanged" meant for an hour tonight. Same fix as sweep_shard's (defect 39).
    """
    try:
        if a is None:
            if os.path.exists(INFLIGHT):
                os.remove(INFLIGHT)
        else:
            json.dump({'anum': a, 'phase': phase, 'cap': CAP, 'budget': BUDGET},
                      open(INFLIGHT, 'w'), indent=0)
    except Exception:
        pass


for h in reversed(hits):
    a = h['anum']
    if a in seen or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    seen.add(a)
    inflight(a, 'start')
    try:
        e = LE.get(a)
        got = uniform.read(e['name'])
    except Exception:
        skip(a, 'entry or name unreadable'); save(); continue
    if not got:
        skip(a, 'no engine reads the name now'); save(); continue
    en, p = got
    if h['engine'] == 'ordwhole':
        o = ORDW.get(a)
        if not o:
            skip(a, 'order-line record missing'); save(); continue
        h = dict(h, engine=o['engine'], nthr=o.get('nthr'), stated=o.get('stated'),
                 order=o.get('order'))
    if en != h['engine']:
        # Two engines reading the same name is an OVERLAP, not a defect: engines written
        # later generalise earlier ones, and `uniform.read` returns whichever comes first in
        # its list. What the paper claims is what ITS engine computes, so the rebuild uses
        # that engine; the overlap is recorded for the duplicate-work audit.
        state.setdefault('overlap', []).append([a, h['engine'], en])
        try:
            p = uniform.M[h['engine']].parse_name(e['name'])
        except Exception:
            p = None
        if not p:
            state['bad'].append([a, f"the engine the paper used ({h['engine']}) no longer "
                                    f"parses the name"])
            save(); continue
        en = h['engine']
    try:
        signal.alarm(BUDGET)
        inflight(a, 'rebuild')
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); skip(a, 'rebuild timed out'); save(); continue
    except Exception:
        signal.alarm(0); skip(a, 'rebuild raised'); save(); continue
    if b is None:
        skip(a, 'rebuild over the cap'); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    order = max(coeffs)
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, len(d) + off + 5)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); skip(a, 'terms timed out'); save(); continue
    except Exception:
        signal.alarm(0); skip(a, 'terms raised'); save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        state['bad'].append([a, 'the rebuilt model no longer reproduces the published DATA'])
        save(); continue
    if a in ORDW and ORDW[a].get('stated') is not None:
        # The paper's claim is that no SHORTER recurrence holds, so a recurrence of the
        # stated order is forced to be this one. Recompute the minimal order over a large
        # prime and then exactly over Q; both must come back at the stated order.
        stated = ORDW[a]['stated']
        try:
            signal.alarm(BUDGET)
            need = 2 * ORDW[a]['Smerged'] + max(8, stated + 4)
            tt = uniform.terms(en, p, b, need + off + 5)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); skip(a, 'order-line terms timed out'); save(); continue
        except Exception:
            signal.alarm(0); skip(a, 'order-line terms raised'); save(); continue
        sq = [x.numerator for x in tt[sh:] if x is not None and x.denominator == 1]
        if len(sq) < 2 * ORDW[a]['Smerged'] + 4:
            skip(a, 'too few exact terms to recompute the minimal order'); save(); continue
        L0 = bmrec.bm_mod([v % P62 for v in sq], P62)
        if L0 != stated:
            state['bad'].append([a, f'minimal order recomputed as {L0}, the paper needs it '
                                    f'to be {stated}'])
            save(); continue
        Lx, cs = bmrec.bm([Fraction(v) for v in sq])
        if Lx != stated or any(c.denominator != 1 for c in cs):
            state['bad'].append([a, 'the minimal recurrence over Q is no longer integral of '
                                    'the stated order'])
            save(); continue
        if {i + 1: int(c) for i, c in enumerate(cs)} != coeffs:
            state['bad'].append([a, 'the recomputed minimal recurrence is not the one the '
                                    'paper prints'])
            save(); continue
    try:
        signal.alarm(BUDGET)
        thr = uniform.threshold(en, p, b, coeffs, order)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); skip(a, 'threshold timed out'); save(); continue
    except Exception:
        signal.alarm(0); skip(a, 'threshold raised'); save(); continue
    if thr is None:
        state['bad'].append([a, 'the recurrence no longer annihilates the rebuilt model'])
        save(); continue
    nthr = thr + off - sh
    # The order-line papers print no threshold: their claim is that the recurrence is the
    # minimal one, recomputed above, and their record's `nthr` is bookkeeping the paper never
    # quotes. Comparing against it flagged a paper for a sentence it does not contain.
    if a in ORDW:
        h = dict(h); h.pop('nthr', None)
    if 'nthr' in h and h['nthr'] is not None and nthr != h['nthr']:
        state['bad'].append([a, f"threshold moved: paper says n > {h['nthr']}, "
                                f"the cold rebuild says n > {nthr}"])
        save(); continue
    bad = [off + k for k in range(len(d))
           if off + k > nthr and k - order >= 0
           and d[k] != sum(coeffs[i] * d[k - i] for i in coeffs)]
    if bad:
        state['bad'].append([a, f'claim contradicted by the entry DATA at n={bad[:3]}'])
        save(); continue
    state['ok'].append(a)
    save()
# The per-shard file is rewritten after every entry, so while a run is going it is dirty in
# the working tree every few seconds and no commit of it is ever current. It is progress. The
# result is the merge of every shard, written when a shard has nothing left to attempt, and
# that is what is stored.
def _summary():
    import glob
    ok, bad, skip = set(), [], {}
    for f in glob.glob(os.path.join(repopaths.DEEPCHECK, 'phase5-*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        ok |= set(d['ok'])
        bad += d['bad']
        for k, v in d.get('skip', {}).items():
            skip[k] = skip.get(k, 0) + v
    json.dump({'recomputed': len(ok), 'disagreements': bad, 'not_recomputed': skip,
               'entries': sorted(ok)},
              open(os.path.join(repopaths.DEEPCHECK, 'phase5.json'), 'w'), indent=1)


_summary()
print(f"Phase 5 shard {SHARD}/{NSHARD}: {len(state['ok'])} recomputed and agreeing, "
      f"{len(state['bad'])} disagreements")
for b in state['bad'][:20]:
    print('   ', *b)
if state.get('overlap'):
    print(f"  {len(state['overlap'])} entries two engines both read (an overlap, not a "
          f"defect); the rebuild used the engine the paper used")
if state['skip']:
    print('  not recomputed:')
    for k, v in sorted(state['skip'].items(), key=lambda x: -x[1]):
        print(f'    {v:5d}  {k}')
