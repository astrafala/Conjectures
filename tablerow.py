"""A ROW of a T(n,k) table is a fixed-height array count.

`tablecol` fixes k and walks in n. This fixes n and walks in k, which is the same thing with
the two dimensions exchanged: substituting the row index for n and renaming k to n turns

    T(n,k) = Number of (n+1) X (k+1) 0..2 arrays with <condition>

into "Number of (2) X (n+1) 0..2 arrays with <condition>" for row 1. The engines already read
a name whose FIRST dimension is fixed --- they walk along columns and transpose the condition
themselves --- so no new machinery is needed, and a wrong reading is rejected by the
requirement that the model reproduce the row's published values exactly.
"""
import re

HEAD = re.compile(r'^\s*T\(n\s*,\s*k\)\s*=?\s*', re.I)


def rewrite(name, r):
    s = re.sub(r'\s+', ' ', name).strip()
    m = HEAD.match(s)
    if not m:
        return None
    s = s[m.end():].strip()
    if not s:
        return None
    s = re.sub(r'^is\s+the\s+number\s+of\b', 'Number of', s, flags=re.I)
    s = s[0].upper() + s[1:]
    if not re.match(r'(Number of|number of|Half|1/\d|One quarter)', s, re.I):
        s = 'Number of ' + s[0].lower() + s[1:]
    # n is the row index, so it becomes the constant; k becomes the walk variable
    s = re.sub(r'\(\s*n\s*\+\s*(\d+)\s*\)', lambda mm: '(%d)' % (r + int(mm.group(1))), s)
    s = re.sub(r'(?<![a-zA-Z])n(?![a-zA-Z(])', str(r), s)
    s = re.sub(r'(?<![a-zA-Z])k(?![a-zA-Z(])', 'n', s)
    if re.search(r'(?<![a-zA-Z])k(?![a-zA-Z(])', s):
        return None
    return s
