#!/usr/bin/env python3
"""The A-numbers this project has taken back, so nothing quietly puts them back.

A withdrawal removes the paper from `paper-engines.json' and records the reason in
WITHDRAWN.md, and that was the whole of it: the hit is still in its sweep's file, so the next
unfiltered `build_new.py' builds the paper again and the next `integrate_rest.py' installs it.
179 papers withdrawn on 13 September were rebuilt within the hour by exactly that route. A
withdrawal has to be sticky, and WITHDRAWN.md is where it is written down, so WITHDRAWN.md is
what the builders read.
"""
import functools
import os
import re

import repopaths

PATH = os.path.join(repopaths.ROOT, 'WITHDRAWN.md')


@functools.lru_cache(maxsize=1)
def anums():
    if not os.path.exists(PATH):
        return frozenset()
    return frozenset(re.findall(r'^\* (A\d{6})\b', open(PATH).read(), re.M))
