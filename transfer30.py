#!/usr/bin/env python3
"""`Number of (n+1) X (K+1) 0..m arrays COLORED WITH <a statistic> of each 2 X 2 subblock.'

The $2\\times2$ subblocks of an $(n+1)\\times(K+1)$ array form an $n\\times K$ grid, and
giving each the value of a statistic of its four entries colours that grid. ``Coloured with''
asks for a PROPER colouring: neighbouring subblocks, horizontally and vertically, must get
different values. The reading is fixed by the entries' own terms rather than guessed --- for
the upper median over $0..2$ the $2\\times2$, $2\\times3$ and $3\\times3$ arrays give $81$,
$294$ and $722$, which are exactly the counts with horizontal and vertical neighbours and
nothing else; adding the diagonal neighbours would give $0$ at $3\\times3$, and imposing no
condition would give $729$.

The colour of a subblock is decided by two consecutive rows, and the vertical condition
compares two consecutive subblock rows, so the state is the PAIR of consecutive array rows;
one step appends a row, which fixes a new subblock row and compares it with the old one. An
$(n+1)$-row array is a walk of $n-1$ steps, so $a(n)=\\iota^\\top M^{n-1}\\tau$ with both
vectors all-ones over the pairs whose own subblock row is properly coloured.
"""
import re
from itertools import product

import namecanon
import transfer17

STATW = r'(?:the\s+)?(maximum|minimum|upper median|lower median)'
NAME = re.compile(
    r'Number of \(\s*n\s*\+\s*(\d+)\s*\)\s*X\s*\(?\s*(\d+)(?:\s*\+\s*(\d+))?\s*\)?\s*'
    r'0\.\.(\d+)\s+arrays\s+colored with\s+(.*?)\s+(?:of|in)\s+(?:each|every)\s+'
    r'2\s*X\s*2 subblock\s*\.?\s*$', re.I)


def _signed(s):
    parts = re.split(r'\s+(plus|minus)\s+', s)
    if len(parts) % 2 == 0:
        return None
    out, sign = {}, 1
    for i, tok in enumerate(parts):
        if i % 2:
            sign = 1 if tok == 'plus' else -1
            continue
        m = re.fullmatch(STATW, tok.strip())
        if not m or m.group(1) in out:
            return None
        out[m.group(1)] = sign
    return out or None


def _colour(s):
    """('set', None) or ('lin', {stat: coefficient}) or None"""
    s = re.sub(r'\s+', ' ', s.strip().lower())
    if s == 'the sets of distinct values':
        return ('set', None)
    if s == 'the upper median value':
        return ('lin', {'upper median': 1})
    if s == 'the sum of the upper and lower median values':
        return ('lin', {'upper median': 1, 'lower median': 1})
    m = re.fullmatch(r'the sum of the (\w+) and (?:the )?(\w+) values?', s)
    if m and m.group(1) in ('maximum', 'minimum') and m.group(2) in ('maximum', 'minimum') \
            and m.group(1) != m.group(2):
        return ('lin', {m.group(1): 1, m.group(2): 1})
    m = re.fullmatch(r'the difference of ' + STATW + r' and ' + STATW, s)
    if m and m.group(1) != m.group(2):
        return ('lin', {m.group(1): 1, m.group(2): -1})
    e = _signed(s)
    return ('lin', e) if e else None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn)])\s*[xX]\s*(?=[\dn(])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    d = int(m.group(1))
    W = int(m.group(2)) + (int(m.group(3)) if m.group(3) else 0)   # the array's width
    alpha = int(m.group(4))
    if d != 1 or W < 2 or alpha < 1:
        return None
    col = _colour(m.group(5))
    if col is None:
        return None
    return {'K': W - 1, 'alpha': alpha, 'kind': col[0], 'coef': col[1], 'frac': 1}


def build(p, cap=40000):
    K, A, kind, coef = p['K'], p['alpha'] + 1, p['kind'], p['coef']
    W = K + 1                                    # K subblocks across, so W cells across
    if A ** W > 20 * cap:
        return None
    key = ('minimum', 'lower median', 'upper median', 'maximum')
    cf = None if kind == 'set' else [coef.get(k, 0) for k in key]
    rows = list(product(range(A), repeat=W))

    def colour(q):
        if kind == 'set':
            return frozenset(q)
        s = sorted(q)
        return cf[0] * s[0] + cf[1] * s[1] + cf[2] * s[2] + cf[3] * s[3]

    def crow(r, s):
        return tuple(colour((r[j], r[j + 1], s[j], s[j + 1])) for j in range(K))

    pair, ok = {}, []
    for i, r in enumerate(rows):
        for j, s in enumerate(rows):
            c = crow(r, s)
            if any(c[t] == c[t + 1] for t in range(K - 1)):
                continue
            pair[(i, j)] = c
            ok.append((i, j))
            if len(ok) > cap:
                return None
    if not ok:
        return None
    index = {k: n for n, k in enumerate(ok)}
    bysecond = {}
    for (i, j) in ok:
        bysecond.setdefault(i, []).append(j)
    adj = []
    for (i, j) in ok:
        c = pair[(i, j)]
        row = []
        for t in bysecond.get(j, ()):
            c2 = pair[(j, t)]
            if all(x != y for x, y in zip(c, c2)):
                row.append(index[(j, t)])
        adj.append(row)
    return ok, adj


terms = transfer17.terms
threshold = transfer17.threshold
