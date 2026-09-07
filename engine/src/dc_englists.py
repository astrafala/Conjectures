#!/usr/bin/env python3
"""Is there anywhere left that keeps its own list of engines?

The same defect appeared five times in one day: a sweep or a check carrying a list of engine
names written into the file, which was the whole set on the day it was written and is now
eleven or twelve of eighty-three. Everything needing any other engine was reported as "no
engine reads the name" and dropped --- 434 table entries behind one of them, and every
conjecture from seventy-two engines never even tested for failure behind another.

`uniform.py` is the one place allowed to know the list. This finds anywhere else that does,
and is the enforcing code for that rule.

    python3 src/dc_englists.py
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uniform

ALLOWED = {'uniform.py'}
# A file that says in its own docstring that it is superseded is not a live route; it is kept
# for the record and reported separately rather than counted as a defect.
SUPERSEDED = re.compile(r'SUPERSEDED')
LIST = re.compile(r'^(\w+)\s*=\s*(\[[^\]]*\'transfer[^\]]*\])', re.M)


def main():
    full = set(uniform.ENG)
    live, dead = [], []
    here = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(glob.glob(os.path.join(here, '*.py'))):
        base = os.path.basename(f)
        if base in ALLOWED:
            continue
        s = open(f).read()
        for m in LIST.finditer(s):
            try:
                lst = eval(m.group(2))
            except Exception:
                continue
            if not isinstance(lst, list) or not all(isinstance(x, str) for x in lst):
                continue
            missing = full - set(lst)
            if not missing:
                continue
            row = (base, m.group(1), len(lst), len(missing))
            (dead if SUPERSEDED.search(s) else live).append(row)
    for base, name, n, miss in live:
        print(f'  DEFECT  {base}: {name} names {n} engines and misses {miss} of '
              f'{len(full)}')
    for base, name, n, miss in dead:
        print(f'  (superseded, not a live route) {base}: {name} names {n}, misses {miss}')
    print(f'\n{len(live)} live files keep their own engine list; '
          f'{len(dead)} superseded ones do.')
    return 1 if live else 0


if __name__ == '__main__':
    raise SystemExit(main())
