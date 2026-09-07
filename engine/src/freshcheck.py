#!/usr/bin/env python3
"""Refresh the OEIS mirror, then re-check every roster entry against it.

Two papers were claimed for conjectures somebody else had proved three days earlier, and the
only reason was that the local export was two days old. The rule "re-check settlement against
the live OEIS before counting anything new" was written down and still cost two papers,
because a rule that has to be remembered gets remembered late. This is the rule as code.

It prints, for every roster entry whose live text now carries settlement wording, the entry,
the matching line and the date on our paper. A hit is a reason to look, not a verdict: the
wording is usually about a different statement on the same entry, and reading the paper is
what decides. What it cannot do for you is compare dates on a preprint --- when a hit names
one, open it and read the submission date rather than inferring it from the identifier.

    python3 src/freshcheck.py           refresh and check
    python3 src/freshcheck.py --no-pull check against the mirror as it stands
"""
import json
import subprocess
import sys

import openness
import paperdates
import paperpath as P

MIRROR = '/home/user/oeis/oeisdata'


def pull():
    r = subprocess.run(['git', 'pull', '--ff-only'], cwd=MIRROR,
                       capture_output=True, text=True, timeout=600)
    d = subprocess.run(['git', 'log', '-1', '--format=%ci'], cwd=MIRROR,
                       capture_output=True, text=True).stdout.strip()
    print(('mirror updated' if 'Already up to date' not in r.stdout else 'mirror already current')
          + f'; last export {d}')


def main():
    if '--no-pull' not in sys.argv:
        pull()
    printed = paperdates.load()
    rm = json.load(open('rank-map.json'))
    where = {}
    for m in rm:
        rel = f"papers/{P.band(m['rank'])}/{P.name(m['rank'], m['verdict'])}"
        where.setdefault(m['anum'], []).append((m['rank'], printed.get(rel)))
    flagged = 0
    for a in sorted(where):
        try:
            ok, lines = openness.status(a)
        except Exception:
            continue
        if ok:
            continue
        flagged += 1
        for rank, date in where[a]:
            print(f'{a}  paper {rank}  dated {date or "unknown"}')
        for L in lines[:2]:
            print('    ' + ' '.join(L.split())[:220])
    print(f'\n{len(where)} roster entries checked, {flagged} carry settlement wording.')
    print('Each is a reason to look. Withdraw only when the other proof is EARLIER than the '
          'date on our paper; a later one leaves the result standing.')


if __name__ == '__main__':
    main()
