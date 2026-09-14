#!/usr/bin/env python3
"""How long the n-th iterate of a block substitution is, and why that is C-finite.

    Conjecture: a(n) is the number of letters (0's and 1's) in the n-th iteration of the
    mapping 00->001, 1->000, starting with 00; see A286939.

66 entries outside the roster carry a claim of this shape and no engine had one, because it is
not a recurrence: it says what a sequence COUNTS, and the counting is over the iterates of a
substitution that acts on BLOCKS rather than on letters.

The rule is pinned against the entries' own data rather than assumed: scan left to right, take
the longest left-hand side that matches at the current position and replace it, and copy any
character that matches nothing. Under that rule `00->001, 1->000` from `00` gives
2, 3, 6, 10, 17, 29, 51, 90, 160, 282, 499 and `00->001, 1->011` gives
2, 3, 6, 13, 29, 65, 146, 328, 737, 1656, 3721 -- the published terms of A285665 and A286062.

NOT IN SERVICE: the length is very likely C-finite and this file does NOT prove it.

The plan was the obvious one. The parse of a step's output is not the concatenation of the
parses of the individual images -- a block's image can end mid-block and merge with what
follows -- but the left-hand sides have bounded length L, so at most L-1 characters are ever
pending at a boundary. Take the state to be (unit being rewritten, characters pending before
it); that is a finite set, and feeding a unit's image into the pending buffer and consuming
greedily is a deterministic function of the pair. Measured, it is: over nine levels of
00->001, 1->000 there are eight such states and the map (unit, carry) -> (emitted units,
carry-out) never once disagreed with itself.

**That is not enough, and the check that catches it is asking whether the CHILDREN are
determined too.** They are not: the same parent pair emits children with different carries
depending on what preceded it, 198 disagreements over eleven levels on A285665 and 15 on
A289131 (A286062 happens to be consistent, which is exactly how a partial check misleads). The
reason is that a child's carry belongs to the NEXT level's parse, not to the buffer position it
came out of, and that carry chains across parent boundaries. Adding the next level's carry to
the state does not close the recursion -- it introduces the level after that.

So this is an HD0L system rather than a substitution, and the length sequence of an HD0L system
is C-finite for reasons that need the theory, not a transfer matrix assembled by inspection.
Three unsound certificates in one day would be careless; this one is left refusing.

What IS settled and is worth keeping: the rule the entries mean. Scan left to right, take the
longest left-hand side that matches, copy any character that matches nothing. Pinned against
the published data of two families -- 00->001, 1->000 gives 2, 3, 6, 10, 17, 29, 51, 90, 160,
282, 499 and 00->001, 1->011 gives 2, 3, 6, 13, 29, 65, 146, 328, 737, 1656, 3721, which are
A285665 and A286062 term for term. `iterate` below is that rule and it is correct; 66 entries
outside the roster carry a claim of this shape.
"""

IN_SERVICE = False
import re

MAP = re.compile(r'\b([01]{1,4})\s*->\s*([01]{1,6})')
START = re.compile(r'starting with\s+([01]{1,6})', re.I)
ITER = re.compile(r'number of letters[^.]*?\bin the n-th iterat\w*\b', re.I)


def read_claim(line):
    """the substitution and its seed, from the entry's own conjecture line"""
    t = ' '.join(line.split())
    if not ITER.search(t):
        return None
    rules = dict(MAP.findall(t))
    m = START.search(t)
    if not rules or not m:
        return None
    return {'rules': rules, 'start': m.group(1)}


def iterate(rules, start, n):
    """letter counts of the first n+1 iterates, by direct simulation"""
    keys = sorted(rules, key=len, reverse=True)
    s = start
    out = [len(s)]
    for _ in range(n):
        r, i = [], 0
        while i < len(s):
            for k in keys:
                if s.startswith(k, i):
                    r.append(rules[k])
                    i += len(k)
                    break
            else:
                r.append(s[i])
                i += 1
        s = ''.join(r)
        out.append(len(s))
    return out


def _units(rules):
    keys = sorted(rules, key=len, reverse=True)
    alph = sorted({c for k in rules for c in k} | {c for v in rules.values() for c in v})
    return keys, alph


def _consume(buf, keys, final=False):
    """greedily take units off the front of buf; returns (units, remainder).

    Stops while fewer than max-key-length characters remain unless `final`, because a shorter
    tail could still be the start of a longer left-hand side once more arrives -- that is
    exactly the boundary effect that makes the naive blockwise parse wrong.
    """
    L = max(len(k) for k in keys)
    out, i = [], 0
    while i < len(buf) and (final or len(buf) - i >= L):
        for k in keys:
            if buf.startswith(k, i):
                out.append(k)
                i += len(k)
                break
        else:
            out.append(buf[i])
            i += 1
    return out, buf[i:]


def _parse(buf, keys, final=False):
    """greedy units off the front of buf, each tagged with the pending seen at its left edge"""
    L = max(len(k) for k in keys)
    out, i = [], 0
    while i < len(buf) and (final or len(buf) - i >= L):
        pend = buf[:i] and ''            # the tag is the buffer state, recorded by the caller
        for k in keys:
            if buf.startswith(k, i):
                out.append(k)
                i += len(k)
                break
        else:
            out.append(buf[i])
            i += 1
    return out, buf[i:]


def build(p, cap=20000):
    """the substitution on states (unit, pending-in), and its matrix.

    A state's expansion is found by feeding its pending-in and its image into the greedy parse:
    the units that come out are the children, and what is left pending goes to whatever follows.
    Because the pending-out is a function of the state, the level-(n+1) sequence of states is
    the image of the level-n sequence under a fixed substitution -- so the state counts evolve
    by a fixed matrix and the letter count is a linear functional of them.
    """
    rules, seed = p['rules'], p['start']
    keys = sorted(rules, key=len, reverse=True)
    L = max(len(k) for k in keys)

    def image(u):
        return rules.get(u, u)

    def expand(state):
        """(children as states, pending-out)"""
        u, pin = state
        buf = pin + image(u)
        kids, i, pend = [], 0, ''
        while i < len(buf) and len(buf) - i >= L:
            here = buf[:i]
            for k in keys:
                if buf.startswith(k, i):
                    kids.append((k, ''))
                    i += len(k)
                    break
            else:
                kids.append((buf[i], ''))
                i += 1
        return kids, buf[i:]

    # the level-0 sequence: parse the seed, carrying pending along
    seq, pend = [], ''
    buf = seed
    units, rest = _parse(buf, keys, final=True)
    for u in units:
        seq.append((u, ''))
    tail0 = rest

    states, index = [], {}

    def sid(st):
        if st not in index:
            index[st] = len(states)
            states.append(st)
        return index[st]

    for st in seq:
        sid(st)
    i = 0
    rows = []
    while i < len(states):
        kids, pend = expand(states[i])
        rows.append(([sid(k) for k in kids], pend, len(states[i][0])))
        i += 1
        if len(states) > cap:
            return None
    adj = [r[0] for r in rows]
    lens = [len(st[0]) for st in states]
    start = [0] * len(states)
    for st in seq:
        start[index[st]] += 1
    return {'adj': adj, 'startv': start, 'lens': lens, 'S': len(states),
            'states': states, 'rules': rules, 'seed': seed}


def terms(b, N):
    """letter counts of iterates 0..N, from the substitution matrix"""
    v = list(b['startv'])
    out = [sum(c * l for c, l in zip(v, b['lens']))]
    for _ in range(N):
        nv = [0] * b['S']
        for i, c in enumerate(v):
            if not c:
                continue
            for j in b['adj'][i]:
                nv[j] += c
        v = nv
        out.append(sum(c * l for c, l in zip(v, b['lens'])))
    return out
