#!/usr/bin/env python3
"""Which lines on an entry are conjectured recurrences -- in EITHER spelling.

Every sweep so far selected conjecture lines with the test

    "a(n-" in line and "=0" in line

which reads only the form "Conjecture: p_0(n)a(n) + ... + p_r(n)a(n-r) = 0". OEIS also
writes the same thing as "Conjecture: a(n) = <combination of earlier terms>", and a census
of the whole encyclopedia found 183 open conjectures written that way -- excluded from
every run so far, not because the engines could not settle them but because the filter
never offered them.
"""
import re

# "Empirical" belongs here too. The docstring's "either spelling" meant the two shapes of
# the recurrence, and the marker test was left matching only "Conjectur" -- so every
# Empirical recurrence, which is the bulk of the corpus, was refused by this function
# before any engine saw it.
CONJ = re.compile(r"^\s*(Conjectur|Empirical)", re.I)
GUESS = re.compile(r"empirical|apparent|it seems|probably", re.I)


def is_recurrence(line):
    """True if the line states a linear recurrence, in either spelling."""
    if not CONJ.match(line):
        return False
    nb = line.replace(" ", "")
    if "a(n-" not in nb and "a(n+" not in nb:
        return False
    if "=0" in nb:
        return True
    # "a(n) = <combination of a(n-1), ...>": an equation whose left side is a(n)
    body = re.sub(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*", "", line, flags=re.I)
    body = re.sub(r"^(D-finite with recurrence|to be D-finite with recurrence)[:.]?\s*",
                  "", body, flags=re.I)
    return re.match(r"\s*a\(n\)\s*=", body) is not None


def recurrences(F):
    return [l for l in F if is_recurrence(l)]
