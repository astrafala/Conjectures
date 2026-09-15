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

# A formula qualified by a FINITE RANGE is not a fact, whatever it does not say:
#
#     A020745  a(n) = 2*a(n-1) - a(n-2) + a(n-3) - a(n-4)
#              (holds at least up to n = 1000 but is not known to hold in general)
#
# That line carries no conjectural word and was read as a premise. Proving the entry's
# conjectured generating function from it would be proving one conjecture from another, and
# two such papers were built and caught by hand before installation. The hedges below are the
# phrasings the corpus actually uses, counted over the whole clone.
WORD = re.compile(
    r'onjectur|mpirical|It appears|Apparently|seems to'
    r'|not known to (?:hold|be true)|but is not known'
    r'|holds at least up to|(?:checked|verified|confirmed|tested) up to\b'
    r'|heuristic|presumably|probably|unproved|unproven|it is likely',
    re.I)


def facts(e):
    """the %C and %F lines the entry states as fact, in file order."""
    conj = {L.strip() for L in conjlines.lines(e)}
    return [L for L in e['comment'] + e['formula']
            if L.strip() not in conj and not WORD.search(L)]
