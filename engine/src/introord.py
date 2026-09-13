#!/usr/bin/env python3
"""Arrays whose new values are introduced in order, from one end or from both.

    Number of 0..5 arrays of length n with no adjacent pair equal to its immediately preceding
      adjacent pair, and new values introduced in 0..5 order.
    Number of length n 0..5 arrays with new values introduced in order from both ends.

"New values introduced in order" is a condition no window can decide -- whether a value may be
used depends on everything before it -- but one counter carries it, since the values arrive in
order: how many of them have been introduced so far.

The first family adds a condition whose reading had to be settled by brute force. "No adjacent
pair equal to its immediately preceding adjacent pair" is NOT "no three equal in a row": the
pairs overlap, and the pair immediately preceding (x_i, x_{i+1}) is (x_{i-2}, x_{i-1}), the one
starting two places back. So the condition forbids a window of four with period two, and it is
vacuous below length four -- which is what the entries' own a(3) says, 5 where the
three-in-a-row reading gives 4.

The second family is the interesting one. Introducing new values in order from BOTH ends says
that every prefix and every suffix has a value set of the form {0,1,...,m}. The prefix half is
the counter above. The suffix half is the same condition on the reversed array, so read left to
right it is the REVERSE of a deterministic automaton -- nondeterministic, but unambiguous, since
each array has exactly one run backwards, and an unambiguous automaton's walk count is still the
number of words. The vertex is (values introduced in the prefix, values still to be introduced
in the suffix, the total), the two ends being tied together by that total: the walk runs from
(0, t) to (t, 0).
"""
import re

PAIR4 = re.compile(
    r'(?i)^Number of 0\.\.(\d+) arrays of length n with no adjacent pair equal to its '
    r'immediately preceding adjacent pair, and new values introduced in 0\.\.(\d+) order'
    r'\s*\.?\s*$')
BOTH = re.compile(
    r'(?i)^Number of length n 0\.\.(\d+) arrays with new values introduced in order from '
    r'both ends\s*\.?\s*$')


def parse_name(nm):
    nm = ' '.join(nm.split())
    m = PAIR4.match(nm)
    if m:
        K = int(m.group(1))
        if K != int(m.group(2)) or K < 1 or K > 9:
            return None
        return {'engine': 'introord', 'kind': 'pair4', 'K': K, 'frac': 1}
    m = BOTH.match(nm)
    if m:
        K = int(m.group(1))
        if K < 1 or K > 12:
            return None
        return {'engine': 'introord', 'kind': 'both', 'K': K, 'frac': 1}
    return None


def build(p, cap=2000000):
    K, kind = p['K'], p['kind']
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    if kind == 'pair4':
        # (the last three values, how many have been introduced). The tail is shorter while the
        # array is starting, because the condition needs four places to bite.
        s0 = sid(((), 0))
        adj = {}
        i = 0
        while i < len(states):
            tail, u = states[i]
            out = []
            for v in range(min(u + 1, K + 1)):
                if len(tail) == 3 and (tail[2], v) == (tail[0], tail[1]):
                    continue                  # the pair two places back repeats
                nt = (tail + (v,))[-3:]
                nu = u + 1 if v == u else u
                out.append(sid((nt, nu)))
            adj[i] = out
            i += 1
            if len(states) > cap:
                return None
        start = [s0]
        end = [1] * len(states)
    else:
        T = K + 1
        starts = []
        adj = {}
        for t in range(1, T + 1):
            starts.append(sid((t, 0, t)))
        i = 0
        while i < len(states):
            t, u, s = states[i]
            out = []
            for v in range(min(u, s - 1) + 1):
                nu = u + 1 if v == u else u
                if nu > t:
                    continue
                for s2 in ([s] if v < s - 1 else [s, s - 1]):
                    out.append(sid((t, nu, s2)))
            adj[i] = out
            i += 1
            if len(states) > cap:
                return None
        start = starts
        end = [1 if (u == t and s == 0) else 0 for (t, u, s) in states]
    import lumpauto
    st = [0] * len(states)
    for j in start:
        st[j] = 1
    wadj, wstart, wend, S = lumpauto.lump(adj, st, end)
    return {'adj': {i: r for i, r in enumerate(wadj)}, 'startv': wstart, 'endv': wend,
            'S': S, 'raw': len(states)}


def terms(b, N):
    """out[n] counts the length-n arrays; out[0] is the empty array."""
    adj, S = b['adj'], b['S']
    vec = list(b['startv'])
    ev = b['endv']
    out = [sum(v * e for v, e in zip(vec, ev))]
    for _ in range(N + 1):
        nxt = [0] * S
        for i, v in enumerate(vec):
            if not v:
                continue
            for j in adj[i]:
                nxt[j] += v
        vec = nxt
        out.append(sum(v * e for v, e in zip(vec, ev)))
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
