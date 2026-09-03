#!/usr/bin/env python3
"""`Number of n X W 0..m arrays with no element equal to the sum modulo k of elements to its
left or elements above it' and its relatives.

The same condition as the ray-sum family, written differently. A cell is forbidden to equal,
modulo `k', the sum of everything lying before it along one of up to four rays --- west, north,
northwest, northeast --- with a constant added, the constant being zero when the entry does not
name one. The entries of this group put the modulus in front (`the sum modulo k of ...') or at
the end (`..., modulo k'), and drop the words `the sum of' from every clause after the first.

The residues of those sums are carried in the state exactly as before: taking the array a slice
at a time, one ray's sum is the running total inside the current slice, the opposite ray's is a
per-position total, and the two diagonal rays shift one position as they advance. This module
reads the wording; the walk is the ray-sum engine's.
"""
import re

import namecanon
import transfer52

NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8, 'nine': 9}
SHAPE = r'(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))\s*X\s*(?:\((n|\d+)\s*\+\s*(\d+)\)|(n|\d+))'
NAME = re.compile(
    r'Number of\s+' + SHAPE + r'\s*0\.\.(\d+)\s*arrays with no element equal to\s+(.*?)\s*'
    r'\.?\s*$', re.I)
RAY = [('west', r'to its left'), ('north', r'above it'),
       ('nw', r'diagonally to its northwest'),
       ('ne', r'(?:anti)?diagonally to its northeast')]


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    ra = m.group(1) or m.group(3)
    rb = int(m.group(2) or 0)
    ca = m.group(4) or m.group(6)
    cb = int(m.group(5) or 0)
    if (ra == 'n') == (ca == 'n'):
        return None
    if ra == 'n':
        W, trans = int(ca) + cb, False
    else:
        W, trans = int(ra) + rb, True
    alpha = int(m.group(7))
    body = m.group(8)
    g = re.match(r'the sum modulo (\d+) of\s+(.*)$', body, re.I)
    if g:
        mod, rest = int(g.group(1)), g.group(2)
    else:
        g = re.match(r'(.*),\s*modulo (\d+)$', body, re.I)
        if not g:
            return None
        mod, rest = int(g.group(2)), g.group(1)
    con = {}
    for chunk in re.split(r'\s+or\s+', rest):
        c = chunk.strip()
        k = None
        for key, pat in RAY:
            if re.search(pat + r'$', c, re.I):
                k = key
                break
        if k is None or k in con:
            return None
        h = re.match(r'(\w+)\s+plus\s+', c, re.I)
        v = 0
        if h:
            w = h.group(1).lower()
            v = int(w) if w.isdigit() else NUM.get(w)
            if v is None:
                return None
        head = re.sub(r'^(?:\w+\s+plus\s+)?(?:the sum of\s+)?(?:the\s+)?elements\s+', '',
                      c, flags=re.I)
        if not re.fullmatch(dict(RAY)[k], head, re.I):
            return None
        con[k] = v % mod
    if not con or W < 1:
        return None
    if trans and 'ne' in con:
        return None                # the northeast ray would point into unwritten slices
    if trans:
        con = {('north' if x == 'west' else 'west' if x == 'north' else x): y
               for x, y in con.items()}
    return {'W': W, 'alpha': alpha, 'mod': mod, 'con': con, 'trans': trans, 'frac': 1}


build = transfer52.build
matvec = transfer52.matvec
terms = transfer52.terms
threshold = transfer52.threshold
