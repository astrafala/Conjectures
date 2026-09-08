#!/usr/bin/env python3
"""The lines an entry states as FACT -- everything the entry does not mean conjecturally.

Every premise vein in this project rests on the difference between a formula the entry asserts
and one it conjectures, and for a long time that difference was tested by looking for a
conjectural word ON the line. It is not there. An entry writes

    Conjectures from _Chai Wah Wu_, Feb 14 2020: (Start)
    a(n) = a(n-1) + a(n-11) - a(n-12) for n > 12.
    G.f.: (x^12 + 3*x^11 + ...)/(x^12 - x^11 - ...)
    (End)

and neither formula line carries a word. Reading the generating function there as a fact and
proving the recurrence from it proves nothing at all: they are one conjecture written twice.
1,336 installed papers were built that way and had to be withdrawn.

`facts(e)` is the complement of `conjlines.lines(e)` within the entry's comment and formula
fields, and is the only list a premise may be taken from.
"""
import re

import conjlines

WORD = re.compile(r'onjectur|mpirical|It appears|Apparently|seems to', re.I)


def facts(e):
    """the %C and %F lines the entry states as fact, in file order."""
    conj = {L.strip() for L in conjlines.lines(e)}
    return [L for L in e['comment'] + e['formula']
            if L.strip() not in conj and not WORD.search(L)]
