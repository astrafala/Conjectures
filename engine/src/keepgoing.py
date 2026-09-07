#!/usr/bin/env python3
"""Rebuild every sweep pool from the OEIS clone, so no sweep is ever left with nothing to do.

The standing rule is that the work does not stop. A sweep that empties its pool must be
pointed at the next one rather than switched off, and the pools themselves go stale --- entries
are added to the OEIS every day, and engines are written every day, so a pool measured last
week is short at both ends.

This rebuilds all of them from the clone and reports what is left to attempt in each, which is
the answer to "what should run next".

    python3 src/keepgoing.py
"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import localentry as LE
import ratrec
import repopaths
import uniform

SC = ('/tmp/claude-0/-home-user-Conjectures/'
      'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json')
MARK = re.compile(r'onjectur|Empirical', re.I)
ORDER = re.compile(r'[Ee]mpirical recurrence of order (\d+)')


def names():
    """every A-number in the clone, with its name --- not a cache built at some past date"""
    nm = json.load(open(SC)) if os.path.exists(SC) else {}
    for p in glob.glob('/home/user/oeis/oeisdata/seq/*/*.seq'):
        a = os.path.basename(p)[:-4]
        if a not in nm:
            try:
                nm[a] = LE.get(a)['name']
            except Exception:
                pass
    if os.path.exists(os.path.dirname(SC)):
        json.dump(nm, open(SC, 'w'))
    return nm


def main():
    nm = names()
    roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    pools = collections.defaultdict(list)
    counts = collections.Counter()
    for a, name in sorted(nm.items()):
        if a in roster:
            continue
        try:
            if not uniform.read(name):
                counts['no engine reads the name'] += 1
                continue
        except Exception:
            continue
        try:
            e = LE.get(a)
        except Exception:
            continue
        marked = [L for L in e['comment'] + e['formula'] if MARK.search(L)]
        if not marked:
            counts['nothing unsettled'] += 1
            continue
        if any(ORDER.search(L) for L in marked):
            pools['order'].append(a)
        elif any(ratrec.parse_rec(L) for L in marked):
            pools['rec'].append(a)
        else:
            pools['other'].append(a)

    done = {'rec': set(), 'order': set()}
    for f in glob.glob('shard_done_*.json') + glob.glob('shardt94_done_*.json'):
        done['rec'] |= set(json.load(open(f)))
    for f in glob.glob('ordwhole_done_*.json'):
        done['order'] |= set(json.load(open(f)))

    print(f'{len(nm)} names in the clone, {len(roster)} already settled here\n')
    for k in ('rec', 'order', 'other'):
        v = sorted(pools[k])
        json.dump(v, open(os.path.join(repopaths.DEEPCHECK, f'pool-{k}.json'), 'w'))
        open(os.path.join(repopaths.DEEPCHECK, f'pool-{k}.txt'), 'w').write(','.join(v))
        left = len(set(v) - done.get(k, set()))
        print(f'  pool-{k:6s} {len(v):5d} candidates, {left:5d} never attempted')
    for k, n in counts.most_common():
        print(f'  ({n} {k})')

    # the answer to "what next" when every pool is empty: the largest cluster of names no
    # engine reads is the next engine to write
    if all(len(set(pools[k]) - done.get(k, set())) == 0 for k in ('rec', 'order')):
        print('\n  every pool is exhausted --- the next work is a new engine.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
