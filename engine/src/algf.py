#!/usr/bin/env python3
"""The generating function an entry states as FACT, when it is an explicit algebraic one.

This is what `holonomic.prove` needs: it turns a conjectured P-recursive recurrence into an
identity of functions, which is a proof rather than a check -- but only if the generating
function is known and algebraic. The corpus writes those as

    G.f.: (1-x-sqrt(1-6x+x^2))/(2x(1+x));
    G.f.: g(z)=(1+z)(z^4+2z^3+2z^2-1+Q)/(2z(1-z-z^2-z^3)), where Q = sqrt((1-z^2)(...))

so three things have to be handled and each defeated an earlier filter: the variable may be z
rather than x; a named abbreviation may be defined in a trailing `where' clause and has to be
substituted, not refused; and implicit multiplication is everywhere -- `2x(1+x)', `1-6x',
`(1-z^2)(1-z)'.

A g.f. the entry marks as conjectural is NOT used: proving one conjecture from another is not
a proof. Neither is one that names another sequence, or is given as a functional equation, a
continued fraction, or a sum -- those are real work and are refused here rather than guessed at.
"""
import re

import sympy as sp

x = sp.Symbol('x')
CONJ = re.compile(r'conjectur|empirical', re.I)
GF = re.compile(r'^\s*G\.f\.\s*:?\s*(.*)$', re.I)
ATTR = re.compile(r'\s*[-—]\s*_[^_]+_,.*$')
LEAD = re.compile(r'^\s*[A-Za-z]\s*\(\s*[xz]\s*\)\s*=\s*')
OUT = re.compile(r'A\d{6}|Sum_|Prod_|satisf|continued fraction|Integral|\bE\(|hypergeom', re.I)


def _implicit(s):
    """the corpus's multiplication, written out"""
    s = s.replace('^', '**')
    s = re.sub(r'(\d)\s*(?=[A-Za-z(])', r'\1*', s)          # 2x, 6x^2, 2(1+x)
    s = re.sub(r'(\))\s*(?=[A-Za-z(])', r'\1*', s)          # (1-z)(1+z), (1-z)Q
    s = re.sub(r'\b([xz])\s*(?=\()', r'\1*', s)             # z(1+z)
    s = re.sub(r'\b([xz])\s*(?=[A-Za-z])', r'\1*', s)       # zQ
    return s


def read(e):
    """the g.f. as a sympy expression in x, or None."""
    for L in e['formula'] + e['comment']:
        t = ' '.join(L.split())
        if CONJ.search(t):
            continue
        m = GF.match(t)
        if not m:
            continue
        body = ATTR.sub('', m.group(1)).strip().rstrip(';').rstrip('.')
        if OUT.search(body):
            continue
        # a trailing "where Q = ..." defines an abbreviation; substitute it
        subs = {}
        mm = re.search(r',?\s*where\s+(.*)$', body, re.I)
        if mm:
            body = body[:mm.start()].strip().rstrip(',')
            for part in re.split(r',\s*(?=[A-Za-z]\w*\s*=)', mm.group(1)):
                q = re.match(r'\s*([A-Za-z]\w*)\s*=\s*(.*?)\s*\.?\s*$', part)
                if q:
                    subs[q.group(1)] = q.group(2)
        body = LEAD.sub('', body).strip()
        if not body:
            continue
        var = 'z' if ('z' in body and 'x' not in body) else 'x'
        loc = {var: x, 'sqrt': sp.sqrt}
        try:
            sub_exprs = {k: sp.sympify(_implicit(v), locals=loc) for k, v in subs.items()}
        except Exception:
            continue
        loc.update(sub_exprs)
        s = _implicit(body)
        # after substitution nothing alphabetic may remain but the variable and the names
        known = set(loc) | {'sqrt'}
        names = set(re.findall(r'[A-Za-z]\w*', s))
        if names - known:
            continue
        try:
            A = sp.sympify(s, locals=loc)
        except Exception:
            continue
        if not A.has(x):
            continue
        return A
    return None
