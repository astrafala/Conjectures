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
def _rows():
    if not os.path.exists(PATH):
        return ()
    return tuple(re.findall(r'^\* (A\d{6})(?: \(build \d+, ([^)]*)\))?', open(PATH).read(),
                            re.M))


@functools.lru_cache(maxsize=1)
def anums():
    """every A-number ever withdrawn."""
    return frozenset(a for a, _r in _rows())


@functools.lru_cache(maxsize=1)
def labels():
    """A-number -> the labels it was withdrawn under."""
    d = {}
    for a, r in _rows():
        d.setdefault(a, set()).add(r.strip())
    return {k: frozenset(v) for k, v in d.items()}


def blocked(anum, label):
    """whether installing THIS argument for this entry would repeat a withdrawal.

    Blocking the A-number outright is too blunt. Twelve entries withdrawn on 8 September for
    `gf-implies-rec' -- proving a conjectured recurrence from a generating function inside the
    same conjecture block, which settles nothing -- are settled properly by an exact model,
    and that is a different argument on the same open conjecture, not the withdrawn one
    returning. What must not come back is the argument, so the label is what is checked.
    """
    return label in labels().get(anum, ())
