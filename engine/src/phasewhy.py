#!/usr/bin/env python3
"""Which PHASE is the out-of-budget pool actually losing to?

    python3 src/phasewhy.py            # walk uniall_tmo.json
    PWSHARD=0 PWNSHARD=6 python3 src/phasewhy.py

Defect 62 made `sweep_shard` record the phase -- and that fix reaches only NEW timeouts, of
which there are almost none, because an entry already in `uniall_tmo.json` at this budget or
more is SKIPPED before it is ever asked again. So the 427 rows sitting there will never say
which phase they lost to unless something re-asks them on purpose. This does.

It mirrors the sweep's sequence exactly -- build, size, terms, then the annihilation test --
giving each phase the budget the tmo row records, and reports where the clock ran out. That
is the measurement that decides the next engine work:

    build      -> raise the cap / write the on-the-fly quotient
    terms      -> speed up the matrix iteration
    threshold  -> the annihilation test, whose length is the STATE COUNT: lump earlier

Nothing else answers it. The sweep's own counters say `out of budget on an earlier pass' and
stop there, which is the shape of defect 48 all over again: a refusal recorded without the
one fact that decides what to do about it.
"""
import collections
import json
import os
import signal
import sys
import time
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conjlines
import localentry as LE
import ratrec
import uniform

SHARD = int(os.environ.get('PWSHARD', '0'))
NSHARD = int(os.environ.get('PWNSHARD', '1'))
OUT = os.environ.get('OUT') or ('deep-check/phasewhy.json' if NSHARD == 1
                                else 'deep-check/phasewhy_%d.json' % SHARD)
CAP = int(os.environ.get('CAP', '8000000'))
# the tmo row's own budget, capped so one entry cannot eat a whole round
MAXB = int(os.environ.get('MAXB', '120'))


class Timeout(BaseException):
    """BaseException, so `uniform.build''s bare `except Exception' cannot absorb it and file
    a clock failure as something else. That is the defect this whole script exists to undo."""


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))


def main():
    tmo = json.load(open('uniall_tmo.json'))
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [a for a in sorted(tmo)
            if a not in out and zlib.crc32(a.encode()) % NSHARD == SHARD]
    print('%d out-of-budget rows, %d for this shard' % (len(tmo), len(todo)), flush=True)
    for a in todo:
        budget = min(int(tmo[a]), MAXB)
        try:
            e = LE.get(a)
            r = uniform.read(e['name'])
        except Exception as exc:
            out[a] = {'phase': 'entry unreadable', 'detail': type(exc).__name__}
            continue
        if not r:
            out[a] = {'phase': 'name unknown', 'budget': budget}
            continue
        en, p = r
        rec = {'engine': en, 'budget': budget}
        t0 = time.time()
        try:
            signal.alarm(budget)
            b = uniform.build(en, p, CAP)
            signal.alarm(0)
            rec['build_s'] = round(time.time() - t0, 1)
            if b is None:
                rec['phase'] = 'build refused'
                rec['detail'] = (uniform.LAST_ERROR[0] or 'cap')[:80]
                out[a] = rec
                continue
            rec['S'] = uniform.size(en, p, b)
            d = [int(v) for v in e['data'].split(',') if v.strip()]
            off = int(e['offset'].split(',')[0])
            t1 = time.time()
            signal.alarm(budget)
            uniform.terms(en, p, b, len(d) + off + 5)
            signal.alarm(0)
            rec['terms_s'] = round(time.time() - t1, 1)
            recs = [x for x in (ratrec.parse_rec(L) for L in conjlines.claims(e)) if x]
            if not recs:
                rec['phase'] = 'no parsable recurrence'
                out[a] = rec
                continue
            coeffs, _ = recs[0]
            t2 = time.time()
            signal.alarm(budget)
            uniform.threshold(en, p, b, coeffs, max(coeffs))
            signal.alarm(0)
            rec['thr_s'] = round(time.time() - t2, 1)
            rec['phase'] = 'finishes'
        except Timeout:
            signal.alarm(0)
            rec['phase'] = ('build' if 'build_s' not in rec else
                            'terms' if 'terms_s' not in rec else 'threshold')
        except MemoryError:
            signal.alarm(0)
            rec['phase'] = 'out of memory'
        except Exception as exc:
            signal.alarm(0)
            rec['phase'] = 'raised'
            rec['detail'] = '%s: %s' % (type(exc).__name__, exc)
        finally:
            signal.alarm(0)
        out[a] = rec
        print('  %-10s %-9s %-16s %s' % (a, en[:9], rec['phase'],
              ' '.join('%s=%s' % (k, rec[k]) for k in ('build_s', 'terms_s', 'thr_s', 'S')
                       if k in rec)), flush=True)
        if len(out) % 10 == 0:
            json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
    json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
    print(collections.Counter(v['phase'] for v in out.values()).most_common())
    print('-> ' + OUT)


if __name__ == '__main__':
    main()
