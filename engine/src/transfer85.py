#!/usr/bin/env python3
"""Arrays where each value must, or must not, be repeated at exactly its own distance.

    Number of n X 1 0..3 arrays with every element value z a city block distance of exactly z
        from another element value z.
    Number of n X 4 1..3 arrays with no element with value z exactly a city block distance of
        z from another element with value z.

The condition ranges over the whole array, but only as far as the value itself: a cell of
value z looks exactly z steps away, and z is at most the largest letter of the alphabet. So
nothing beyond D lines away matters, D being that largest letter, and a cell's verdict is
settled once the line D below it has arrived.

The state is therefore the last D lines together with one bit per cell in them, recording
whether that cell has already found its partner. Adding a line pairs it against the lines it
can still reach, sets the bits it completes, and retires the line that has now seen
everything it will ever see --- keeping it if its bits say what the entry asks and discarding
the walk otherwise.

The reading was pinned against published data before any of this was written. "Another
element value z" includes the element itself when z = 0: a zero is a distance 0 from itself
and so always satisfies the condition. Reading "another" as strictly some other cell gives
0, 1, 1, 3 for A209173 where the entry publishes 1, 2, 5, 12.
"""
import re
from itertools import product

import lumpauto
import namecanon
import transfer19

HEAD = re.compile(
    r'^(?:Number of|number of)\s+(.+?)\s+(\d+)\.\.(\d+)\s+arrays\s+with\s+'
    r'(every|no) element (?:with )?value z (?:exactly )?a city block distance of '
    r'(?:exactly )?z from another element (?:with )?value z\s*\.?\s*$', re.I)
SHAPE = [
    (re.compile(r'^\(n\+(\d+)\) X \(?(\d+)\)?$', re.I), 'rows'),
    (re.compile(r'^n X \(?(\d+)\)?$', re.I), 'rows0'),
    (re.compile(r'^\(?(\d+)\)? X \(n\+(\d+)\)$', re.I), 'cols'),
    (re.compile(r'^\(?(\d+)\)? X n$', re.I), 'cols0'),
]


def _shape(s):
    for rx, kind in SHAPE:
        m = rx.match(s)
        if not m:
            continue
        if kind == 'rows':
            return int(m.group(2)), int(m.group(1)), False
        if kind == 'rows0':
            return int(m.group(1)), 0, False
        if kind == 'cols':
            return int(m.group(1)), int(m.group(2)), True
        return int(m.group(1)), 0, True
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    nm = re.sub(r'(?<=[\dn\)])\s*[xX]\s*(?=[\dn\(])', ' X ', nm)
    m = HEAD.match(nm)
    if not m:
        return None
    sh = _shape(m.group(1).strip())
    if sh is None:
        return None
    L, a, tr = sh
    lo, hi = int(m.group(2)), int(m.group(3))
    if lo < 0 or hi < lo or hi > 4 or L > 4:
        return None
    return {'L': L, 'a': a, 'lo': lo, 'hi': hi, 'every': m.group(4).lower() == 'every',
            'transposed': tr, 'frac': 1}


def build(p, cap=200000):
    L, lo, hi, every = p['L'], p['lo'], p['hi'], p['every']
    D = hi                                    # nothing further than the largest letter
    lines = list(product(range(lo, hi + 1), repeat=L))

    def fresh(line):
        """flags for a new line: a zero is a distance 0 from itself, so it starts satisfied"""
        flags = [v == 0 for v in line]
        for x in range(L):                    # pairs inside the line itself
            for y in range(x + 1, L):
                if line[x] == line[y] and (y - x) == line[x]:
                    flags[x] = flags[y] = True
        return tuple(flags)

    def decide(flags):
        got = any(flags)
        return (all(flags) if every else not got) if every else not got

    def keep(flags):
        return all(flags) if every else not any(flags)

    def step(buf, line):
        """buf is a tuple of (line, flags); pair the new line against it"""
        nf = list(fresh(line))
        out = []
        for d, (bl, bf) in enumerate(buf):    # buf[-1] is one line back
            gap = len(buf) - d
            bfl = list(bf)
            for x in range(L):
                for y in range(L):
                    if bl[x] == line[y] and gap + abs(y - x) == bl[x]:
                        bfl[x] = True
                        nf[y] = True
            out.append((bl, tuple(bfl)))
        out.append((line, tuple(nf)))
        return out

    index, states, adj = {}, [], []

    def sid(key):
        i = index.get(key)
        if i is None:
            i = index[key] = len(states)
            states.append(key)
            adj.append([])
        return i

    starts = [sid((((r), fresh(r)),)) for r in lines]
    frontier, seen = list(starts), set(starts)
    while frontier:
        u = frontier.pop()
        buf = states[u]
        for r in lines:
            nb = step(list(buf), r)
            if len(nb) > D:                   # the oldest line has seen all it will see
                bl, bf = nb.pop(0)
                if not keep(bf):
                    continue
            v = sid(tuple(nb))
            if len(states) > cap:
                return None
            adj[u].append(v)
            if v not in seen:
                seen.add(v)
                frontier.append(v)
    S = len(states)
    start = [0] * S
    for i in set(starts):
        start[i] = 1
    # nothing follows, so every line still held must already satisfy the condition
    end = [1 if all(keep(f) for _, f in buf) else 0 for buf in states]
    return lumpauto.lump(adj, start, end)


terms = transfer19.terms
