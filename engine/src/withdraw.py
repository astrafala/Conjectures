#!/usr/bin/env python3
"""Withdraw installed papers whose premise does not hold, and record why.

    python3 src/withdraw.py deep-check/withdraw-blockpremise.txt "one line of reason"

A withdrawal removes the paper from the roster keyed by its build number, leaves the built
PDF in papers-old-numbering (nothing is deleted that a later audit might want to read), and
appends the A-number and the reason to WITHDRAWN.md. rank.py then rebuilds papers/ from what
is left, so the ranking, the index and the counts follow.

Withdrawing is not a failure mode to be minimised. A result that rests on a premise the entry
does not actually assert is worth less than no result at all.
"""
import json
import os
import sys
import time

import repopaths

WITHDRAWN = os.path.join(repopaths.ROOT, 'WITHDRAWN.md')


def main():
    pool = [a for a in open(sys.argv[1]).read().split() if a.startswith('A')]
    reason = sys.argv[2]
    eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
    cls = json.load(open('paper-classes.json'))
    drop = {n for n, v in eng.items() if v['anum'] in set(pool)}
    if not drop:
        print('nothing to withdraw')
        return
    gone = sorted((eng[n]['anum'], eng[n]['engine'], n) for n in drop)
    for n in drop:
        del eng[n]
    json.dump({str(k): v for k, v in sorted(eng.items())},
              open('paper-engines.json', 'w'), indent=1)
    for k in cls:
        if isinstance(cls[k], list):
            cls[k] = [n for n in cls[k] if n not in drop]
    json.dump(cls, open('paper-classes.json', 'w'), indent=1)
    head = '' if os.path.exists(WITHDRAWN) else (
        '# Withdrawn results\n\nEvery result this project has taken back, with the reason.\n'
        'A withdrawal is recorded here permanently; the built PDF stays in the archive so\n'
        'the claim can be read against the reason it was withdrawn for.\n')
    with open(WITHDRAWN, 'a') as fh:
        if head:
            fh.write(head)
        fh.write(f'\n## {time.strftime("%d %B %Y")} -- {len(gone)} withdrawn\n\n{reason}\n\n')
        for a, e, n in gone:
            fh.write(f'* {a} (build {n}, {e})\n')
    print(f'withdrew {len(gone)}; roster now {len(eng)}')


if __name__ == '__main__':
    main()
