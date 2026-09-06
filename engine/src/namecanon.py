"""One place for the ways an entry can say "the number of".

Every engine's name parser expects a name beginning `Number of ...`, or one of the scaled
forms `Half the number of ...`, `One quarter the number of ...`, `1/3 the number of ...`.
The encyclopedia also writes, for the same thing:

    a(n) is the number of ...        (135 entries)
    1/4 of the number of ...          (51)
    a(n) = Number of ...              (23)
    a(n) is half the number of ...
    Half of the number of ...

Those were refused by every engine, and a refusal is invisible: it looks exactly like "there
was nothing there". This rewrites them into the canonical form and leaves anything already
canonical untouched.
"""
import re

_PRE = re.compile(r'^\s*a\(n\)\s*(?:=|is)\s*', re.I)
_OF = re.compile(r'^\s*(Half|One quarter|1/\d+)\s+of\s+the\s+number\s+of\s+', re.I)
_THE = re.compile(r'^\s*the\s+number\s+of\s+', re.I)


def canon(nm):
    s = nm
    m = _PRE.match(s)
    if m:
        s = s[m.end():]
        s = s[0].upper() + s[1:] if s else s
    m = _OF.match(s)
    if m:
        s = '%s the number of %s' % (m.group(1), s[m.end():])
    m = _THE.match(s)
    if m:
        s = 'Number of ' + s[m.end():]
    if re.match(r'^\s*half\s+the\s+number\s+of\s', s, re.I):
        s = 'Half' + s[s.lower().index('half') + 4:]
    return s
