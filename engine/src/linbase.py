#!/usr/bin/env python3
"""The cross-BASE identity on the linear digit-string family, both of its clauses.

    Number of base 11 n-digit numbers with adjacent digits differing by two or less.
      [Empirical] a(base,n)=a(base-1,n)+5^(n-1) for base>=2n-1;
                  a(base,n)=a(base-1,n)+5^(n-1)-2 when base=2n-2.

Same shape as `circbase' one dimension simpler, and with a second clause that is the more
interesting half. Write L_d(b,n) for the number of (d_1,...,d_n) in {0,...,b-1}^n with
|d_i - d_{i+1}| <= d for every i -- no wrap-around this time. Leading zeros are counted: the
entry's a(1) is b.

  1. L_d(b,n) - L_d(b-1,n) counts the admissible strings over {0,...,b-1} that USE the value
     b-1, since the rest are exactly the strings over {0,...,b-2}.
  2. Every admissible string has max - min <= d(n-1), and translation acts freely on the
     admissible strings over Z with each orbit containing exactly one string with maximum 0
     and exactly one with d_1 = 0. The latter are the step vectors in {-d,...,d}^(n-1), so
     there are (2d+1)^(n-1) orbits.
  3. A string counted in 1 has maximum b-1, so it is the translate of an orbit representative
     with maximum 0 whose RANGE is at most b-1. When b >= d(n-1)+1 every orbit qualifies and
     the difference is (2d+1)^(n-1).
  4. When b = d(n-1) exactly, the orbits of range d(n-1) are excluded and no others. An orbit
     has range d(n-1) only if the walk from its minimum to its maximum uses all n-1 steps in
     one direction at full size, so there are exactly TWO of them -- all steps +d and all
     steps -d. The difference is (2d+1)^(n-1) - 2.

Clause 4 is the entry's second clause, and the -2 is those two monotone strings.
"""
import re

import conjlines
import localentry as LE

WORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
        'eight': 8, 'nine': 9, 'ten': 10}
_D = r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten)'

NAMES = (
    re.compile(r'(?i)^Number of base[- ](\d+) n-digit numbers with adjacent digits differing '
               r'by ' + _D + r' or less\s*\.?\s*$'),
    re.compile(r'(?i)^Number of strings over a (\d+) symbol alphabet with adjacent symbols '
               r'differing by ' + _D + r' or less\s*\.?\s*$'),
)

LINE = re.compile(
    r'a\(base\s*,\s*n\)\s*=\s*a\(base\s*-\s*1\s*,\s*n\)\s*\+\s*(\d+)\^\(n-1\)'
    r'[^;]*;\s*a\(base\s*,\s*n\)\s*=\s*a\(base\s*-\s*1\s*,\s*n\)\s*\+\s*(\d+)\^\(n-1\)\s*-\s*'
    r'(\d+)', re.I)


def _num(t):
    t = t.lower()
    return int(t) if t.isdigit() else WORD[t]


def parse_name(nm):
    nm = ' '.join(nm.split())
    for rx in NAMES:
        m = rx.match(nm)
        if m:
            b, d = int(m.group(1)), _num(m.group(2))
            if b < 2 or b > 60 or d < 1:
                return None
            return {'engine': 'linbase', 'b': b, 'd': d, 'frac': 1}
    return None


def claim(anum, e=None):
    e = e or LE.get(anum)
    for L in conjlines.lines(e):
        t = ' '.join(L.split())
        m = LINE.search(t)
        if m:
            return {'line': t, 'k': int(m.group(1)), 'k2': int(m.group(2)),
                    'minus': int(m.group(3))}
    return None


def Lcount(b, d, n):
    """admissible strings of length n over an alphabet of b symbols"""
    if n == 0:
        return 1
    v = [1] * b
    for _ in range(n - 1):
        w = [0] * b
        for u in range(b):
            if not v[u]:
                continue
            lo, hi = max(0, u - d), min(b - 1, u + d)
            for t in range(lo, hi + 1):
                w[t] += v[u]
        v = w
    return sum(v)


def check(anum, nlimit=60):
    e = LE.get(anum)
    p = parse_name(e['name'])
    if p is None:
        return None
    cl = claim(anum, e)
    if cl is None:
        return None
    b, d = p['b'], p['d']
    if cl['k'] != 2 * d + 1 or cl['k2'] != 2 * d + 1 or cl['minus'] != 2:
        return {'anum': anum, 'FAILS': True, 'why': 'the line names %d^(n-1) - %d on a '
                                                    'difference-%d entry'
                                                    % (cl['k'], cl['minus'], d)}
    data = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    model = [Lcount(b, d, n) for n in range(len(data) + off + 4)]
    sh = next((s for s in range(0, off + 4) if model[s:s + len(data)] == data), None)
    if sh is None:
        return {'anum': anum, 'FAILS': True, 'why': 'model does not match DATA'}
    if sh != off:
        # the entry's declared offset and the string length its first term counts disagree
        # (A126404 declares offset 1 and opens with the empty string's 1). The claim is stated
        # in the entry's own n, so with the two indexings out of step by one there is no
        # reading of "n" here that can be defended; refuse rather than pick one.
        return {'anum': anum, 'FAILS': True,
                'why': 'the entry offset is %d but its terms start at string length %d'
                       % (off, sh)}
    K = 2 * d + 1
    # clause 1 holds for every n with b >= d(n-1)+1, clause 2 at the single n with b = d(n-1)
    N1 = min((b - 1) // d + 1, nlimit)
    bad1 = [n for n in range(1, N1 + 1)
            if Lcount(b, d, n) - Lcount(b - 1, d, n) != K ** (n - 1)]
    n2 = None
    if b % d == 0 and b // d + 1 <= nlimit:
        n2 = b // d + 1                                   # b = d(n-1)
    bad2 = []
    if n2 and n2 >= 2:
        if Lcount(b, d, n2) - Lcount(b - 1, d, n2) != K ** (n2 - 1) - 2:
            bad2 = [n2]
    return {'anum': anum, 'b': b, 'd': d, 'N': N1, 'n2': n2, 'bad': bad1 + bad2,
            'line': cl['line'], 'nterms': len(data), 'offset': off}
