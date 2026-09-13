#!/usr/bin/env python3
"""n X k and k X n arrays under local difference conditions and lexicographic order.

    Number of 5 X n 0..2 arrays with horizontal differences mod 3 never 1, vertical differences
      mod 3 never -1, and rows and columns lexicographically nondecreasing.
    Number of n X 2 0..2 arrays with horizontal differences mod 3 never 1, vertical differences
      mod 3 never -1, rows lexicographically nondecreasing, and columns lexicographically
      nonincreasing.

`arrlex' carries the lexicographic conditions for a growing HEIGHT. These names grow the WIDTH
as well, and add a local condition on the differences. Both are the same walk once the array is
read line by line along whichever dimension grows: the fixed dimension gives the line length,
one of the two lexicographic conditions compares CONSECUTIVE lines and is local, and the other
compares the k lines running the other way over the whole growth and is carried by one flag per
adjacent pair -- `still equal', or `already decided' with which way. A difference condition is
local either way: within a line, or between consecutive lines.
"""
import re
from itertools import product

HEAD = re.compile(
    r'^\s*Number of (?:(n) ?X ?(\d+)|(\d+) ?X ?(n)) 0\.\.(\d+) arrays with (.*?)\s*\.?\s*$',
    re.I)
MODC = re.compile(r'(horizontal|vertical) differences mod (\d+) never (-?\d+)')
LEXC = re.compile(r'(rows|columns)(?: and (rows|columns))? lexicographically '
                  r'(nondecreasing|nonincreasing)')


def parse_name(nm):
    m = HEAD.match(' '.join(nm.split()))
    if not m:
        return None
    if m.group(1):
        grow, k = 'height', int(m.group(2))
    else:
        grow, k = 'width', int(m.group(3))
    A = int(m.group(5))
    body = ' '.join(m.group(6).lower().split())
    mods, lex = {}, {}
    rest = body
    for mm in MODC.finditer(body):
        mods[mm.group(1)] = (int(mm.group(2)), int(mm.group(3)))
        rest = rest.replace(mm.group(0), '')
    for mm in LEXC.finditer(body):
        for who in (mm.group(1), mm.group(2)):
            if who:
                lex[who] = mm.group(3)
        rest = rest.replace(mm.group(0), '')
    if not lex:
        return None
    if re.sub(r'[,\s]|and', '', rest):
        return None                              # an unread clause: refuse rather than ignore
    if not 1 <= k <= 8 or not 1 <= A <= 4 or (A + 1) ** k > 30000:
        return None
    return {'engine': 'arrline', 'grow': grow, 'k': k, 'A': A, 'mods': mods, 'lex': lex,
            'frac': 1}


def build(p, cap=200000):
    k, A, grow, mods, lex = p['k'], p['A'], p['grow'], p['mods'], p['lex']
    lines = list(product(range(A + 1), repeat=k))
    # the line runs down a column when the width grows, so `vertical' is within the line then
    within = 'horizontal' if grow == 'height' else 'vertical'
    between = 'vertical' if grow == 'height' else 'horizontal'
    # the lex condition on consecutive lines, and the one carried by flags
    seq = 'rows' if grow == 'height' else 'columns'
    cross = 'columns' if grow == 'height' else 'rows'
    if seq not in lex or cross not in lex:
        return None
    sdir, cdir = lex[seq], lex[cross]

    def okwithin(L):
        if within not in mods:
            return True
        M, d = mods[within]
        return all((L[j + 1] - L[j]) % M != d % M for j in range(k - 1))

    def okbetween(prev, cur):
        if between not in mods:
            return True
        M, d = mods[between]
        return all((cur[j] - prev[j]) % M != d % M for j in range(k))

    def okseq(prev, cur):
        if prev is None:
            return True
        return list(cur) >= list(prev) if sdir == 'nondecreasing' else list(cur) <= list(prev)

    want_less = cdir == 'nondecreasing'

    def colstep(flags, cur):
        out = 0
        for j in range(k - 1):
            b = flags >> j & 1
            if b:
                out |= 1 << j
                continue
            if cur[j] == cur[j + 1]:
                continue
            good = cur[j] < cur[j + 1] if want_less else cur[j] > cur[j + 1]
            if not good:
                return None
            out |= 1 << j
        return out

    ok = [L for L in lines if okwithin(L)]
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    start = []
    for L in ok:
        f = colstep(0, L)
        if f is not None:
            start.append(sid((L, f)))
    adj = {}
    i = 0
    while i < len(states):
        prev, f = states[i]
        out = []
        for cur in ok:
            if not okseq(prev, cur) or not okbetween(prev, cur):
                continue
            nf = colstep(f, cur)
            if nf is None:
                continue
            out.append(sid((cur, nf)))
            if len(states) > cap:
                return None
        adj[i] = out
        i += 1
    return {'adj': adj, 'start': start, 'S': len(states), 'k': k, 'A': A}


def terms(b, N):
    """a(n) = arrays with n lines along the growing dimension."""
    adj, S = b['adj'], b['S']
    vec = [0] * S
    for s in b['start']:
        vec[s] += 1
    out = [0, sum(vec)]
    for _ in range(N - 1):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(vec))
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    last, run = None, 0
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
