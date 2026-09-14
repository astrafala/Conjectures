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


# A line can carry more than one claim:
#
#     Conjecture: a(n) = 16*n-12 for n>1. a(n) = 2*a(n-1)-a(n-2) for n>3. G.f.: x*(5+10*x+x^2)/(1-x)^2.
#
# `ratrec.parse_rec` is handed the whole line and sees none of the three. Measured across the
# pool this costs 17 entries, of which 3 have a name an engine reads -- small, but the three are
# cusp-form dimensions, where the sequence is known in exact closed form and the claim is
# therefore decidable outright. `claims` splits a line into its sentences so each is read alone.
#
# The split is on ". " only where the preceding character ends a formula (a digit or a closing
# parenthesis) and the next starts a new one; that leaves "a(n-1)" and "Gamma_0( 60 )." intact.
SPLIT = re.compile(r'(?<=[)\d])\.\s+(?=[A-Za-z(])')
SIG = re.compile(r'\s*[-—]\s*_[^_]+_,.*$')
BRACKET = re.compile(r'\[_[^_]+_,[^\]]*\]')


def claims(e):
    """the conjectural lines, each further split into its separate claims"""
    out = []
    for L in lines(e):
        t = BRACKET.sub('', SIG.sub('', ' '.join(L.split())))
        parts = [p.strip(' .') for p in SPLIT.split(t)]
        # the line itself first: a claim that legitimately contains ". " must still be read
        out.append(L)
        if len(parts) > 1:
            out.extend(p for p in parts if p)
    return out
