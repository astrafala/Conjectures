#!/usr/bin/env python3
"""How much would lumping DURING exploration buy, per engine?

    python3 src/lumpgain.py [engine ...]     # default: the engines with the most cap refusals

2,759 entries are refused at the cap and IDEAS.md section T names the lever: every one of
these engines builds the whole reachable set and only then merges, so the cap is hit during
exploration and `lumpauto' runs too late to help. `transfer88' at width 7 built 20,384 states
and merged to 3,421 -- more than four fifths of the exploration redundant -- and `transfer17'
got a Myhill-Nerode quotient of its own (`build_lineset', median 2.13x, max 81x).

Before writing that for another engine, measure whether it would pay. This takes entries the
engine HAS built, re-builds them, lumps, and reports the ratio. An engine whose builds lump by
1.1x is not worth the surgery whatever its refusal count; one that lumps by 5x is.

The number to read is the MEDIAN, not the maximum: one 81x outlier says nothing about the 200
entries behind it.
"""
import collections
import json
import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import localentry as LE
import lumpauto
import uniform

CAP = int(os.environ.get('CAP', '200000'))
PER = int(os.environ.get('PER', '6'))
BUDGET = int(os.environ.get('BUDGET', '90'))


class Timeout(Exception):
    pass


def _alarm(*_):
    raise Timeout()


def ratios(en, anums):
    out = []
    for a in anums:
        r = uniform.read(LE.get(a)['name'])
        if not r or r[0] != en:
            continue
        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(BUDGET)
        try:
            b = uniform.build(en, r[1], CAP)
        except Timeout:
            print('  %-10s build hit the %ds budget' % (a, BUDGET))
            continue
        except Exception as exc:
            print('  %-10s build raised %s' % (a, type(exc).__name__))
            continue
        finally:
            signal.alarm(0)
        if b is None:
            print('  %-10s no model (%s)' % (a, (uniform.LAST_ERROR[0] or 'cap')[:44]))
            continue
        shape = uniform.lumpable(en, b)
        if shape is None:
            print('  %-10s model is not a plain weighted digraph; nothing to measure' % a)
            continue
        adj, start, end = shape
        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(BUDGET)
        try:
            wadj, _, _, _ = lumpauto.lump(adj, start, end)
        except Timeout:
            print('  %-10s lump hit the %ds budget at %d states' % (a, BUDGET, len(adj)))
            continue
        finally:
            signal.alarm(0)
        out.append((a, len(adj), len(wadj)))
        print('  %-10s %7d -> %7d   %5.2fx' % (a, len(adj), len(wadj), len(adj) / len(wadj)))
    return out


def main():
    caps = json.load(open('uniall_caps.json'))
    done = json.load(open('uniall_done.json'))
    byeng = collections.defaultdict(list)
    for a in done:
        if a in caps:
            continue           # a capped entry cannot be rebuilt to measure anything
        r = uniform.read(LE.get(a)['name'])
        if r:
            byeng[r[0]].append(a)
    capcount = collections.Counter()
    for a in caps:
        r = uniform.read(LE.get(a)['name'])
        if r:
            capcount[r[0]] += 1
    want = sys.argv[1:] or [e for e, _ in capcount.most_common(6)]
    for en in want:
        print('%s: %d entries refused at the cap, %d built ones to measure on'
              % (en, capcount[en], len(byeng[en])))
        got = ratios(en, byeng[en][:PER * 3])
        got = got[:PER] or got
        if got:
            rs = sorted(x[1] / x[2] for x in got)
            med = rs[len(rs) // 2]
            print('  -> median %.2fx over %d builds (min %.2f, max %.2f)'
                  % (med, len(rs), rs[0], rs[-1]))
        else:
            print('  -> nothing measurable')
        print()


if __name__ == '__main__':
    main()
