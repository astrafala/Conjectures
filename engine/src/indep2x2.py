#!/usr/bin/env python3
"""An independent check of the 2 X 2 subblock family.

This program shares no code with any engine. It reads the entry's name with its own grammar,
enumerates every array of the stated shape one cell at a time, tests the stated condition on
each 2 X 2 window directly, and counts. No transfer matrix, no state merging, no recurrence:
just the definition, done the slow way.

That is the whole point. An engine that reads a name wrongly still reproduces its own terms,
so agreement between an engine and itself is no evidence at all about the reading. Agreement
between two programs that share nothing but the English is.

The readings taken here, stated so they can be argued with rather than trusted:

  * the subblock at (i,j) is x00=A[i][j], x01=A[i][j+1], x10=A[i+1][j], x11=A[i+1][j+1];
  * its DIAGONAL elements are x00 and x11, its ANTIDIAGONAL elements x01 and x10;
  * its six EDGE AND DIAGONAL DIFFERENCES are the four edges (00-01, 00-10, 01-11, 10-11)
    together with the two diagonals (00-11, 01-10); the four EDGE DIFFERENCES are the edges
    alone;
  * ADJACENT, inside a subblock, means joined by an edge, not by a diagonal;
  * the PERMANENT of the subblock is x00*x11 + x01*x10.

    python3 src/indep2x2.py [max_cells] [limit]
"""
import itertools
import json
import re
import sys

import localentry as LE

# Many of these entries count a quotient: "Half the number of ...", "1/4 the number of ...".
# Ignoring the divisor makes the brute force disagree by exactly that factor and report three
# perfectly sound papers as wrong, which is what it did before this was added.
DIV = re.compile(r'(?i)^\s*(?:(half|a third|a quarter)|1\s*/\s*(\d+))\s+the number of\b')
_WORD = {'half': 2, 'a third': 3, 'a quarter': 4}

# "(n+1)X(3+1) 0..2", "nX4 0..1", "(n+2)X(2+2) 0..3"
SHAPE = re.compile(r'(?i)(?:^|\s)(\(?n(?:\+(\d+))?\)?)\s*X\s*(?:\((\d+)\+(\d+)\)|(\d+))'
                   r'\s+0\.\.(\d+)\s+arrays?\b')
COND = re.compile(r'(?i)arrays?\s+with\s+(every|no)\s+2\s?X\s?2\s+subblock\s+having\s+'
                  r'(.+?)\s*(?:\(constant-stress[^)]*\))?\s*$')
REL = {'greater than or equal to': lambda a, b: a >= b,
       'less than or equal to': lambda a, b: a <= b,
       'greater than': lambda a, b: a > b,
       'less than': lambda a, b: a < b,
       'equal to': lambda a, b: a == b,
       'unequal to': lambda a, b: a != b,
       'no larger than': lambda a, b: a <= b,
       'no smaller than': lambda a, b: a >= b}
AGG = {'the sum of': sum, 'the maximum of': max, 'the minimum of': min,
       'the absolute difference of': lambda v: abs(v[0] - v[1])}


def _rel(text):
    """the longest relation name that starts `text`, so 'greater than' cannot eat
    'greater than or equal to'"""
    for k in sorted(REL, key=len, reverse=True):
        if text.startswith(k):
            return k, text[len(k):].strip()
    return None, text


def _side(text):
    """an aggregate over one diagonal: returns (function, which) and the rest"""
    for k in sorted(AGG, key=len, reverse=True):
        if text.startswith(k):
            rest = text[len(k):].strip()
            for w, which in (('its diagonal elements', 'd'), ('its antidiagonal elements', 'a')):
                if rest.startswith(w):
                    return (AGG[k], which), rest[len(w):].strip()
            return None, text
    for w, which, f in (('its maximum diagonal element', 'd', max),
                        ('its minimum diagonal element', 'd', min),
                        ('its maximum antidiagonal element', 'a', max),
                        ('its minimum antidiagonal element', 'a', min),
                        ('its diagonal sum', 'd', sum),
                        ('its antidiagonal sum', 'a', sum)):
        if text.startswith(w):
            return (f, which), text[len(w):].strip()
    return None, text


def compile_pred(text):
    """Return f(x00, x01, x10, x11) -> bool for the subblock condition, or None."""
    # The wording often ends with a parenthetical naming the objects being counted --- e.g.
    # "(constant-stress 1 X 1 tilings)" --- which describes the sequence, not the condition.
    # Leaving it in place made this program refuse two hundred entries it can read perfectly
    # well.
    t = ' '.join(re.sub(r'\([^)]*\)', ' ', text).split()).rstrip('. ')
    adj_ne = False
    for tail in (', with no adjacent elements equal', ', and no two adjacent values equal',
                 ', and no two adjacent elements equal'):
        if t.endswith(tail):
            adj_ne, t = True, t[:-len(tail)]
    core = _core(t)
    if core is None:
        return None
    if not adj_ne:
        return core

    def both(a, b, c, d, core=core):
        return core(a, b, c, d) and a != b and a != c and b != d and c != d
    return both


def _core(t):
    if t == 'equal diagonal elements or equal antidiagonal elements':
        return lambda a, b, c, d: a == d or b == c
    if t == 'nonzero determinant':
        return lambda a, b, c, d: a * d - b * c != 0
    if t == 'zero determinant':
        return lambda a, b, c, d: a * d - b * c == 0
    if t == 'distinct edge sums':
        return lambda a, b, c, d: len({a + b, b + d, d + c, c + a}) == 4
    if t == 'at least two equal elements connected horizontally or vertically':
        return lambda a, b, c, d: a == b or c == d or a == c or b == d
    if t == 'zero permanent':
        return lambda a, b, c, d: a * d + b * c == 0
    if t == 'x11-x00 less than x10-x01':
        return lambda a, b, c, d: d - a < c - b
    # A subblock's clockwise edges run 00 -> 01 -> 11 -> 10 -> 00, so its clockwise edge
    # differences are those four steps in that order; the counterclockwise ones are their
    # negatives, so a counterclockwise increase is a clockwise decrease.
    def _cw(a, b, c, d):
        return [b - a, d - b, c - d, a - c]

    m = re.match(r'^(exactly two|two or four|two|three|four) distinct clockwise edge '
                 r'differences$', t)
    if m:
        want = {'exactly two': {2}, 'two or four': {2, 4}, 'two': {2}, 'three': {3},
                'four': {4}}[m.group(1)]
        return lambda a, b, c, d, w=want: len(set(_cw(a, b, c, d))) in w
    if t in ('the number of clockwise edge increases equal to the number of counterclockwise '
             'edge increases',
             'the number of clockwise edge increases equal to the number of clockwise edge '
             'decreases'):
        return lambda a, b, c, d: (sum(x > 0 for x in _cw(a, b, c, d))
                                   == sum(x < 0 for x in _cw(a, b, c, d)))
    m = re.match(r'^sum (\d+)$', t)
    if m:
        k = int(m.group(1))
        return lambda a, b, c, d, k=k: a + b + c + d == k
    m = re.match(r'^its diagonal sum differing from its antidiagonal sum by (\d+)$', t)
    if m:
        k = int(m.group(1))
        return lambda a, b, c, d, k=k: abs((a + d) - (b + c)) == k
    m = re.match(r'^the sum of (the squares of |the absolute values of )?'
                 r'(all six edge and diagonal|the edge) differences (.+)$', t)
    if m:
        how, which, rest = m.group(1) or '', m.group(2), m.group(3)
        rel, rhs = _rel(rest)
        if rel is None or not rhs.isdigit():
            return None
        f, k = REL[rel], int(rhs)
        six = which.startswith('all six')

        def g(a, b, c, d, f=f, k=k, how=how, six=six):
            ds = [a - b, a - c, b - d, c - d] + ([a - d, b - c] if six else [])
            if 'squares' in how:
                ds = [x * x for x in ds]
            elif 'absolute' in how:
                ds = [abs(x) for x in ds]
            return f(sum(ds), k)
        return g
    m = re.match(r'^the absolute values of (all six edge and diagonal|the edge) differences '
                 r'(.+)$', t)
    if m:
        which, rest = m.group(1), m.group(2)
        rel, rhs = _rel(rest)
        if rel is None or not rhs.isdigit():
            return None
        f, k = REL[rel], int(rhs)
        six = which.startswith('all six')

        def h(a, b, c, d, f=f, k=k, six=six):
            ds = [a - b, a - c, b - d, c - d] + ([a - d, b - c] if six else [])
            return all(f(abs(x), k) for x in ds)
        return h
    left, rest = _side(t)
    if left is None:
        return None
    rel, rest = _rel(rest)
    if rel is None:
        return None
    right, rest = _side(rest)
    if right is None or rest:
        return None
    lf, lw = left
    rf, rw = right
    f = REL[rel]

    def cmp2(a, b, c, d, lf=lf, lw=lw, rf=rf, rw=rw, f=f):
        dd, aa = [a, d], [b, c]
        return f(lf(dd if lw == 'd' else aa), rf(dd if rw == 'd' else aa))
    return cmp2


def parse(name):
    """(rows_offset, cols, alpha, quantifier, predicate, divisor) or None"""
    m = SHAPE.search(name)
    c = COND.search(name)
    if not m or not c:
        return None
    dv = DIV.match(name)
    div = 1
    if dv:
        div = _WORD[dv.group(1).lower()] if dv.group(1) else int(dv.group(2))
    add = int(m.group(2) or 0)
    cols = (int(m.group(3)) + int(m.group(4))) if m.group(3) else int(m.group(5))
    alpha = int(m.group(6))
    pred = compile_pred(c.group(2))
    if pred is None:
        return None
    return add, cols, alpha, c.group(1).lower(), pred, div


def count(rows, cols, alpha, every, pred):
    """Every array, one at a time. No shortcuts: that is what makes this independent."""
    tot = 0
    for flat in itertools.product(range(alpha + 1), repeat=rows * cols):
        ok = True
        for i in range(rows - 1):
            for j in range(cols - 1):
                p = pred(flat[i * cols + j], flat[i * cols + j + 1],
                         flat[(i + 1) * cols + j], flat[(i + 1) * cols + j + 1])
                if p != every:
                    ok = False
                    break
            if not ok:
                break
        tot += ok
    return tot


def check(a, max_cells=18):
    """Compare the enumeration with the entry's own first terms. Returns a verdict string."""
    e = LE.get(a)
    got = parse(e['name'])
    if not got:
        return 'not this family, or a condition this program does not read'
    add, cols, alpha, q, pred, div = got
    every = (q == 'every')
    off = int(e['offset'].split(',')[0])
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mine, k = [], 0
    while True:
        rows = off + k + add
        if rows * cols > max_cells or (alpha + 1) ** (rows * cols) > 4 * 10 ** 7:
            break
        n = count(rows, cols, alpha, every, pred)
        if n % div:
            return (f'the entry counts a {div}th of the arrays but the brute force found '
                    f'{n}, which {div} does not divide')
        mine.append(n // div)
        k += 1
        if k >= len(d) or k >= 6:
            break
    if not mine:
        return 'the smallest array is already too big to enumerate'
    if mine == d[:len(mine)]:
        return f'OK on {len(mine)} terms'
    return f'DISAGREES: brute force {mine}, entry {d[:len(mine)]}'


def main():
    max_cells = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    out = json.load(open('indep2x2_done.json')) if __import__('os').path.exists(
        'indep2x2_done.json') else {}
    n = 0
    for a in sorted(roster):
        if a in out:
            continue
        try:
            e = LE.get(a)
        except Exception:
            continue
        if not COND.search(e['name']):
            continue
        out[a] = check(a, max_cells)
        json.dump(out, open('indep2x2_done.json', 'w'), indent=0)
        print(a, out[a], flush=True)
        n += 1
        if n >= limit:
            break
    ok = sum(1 for v in out.values() if v.startswith('OK'))
    bad = [a for a, v in out.items() if v.startswith('DISAGREES')]
    print(f'\n{len(out)} entries in the 2 X 2 family attempted, {ok} independently confirmed, '
          f'{len(bad)} disagreeing')
    for a in bad[:20]:
        print('  ', a, out[a])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
