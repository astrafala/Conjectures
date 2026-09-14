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
    # **The conjecture that is not in the entry.** An entry may say only
    #
    #     Empirical recurrence of order 42 (see link above).
    #
    # and keep the recurrence in a linked a-file. Quoting the sentence alone would print a
    # paper about a recurrence whose statement appears nowhere in it, so both are quoted: the
    # entry's own words, and the line the link holds.
    if head is not None:
        try:
            import linkrec
            if linkrec.points_at_link(head):
                txt = linkrec.text(anum)
                if txt:
                    first = txt.strip().split('\n')[0].strip()
                    if first:
                        # The a-files are written without spaces --
                        # "a(n)=6*a(n-1)-4*a(n-2)-31*a(n-3)..." -- and at order 95 that is one
                        # unbreakable word several pages wide. TeX has nowhere to break it, so
                        # the quote ran off the page on every one of these. Spacing the signs
                        # gives it breakpoints and changes nothing else.
                        first = re.sub(r'(?<=[\d)])\s*([+-])\s*(?=\d|a\()',
                                       r' \1 ', first)
                        first = re.sub(r'\s*=\s*', ' = ', first, count=1)
                        return head.rstrip() + '\n\n' + first
        except Exception:
            pass
    return head
