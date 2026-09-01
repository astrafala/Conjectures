#!/usr/bin/env python3
"""Column k of a T(n,k) table is a fixed-width array count, which the engines already read.

    T(n,k) = Number of (n+1) X (k+1) 0..2 arrays with every 2 X 2 subblock summing to 4.

is a two-dimensional table; its column k = 3 is the ordinary sequence

    Number of (n+1) X (3+1) 0..2 arrays with every 2 X 2 subblock summing to 4.

so the whole battery of engines applies once k is substituted. The only new work is the
substitution and knowing which column a given conjecture line is about.
"""
import re

HEAD = re.compile(r'^\s*T\(n\s*,\s*k\)\s*=?\s*', re.I)


def rewrite(name, k):
    """T(n,k) name -> the ordinary name for column k, or None."""
    s = re.sub(r'\s+', ' ', name).strip()
    m = HEAD.match(s)
    if not m:
        return None
    s = s[m.end():].strip()
    if not s:
        return None
    s = s[0].upper() + s[1:]
    if not re.match(r'(Number of|number of|Half|1/\d)', s):
        s = 'Number of ' + s[0].lower() + s[1:]
    # substitute k everywhere it occurs as a dimension token
    def sub_dim(t):
        t = re.sub(r'\(\s*k\s*\+\s*(\d+)\s*\)', lambda mm: '(%d)' % (k + int(mm.group(1))), t)
        t = re.sub(r'(?<![a-zA-Z])k(?![a-zA-Z(])', str(k), t)
        return t
    s2 = sub_dim(s)
    if 'k' in re.sub(r'[a-zA-Z]k|k[a-zA-Z]', '', s2):
        return None                     # a k survived somewhere unexpected
    return s2
