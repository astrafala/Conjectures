#!/usr/bin/env python3
"""Read a CONJECTURED generating function, however the entry marks it as conjectural.

`gfonly.clean` strips a marker written in front of the line -- `Conjecture: G.f. ...`,
`Empirical g.f.: ...`. The corpus also writes the marker BEHIND the expression:

    G.f.: x*(1 + x - x^2) / ((1 - x)^3*(1 + x)) (conjectured). - _Colin Barker_, ...

and every sweep in this project refuses that line, because the shared parser sees the word
`conjectured' inside the body and returns None -- the same instrument-blindness that hid the
closed-form vein. 154 entries outside the roster carry a conjectured generating function
written only in this form and have never been examined by anything.

The trailing marker is removed here, after the attribution, and the bare expression is handed
to the shared parser. `mark(line)` says whether a conjectural word was found at either end, so
a caller can tell a conjecture from a statement of fact.
"""
import re

import gfrec
import gfonly

TAIL = re.compile(r'\s*\(\s*conjectur\w*\s*\.?\s*\)\s*\.?\s*$', re.I)
TAIL2 = re.compile(r'\s*[;,]?\s*(?:but\s+)?(?:this\s+is\s+)?conjectur\w*\s*\.?\s*$', re.I)


def strip_tail(line):
    """the line with a trailing conjectural qualifier removed."""
    s = gfrec.ATTR.sub('', line.strip())
    s = re.sub(r'\(End\)\s*$', '', s).strip()
    for _ in range(2):
        s2 = TAIL.sub('', s)
        if s2 == s:
            s2 = TAIL2.sub('', s)
        if s2 == s:
            break
        s = s2.strip()
    return s


def normalise(s):
    """implicit multiplication written out, and a stray `=' after the label removed.

    The corpus writes `24 x^2' and `Conjecture: G.f. = x/(1-2*x)'. Neither reaches sympy: the
    first is not valid syntax and the second leaves an `=' where the expression should start.
    """
    s = re.sub(r'(G\.\s*f\.\s*:?)\s*=\s*', r'\1 ', s, flags=re.I)
    s = re.sub(r'(\d)\s+(?=[x(])', r'\1*', s)
    s = re.sub(r'(x(?:\^\d+)?)\s+(?=[x(])', r'\1*', s)
    return s


def parse(line):
    """the rational generating function this line conjectures, or None."""
    s = normalise(strip_tail(line))
    if not gfrec.CONJ.search(s):
        # a bare `G.f.: ...' with the marker only at the end reaches the shared parser now;
        # a marker in front is still gfonly's business
        e = gfrec.parse_gf(s)
        if e is not None:
            return e
    c = gfonly.clean(s)
    return None if c is None else gfrec.parse_gf(normalise(c))


def is_conjectural(line):
    return bool(gfrec.CONJ.search(line) or re.search(r'\bempirical', line, re.I))
