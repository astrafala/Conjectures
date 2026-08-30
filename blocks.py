#!/usr/bin/env python3
"""Every conjectured statement on an entry, including the ones inside blocks.

OEIS writes multi-statement conjectures as

    Conjectures from _Someone_, date: (Start)
    a(n) = a(n-1) + a(n-6) - a(n-7) for n > 14.
    G.f.: (...)/(...).
    (End)

and the lines after the heading do not begin with "Conjecture". Every sweep in this
project selected conjecture lines by that word, so 6,537 statements inside 3,160 such
blocks were invisible to every engine -- among them 2,451 recurrences, 2,396 generating
functions and 1,392 closed forms.

This returns the conjectured statements on an entry as a flat list, block contents
included, each tagged with the heading it came under so a paper can quote the attribution
correctly.
"""
import re

HEAD = re.compile(r"^\s*Conjectur\w*.*\(\s*Start\s*\)\s*$", re.I)
END = re.compile(r"\(\s*End\s*\)", re.I)
CONJ = re.compile(r"^\s*Conjectur", re.I)


def statements(F):
    """[(statement, heading, original line)] for every conjectured statement in F.

    The ORIGINAL line is carried alongside the cleaned statement because the last line of
    a block ends with "(End)", which the statement drops. Excluding conjectures from the
    "known side" by comparing cleaned text against original lines therefore fails on
    exactly that line -- and the engine then used a conjectured generating function as its
    own justification and reported it proved. Twenty-one such results were produced before
    that was noticed, and discarded.
    """
    out, heading = [], None
    for l in F:
        if HEAD.match(l):
            heading = l
            continue
        if heading is not None:
            body = l
            if END.search(l):
                body = END.sub("", l).strip()
                if body:
                    out.append((body, heading, l))
                heading = None
                continue
            if body.strip():
                out.append((body.strip(), heading, l))
            continue
        if CONJ.match(l):
            out.append((l, None, l))
    return out


def conjectured_lines(F):
    """The set of lines that are conjectural, block contents included.

    This matters more than it looks. A line inside a conjecture block does not contain the
    word "conjecture", so any code that decides "is this stated as fact?" by looking for
    that word will treat a conjecture as established -- and an engine that derives a
    recurrence from one conjecture and uses it to prove another has proved nothing at all.
    Every known-side detector must subtract this set.
    """
    out = set()
    for s, h, orig in statements(F):
        out.add(s.strip())
        out.add(orig.strip())          # the raw line too: the last one carries "(End)"
    return out
