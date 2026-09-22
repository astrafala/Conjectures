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
import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import localentry as LE
import uniform

BUDGET = int(os.environ.get('BUDGET', '120'))
OUT = os.environ.get('OUT', 'deep-check/capwhy.json')


class Timeout(Exception):
    pass


def main():
    caps = json.load(open('uniall_caps.json'))
    byeng = collections.defaultdict(list)
    for a, c in caps.items():
        r = uniform.read(LE.get(a)['name'])
        if r:
            byeng[r[0]].append((a, c, r[1]))
    want = sys.argv[1:] or [e for e, _ in
                            collections.Counter({k: len(v) for k, v in byeng.items()}).most_common(6)]
    out = {}
    for en in want:
        tally = collections.Counter()
        for a, cap, p in byeng[en]:
            signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Timeout()))
            signal.alarm(BUDGET)
            try:
                b = uniform.build(en, p, cap)
                verdict = 'BUILDS' if b is not None else (
                    'RAISED' if uniform.LAST_ERROR[0] else 'CAP')
                detail = uniform.LAST_ERROR[0]
            except Timeout:
                verdict, detail = 'TIMEOUT', None
            except Exception as exc:
                verdict, detail = 'RAISED', '%s: %s' % (type(exc).__name__, exc)
            finally:
                signal.alarm(0)
            tally[verdict] += 1
            out[a] = {'engine': en, 'cap': cap, 'verdict': verdict,
                      'detail': (detail or '')[:120]}
            print('  %-10s %-8s %s' % (a, verdict, (detail or '')[:70]), flush=True)
        print('%s: %s' % (en, dict(tally)), flush=True)
        json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
    print('-> ' + OUT)
    print(collections.Counter(v['verdict'] for v in out.values()))


if __name__ == '__main__':
    main()
