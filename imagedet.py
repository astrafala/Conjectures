#!/usr/bin/env python3
"""The subset construction shared by the image-counting engines.

Several Hardin families count the IMAGE of a map on arrays -- how many different derived
arrays arise as the underlying array runs over its values -- rather than the arrays
themselves. Two underlying arrays with the same derived array must be counted once, so the
count is not a walk count on the underlying arrays.

It becomes one after determinising. The derived row is decided by a bounded window of
consecutive underlying rows, so that window is the state of a nondeterministic machine whose
OUTPUT is the derived array, and the distinct outputs are the paths of its determinisation,
whose states are the SETS of windows still consistent with the output emitted so far.

`build` takes the machine and returns the determinised digraph:

    starts   the windows the machine may begin in
    nexts    the underlying rows that may be read
    step     step(window, row) -> (emitted, new window), or None if the row may not follow
    final    final(window) -> the row emitted with nothing below, or None if the family
             emits nothing at the end

and gives back `(adj, start, end, S)` in the shape the rest of the machinery expects: `adj`
lists one target per emitted row (repeats are deliberate -- two different outputs may leave
the machine in the same set), `start` is the indicator of the initial set, and `end` counts
the distinct final rows each set admits, or is all-ones when the family has no final emission.
"""


def build(starts, nexts, step, final, cap=20000):
    states, index, adj, end = [], {}, [], []

    def sid(s):
        i = index.get(s)
        if i is None:
            i = index[s] = len(states)
            states.append(s); adj.append([]); end.append(1)
        return i

    sid(frozenset(starts))
    qi = 0
    while qi < len(states):
        s = states[qi]
        i = qi
        qi += 1
        groups, finals = {}, set()
        for el in s:
            if final is not None:
                finals.add(final(el))
            for x in nexts:
                r = step(el, x)
                if r is None:
                    continue
                b, nel = r
                groups.setdefault(b, set()).add(nel)
        if final is not None:
            end[i] = len(finals)
        for b, tgt in groups.items():
            adj[i].append(sid(frozenset(tgt)))
            if len(states) > cap:
                return None
    S = len(states)
    start = [0] * S
    start[0] = 1
    return adj, start, end, S
