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
    # 'T(n,k) is the number of ...' as well as 'T(n,k) = Number of ...': prepending
    # 'Number of' blindly produced 'Number of is the number of'
    s = re.sub(r'^is\s+the\s+number\s+of\b', 'Number of', s, flags=re.I)
    s = s[0].upper() + s[1:]
    if not re.match(r'(Number of|number of|Half|1/\d|One quarter)', s, re.I):
        s = 'Number of ' + s[0].lower() + s[1:]
    # substitute k everywhere it occurs as a dimension token
    def sub_dim(t):
        t = re.sub(r'\(\s*k\s*\+\s*(\d+)\s*\)', lambda mm: '(%d)' % (k + int(mm.group(1))), t)
        t = re.sub(r'(?<![a-zA-Z])k(?![a-zA-Z(])', str(k), t)
        return t
    s2 = sub_dim(s)
    if 'k' in re.sub(r'[a-zA-Z]k|k[a-zA-Z]', '', s2):
        return None                     # a k survived somewhere unexpected
    return _tidy(s2)


def _tidy(s):
    """Drop a trailing parenthetical remark and the parentheses round a substituted width.

    A table name often ends with an aside about the table rather than about the arrays ---
    "(2 maximizes T(1,1))", "(constant-stress 1 X 1 tilings)" --- and no engine's name regex
    expects it, so 192 tables were being reported unreadable for a remark that says nothing
    about what is counted. The remark can itself contain brackets, so it is matched from the
    end rather than with a flat pattern. The substitution above also leaves the width in
    brackets, "(n+1)X(3)", where the engines are written for "(n+1)X3".
    """
    s = re.sub(r'X\s*\(\s*(\d+)\s*\)', lambda m: 'X' + m.group(1), s)
    t = s.rstrip()
    dot = t.endswith('.')
    if dot:
        t = t[:-1]
    if t.endswith(')'):
        depth = 0
        for i in range(len(t) - 1, -1, -1):
            if t[i] == ')':
                depth += 1
            elif t[i] == '(':
                depth -= 1
                if depth == 0:
                    head = t[:i].rstrip()
                    # only an ASIDE is dropped: if the brackets are part of the sentence the
                    # head would not read as a complete name, so require it to end in a word
                    if re.search(r'[A-Za-z0-9]$', head):
                        return head + ('.' if dot else '')
                    break
    return s
