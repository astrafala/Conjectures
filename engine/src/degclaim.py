#!/usr/bin/env python3
"""The claim that names a DEGREE and no coefficients.

    Empirical: a(n) is a polynomial of degree 26 for n>13

Seven entries in the pool say only this, and nothing here reads them: there is no formula to
parse and `ratrec` and `closedform` both want one. But the claim is decidable, and by exactly
the machinery already present, because "a is a polynomial of degree d from n_0 on" is a
statement about a linear recurrence:

  * a agrees with a polynomial of degree at most d on n >= n_0 exactly when the (d+1)-st
    finite difference vanishes there, i.e. when (z-1)^(d+1) annihilates a from n_0+d+1 on;
  * the degree is exactly d, not less, exactly when (z-1)^d does NOT annihilate the tail.

So the entry's "for n>k" predicts a threshold of precisely k+d+1, and that prediction is what
is tested. On A201534 (degree 26, n>13) the threshold is 40 = 13+26+1, and on A201350
(degree 31, n>10) it is 42 = 10+31+1 -- tight in both, which is also the check that this
reading of the sentence is the right one.
"""
import re
from math import comb

PAT = re.compile(
    r'\ba\(n\)\s+is\s+a\s+polynomial\s+(?:in\s+n\s+)?of\s+degree\s+(\d+)'
    r'(?:\s*(?:,|\s)\s*for\s+n\s*>\s*(\d+))?', re.I)


def read(line):
    """(degree, first n claimed) or None. A line with no range claims it for every n."""
    m = PAT.search(' '.join(line.split()))
    if not m:
        return None
    d = int(m.group(1))
    if not 0 < d < 400:
        return None
    return d, (int(m.group(2)) + 1 if m.group(2) else None)


def coeffs(d):
    """(z-1)^(d+1) as a monic recurrence: a(n) = sum_i c_i a(n-i)"""
    return {i: -comb(d + 1, i) * (-1) ** i for i in range(1, d + 2)}
