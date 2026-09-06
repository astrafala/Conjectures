#!/usr/bin/env python3
"""Has the roster reached the size at which the deep check runs?

The check described in deep-check/PLAN.md is meant to fire on its own, not when somebody
remembers it, so the condition lives in code rather than in a document. It reports the
roster size and exits 0 exactly when the check is due.
"""
import csv
import os
import sys

import repopaths

THRESHOLD = 10000


def roster_size():
    with open(os.path.join(repopaths.ROOT, 'papers', 'index.csv')) as f:
        return sum(1 for _ in csv.DictReader(f))


if __name__ == '__main__':
    n = roster_size()
    due = n >= THRESHOLD
    print(f'{n} papers; the deep check is {"DUE" if due else "not due"} '
          f'({THRESHOLD - n} to go)' if not due else f'{n} papers; the deep check is DUE')
    sys.exit(0 if due else 1)
