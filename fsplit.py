#!/usr/bin/env python3
"""Split a %F line into the separate formulas it actually contains.

A single OEIS formula line often carries several statements:

    G.f.: x/(1-x)^2. E.g.f.: x*exp(x). a(n)=n. a(-n)=-a(n).

Every parser in this project reads the line whole, fails to make sense of it, and reports
no closed form -- for A000027, whose closed form a(n) = n is sitting in the middle of that
line. The fact side of an entry is the scarce resource here, so a line thrown away for
punctuation is a conjecture left unsettled.

Splitting on ". " needs care. These must NOT split:
    g.f.  e.g.f.  o.g.f.  Dgf.  cf.  resp.  etc.  i.e.  e.g.
    0.5, 1.25 and any other decimal
    ...  and  .. (a range, as in k=0..n)
    an initial "A. Author"
so the split point is a period followed by whitespace and then a capital letter, a digit or
"a(", with those abbreviations and decimals excluded first by masking them.
"""
import re

_ABBR = [r"e\.g\.f\.", r"o\.g\.f\.", r"g\.f\.", r"[Dd]gf\.", r"l\.g\.f\.", r"b\.g\.f\.",
         r"cf\.", r"resp\.", r"etc\.", r"i\.e\.", r"e\.g\.", r"vs\.", r"approx\.",
         r"Ref\.", r"Eq\.", r"eq\.", r"no\.", r"cor\.", r"Thm\.", r"Ch\."]
_MASK = "\x00"


def split(line):
    """The statements on the line, in order. A line with one statement returns [line]."""
    s = line
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return _MASK + str(len(holes) - 1) + _MASK

    s = re.sub("|".join(_ABBR), stash, s, flags=0)
    s = re.sub(r"\d+\.\d+", stash, s)          # decimals
    s = re.sub(r"\.{2,}", stash, s)            # ranges and ellipses
    # not \b before the initial: inside "_A. Author_" the underscore is a word character,
    # so \b does not match there and the attribution split in two.
    s = re.sub(r"(?<![A-Za-z])[A-Z]\.(?=\s*[A-Z])", stash, s)   # initials in a name
    parts = re.split(r"(?<=\.)\s+(?=[A-Z(]|\d|a\()", s)

    def unstash(p):
        return re.sub(_MASK + r"(\d+)" + _MASK, lambda m: holes[int(m.group(1))], p)

    return [unstash(p).strip() for p in parts if unstash(p).strip()]


if __name__ == "__main__":
    for t in ["G.f.: x/(1-x)^2. E.g.f.: x*exp(x). a(n)=n. a(-n)=-a(n).",
              "a(n) = Sum_{k=0..n} binomial(n,k). - _A. Author_, Jan 01 2020",
              "The constant is 1.6180339887. G.f.: 1/(1-x-x^2).",
              "a(n) = n^2."]:
        print(t)
        for p in split(t):
            print("   |", p)
