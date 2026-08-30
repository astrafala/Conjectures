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


EMP = re.compile(r"^\s*Empirical\s*[:.]?\s*", re.I)


def unproved(F):
    """(statements, raw lines) for everything on the entry that is not asserted as fact.

    Covers both markers. "Empirical" is the OEIS's usual label for a fitted formula and
    there are more lines carrying it -- 23,322 -- than lines saying "Conjecture", so a
    reader that knows only the second word sees barely half of what is open.

    Two collections again, for the reason learned the hard way: the RAW lines are what a
    known-side detector subtracts, and the STATEMENTS are what an engine tries to prove.
    A cleaned statement no longer matches the line it came from, and using one set for
    both fails in whichever direction you pick.
    """
    stmts, raw, heading = [], set(), None
    for l in F:
        s = l.strip()
        if HEAD.match(l) or (EMP.match(l) and END_START(l)):
            heading = l
            raw.add(s)
            continue
        if heading is not None:
            raw.add(s)
            body = END.sub("", l).strip()
            raw.add(body)
            if body:
                stmts.append((body, heading, l))
            if END.search(l):
                heading = None
            continue
        if CONJ.match(l):
            stmts.append((l, None, l))
            raw.add(s)
        elif EMP.match(l):
            body = EMP.sub("", l).strip()
            if body:
                stmts.append((body, l, l))
            raw.add(s)
            raw.add(body)
    return stmts, raw


def END_START(l):
    return bool(re.search(r"\(\s*Start\s*\)\s*$", l, re.I))
