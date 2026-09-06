#!/usr/bin/env python3
"""Is this conjecture still open? Decided BEFORE any engine runs, not after.

Every sweep here has proved things first and checked openness afterwards, which wastes the
expensive half of the work on conjectures that were already settled -- 5 of 14 in one
sweep, and A105750 got as far as a verdict before its entry turned out to say "Mathar's
third-order recurrence above follows easily from this".

Two lessons are baked in:

  * The settlement wording is not only in %F. A052627 and A045406 carry Tong Niu's proofs
    as %H links; A126674 says "R. J. Mathar's recurrence is correct" in a %C comment. All
    tags are read.
  * "follows from" as adjacent words is not enough. Any adverb can sit in the gap
    ("follows easily from"), and there are several other ways to say it.

A hit is a REASON TO LOOK, not a verdict: the wording often refers to a different statement
on the same entry, and 26 of 26 flagged papers in the roster audit turned out to be exactly
that. So `status` returns the matching lines and the caller decides.
"""
import os, re

ROOT = "/home/user/oeis/oeisdata/seq"

SETTLED = re.compile(
    # "is true" alone missed "The above conjectures ARE true" (A208658) and "Barker's
    # conjectures are true" (A235089), both of which settle the entry outright. Any of
    # is/are/was/were, and any of the words that follow, must match.
    # "the empirical/conjectured formulas BECOME true" (A188555) is a settlement, and the
    # is/are/was/were list did not reach it. Any of become/becomes/became/turn out, and the
    # copula list, count.
    r"\bproof\b|prove[sndg]?\b|confirm\w*|verif\w*|establish\w*"
    r"|\b(is|are|was|were|become|becomes|became|turns?\s+out\s+to\s+be)\s+"
    r"(true|correct|proved|proven|verified|established|known)\b"
    # Robert Israel settles two entries with "which implies Mathar's conjectured recurrence"
    # and "from which follows ... as well as Mathar's conjecture"; Sela Fried settles a third
    # with "All conjectures stated above hold true". None of the three matched.
    r"|\b(?:implies|implying|from\s+which\s+follows?)\b[^.]{0,120}conjectur"
    r"|conjectur\w*[^.]{0,40}\bhold[s]?\s+true\b"
    r"|follows\s+(?:\w+\s+){0,2}from"
    r"|is\s+(?:an?\s+)?(?:easy|immediate|direct|simple)?\s*consequence"
    r"|can\s+be\s+(?:easily\s+)?(?:proved|proven|derived|shown|deduced|obtained)"
    r"|no\s+longer\s+a\s+conjecture|is\s+now\s+a\s+theorem"
    r"|(?:was|has\s+been)\s+(?:settled|resolved|answered)", re.I)

# these say the opposite -- a finite check is not a proof
FINITE = re.compile(r"for\s+n\s*=\s*\d+\s*\.\.\s*\d+|\bchecked\b|\bverified for\s+n"
                    r"|\bup to\b\s+n|verification needed", re.I)


def lines(anum, tags="FCHDNe"):
    p = os.path.join(ROOT, anum[:4], anum + ".seq")
    if not os.path.exists(p):
        return []
    out = []
    for l in open(p, errors="ignore"):
        if len(l) > 3 and l[0] == "%" and l[1] in tags:
            out.append(re.sub(r"^%.\s+A\d{6}\s*", "", l.rstrip()))
    return out


def status(anum):
    """(open?, the lines that say otherwise). A hit is a reason to read, not a verdict."""
    hits = [l for l in lines(anum) if SETTLED.search(l) and not FINITE.search(l)]
    return (not hits), hits


def is_open(anum):
    return status(anum)[0]
