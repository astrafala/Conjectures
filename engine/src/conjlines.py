#!/usr/bin/env python3
"""The lines of an entry that state a conjecture, blocks included.

Every sweep in this repository decided which lines to read with

    MARK = re.compile(r'onjectur|Empirical', re.I)

and that requires the conjectural word to be ON the line. A conjecture is very often written
as a block instead, and then the formulas carry no such word at all:

    Conjectures from _Colin Barker_, Jun 04 2017: (Start)
    a(n) = 3*a(n-1) - a(n-3).
    G.f.: x*(1 + x) / (1 - 3*x + x^3).
    (End)

Those formula lines were invisible to every sweep the project has ever run. The same defect
was found and fixed in `pooltrim.py`, where it had hidden 1,648 entries from the candidate
pools; this is the same mistake one level down, deciding what to read inside an entry that had
already been selected.

`lines(entry)` returns the conjectural lines: those carrying the word themselves, plus every
line inside an opened block up to its "(End)".
"""
import re

MARK = re.compile(r'onjectur|Empirical', re.I)
OPEN = re.compile(r'(?:conjectur\w*|empirical)\b.*\(Start\)', re.I)
END = re.compile(r'\(End\)', re.I)


def lines(e):
    """the conjectural lines of an entry dict, in file order"""
    out, inside = [], False
    for L in e['comment'] + e['formula']:
        t = L.strip()
        if OPEN.search(t):
            inside = True
            out.append(L)
            continue
        if inside:
            out.append(L)
            if END.search(t):
                inside = False
            continue
        if MARK.search(L):
            out.append(L)
    return out
