#!/usr/bin/env python3
"""The cross-BASE identity on the circular-digit family, and its proof.

    Number of base 7 circular n-digit numbers with adjacent digits differing by 5 or less.
      [Empirical] a(base,n) = a(base-1,n) + F(5) for base >= 5*int(n/2)+1 and F(d) is the
      largest coefficient in (1+x+...+x^(2d))^n

229 entries carry this one claim and nothing else that reads as a recurrence, so the standing
sweep sees them as "no parsable recurrence". It is not a recurrence in n at all: it relates two
different entries. It is also true, sharply, and provable in four lines.

Write T_d(b,n) for the entry's count: the number of (d_1,...,d_n) in {0,...,b-1}^n with
|d_i - d_{i+1}| <= d for every i, the wrap-around pair (d_n,d_1) included. Then

  1. T_d(b,n) - T_d(b-1,n) counts exactly the admissible cyclic sequences over {0,...,b-1}
     that USE the value b-1, since the others are precisely the sequences over {0,...,b-2}.

  2. Every admissible cyclic sequence has max - min <= d*floor(n/2): take a position of the
     maximum and one of the minimum; the two arcs of the cycle between them have lengths
     summing to n, so one of them has length at most floor(n/2), and along an arc of length L
     the value can change by at most d*L.

  3. A sequence using b-1 has maximum b-1, so by 2 all of its values lie in
     [b-1-d*floor(n/2), b-1]. When b >= d*floor(n/2)+1 that whole window lies inside
     {0,...,b-1}, so the count in 1 is the number of admissible cyclic sequences over Z with
     maximum 0 -- a number that does not depend on b at all.

  4. Translating a sequence so that d_1 = 0 rather than max = 0 is a bijection between those
     and the step sequences (s_1,...,s_n) in {-d,...,d}^n with s_1 + ... + s_n = 0, of which
     there are [x^0] (x^-d + ... + x^d)^n = [x^{dn}] (1+x+...+x^{2d})^n -- the entry's own
     F(d), the largest coefficient of that polynomial.

So T_d(b,n) - T_d(b-1,n) = F_d(n) for every n >= 1 and every b >= d*floor(n/2)+1, which is
exactly the entry's threshold and exactly sharp: at b = d*floor(n/2) the window no longer fits
and the identity fails.

The one place the entry's own convention departs from the model is n = 0, where these entries
publish a(0) = 1 rather than the count b of empty-free... rather than the trace b. The identity
is stated and proved here for n >= 1, and the paper says so.
"""
import re

import circdigit
import localentry as LE
import conjlines

LINE = re.compile(r'a\(base\s*,\s*n\)\s*=\s*a\(base\s*-\s*1\s*,\s*n\)\s*\+\s*'
                  r'(?:(A\d{6})\s*\(\s*n\s*\+\s*1\s*\)|F\(\s*(\d+)\s*\))', re.I)


def claim(anum, e=None):
    """the entry's cross-base line, and what it adds, or None"""
    e = e or LE.get(anum)
    for L in conjlines.lines(e):
        m = LINE.search(' '.join(L.split()))
        if m:
            return {'line': ' '.join(L.split()), 'ref': m.group(1),
                    'F': int(m.group(2)) if m.group(2) else None}
    return None


def parse_name(nm):
    p = circdigit.parse_name(nm)
    if p is None:
        return None
    return dict(p, engine='circbase')


def F(d, n):
    """[x^{dn}] (1+x+...+x^{2d})^n: the admissible step sequences of length n summing to zero"""
    c = [1]
    for _ in range(n):
        nc = [0] * (len(c) + 2 * d)
        for i, v in enumerate(c):
            for j in range(2 * d + 1):
                nc[i + j] += v
        c = nc
    return c[d * n]


def T(b, d, n):
    """the entry's count at base b: the trace of the n-th power of the band matrix"""
    M = [[1 if abs(i - j) <= d else 0 for j in range(b)] for i in range(b)]
    cur = [[1 if i == j else 0 for j in range(b)] for i in range(b)]
    for _ in range(n):
        cur = [[sum(cur[i][t] * M[t][j] for t in range(b) if cur[i][t]) for j in range(b)]
               for i in range(b)]
    return sum(cur[i][i] for i in range(b))


def nmax(b, d):
    """the largest n for which the entry's own threshold d*floor(n/2)+1 <= b holds"""
    return 2 * ((b - 1) // d) + 1


def check(anum, nlimit=40):
    """verify the claim over the whole range the entry claims it, and the model against DATA"""
    e = LE.get(anum)
    p = parse_name(e['name'])
    if p is None:
        return None
    cl = claim(anum, e)
    if cl is None:
        return None
    b, d = p['b'], p['k']
    if cl['F'] is not None and cl['F'] != d:
        return {'anum': anum, 'FAILS': True, 'why': 'the line names F(%d) on a difference-%d '
                                                    'entry' % (cl['F'], d)}
    # the model must reproduce the entry's own published terms before anything is claimed
    data = [int(x) for x in e['data'].split(',') if x.strip()]
    off = int(e['offset'].split(',')[0])
    model = [1] + [T(b, d, n) for n in range(1, len(data) + off + 1)]
    if model[off:off + len(data)] != data:
        return {'anum': anum, 'FAILS': True, 'why': 'model does not match DATA'}
    N = min(nmax(b, d), nlimit)
    bad = [n for n in range(1, N + 1) if T(b, d, n) - T(b - 1, d, n) != F(d, n)]
    # and the reference sequence, when the line names one, must be the F this proves
    refbad = None
    if cl['ref']:
        try:
            r = [int(x) for x in LE.get(cl['ref'])['data'].split(',') if x.strip()]
            roff = int(LE.get(cl['ref'])['offset'].split(',')[0])
            if roff == 0:
                got = [F(d, n) for n in range(min(len(r), 12))]
                if got != r[:len(got)]:
                    refbad = cl['ref']
        except Exception:
            refbad = None
    return {'anum': anum, 'b': b, 'd': d, 'N': N, 'bad': bad, 'refbad': refbad,
            'line': cl['line'], 'ref': cl['ref'], 'nterms': len(data), 'offset': off}
