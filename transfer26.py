#!/usr/bin/env python3
"""The Hardin `... maps' families: counting the IMAGE of a map, not its domain.

Name shape:
    <Family> maps: number of n X W binary arrays indicating the locations of corresponding
    elements <condition> in a random 0..m n X W array

and the same with the array written W X n. The families are Hilltop (``not exceeded by any
... neighbor''), Unmatched value (``not equal to any''), Unchanging value (``unequal to no'',
i.e. equal to every), Majority value (``equal to at least half of''), Equals one, Equals two,
and Sum of neighbor (``equal to the sum mod k of'').

What is counted is not the arrays: it is how many DIFFERENT indicator arrays arise as the
$0..m$ array runs over all of its values. That is the size of the image of a map, and an image
is not a walk count in the obvious graph -- two different $0..m$ arrays with the same indicator
must be counted once. The standard cure is the subset construction. Reading the array one row
at a time, the indicator of row $i$ is decided by rows $i-1,i,i+1$, so the pair of the last two
rows read is a state of a nondeterministic machine whose OUTPUT is the indicator array; the
distinct outputs are the paths of its determinisation, whose states are the sets of pairs still
consistent with the indicator emitted so far. Those sets are generated from the start set
outward, and in this family there are few of them.

The last row's indicator is emitted with no row below it, so it is not a step of the walk but a
count attached to the state the walk stops in: the number of distinct final indicator rows the
state admits. That is the vector tau below, and it is not the all-ones vector.
"""
import re
from itertools import product

import namecanon

CLASS = {'horizontal': [(0, -1), (0, 1)],
         'vertical': [(-1, 0), (1, 0)],
         'diagonal': [(-1, -1), (1, 1)],
         'antidiagonal': [(-1, 1), (1, -1)],
         'king-move': [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]}

FAM = ('Hilltop', 'Unmatched value', 'Unchanging value', 'Majority value',
       'Equals one', 'Equals two', 'Sum of neighbor')

NAME = re.compile(
    r'(' + '|'.join(FAM) + r') maps:\s*number of\s+'
    r'(?:n\s*X\s*(\d+)|(\d+)\s*X\s*n)\s+binary arrays'
    r'\s+indicating the locations of corresponding elements\s+(.*?)\s+in a random\s+'
    r'0\.\.(\d+)\s+.*$', re.I)

BODY = {'hilltop': r'not exceeded by any',
        'unmatched value': r'not equal to any',
        'unchanging value': r'unequal to no',
        'majority value': r'equal to at least half of their',
        'equals one': r'equal to exactly one of their',
        'equals two': r'equal to exactly two of their',
        'sum of neighbor': r'equal to the sum mod \d+ of their'}


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'(?<=[\dn])\s*[xX]\s*(?=[\dn])', ' X ', re.sub(r'\s+', ' ', nm)).strip()
    m = NAME.search(nm)
    if not m:
        return None
    fam = m.group(1).lower()
    W = int(m.group(2) or m.group(3))
    walk = 'rows' if m.group(2) else 'cols'
    body = m.group(4).lower()
    alpha = int(m.group(5))
    head = re.match(BODY[fam], body)
    if not head:
        return None
    tail = body[head.end():]
    words = re.findall(r'antidiagonal|king-move|horizontal|vertical|diagonal', tail)
    left = re.sub(r'antidiagonal|king-move|horizontal|vertical|diagonal', ' ', tail)
    left = re.sub(r'\b(and|or|their|neighbou?rs?)\b|,|\s+', '', left)
    if not words or left:
        return None
    D = set()
    for w in words:
        D.update(CLASS[w])
    if walk == 'cols':
        D = {(b, a) for a, b in D}
    mod = None
    if fam == 'sum of neighbor':
        mod = int(re.search(r'sum mod (\d+)', body).group(1))
    if W < 1 or alpha < 1:
        return None
    return {'fam': fam, 'W': W, 'dirs': sorted(D), 'alpha': alpha, 'mod': mod, 'frac': 1}


def _holds(fam, mod, v, nb):
    if fam == 'hilltop':
        return all(u <= v for u in nb)
    if fam == 'unmatched value':
        return all(u != v for u in nb)
    if fam == 'unchanging value':
        return all(u == v for u in nb)
    if fam == 'majority value':
        return 2 * sum(1 for u in nb if u == v) >= len(nb)
    if fam == 'equals one':
        return sum(1 for u in nb if u == v) == 1
    if fam == 'equals two':
        return sum(1 for u in nb if u == v) == 2
    return v == sum(nb) % mod


def build(p, cap=20000):
    W, A, fam, mod = p['W'], p['alpha'] + 1, p['fam'], p['mod']
    D = set(map(tuple, p['dirs']))
    if A ** W > 40 * cap:
        return None
    rows = list(product(range(A), repeat=W))

    def brow(prev, cur, nxt):
        out = []
        for j in range(W):
            nb = []
            for (di, dj) in D:
                jj = j + dj
                if not 0 <= jj < W:
                    continue
                line = prev if di < 0 else (cur if di == 0 else nxt)
                if line is None:
                    continue
                nb.append(line[jj])
            out.append(1 if _holds(fam, mod, cur[j], nb) else 0)
        return tuple(out)

    states, index, adj, fin = [], {}, [], []

    def sid(s):
        i = index.get(s)
        if i is None:
            i = index[s] = len(states)
            states.append(s); adj.append([]); fin.append(0)
        return i

    sid(frozenset((None, r) for r in rows))
    qi = 0
    while qi < len(states):
        s = states[qi]
        i = qi
        qi += 1
        groups, finals = {}, set()
        for (p0, c) in s:
            finals.add(brow(p0, c, None))
            for x in rows:
                groups.setdefault(brow(p0, c, x), set()).add((c, x))
        fin[i] = len(finals)
        for b, tgt in groups.items():
            adj[i].append(sid(frozenset(tgt)))
            if len(states) > cap:
                return None
    S = len(states)
    start = [0] * S
    start[0] = 1
    return adj, start, fin, S


matvec = __import__('transfer19').matvec
terms = __import__('transfer19').terms
threshold = __import__('transfer19').threshold
