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


# "G.f. (1-3*x-...)/(...)" and "G.f. (for offset 1): ..." carry no colon after the prefix,
# or carry one only after a parenthetical, and the strippers below all key on the colon.
_NOCOLON = re.compile(r"^\s*((?:o\.|e\.)?g\.f\.)\s*(\(for offset [^)]*\))?\s*:?\s*", re.I)


def _colonise(line):
    """Rewrite a prefix that has no colon, or one interrupted by a parenthetical.

    "G.f. <expr>" has no colon at all, and "G.f. (for offset 1): <expr>" has one only
    after an aside. Both are refused by strippers that key on the colon, and the aside is
    otherwise carried into the candidate and breaks sympify. The g.f. is checked against
    the entry's terms downstream, so a wrong offset is caught there.
    """
    m = _NOCOLON.match(line)
    if not m:
        return line
    aside = m.group(2)
    if ":" in line[:m.end()] and not aside:
        return line
    rest = line[m.end():].lstrip()
    if not rest or rest[0] not in "(-0123456789x":
        return line
    return m.group(1) + ": " + rest


def candidates(line):
    line = _colonise(line)
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


def polynomial_correction(base, data, off, maxfix=6):
    """The finitely many low-order terms by which a posted g.f. misses the entry's data.

    Entries often post a generating function that is right from some index on but wrong
    at the first term or two -- written for a(n) with n >= 1 while the offset is 0, or
    ignoring a constant. Requiring an exact match everywhere throws those away; using the
    g.f. as posted would prove something about a different sequence.

    Adding a polynomial keeps the function algebraic and changes the residual by a
    polynomial, so the criterion still applies. Returns (correction terms as a list of
    (index, value), first index that already agreed), or None when the mismatch is not
    confined to an initial segment.
    """
    import sympy as sp
    x = sp.Symbol('x')
    diffs = []
    for k in range(len(data)):
        i = off + k
        if i >= len(base):
            return None
        d = sp.simplify(base[i] - data[k])
        if d != 0:
            diffs.append((i, sp.nsimplify(-d, rational=True)))
    if not diffs:
        return [], off
    if len(diffs) > maxfix:
        return None
    # the mismatch must be an INITIAL SEGMENT. A scattered one -- agreeing at the first
    # few indices, differing in the middle -- means the posted function is not this
    # sequence's generating function at all, and patching it would mean proving something
    # about a function nobody posted. Adding a polynomial is mathematically harmless
    # either way; the restriction is about what the paper is entitled to claim as input.
    idxs = sorted(i for i, _ in diffs)
    if idxs != list(range(off, off + len(idxs))):
        return None
    return diffs, idxs[-1] + 1
