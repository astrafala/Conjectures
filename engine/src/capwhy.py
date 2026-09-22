#!/usr/bin/env python3
"""Why is a capped entry capped? Ask the build, with LAST_ERROR in hand.

    python3 src/capwhy.py [engine ...]     # default: the engines with the most cap rows

`uniall_caps.json` is supposed to mean one thing: the build's state count outgrew the cap.
It has meant four things, because `uniform.build` ended in a bare `except Exception: return
None` and every caller read that None as "too big". `uniform.LAST_ERROR` now says which, so
the file can be audited instead of trusted.

For each capped entry this rebuilds at the cap the file records and classifies:

    CAP        the build refused and raised nothing -- the row is honest
    RAISED     the build raised; the row is a bug wearing a cap's clothes
    BUILDS     the build SUCCEEDS at that cap, so the row is wrong and the entry is askable
    TIMEOUT    the build did not finish inside the budget -- a clock row, not a cap row

A BUILDS row is the valuable one: the entry is sitting in the refused pool for no reason.
"""
import collections
import json
import zlib
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import localentry as LE
import uniform

BUDGET = int(os.environ.get('BUDGET', '120'))
SHARD = int(os.environ.get('CWSHARD', '0'))
NSHARD = int(os.environ.get('CWNSHARD', '1'))
OUT = os.environ.get('OUT') or ('deep-check/capwhy.json' if NSHARD == 1
                                else 'deep-check/capwhy_%d.json' % SHARD)


class Timeout(BaseException):
    """Derived from BaseException so `uniform.build''s `except Exception' cannot absorb it.

    `sweep_shard' already does this and says why: a Timeout derived from Exception is
    swallowed there and the build returns None, which every caller reads as "the state space
    exceeded the cap". That is the single defect this whole audit exists to measure, so the
    audit must not commit it.
    """


def main():
    caps = json.load(open('uniall_caps.json'))
    # ONLY: audit a named subset. Pointed at `deep-check/cap-withconj.json' this cuts the work
    # by 63 percent and loses nothing, because **1,109 of the 1,754 cap rows carry no
    # conjecture at all** -- no formula line, and none on the parent table either. They were
    # put in the pool by a name-shape scan, the sweep finished them correctly as "no parsable
    # recurrence", and the cap row is a leftover from a generation that hit the cap during the
    # BUILD, before ever reaching the recurrence check. Auditing them answers a question
    # nobody has: whether an entry with nothing to prove would build.
    only = os.environ.get('ONLY')
    if only:
        keep = set(json.load(open(only)))
        caps = {a: c for a, c in caps.items() if a in keep}
        print('restricted to %s: %d rows' % (only, len(caps)))
    # resumable: this is 2,759 builds and a container restart in the middle of it must not
    # mean starting over. The restart that killed the first run cost every row it had.
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    byeng = collections.defaultdict(list)
    for a, c in sorted(caps.items()):
        if a in out or zlib.crc32(a.encode()) % NSHARD != SHARD:
            continue
        r = uniform.read(LE.get(a)['name'])
        if r:
            byeng[r[0]].append((a, c, r[1]))
    want = sys.argv[1:] or [e for e, _ in
                            collections.Counter({k: len(v) for k, v in byeng.items()}).most_common(6)]
    for en in want:
        tally = collections.Counter()
        for a, cap, p in byeng[en]:
            signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Timeout()))
            signal.alarm(BUDGET)
            t0 = time.time()
            try:
                b = uniform.build(en, p, cap)
                detail = uniform.LAST_ERROR[0]
                # the alarm fires INSIDE uniform.build, whose bare except swallows it and
                # records it like any other exception -- so a clock row would be filed as a
                # bug unless it is read back out here
                verdict = ('BUILDS' if b is not None else
                           'TIMEOUT' if (detail or '').startswith('Timeout') else
                           'RAISED' if detail else 'CAP')
            except Timeout:
                verdict, detail = 'TIMEOUT', None
            except Exception as exc:
                verdict, detail = 'RAISED', '%s: %s' % (type(exc).__name__, exc)
            finally:
                signal.alarm(0)
            el = time.time() - t0
            # the seconds are what make a BUILDS row actionable. `sweep_shard' does not skip
            # an entry because it has a cap row -- it re-asks it every round -- so a row that
            # persists while the build SUCCEEDS here means the shard is losing it to its own
            # clock, not to the cap. A build that succeeds in three seconds is a wrong row; one
            # that takes fifty is a clock row wearing a cap's name.
            tally[verdict] += 1
            out[a] = {'engine': en, 'cap': cap, 'verdict': verdict, 'secs': round(el, 1),
                      'detail': (detail or '')[:120]}
            print('  %-10s %-8s %6.1fs %s' % (a, verdict, el, (detail or '')[:60]), flush=True)
            if len(out) % 5 == 0:
                json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
        print('%s: %s' % (en, dict(tally)), flush=True)
        json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
    print('-> ' + OUT)
    print(collections.Counter(v['verdict'] for v in out.values()))


if __name__ == '__main__':
    main()
