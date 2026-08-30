#!/usr/bin/env python3
"""Recover the expression from a generating-function line whose tail is prose.

The parser was not defeated by hard notation on most of the entries it could not read.
It was defeated by what comes AFTER the formula: an old-style attribution with no
underscores ("- Maksym Voznyy (voznyy(AT)mail.ru), Aug 11 2009"), an editorial note
("- amended by _Georg Fischer_"), a pointer to a paper ("(See theorem 3.1 in Albert et
al. reference)"), or a second English sentence.

Rather than try to write one regex that always cuts in the right place, this offers a
handful of candidate cuts, longest first. The caller expands each and keeps the one whose
coefficients are the entry's own terms, so a bad cut is rejected by the data rather than
trusted. A cut that happens to parse but means something else cannot survive that.
"""
import re

ATTRIB = re.compile(
    r"\s+-\s+(?:_[^_]+_|[A-Z][A-Za-z.'\- ]{2,30}\s*(?:\([^)]*\))?)\s*,?\s*"
    r"(?:[A-Z][a-z]{2}\s+\d{1,2},?\s+\d{4})?\s*$")
LEAD = re.compile(r"^\s*(O\.?g\.?f\.?|E\.?g\.?f\.?|G\.?f\.?|Generating function)"
                  r"\s*[:.]\s*", re.I)
EDIT = re.compile(r"\s+-\s+(?:corrected|amended|reformulated|edited|added|rewritten|"
                  r"simplified|From)\b.*$", re.I)


def candidates(line):
    """Plausible expression strings from one formula line, longest first."""
    s = LEAD.sub("", line.strip())
    outs = []

    def add(t):
        t = t.strip().rstrip(".").strip().rstrip(",").strip()
        if t and t not in outs:
            outs.append(t)

    add(s)
    # the tails are stripped cumulatively, and every intermediate form is offered:
    # a line can carry a bracketed note AND a parenthetical pointer AND an attribution
    for pat, repl in (
            (EDIT, ""),
            (ATTRIB, ""),
            (re.compile(r"\s*\[[^\[\]]*\]\s*$"), ""),
            (re.compile(r"\s*\((?:See|see|cf\.|Cf\.)[^()]*\)\s*$"), ""),
            (ATTRIB, ""),
            (re.compile(r"\s*\[[^\[\]]*\]\s*$"), ""),
    ):
        t = pat.sub(repl, s).strip().rstrip(".").strip()
        if t and t != s:
            s = t
            add(s)
    # an old-style e-mail attribution anywhere after the formula
    m = re.search(r"\s+-\s+[^-]*\(AT\)", s)
    if m:
        add(s[:m.start()])
    # a second English sentence: cut at ". " when what follows starts a word and the
    # head still contains the variable
    for m in re.finditer(r"\.\s+(?=[A-Z])", s):
        head = s[:m.start()]
        if re.search(r"[xtz]", head):
            add(head)
    # a trailing prose clause introduced by a semicolon
    add(s.split(";")[0])
    outs.sort(key=len, reverse=True)
    return outs
