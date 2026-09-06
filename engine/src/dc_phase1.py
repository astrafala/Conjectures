#!/usr/bin/env python3
"""Deep check, Phase 1: does the published inventory hold together?

Mechanical, and it has to be perfect before anything mathematical is believed. Every
check here is one that has already failed at least once on this project, or one whose
failure would be silent -- GitHub truncating a directory listing at 1000 entries being
the worst of those, because nothing on screen says it happened.

Prints one line per check and a defect list. Exit status is the number of failed checks.
"""
import collections
import csv
import json
import os
import subprocess
import sys

import paperpath
import repopaths

BAND_LIMIT = 1000


def load_index():
    with open(os.path.join(repopaths.ROOT, 'papers', 'index.csv')) as f:
        return list(csv.DictReader(f))


def check(name, defects, shown=6):
    ok = not defects
    print(f'  [{"ok" if ok else "FAIL"}] {name}' + ('' if ok else f': {len(defects)} defects'))
    for d in defects[:shown]:
        print(f'         {d}')
    if len(defects) > shown:
        print(f'         ... and {len(defects) - shown} more')
    return 0 if ok else 1


def main():
    idx = load_index()
    roster = json.load(open(os.path.join(repopaths.ROOT, 'engine', 'paper-engines.json')))
    bad = 0
    print(f'Phase 1: inventory integrity over {len(idx)} papers')

    ranks = sorted(int(r['rank']) for r in idx)
    bad += check('ranks are exactly 1..N with no gap and no repeat',
                 [] if ranks == list(range(1, len(ranks) + 1)) else
                 [f'{len(ranks)} rows but ranks run {ranks[0]}..{ranks[-1]}'
                  f' with {len(ranks) - len(set(ranks))} repeats'])

    bad += check('every indexed paper exists on disk, at the path the index gives',
                 [r['file'] for r in idx
                  if not os.path.exists(os.path.join(repopaths.ROOT, r['file']))])

    bad += check('every paper on disk is in the index',
                 sorted(set(
                     os.path.relpath(os.path.join(dp, f), repopaths.ROOT)
                     for dp, _, fs in os.walk(repopaths.PAPERS) for f in fs
                     if f.endswith('.pdf')) - set(r['file'] for r in idx)))

    bad += check('every paper sits in the band its rank belongs to, under the name its '
                 'rank and verdict give',
                 [r['file'] for r in idx
                  if r['file'] != 'papers/%s/%s' % (paperpath.band(int(r['rank'])),
                                                    paperpath.name(int(r['rank']),
                                                                   r['verdict']))])

    # the roster is keyed by the internal number a paper was built under, NOT by rank;
    # comparing it to the index rank by rank reports thousands of mismatches that are not
    # there. What the two must agree on is the multiset of (A-number, verdict, engine).
    rk = collections.Counter((v['anum'], 'DISPROOF' if v['disproof'] else 'PROOF',
                              v['engine']) for v in roster.values())
    ix = collections.Counter((r['anum'], r['verdict'], r['engine']) for r in idx)
    bad += check('roster and index agree on every (A-number, verdict, engine)',
                 [f'{k}: roster {rk[k]}, index {ix[k]}' for k in sorted(set(rk) | set(ix))
                  if rk[k] != ix[k]])

    # only what git actually tracks: the working tree also holds regenerable caches that
    # are gitignored, and counting those reports three directories nobody will ever browse
    tracked = subprocess.run(['git', 'ls-files'], cwd=repopaths.ROOT,
                             capture_output=True, text=True).stdout.split()
    held = collections.defaultdict(set)
    for f in tracked:
        parts = f.split('/')
        for i in range(len(parts)):
            held['/'.join(parts[:i]) or '.'].add(parts[i])
    over = [f'{d}: {len(v)} entries' for d, v in sorted(held.items())
            if len(v) > BAND_LIMIT]
    bad += check(f'no tracked directory holds more than {BAND_LIMIT} entries', over)

    # MISSING.txt lists a paper as "rank  A-number  engine", so the rank is the key
    ml = os.path.join(repopaths.SOURCES, 'MISSING.txt')
    listed = set()
    if os.path.exists(ml):
        for line in open(ml):
            w = line.split()
            if w and w[0].isdigit():
                listed.add(int(w[0]))
    really = set()
    for r in idx:
        tex = os.path.join(repopaths.SOURCES, paperpath.band(int(r['rank'])),
                           paperpath.name(int(r['rank']), r['verdict'])[:-4] + '.tex')
        if not os.path.exists(tex):
            really.add(int(r['rank']))
    bad += check('the list of source-less papers is exactly the set of source-less papers',
                 [f'rank {n}: has no source, not listed' for n in sorted(really - listed)] +
                 [f'rank {n}: listed, but its source is present' for n in sorted(listed - really)])

    docs = [d for d in os.listdir(repopaths.ROOT)
            if os.path.isdir(os.path.join(repopaths.ROOT, d)) and not d.startswith('.')]
    bad += check('every top-level directory has a README',
                 [d for d in docs
                  if not any(os.path.exists(os.path.join(repopaths.ROOT, d, n))
                             for n in ('README.md', 'MISSING.txt'))])

    print(f'Phase 1: {bad} failed checks')
    return bad


if __name__ == '__main__':
    sys.exit(min(main(), 100))
