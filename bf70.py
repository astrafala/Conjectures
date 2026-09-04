#!/usr/bin/env python3
"""Independent brute force for the symmetric sum-zero matrices.

Symmetric matrices are written out entry by entry over the entry's own range and tested by its
own words: every 2 X 2 subblock must sum to zero and must have an allowed number of distinct
entries. The sequence u of transfer70, the sign pattern, the clique and the state play no part
here -- a partial fill is abandoned only when a subblock it has just completed already fails.
"""
import json, sys
import localentry as LE, transfer70


def count(N, m, D):
    """Symmetric N x N matrices over -m..m with every 2 X 2 subblock summing to zero and having
    a number of distinct entries in D."""
    x = [[0] * N for _ in range(N)]
    cells = [(i, j) for i in range(N) for j in range(i, N)]
    pos = {c: k for k, c in enumerate(cells)}
    n = 0

    def full():
        for i in range(N - 1):
            for j in range(N - 1):
                v = (x[i][j], x[i][j + 1], x[i + 1][j], x[i + 1][j + 1])
                if sum(v) != 0 or len(set(v)) not in D:
                    return False
        return True

    def rec(t):
        nonlocal n
        if t == len(cells):
            n += full()
            return
        i, j = cells[t]
        for v in range(-m, m + 1):
            x[i][j] = x[j][i] = v
            ok = True
            for a in range(max(0, i - 1), i + 1):
                for b in range(max(0, j - 1), j + 1):
                    if a + 1 >= N or b + 1 >= N:
                        continue
                    q = [(a, b), (a, b + 1), (a + 1, b), (a + 1, b + 1)]
                    if all(pos[(min(r, c), max(r, c))] <= t for r, c in q):
                        w = [x[r][c] for r, c in q]
                        if sum(w) != 0 or len(set(w)) not in D:
                            ok = False
                            break
                if not ok:
                    break
            if ok:
                rec(t + 1)
    rec(0)
    return n


def sumzero_direct(N, m):
    """Symmetric N x N matrices over -m..m with every 2 X 2 subblock summing to zero, counted by
    direct enumeration -- the left-hand side of Lemma 1."""
    return count(N, m, set(range(1, 5)))


def sumzero_sequences(N, m):
    """Sequences u_0..u_{N-1} in -m..m all of one parity -- the right-hand side of Lemma 1."""
    t = 0
    for par in (0, 1):
        k = len([v for v in range(-m, m + 1) if (v - par) % 2 == 0])
        t += k ** N
    return t


def lemma1(mmax=3, Nmax=4):
    """Both sides of Lemma 1, counted independently, for small sizes and ranges."""
    bad = []
    for m in range(1, mmax + 1):
        for N in range(1, Nmax + 1):
            a, b = sumzero_direct(N, m), sumzero_sequences(N, m)
            if a != b:
                bad.append((N, m, a, b))
    return bad


def check(anum, steps=4):
    e = LE.get(anum)
    p = transfer70.parse_name(e['name'])
    if not p:
        return anum, 'PARSE-FAIL', None
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    out = [count(N, p['m'], p['D']) for N in range(2, 2 + steps)]
    for k in range(len(out) - 1):
        tail = out[k:]
        for s in range(len(d) - len(tail) + 1):
            if d[s:s + len(tail)] == tail:
                return anum, 'OK', (len(tail), s)
    return anum, 'MISMATCH', (out, d[:6])


if __name__ == '__main__':
    import collections
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer70' and not h.get('FAILS')]
    todo = sys.argv[1:] or [h['anum'] for h in hits]
    c = collections.Counter()
    for a in todo:
        r = check(a)
        c[r[1]] += 1
        if r[1] != 'OK':
            print(*r)
    print(c)
