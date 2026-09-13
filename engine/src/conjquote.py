#!/usr/bin/env python3
"""The entry's own words for the conjecture a paper proves, for its section 1 to quote.

Two defects, one place.

**A word test for "conjecture" ON the line.** This is the defect this project keeps paying
for. An entry writes

    Conjectures from _Colin Barker_, Feb 14 2020: (Start)
    a(n) = a(n-1) + a(n-11) - a(n-12) for n > 12.
    (End)

and no formula line carries a conjectural word of its own. 542 installed papers therefore had
nothing to quote and printed a parenthetical placeholder in place of the conjecture they were
about. `conjlines' understands the block and is what is asked here; the header line is carried
along when the recurrence itself is bare, since that is where the contributor and the date are.

**The wrong line of the block.** A block usually holds a closed form, a recurrence and a
generating function, and only ONE of them is what the paper proves. Taking the first line with
an `a(n) =' on it quoted A266975 a closed form in decimal powers while the theorem below it
stated the entry's recurrence -- two different conjectures, one quoted, the other proved. When
the coefficients are known, the line that PARSES to them is preferred; 41 installed papers
quote a different one.
"""
import re

import conjlines
import localentry as LE
import ratrec


def line(anum, coeffs=None, e=None):
    e = e or LE.get(anum)
    cand = conjlines.lines(e)
    head = next((L for L in cand if re.search(r'onjectur|Empirical', L, re.I)), None)

    def dress(L):
        if re.search(r'onjectur|Empirical', L, re.I) or head is None:
            return L
        return head.rstrip() + ' ' + L.strip()

    if coeffs:
        want = {int(k): int(v) for k, v in coeffs.items()}
        for L in cand:
            r = ratrec.parse_rec(L)
            if not r:
                continue
            d = r[0] if isinstance(r, tuple) else r
            try:
                if {int(k): int(v) for k, v in d.items()} == want:
                    return dress(L)
            except Exception:
                continue
    for L in cand:
        if re.search(r'a\(n\)\s*=', L):
            return dress(L)
    return head
