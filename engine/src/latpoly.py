#!/usr/bin/env python3
"""`-n..n' arrays of FIXED length, counted exactly as a quasi-polynomial in n.

    Number of -n..n arrays x(0..6) of 7 elements with zero sum and no two neighbors equal.
    Number of -n..n arrays of 5 elements with first and second differences also in -n..n.

`ordpoly' counts fixed-length arrays whose condition is decided by the ORDER of the terms.
These are its arithmetic twin: the length is fixed, the alphabet -n..n grows, and the
condition names actual values -- a sum, a difference, a residue -- so no weak ordering
describes it.

They are still exactly countable. Every condition here is a boolean combination of
HOMOGENEOUS linear statements in (x, n): `|x_i| <= n', `|x_{i+1} - x_i| <= n',
`sum x_i = 0', `x_i - x_{i+1} != 0'. So the admissible x for a given n are the lattice
points at height n in a finite union of relatively open rational cones in R^{L+1}, and
a(n) is the Ehrhart quasi-polynomial of that union: degree at most L, and period dividing
the heights of the cones' ray generators.

The period is the whole difficulty, and it is what stopped this family before. It is
DERIVED here, never assumed. Every ray of every cell of the arrangement is cut out by L
independent hyperplanes drawn from the constraint set, so its primitive generator (x*, t*)
has t* dividing the determinant of the x-parts of those L forms (Cramer: the null direction
of the L X (L+1) matrix has t-component equal to that determinant, and the primitive
generator divides it). Let T be the set of those determinants. Each simplicial cone in a
triangulation contributes a denominator prod (1 - z^{t_i}) with t_i in T and at most L+1
factors, so

    A(z) = prod_{d | some t in T} Phi_d(z)^{L+1}

annihilates a, and S = deg A = (L+1) * sum_{d} phi(d). Written as (z^P - 1)^{L+1} with
P = lcm T this would be far larger: for seven elements with no two neighbours equal,
P = 420 gives 3360 where the cyclotomic form gives 144.

A congruence condition -- `adjacent elements not equal modulo three' -- is counted one
residue class at a time. A class is a coset of M*Z^L, and a ray generator primitive in
Z^{L+1} must be scaled by a divisor of M to lie in it, so every t is replaced by M*t and
nothing else changes.

Over the common denominator A the numerator has degree at most S: below S for every cell that
has a ray, since such a cell's numerator collects a fundamental parallelepiped whose heights
are below the sum of its generators' heights, and exactly S for the one cell that has none,
the origin, whose series is the constant 1. So the bound used is z*A, of degree S + 1, and
a(0..S) determine every later term. Taking a(0..S-1) is one short: A189327 counts 3n on the
even n and (5n-1)/2 on the odd from n = 1, but a(0) = 1 rather than 0, and that single point
is the whole difference.

A condition that is NOT homogeneous -- `no element more than one greater than the previous',
`adjacent elements differing by more than one' -- is refused: the region is then a shifted
polyhedron, its counting function is quasi-polynomial only beyond some n_0, and without a
bound on n_0 there is no proof. Those names are read and rejected, not silently skipped.
"""
import re
from itertools import combinations
from math import gcd


FRAC = re.compile(r'^\s*(?:(Half)|(One quarter)|1/(\d+)) the number of\s+', re.I)
HEAD = re.compile(
    r'^\s*Number of (zero-sum )?(-n|0)\.\.n arrays (?:x\(\s*0\s*\.\.\s*(\d+)\s*\) )?'
    r'of (?:length )?(\d+) elements? with(out)? (.*?)\s*\.?\s*$', re.I)
HEAD2 = re.compile(
    r'^\s*Number of (zero-sum )?(-n|0)\.\.n arrays of length (\d+) with(out)? (.*?)'
    r'\s*\.?\s*$', re.I)
HEAD4 = re.compile(
    r'^\s*Number of arrays of (\d+) (nondecreasing )?integers in -n\.\.n with (.*?)\s*\.?\s*$',
    re.I)
HEAD5 = re.compile(
    r'^\s*Number of strings of numbers x\(i\s*=\s*1\.\.(\d+)\) in 0\.\.n with '
    r'(?:sum|Sum_\{i=1\.\.\d+\})\s+(.*?)\s*(?:equal to|=)\s*(.*?)\s*\.?\s*$', re.I)
HEAD6 = re.compile(
    r'^\s*Number of nondecreasing arrangements of (\d+) (nonzero )?numbers in '
    r'(?:-\(n\+(\d+)\)\.\.\(n\+(\d+)\)|(0)\.\.n) with (.*?)\s*\.?\s*$', re.I)
HEAD3 = re.compile(
    r'^\s*Number of length[- ]\(?(\d+(?:\s*\+\s*\d+)?)\)? (-n|0)\.\.n arrays? with(out)? '
    r'(.*?)\s*\.?\s*$', re.I)
ORD = {'zeroth': 0, 'zero': 0, 'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
       '0th': 0, '1st': 1, '2nd': 2, '3rd': 3, '4th': 4, '5th': 5, '6th': 6}
WORDNUM = {'two': 2, 'three': 3, 'four': 4, 'five': 5}


def _unit(L, i):
    v = [0] * L
    v[i] = 1
    return tuple(v)


def _dforms(L, k):
    """the k-th difference forms of a length-L array (k = 0 gives the elements)."""
    cur = [_unit(L, i) for i in range(L)]
    for _ in range(k):
        cur = [tuple(a - b for a, b in zip(cur[i + 1], cur[i])) for i in range(len(cur) - 1)]
    return cur


SEP = re.compile(r',\s*and\s+|\s+and\s+|,\s*')


def _snapshot(p):
    return {k: (list(v) if isinstance(v, list) else v) for k, v in p.items()}


def _split_read(body, L, out):
    """read the condition text as a sequence of clauses.

    `and' both joins clauses and sits inside them -- "not both strictly positive and not
    both strictly negative" is one condition, "zero sum and no two neighbors equal" is two.
    Splitting on every `and' broke the first kind and splitting on none broke the second, so
    the longest clause that the vocabulary knows is taken first and the rest is read the same
    way. A body that cannot be covered is refused whole."""
    body = ' '.join(body.split()).strip().rstrip('.')
    if not body:
        return True
    save = _snapshot(out)
    if _read_clause(body, L, out):
        return True
    for k, v in save.items():
        out[k] = v
    for m in SEP.finditer(body):
        save = _snapshot(out)
        if _read_clause(body[:m.start()], L, out) and _split_read(body[m.end():], L, out):
            return True
        for k, v in save.items():
            out[k] = v
    return False


NUM = {'one': 1, 'two': 2, 'twice': 2, 'three': 3, 'thrice': 3, 'four': 4, 'five': 5,
       'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
NTH = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6,
       'seventh': 7, 'eighth': 8}
_NW = r'(?:one|two|twice|three|thrice|four|five|six|seven|eight|nine|ten)'


def _num(w):
    return NUM.get(w) if w in NUM else (int(w) if w and w.isdigit() else None)


def _windows(L, K):
    return [tuple(range(s, s + K)) for s in range(L - K + 1)] if 1 <= K <= L else []


def _form(L, coef):
    """coef: dict position -> integer coefficient."""
    return tuple(coef.get(i, 0) for i in range(L))


def _side(t):
    """one side of a `having X equal to Y' condition: (multiplier, size, chosen?)."""
    t = t.strip()
    m = re.fullmatch(r'(?:(%s) times )?the sum of (?:some|any) (%s) elements' % (_NW, _NW), t)
    if m:
        return _num(m.group(1)) or 1, _num(m.group(2)), True
    m = re.fullmatch(r'(%s) times (?:some|any) element' % _NW, t)
    if m:
        return _num(m.group(1)), 1, True
    m = re.fullmatch(r'(?:some|any) element', t)
    if m:
        return 1, 1, True
    m = re.fullmatch(r'(?:(%s) times )?the sum of the remaining (%s)' % (_NW, _NW), t)
    if m:
        return _num(m.group(1)) or 1, _num(m.group(2)), False
    m = re.fullmatch(r'(?:(%s) times|(twice|thrice)) the (%s)' % (_NW, '|'.join(NTH)), t)
    if m:
        return _num(m.group(1) or m.group(2)), 1, False
    m = re.fullmatch(r'the (%s)' % '|'.join(NTH), t)
    if m:
        return 1, 1, False
    return None


def _read_window_clause(c, L, out):
    """the conditions that name a window of consecutive terms and a linear relation in it."""
    # some/no pair in every/any consecutive K terms totalling exactly n
    m = re.fullmatch(r'(some|no) pair in (?:every|any|each) consecutive (%s) terms '
                     r'total(?:l)?ing exactly n' % _NW, c)
    if m:
        K = _num(m.group(2))
        if not K or K > L:
            return False
        for W in _windows(L, K):
            pairs = [(_form(L, {i: 1, j: 1}), -1) for a, i in enumerate(W) for j in W[a + 1:]]
            if m.group(1) == 'some':
                out['cl'].append(tuple(((f, tc, 'eq'),) for f, tc in pairs))
            else:
                for f, tc in pairs:
                    out['cl'].append((((f, tc, 'ne'),),))
        out['tex'].append(r'\text{%s pair in a window of %d sums to }n'
                          % (m.group(1), K))
        return True
    # no consecutive K elements summing to more than C*n
    m = re.fullmatch(r'no consecutive (%s) elements summing to more than (?:(\d+)\*)?n' % _NW, c)
    if m:
        K = _num(m.group(1))
        C = int(m.group(2)) if m.group(2) else 1
        if not K or K > L:
            return False
        for W in _windows(L, K):
            f = _form(L, {i: 1 for i in W})
            out['cl'].append((((f, -C, 'le'),),))
        out['tex'].append(r'\text{no %d consecutive terms sum above }%dn' % (K, C))
        return True
    # some/no [m] disjoint pairs/triples in every/any consecutive K terms having the same sum
    m = re.fullmatch(r'(some|no) (?:(%s) )?disjoint (pairs|triples) in '
                     r'(?:any|every|each) consecutive (%s) terms having the same sum'
                     % (_NW, _NW), c)
    if m:
        want, howmany, kind, K = m.group(1), _num(m.group(2)) or 2, m.group(3), _num(m.group(4))
        size = 2 if kind == 'pairs' else 3
        if not K or K > L or howmany * size > K:
            return False
        from itertools import combinations
        for W in _windows(L, K):
            groups = []
            for chosen in combinations(range(len(W)), howmany * size):
                for part in _partitions(list(chosen), size):
                    groups.append([[W[q] for q in blk] for blk in part])
            for g in groups:
                sums = [_form(L, {q: 1 for q in blk}) for blk in g]
                eqs = [tuple(a - b for a, b in zip(sums[0], sums[t]))
                       for t in range(1, len(sums))]
                if want == 'some':
                    pass
                else:
                    out['cl'].append(tuple(((f, 0, 'ne'),) for f in eqs))
            if want == 'some':
                out['cl'].append(tuple(
                    tuple((tuple(a - b for a, b in zip(
                        _form(L, {q: 1 for q in g[0]}), _form(L, {q: 1 for q in g[t]}))), 0, 'eq')
                        for t in range(1, len(g)))
                    for g in groups))
        out['tex'].append(r'\text{%s %d disjoint %s in every window of %d share a sum}'
                          % (want, howmany, kind, K))
        return True
    # every/no K consecutive terms having <side> equal to <side>
    m = re.fullmatch(r'(every|no) (%s) consecutive terms having (.+?) equal to (.+)' % _NW, c)
    if m:
        quant, K = m.group(1), _num(m.group(2))
        A, B = _side(m.group(3)), _side(m.group(4))
        if not K or K > L or A is None or B is None or A[2] == B[2]:
            return False
        (am, asz, _), (bm, bsz, _) = (A, B) if A[2] else (B, A)
        if asz + bsz != K:
            return False
        from itertools import combinations
        for W in _windows(L, K):
            atoms = []
            for S in combinations(W, asz):
                rest = [q for q in W if q not in S]
                coef = {}
                for q in S:
                    coef[q] = coef.get(q, 0) + am
                for q in rest:
                    coef[q] = coef.get(q, 0) - bm
                atoms.append(_form(L, coef))
            if quant == 'every':
                out['cl'].append(tuple(((f, 0, 'eq'),) for f in atoms))
            else:
                for f in atoms:
                    out['cl'].append((((f, 0, 'ne'),),))
        out['tex'].append(r'\text{%s window of %d has a subset with }%d\sum_S = %d\sum_{W-S}'
                          % (quant, K, am, bm))
        return True
    return False


def _partitions(items, size):
    """the ways of splitting `items' into unordered blocks of exactly `size'."""
    if not items:
        yield []
        return
    from itertools import combinations
    first = items[0]
    rest = items[1:]
    for others in combinations(rest, size - 1):
        blk = [first] + list(others)
        left = [q for q in rest if q not in others]
        for tailp in _partitions(left, size):
            yield [blk] + tailp


def _read_clause(c, L, out):
    c = c.lower().strip().rstrip('.')
    if c in ('zero sum', 'sum zero'):
        out['eq'].append(tuple([1] * L))
        out['tex'].append(r'\sum_i x_i = 0')
        return True
    if c == 'nonzero sum':
        out['ne'].append(tuple([1] * L))
        out['tex'].append(r'\sum_i x_i \ne 0')
        return True
    if c in ('no two neighbors equal', 'no two neighbours equal', 'no adjacent equal elements'):
        out['ne'] += _dforms(L, 1)
        out['tex'].append(r'x_i \ne x_{i+1}')
        return True
    if c == 'no two neighbors summing to zero':
        out['ne'] += [tuple(1 if j in (i, i + 1) else 0 for j in range(L)) for i in range(L - 1)]
        out['tex'].append(r'x_i + x_{i+1} \ne 0')
        return True
    if c == 'no two or three adjacent elements summing to zero':
        out['ne'] += [tuple(1 if j in (i, i + 1) else 0 for j in range(L)) for i in range(L - 1)]
        out['ne'] += [tuple(1 if j in (i, i + 1, i + 2) else 0 for j in range(L))
                      for i in range(L - 2)]
        out['tex'].append(r'x_i + x_{i+1} \ne 0\text{ and }x_i + x_{i+1} + x_{i+2} \ne 0')
        return True
    if c == 'no two consecutive zero elements':
        out['nand'] += [(((_unit(L, i), 'eq0'), (_unit(L, i + 1), 'eq0')))
                        for i in range(L - 1)]
        out['tex'].append(r'\text{not both }x_i = 0\text{ and }x_{i+1} = 0')
        return True
    if c == ('adjacent elements not both strictly positive and not both strictly negative'):
        for r in ('gt0', 'lt0'):
            out['nand'] += [((_unit(L, i), r), (_unit(L, i + 1), r)) for i in range(L - 1)]
        out['tex'].append(r'x_i x_{i+1} > 0\text{ for no }i')
        return True
    if c == 'elements alternately strictly increasing and strictly decreasing':
        out['alt'] = True
        out['tex'].append(r'x_0 < x_1 > x_2 < \cdots\text{ or }x_0 > x_1 < x_2 > \cdots')
        return True
    if _read_window_clause(c, L, out):
        return True
    if c == 'not more than two numbers equal':
        d1 = _dforms(L, 1)
        for i in range(L - 2):
            out['nand'].append(((d1[i], 'eq0'), (d1[i + 1], 'eq0')))
        out['tex'].append(r'\text{no three equal}')
        return True
    if c == 'the last equal to n':
        out['cl'].append((((_unit(L, L - 1), -1, 'eq'),),))
        out['tex'].append(r'x_{L-1} = n')
        return True
    m = re.fullmatch(r'each after the second equal to the sum of one or two of the '
                     r'(?:preceding|previous) (%s)' % _NW, c)
    if m:
        j = _num(m.group(1))
        if not j or j > L:
            return False
        for i in range(2, L):
            prev = list(range(max(0, i - j), i))
            conj = []
            for a in prev:
                conj.append(((tuple((1 if q == i else 0) - (1 if q == a else 0)
                                    for q in range(L)), 0, 'eq'),))
            for ai in range(len(prev)):
                for bi in range(ai + 1, len(prev)):
                    a, b = prev[ai], prev[bi]
                    conj.append(((tuple((1 if q == i else 0) - (1 if q == a else 0)
                                        - (1 if q == b else 0) for q in range(L)), 0, 'eq'),))
            out['cl'].append(tuple(conj))
        out['tex'].append(r'x_i\text{ is one of the preceding %d or a sum of two of them}' % j)
        return True
    m = re.fullmatch(r'each no smaller than the sum of its '
                     r'(?:(two|three|four|five|six|seven) )?previous '
                     r'(?:elements|neighbors|neighbours) modulo \(n\+1\)', c)
    if m:
        kk = WORDNUM.get(m.group(1)) if m.group(1) else None
        if kk is not None and not 1 <= kk <= L - 1:
            return False
        out['modge'] = kk                                 # None means the whole prefix
        out['tex'].append(r'x_i \ge \Big(\sum_{j} x_j\Big) \bmod (n+1)')
        return True
    if c in ('equal numbers of elements greater than zero and less than zero',
             'equal numbers greater than zero and less than zero'):
        out['acc'].append({'kind': 'sign', 'rel': 'eq', 'tc': 0})
        out['tex'].append(r'\#\{i: x_i>0\} = \#\{i: x_i<0\}')
        return True
    if c == 'the sum of every adjacent pair being odd':
        out['ncong'] += [(tuple(1 if j in (i, i + 1) else 0 for j in range(L)), 2)
                         for i in range(L - 1)]
        out['tex'].append(r'x_i + x_{i+1}\text{ odd}')
        return True
    if c == 'adjacent elements differing in absolute value':
        out['ne'] += _dforms(L, 1)
        out['ne'] += [tuple(1 if j in (i, i + 1) else 0 for j in range(L)) for i in range(L - 1)]
        out['tex'].append(r'|x_i| \ne |x_{i+1}|')
        return True
    m = re.fullmatch(r'without any two consecutive (increases|decreases)'
                     r'(?: or two consecutive (increases|decreases))?', c)
    if m:
        want = {g for g in m.groups() if g}
        d1 = _dforms(L, 1)
        for w in sorted(want):
            r = 'gt0' if w == 'increases' else 'lt0'
            out['nand'] += [((d1[i], r), (d1[i + 1], r)) for i in range(L - 2)]
        out['tex'].append(r'\text{no two consecutive %s}' % ' or '.join(sorted(want)))
        return True
    m = re.fullmatch(r'without any interior element (greater|less) than both neighbors'
                     r'(?: or (greater|less) than both neighbors)?', c)
    if m:
        want = {g for g in m.groups() if g}
        for w in sorted(want):
            r = 'gt0' if w == 'greater' else 'lt0'
            for i in range(1, L - 1):
                a = tuple(1 if q == i else -1 if q == i - 1 else 0 for q in range(L))
                b = tuple(1 if q == i else -1 if q == i + 1 else 0 for q in range(L))
                out['nand'].append(((a, r), (b, r)))
        out['tex'].append(r'\text{no interior element %s than both neighbours}'
                          % ' or '.join(sorted(want)))
        return True
    m = re.fullmatch(r'zero (\d+)(?:st|nd|rd|th) differences?', c)
    if m:
        j = int(m.group(1))
        if not 1 <= j <= L - 1:
            return False
        out['eq'] += _dforms(L, j)
        out['tex'].append(r'\Delta^{%d}x = 0' % j)
        return True
    m = re.fullmatch(r'(first|second|third|fourth|fifth|\d+(?:st|nd|rd|th)) differences? nonzero',
                     c)
    if m:
        w = m.group(1)
        j = ORD.get(w, int(re.sub(r'\D', '', w)) if re.search(r'\d', w) else None)
        if j is None or not 1 <= j <= L - 1:
            return False
        out['ne'] += _dforms(L, j)
        out['tex'].append(r'\Delta^{%d}x \ne 0' % j)
        return True
    m = re.fullmatch(r'(\d+) never adjacent to n', c)
    if m:
        if int(m.group(1)) != 0:
            return False                                  # only 0 is a homogeneous level
        for i in range(L - 1):
            out['nand'].append(((_unit(L, i), 'eq0'), (_unit(L, i + 1), 'eqn')))
            out['nand'].append(((_unit(L, i), 'eqn'), (_unit(L, i + 1), 'eq0')))
        out['tex'].append(r'\text{no }i\text{ with }\{x_i,x_{i+1}\} = \{0,n\}')
        return True
    if c == 'each element unequal to at least one neighbor':
        d1 = _dforms(L, 1)
        out['ne'] += [d1[0], d1[L - 2]]
        for i in range(1, L - 1):
            out['nand'].append(((d1[i - 1], 'eq0'), (d1[i], 'eq0')))
        out['tex'].append(r'\text{every element differs from some neighbour}')
        return True
    m = re.fullmatch(r'starting with (\d+)', c)
    if m:
        if int(m.group(1)) != 0:
            return False
        out['eq'].append(_unit(L, 0))
        out['tex'].append(r'x_0 = 0')
        return True
    m = re.fullmatch(r'adjacent elements not equal modulo (two|three|four|five|\d+)'
                     r'(?: \(with -\d+ modulo \d+ = \d+\))?', c)
    if m:
        w = WORDNUM.get(m.group(1)) or int(m.group(1))
        if not 2 <= w <= 12:
            return False
        out['ncong'] += [(f, w) for f in _dforms(L, 1)]
        out['tex'].append(r'x_i \not\equiv x_{i+1} \pmod{%d}' % w)
        return True
    m = re.fullmatch(r'nonzero ([a-z]+)(?: and ([a-z]+))? differences?', c)
    if m:
        for g in m.groups():
            if g is None:
                continue
            if g not in ORD:
                return False
            out['ne'] += _dforms(L, ORD[g])
            out['tex'].append(r'\Delta^{%d}x \ne 0' % ORD[g])
        return True
    m = re.fullmatch(r'(?:with )?([a-z0-9]+) through ([a-z0-9]+) differences all nonzero', c)
    if m:
        a, b = m.group(1), m.group(2)
        ja = ORD.get(a, int(a) if a.isdigit() else None)
        jb = ORD.get(b, int(b) if b.isdigit() else None)
        if ja is None or jb is None or not 0 <= ja <= jb <= 8:
            return False
        for j in range(ja, jb + 1):
            out['ne'] += _dforms(L, j)
        out['tex'].append(r'\Delta^{j}x \ne 0\text{ for }%d \le j \le %d' % (ja, jb))
        return True
    if c == 'adjacent element differences also in -n..n':
        out['box'] += _dforms(L, 1)
        out['tex'].append(r'|x_{i+1} - x_i| \le n')
        return True
    m = re.fullmatch(r'((?:first|second|third|fourth|fifth)'
                     r'(?:(?:,| and) (?:first|second|third|fourth|fifth))*)'
                     r' differences also in -n\.\.n', c)
    if m:
        for w in re.findall(r'first|second|third|fourth|fifth', m.group(1)):
            out['box'] += _dforms(L, ORD[w])
        out['tex'].append(r'|\Delta^{j}x| \le n')
        return True
    m = re.fullmatch(r'(first|second) through (second|third|fourth|fifth)'
                     r' differences also in -n\.\.n', c)
    if m:
        for j in range(ORD[m.group(1)], ORD[m.group(2)] + 1):
            out['box'] += _dforms(L, j)
        out['tex'].append(r'|\Delta^{j}x| \le n')
        return True
    return False


def _blank(L, sym):
    return {'L': L, 'shift': 0, 'sym': sym, 'ne': [], 'eq': [], 'nand': [], 'ncong': [], 'alt': False,
            'cl': [], 'acc': [], 'modge': False, 'tex': [],
            'box': [_unit(L, i) for i in range(L)] if sym else [],
            'lo': [] if sym else [_unit(L, i) for i in range(L)],
            'hi': [] if sym else [_unit(L, i) for i in range(L)]}


def _nondec(m, frac):
    """`Number of nondecreasing arrangements of K numbers in -(n+6)..(n+6) with ...'

    The alphabet is a SHIFT of n, so the count is homogeneous in (x, n+c) rather than in
    (x, n). A quasi-polynomial in n+c is one in n with the same annihilator, so only the
    bound the walk uses moves; the derived S does not.
    """
    L = int(m.group(1))
    if not 2 <= L <= 10:
        return None
    c1, c2 = m.group(3), m.group(4)
    if c1 is not None and c1 != c2:
        return None
    sym = c1 is not None
    p = _blank(L, sym)
    p['shift'] = int(c1) if sym else 0
    for f in _dforms(L, 1):
        p['cl'].append((((f, 0, 'ge'),),))
    p['tex'].append(r'x_0 \le x_1 \le \cdots')
    if m.group(2):
        p['ne'] += [_unit(L, i) for i in range(L)]
        p['tex'].append(r'x_i \ne 0')
    if not _split_read(m.group(6), L, p):
        return None
    p['body'] = ' '.join(m.group(6).split())
    p['frac'] = frac
    return p


def _arrays(m, frac):
    """`Number of arrays of K integers in -n..n with ...' --- the same objects, another
    wording, and one no engine read."""
    L = int(m.group(1))
    if not 2 <= L <= 10:
        return None
    p = _blank(L, True)
    if m.group(2):
        for f in _dforms(L, 1):
            p['cl'].append((((f, 0, 'ge'),),))
        p['tex'].append(r'x_0 \le x_1 \le \cdots')
    if not _split_read(m.group(3), L, p):
        return None
    p['body'] = ' '.join(m.group(3).split())
    p['frac'] = frac
    return p


POW = re.compile(r'^i(?:\^(\d+))?\s*\*?\s*x\(i\)$')


def _strings(m, frac):
    """`Number of strings of numbers x(i=1..K) in 0..n with sum i^2*x(i) equal to n*16'."""
    L = int(m.group(1))
    if not 2 <= L <= 12:
        return None
    pm = POW.match(m.group(2).replace(' ', ''))
    if not pm:
        return None
    e = int(pm.group(1) or 1)
    rhs = m.group(3).replace(' ', '')
    rm = re.fullmatch(r'n\*(\d+)|(\d+)\*n|n', rhs)
    if not rm:
        return None
    c = int(rm.group(1) or rm.group(2) or 1)
    p = _blank(L, False)
    w = tuple((i + 1) ** e for i in range(L))
    p['acc'].append({'kind': 'linear', 'w': w, 'tc': -c, 'rel': 'eq'})
    p['tex'].append(r'\sum_i i^{%d}x_i = %dn' % (e, c))
    p['body'] = 'sum i^%d*x(i) equal to %d*n' % (e, c)
    p['frac'] = frac
    return p


def parse_name(nm):
    nm = ' '.join(nm.split())
    frac = 1
    fm = FRAC.match(nm)
    if fm:
        frac = 2 if fm.group(1) else 4 if fm.group(2) else int(fm.group(3))
        nm = 'Number of ' + nm[fm.end():]
    m5 = HEAD5.match(nm)
    if m5:
        return _strings(m5, frac)
    m6 = HEAD6.match(nm)
    if m6:
        return _nondec(m6, frac)
    m4 = HEAD4.match(nm)
    if m4:
        return _arrays(m4, frac)
    m = HEAD.match(nm)
    if m:
        zs, alph, xr, Ls, neg, body = m.groups()
    else:
        m = HEAD2.match(nm)
        if m:
            zs, alph, Ls, neg, body = m.groups()
            xr = None
        else:
            m = HEAD3.match(nm)
            if not m:
                return None
            Ls, alph, neg, body = m.groups()
            zs, xr = None, None
    if neg:
        body = 'without ' + body
    L = sum(int(x) for x in Ls.replace(' ', '').split('+'))
    if not 2 <= L <= 10:
        return None
    if xr is not None and int(xr) != L - 1:
        return None
    sym = alph == '-n'
    p = {'L': L, 'sym': sym, 'ne': [], 'eq': [], 'nand': [], 'ncong': [], 'alt': False,
         'cl': [], 'acc': [], 'modge': False,
         'tex': [], 'box': [_unit(L, i) for i in range(L)] if sym else [],
         'lo': [] if sym else [_unit(L, i) for i in range(L)],
         'hi': [] if sym else [_unit(L, i) for i in range(L)]}
    if not sym and zs:
        pass
    if zs:
        p['eq'].append(tuple([1] * L))
        p['tex'].append(r'\sum_i x_i = 0')
    if not _split_read(body, L, p):
        return None
    if p['modge'] is not False and (p['sym'] or p['cl'] or p['nand'] or p['ncong']
                                    or p['eq'] or p['ne'] or p['alt']):
        # the mod condition is homogeneous in (x, n+1), not in (x, n), so it may not be
        # mixed with a clause that names n itself
        return None
    if not (p['eq'] or p['ne'] or p['nand'] or p['ncong'] or p['alt'] or p['cl']
            or p['modge'] is not False
            or len(p['box']) > L or len(p['hi']) > L):
        return None
    p['body'] = ' '.join(body.split())
    p['frac'] = frac
    p.setdefault('shift', 0)
    return p


# ---------------------------------------------------------------- the bound S

def _det(M):
    """fraction-free (Bareiss) integer determinant."""
    M = [row[:] for row in M]
    n = len(M)
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    M[k], M[i] = M[i], M[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
            M[i][k] = 0
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def _hyperplane_forms(p):
    """the hyperplanes of the arrangement, as (x-form, coefficient of n) pairs.

    A constraint `f(x) + c n <> 0' is the hyperplane f + c t = 0 in R^(L+1); the box gives
    f -+ t, an equality or a difference that must not vanish gives f alone. Guessing all three
    of f, f-t, f+t for every form instead of reading the coefficient off the constraint
    tripled the arrangement and put every larger family over the enumeration budget.
    """
    H = []
    for f in p['box']:
        H.append((f, -1))
        H.append((f, 1))
    for f in p['lo']:
        H.append((f, 0))
    for f in p['hi']:
        H.append((f, -1))
    for f in p['eq'] + p['ne']:
        H.append((f, 0))
    for atoms in p['nand']:
        for f, r in atoms:
            H.append((f, -1 if r == 'eqn' else 0))
    for dnf in p['cl']:
        for conj in dnf:
            for f, tc, _r in conj:
                H.append((f, tc))
    for f, _m in p['ncong']:
        H.append((f, 0))
    for a in p.get('acc', ()):
        if a['kind'] == 'linear':
            H.append((a['w'], a['tc']))
    if p.get('modge', False) is not False:
        # x_i >= s mod (n+1) with s the sum of the named previous entries. Write m = n+1:
        # the box is 0 <= x_i < m, s lies in [0, k(m-1)], and s mod m is s - jm on the piece
        # where jm <= s < (j+1)m. Both the breakpoints and the comparison are homogeneous in
        # (x, m) -- they are NOT in (x, n), which is why this family needed its own parameter.
        L = p['L']
        kk = p['modge']
        for i in range(L):
            st = 0 if kk is None else max(0, i - kk)
            if st >= i:
                continue
            sform = tuple(1 if st <= q < i else 0 for q in range(L))
            dform = tuple((1 if q == i else 0) - (1 if st <= q < i else 0) for q in range(L))
            for j in range(0, i - st + 1):
                H.append((sform, -j))
                H.append((dform, j))
    if p['alt']:
        for f in _dforms(p['L'], 1):
            H.append((f, 0))
    return sorted(set(H))


def _rays(H, L, boxes, eqs):
    """the set T of ray heights, kept to the rays that lie in the region.

    Every ray of every cell of the arrangement is cut out by L of its hyperplanes, and the
    null direction of that L x (L+1) system has t-component the determinant of the x-parts,
    so t* divides it. Taking every such determinant is rigorous but crude: for seven elements
    with no two neighbours equal it gives lcm 420 where the rays that actually meet the region
    give 60. A cell's rays lie in the closure of the region, so a subset whose ray leaves the
    box contributes nothing and is dropped.

    The determinant is computed first and the ray only when it exceeds one, because a ray of
    height one changes nothing and most subsets give one.
    """
    T = {}
    for S in combinations(H, L):
        Mx = [list(v[:L]) for v in S]
        D = _det(Mx)
        if D == 0:
            continue
        if abs(D) == 1:
            T.setdefault(1, set()).add(None)
            continue
        # dx solves Mx.dx = -D * (t-column), by integer Cramer: replacing column j of Mx
        # by the right-hand side and taking determinants keeps everything in Z, where the
        # Fraction elimination this replaced spent most of the run.
        rhs = [-v[L] * D for v in S]
        dx = []
        for j in range(L):
            Mj = [row[:] for row in Mx]
            for i in range(L):
                Mj[i][j] = rhs[i]
            q, r = divmod(_det(Mj), D)
            if r:
                break
            dx.append(q)
        else:
            pass
        if len(dx) < L:
            continue
        dt = D
        if dt < 0:
            dx = [-x for x in dx]
            dt = -dt
        g = dt
        for x in dx:
            g = gcd(g, abs(x))
        if g > 1:
            dx = [x // g for x in dx]
            dt //= g
        if dt <= 0:
            continue
        if any(sum(a * b for a, b in zip(f, dx)) != 0 for f in eqs):
            continue
        good = True
        for f, lo, hi in boxes:
            v = sum(a * b for a, b in zip(f, dx))
            if (lo is not None and v < lo * dt) or (hi is not None and v > hi * dt):
                good = False
                break
        if not good:
            continue
        T.setdefault(dt, set()).add(tuple(dx))
    return T


def _heights(p, budget=250000):
    """T, the possible heights of a ray of the arrangement inside the region."""
    L = p['L']
    H = _hyperplane_forms(p)
    if len(H) < L:
        return None
    boxes = [(f, -1, 1) for f in p['box']]
    boxes += [(f, 0, 1) for f in p['lo'] if f in p['hi']]
    boxes += [(f, 0, None) for f in p['lo'] if f not in p['hi']]
    boxes += [(f, None, 1) for f in p['hi'] if f not in p['lo']]
    eqs = list(p['eq'])
    tot = 1
    for i in range(L):
        tot = tot * (len(H) - i) // (i + 1)
    if tot <= budget:
        return _rays([tuple(list(f) + [c]) for f, c in H], L, boxes, eqs)
    # The arrangement carries two hyperplanes for every box form, so C(|H|, L) grows fast: for
    # nine elements it is 4.7 million where the forms alone give 49 thousand. Falling back to
    # the CRUDER bound is still rigorous -- t* divides the determinant of the x-parts whether
    # or not the ray meets the region, and dropping the ones outside only sharpens it -- and
    # it is what these entries were proved with before the sharper version existed. Refusing
    # instead lost them.
    F = sorted({f for f, _c in H})
    tot = 1
    for i in range(L):
        tot = tot * (len(F) - i) // (i + 1)
    if tot > 4 * budget:
        return None
    T = {}
    for S in combinations(F, L):
        d = _det([list(v) for v in S])
        if d:
            T.setdefault(abs(d), set()).add(None)
    return T


def _rank(rows):
    """rank of an integer matrix, over the rationals."""
    from fractions import Fraction
    M = [[Fraction(x) for x in r] for r in rows]
    r = 0
    for c in range(len(M[0]) if M else 0):
        piv = next((i for i in range(r, len(M)) if M[i][c]), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        r += 1
    return r


def _dim(p):
    """the dimension of the cone the region lives in, at most L + 1."""
    eqs = [list(f) for f in p['eq']]
    return p['L'] + 1 - (_rank(eqs) if eqs else 0)


def _totient(m):
    r, k, mm = m, 2, m
    while k * k <= mm:
        if mm % k == 0:
            while mm % k == 0:
                mm //= k
            r -= r // k
        k += 1
    if mm > 1:
        r -= r // mm
    return r


def _divisors(m):
    out = set()
    k = 1
    while k * k <= m:
        if m % k == 0:
            out.add(k)
            out.add(m // k)
        k += 1
    return out


def _cyclotomic(d, cache):
    """Phi_d as a list of integer coefficients, lowest degree first."""
    if d in cache:
        return cache[d]
    num = [-1] + [0] * (d - 1) + [1]                     # z^d - 1
    for e in sorted(_divisors(d)):
        if e == d:
            continue
        num = _polydiv(num, _cyclotomic(e, cache))
    cache[d] = num
    return num


def _polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        if u:
            for j, v in enumerate(b):
                out[i + j] += u * v
    return out


def _polydiv(a, b):
    """exact division of integer polynomials, lowest degree first."""
    a = list(a)
    q = [0] * (len(a) - len(b) + 1)
    for i in range(len(q) - 1, -1, -1):
        c = a[i + len(b) - 1] // b[-1]
        q[i] = c
        if c:
            for j, v in enumerate(b):
                a[i + j] -= c * v
    return q


def _annihilator(T, M, L, dim=None):
    """A(z) = prod_d Phi_d(z)^m_d, coefficients lowest degree first.

    The exponent is the largest number of rays a simplicial cone in the triangulation can
    have, which is the DIMENSION of the cone rather than L+1. An equality among the
    conditions -- a vanishing sum, a difference forced to zero -- drops that dimension by
    one for each independent form, and with it the order of the annihilator."""
    dim = L + 1 if dim is None else dim
    # how many DISTINCT arrangement rays carry each height, when that is known
    cnt = {}
    for t, gens in (T.items() if isinstance(T, dict) else ((t, None) for t in T)):
        cnt[M * t] = None if gens is None or None in gens else len(gens)
    D = set()
    for t in cnt:
        D |= _divisors(t)
    cache = {}
    A = [1]
    for d in sorted(D):
        avail = 0
        for t, c in cnt.items():
            if t % d == 0:
                if c is None:
                    avail = dim
                    break
                avail += c
        m = min(dim, max(1, avail))
        phi = _cyclotomic(d, cache)
        for _ in range(m):
            A = _polymul(A, phi)
    return A


# ---------------------------------------------------------------- exact counts

TOT = None


def _local(p, skip=()):
    """every condition as a window constraint, with the window width it needs.

    The all-ones form is the one exception: it reaches the whole array and is carried by a
    running-sum axis instead."""
    L = p['L']
    tot = tuple([1] * L)
    loc = []
    k = 0

    def add(kind, forms):
        """a constraint reaches from the first position any of its forms names to the last.

        `no two consecutive zero elements' is two forms, x_i and x_{i+1}, each of span zero;
        taking the span form by form made it a condition on one element and counted the wrong
        sequence."""
        nonlocal k
        lo = min(min(q for q, c in enumerate(f) if c) for f in forms)
        hi = max(max(q for q, c in enumerate(f) if c) for f in forms)
        k = max(k, hi - lo)
        loc.append((kind, forms, lo, hi))

    for f in p['box']:
        if f == tot:
            return None
        add('box', (f,))
    for f in p['lo']:
        if f == tot:
            return None
        add('lo', (f,))
    for f in p['hi']:
        if f == tot:
            return None
        add('hi', (f,))
    for f in p['ne']:
        if f not in skip:
            add('ne', (f,))
    for f in p['eq']:
        if f not in skip:
            add('eq', (f,))
    for atoms in p['nand']:
        add('nand:' + ','.join(r for _, r in atoms), tuple(f for f, _ in atoms))
    for dnf in p['cl']:
        pos = [q for conj in dnf for f, _tc, _r in conj
               for q, c in enumerate(f) if c]
        lo, hi = min(pos), max(pos)
        k = max(k, hi - lo)
        loc.append(('cl', dnf, lo, hi))
    for f, m in p['ncong']:
        add('ncong%d' % m, (f,))
    if p['alt']:
        for f in _dforms(L, 1):
            add('alt', (f,))
    if p.get('modge', False) is not False:
        kk = p['modge']
        for i in range(L):
            st = 0 if kk is None else max(0, i - kk)
            if st >= i:
                continue
            if kk is None:
                # the whole prefix reaches further than a window can, so the walk carries the
                # running sum and the condition READS it -- the first predicate here that
                # depends on an accumulator rather than on the window alone
                loc.append(('modgeacc', (i,), i, i))
                continue
            f = tuple(1 if st <= q <= i else 0 for q in range(L))
            k = max(k, i - st)
            loc.append(('modge', (f,), st, i))
    return k, loc


def _accs(p, n, acap=400000):
    """which conditions are carried as a running accumulator rather than a window.

    `sum x_i = 0' reaches the whole array, so no window of bounded width decides it; the walk
    carries the running sum instead and reads it off at the end. Nothing about that is special
    to the all-ones form: `zero 6th difference' and `sum i^2 x(i) = 16n' are the same shape,
    and carrying them the same way is what brings them into range. A form is promoted when it
    reaches further than a window can afford, and only while the product of the accumulators'
    ranges stays small.
    """
    L = p['L']
    cand = []
    for f, rel in [(f, 'eq') for f in p['eq']] + [(f, 'ne') for f in p['ne']]:
        nz = [q for q, c in enumerate(f) if c]
        span = nz[-1] - nz[0]
        if span >= 4 or span == L - 1:
            cand.append((span, f, rel))
    cand.sort(key=lambda t: -t[0])
    out, prod = [], 1
    for span, f, rel in cand:
        half = sum(abs(c) for c in f) * n
        if len(out) >= 2 or prod * (2 * half + 1) > acap:
            continue
        out.append({'kind': 'linear', 'w': f, 'tc': 0, 'rel': rel, 'half': half})
        prod *= 2 * half + 1
    for a in p.get('acc', ()):
        half = L if a['kind'] == 'sign' else sum(abs(c) for c in a['w']) * n
        if prod * (2 * half + 1) > acap:
            return None
        out.append(dict(a, half=half))
        prod *= 2 * half + 1
    if p.get('modge', False) is None:
        half = L * n
        if prod * (2 * half + 1) > acap:
            return None
        out.append({'kind': 'linear', 'w': tuple([1] * L), 'tc': 0, 'rel': 'any',
                    'half': half})
    return out


def _axis(accs):
    lens = [2 * a['half'] + 1 for a in accs]
    strides, s = [], 1
    for ln in reversed(lens):
        strides.insert(0, s)
        s *= ln
    return lens, strides, s


def _inc(accs, i, x):
    out = []
    for a in accs:
        if a['kind'] == 'sign':
            out.append(1 if x > 0 else -1 if x < 0 else 0)
        else:
            out.append(a['w'][i] * x)
    return out


def _accepted(accs, lens, strides, n):
    """the flat indices whose accumulator values satisfy every final condition."""
    tgt = []
    for a in accs:
        tgt.append(-a['tc'] * n + a['half'])
    idx = [0]
    for j, a in enumerate(accs):
        nxt = []
        for base in idx:
            if a['rel'] == 'any':
                nxt += [base + v * strides[j] for v in range(lens[j])]
            elif a['rel'] == 'eq':
                if 0 <= tgt[j] < lens[j]:
                    nxt.append(base + tgt[j] * strides[j])
            else:
                for v in range(lens[j]):
                    if v != tgt[j]:
                        nxt.append(base + v * strides[j])
        idx = nxt
    return idx


def _closing(loc, i):
    """the constraints whose last position is i."""
    return [c for c in loc if c[3] == i]


def _ok_window(cons, win, first_pos):
    """cons closing at the newest position; win holds the values at first_pos .. newest."""
    for kind, forms, start, lastpos in cons:
        if kind == 'modgeacc':
            continue
        if start < first_pos:
            continue
        if kind == 'cl':
            n = _ok_window.n
            for conj in forms:
                for f, tc, rel in conj:
                    u = tc * n
                    for q in range(start, lastpos + 1):
                        if f[q]:
                            u += f[q] * win[q - first_pos]
                    if not (u == 0 if rel == 'eq' else u != 0 if rel == 'ne' else
                            u > 0 if rel == 'gt' else u < 0 if rel == 'lt' else
                            u >= 0 if rel == 'ge' else u <= 0):
                        break
                else:
                    break
            else:
                return False
            continue

        def lin(g):
            return sum(g[q] * win[q - first_pos] for q in range(start, lastpos + 1) if g[q])
        v = lin(forms[0])
        if kind == 'modge':
            sm = sum(win[q - first_pos] for q in range(start, lastpos))
            if win[lastpos - first_pos] < sm % (_ok_window.n + 1):
                return False
            continue
        if kind == 'box':
            if abs(v) > _ok_window.n:
                return False
        elif kind == 'lo':
            if v < 0:
                return False
        elif kind == 'hi':
            if v > _ok_window.n:
                return False
        elif kind.startswith('nand:'):
            rels = kind[5:].split(',')
            for g, r in zip(forms, rels):
                u = lin(g)
                if not ((u == 0) if r == 'eq0' else (u > 0) if r == 'gt0'
                        else (u < 0) if r == 'lt0' else (u >= 0) if r == 'ge0'
                        else (u <= 0) if r == 'le0' else (u == _ok_window.n) if r == 'eqn'
                        else False):
                    break
            else:
                return False
        elif kind == 'ne':
            if v == 0:
                return False
        elif kind == 'eq':
            if v != 0:
                return False
        elif kind.startswith('ncong'):
            if v % int(kind[5:]) == 0:
                return False
        elif kind == 'alt':
            # the name fixes only that the direction alternates, not which way it starts:
            # both zigzags are counted, and reading one of them halved every term.
            if (lastpos % 2 == 1) == (_ok_window.phase == 0):
                if not v > 0:
                    return False
            elif not v < 0:
                return False
    return True


def _count(p, n, cap=9_000_000):
    """a(n), exactly. A zigzag condition is counted once for each starting direction."""
    if p['alt']:
        a = _count1(p, n, 0, cap)
        b = _count1(p, n, 1, cap)
        tot = None if a is None or b is None else a + b
    else:
        tot = _count1(p, n, 0, cap)
    if tot is None:
        return None
    f = p.get('frac', 1)
    if f == 1:
        return tot
    if tot % f:
        return None
    return tot // f


def _count1(p, n, phase, cap=9_000_000):
    L = p['L']
    n = n + p.get('shift', 0)
    accs = _accs(p, n)
    if accs is None:
        return None
    skip = {a['w'] for a in accs if a['kind'] == 'linear'}
    got = _local(p, skip)
    if got is None:
        return None
    k, loc = got
    w = min(k, L - 1)
    V = 2 * n + 1
    vals = list(range(-n, n + 1))
    _ok_window.n = n
    _ok_window.phase = phase
    lens, strides, alen = _axis(accs)
    apos = {c[2] for c in loc if c[0] == 'modgeacc'}
    if V ** (w + 1) > cap or V ** w * alen > cap:
        return None

    seeds = []

    def grow(pref):
        i = len(pref)
        if i == w:
            seeds.append(tuple(pref))
            return
        for a in range(V):
            pref.append(a)
            if _ok_window(_closing(loc, i), [vals[q] for q in pref], 0):
                grow(pref)
            pref.pop()
    grow([])
    if w == 0:
        seeds = [()]

    layer = {}
    for st in seeds:
        j = 0
        for jj, a in enumerate(accs):
            v = a['half']
            for i, q in enumerate(st):
                v += _inc([a], i, vals[q])[0]
            j += v * strides[jj]
        row = layer.get(st)
        if row is None:
            row = layer[st] = [0] * alen
        row[j] += 1

    for i in range(w, L):
        cons = _closing(loc, i)
        nxt = {}
        bytail = {}
        for st, row in layer.items():
            bytail.setdefault(st[1:] if w else (), {})[st[0] if w else 0] = row
        for tail, byfirst in bytail.items():
            if w:
                cs_ = [[0] * alen]
                for a in range(V):
                    r = byfirst.get(a)
                    prev = cs_[-1]
                    cs_.append([x + y for x, y in zip(prev, r)] if r else prev[:])
            for b in range(V):
                if w:
                    allowed = [a for a in range(V)
                               if _ok_window(cons, [vals[a]] + [vals[q] for q in tail]
                                             + [vals[b]], i - w)]
                    if not allowed:
                        continue
                    acc = None
                    a0 = 0
                    while a0 < len(allowed):
                        a1 = a0
                        while a1 + 1 < len(allowed) and allowed[a1 + 1] == allowed[a1] + 1:
                            a1 += 1
                        lo, hi = allowed[a0], allowed[a1] + 1
                        seg = [x - y for x, y in zip(cs_[hi], cs_[lo])]
                        acc = seg if acc is None else [x + y for x, y in zip(acc, seg)]
                        a0 = a1 + 1
                else:
                    if not _ok_window(cons, [vals[b]], i):
                        continue
                    acc = byfirst[0]
                if apos and i in apos:
                    ah = accs[-1]['half']
                    astr = strides[-1]
                    alensj = lens[-1]
                    xv = vals[b]
                    acc = list(acc)
                    for q in range(alen):
                        if acc[q] and xv < ((q // astr) % alensj - ah) % (n + 1):
                            acc[q] = 0
                st = (tail + (b,))[-w:] if w else ()
                row = nxt.get(st)
                if row is None:
                    row = nxt[st] = [0] * alen
                sh = 0
                for jj, d in enumerate(_inc(accs, i, vals[b])):
                    sh += d * strides[jj]
                if sh > 0:
                    for q in range(alen - sh):
                        x = acc[q]
                        if x:
                            row[q + sh] += x
                elif sh < 0:
                    for q in range(-sh, alen):
                        x = acc[q]
                        if x:
                            row[q + sh] += x
                else:
                    for q in range(alen):
                        x = acc[q]
                        if x:
                            row[q] += x
        layer = nxt
        if not layer:
            return 0
    keep = _accepted(accs, lens, strides, n)
    return sum(r[j] for r in layer.values() for j in keep)


def _brute(p, n):
    from itertools import product
    if p['alt']:
        return _brute1(p, n, 0) + _brute1(p, n, 1)
    return _brute1(p, n, 0)


def _brute1(p, n, phase):
    """the same count by direct enumeration --- the instrument checked against itself."""
    from itertools import product
    L = p['L']
    n = n + p.get('shift', 0)
    accs = _accs(p, n)
    if accs is None:
        return None
    skip = {a['w'] for a in accs if a['kind'] == 'linear'}
    k, loc = _local(p, skip)
    _ok_window.n = n
    _ok_window.phase = phase
    c = 0
    for x in product(range(-n, n + 1), repeat=L):
        ok = True
        for i in range(L):
            if not _ok_window(_closing(loc, i), list(x[:i + 1]), 0):
                ok = False
                break
        if not ok:
            continue
        if p.get('modge', False) is None:
            for i in range(L):
                if x[i] < sum(x[:i]) % (n + 1):
                    ok = False
                    break
            if not ok:
                continue
        for a in accs:
            if a['rel'] == 'any':
                continue
            if a['kind'] == 'sign':
                v = sum(1 if q > 0 else -1 if q < 0 else 0 for q in x)
            else:
                v = sum(w * q for w, q in zip(a['w'], x)) + a['tc'] * n
            if (v != 0) if a['rel'] == 'eq' else (v == 0):
                ok = False
                break
        if ok:
            c += 1
    return c


def build(p, cap=200000):
    L = p['L']
    if _local(p) is None:
        return None
    T = _heights(p)
    if not T:
        return None
    M = 1
    for _, m in p['ncong']:
        M = M * m // gcd(M, m)
    A = _annihilator(T, M, L, dim=_dim(p))
    # One more than the cyclotomic degree, and the extra one is not slack. The numerator over
    # A has degree below S for every cell of the arrangement that HAS a ray, because such a
    # cell's numerator collects a fundamental parallelepiped whose heights are below the sum
    # of its generators' heights. The origin is a cell too, and it has no ray: it contributes
    # the constant series 1, which over A is A/A and pushes the numerator's degree to exactly
    # S. So a(0..S-1) do NOT determine the rest; a(0..S) do, and the recurrence is the one
    # given by z*A. A189327 is where this showed: its count is 3n on the evens and (5n-1)/2 on
    # the odds from n = 1, but a(0) = 1 rather than 0 -- the all-zero arrangement -- and the
    # bound was one short by exactly that point.
    A = [0] + A
    S = len(A) - 1
    if S > 420:
        return None
    extra = 6
    vals = []
    for n in range(S + extra):
        v = _count(p, n)
        if v is None:
            return None
        vals.append(v)
    # the instrument, tested on cases whose answer can be got another way
    for n in range(min(3, len(vals))):
        if (2 * n + 1) ** L <= 400000 and _brute(p, n) != vals[n]:
            return None
    # and the derived annihilator, tested on terms it did not see
    for m in range(S, len(vals)):
        if vals[m] != -sum(A[j] * vals[m - S + j] for j in range(S)):
            return None
    return {'vals': vals, 'A': A, 'S': S, 'L': L}


def terms(b, N):
    """a(n) for n = 0, 1, 2, ... -- the entry's own index."""
    A, S = b['A'], b['S']
    out = list(b['vals'])
    while len(out) < N + 3:
        out.append(-sum(A[j] * out[len(out) - S + j] for j in range(S)))
    return out


def threshold(b, coeffs, order):
    """the last index at which the conjectured recurrence fails, or None."""
    S = b['S']
    t = terms(b, 2 * S + order + 20)
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
