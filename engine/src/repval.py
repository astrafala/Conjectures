#!/usr/bin/env python3
"""Arrays over 0..k constrained through their REPEATED VALUES.

    Number of length-n 0..5 arrays with no repeated value equal to the previous repeated value.
    Number of length-n 0..2 arrays with no repeated value differing from the previous repeated
      value by other than one.
    Number of length-(n+1) 0..3 arrays with new repeated values introduced in sequential order
      starting with zero.

96 entries outside the roster carry a conjectured recurrence and a name of this shape, and no
engine read any of them. A *repeated value* is a term equal to the one before it, and its value
is that term; the conditions relate each repeated value to the previous one, or to the first
one, or ask that the repeated values be introduced in increasing order.

All of that is a finite automaton. The state after reading a prefix is the last symbol together
with whatever the condition needs remembered -- the previous repeated value, or the first one,
or how many distinct repeated values have appeared -- and none of those has more than k + 2
possibilities. The count of arrays of each length is then a walk count on at most (k+1)(k+2)
states, which is what every transfer-matrix paper in this project already knows how to settle:
det(I - xM) has degree at most the number of states, so the residual test proves a conjectured
recurrence rather than checking it.
"""
import re

NAME = re.compile(
    r'^\s*Number of length[- ]\(?(n(?:\s*\+\s*\d+)?)\)?\s+0\.\.(\d+)\s+arrays?\s+with\s+(.*?)\s*\.?\s*$',
    re.I)


def _cond(text, K):
    """a predicate (this repeated value, previous repeated value) -> allowed, or None."""
    t = ' '.join(text.lower().split())
    neg = t.startswith('no ')
    body = t[3:] if neg else (t[6:] if t.startswith('every ') else None)
    if body is None:
        return None
    m = re.match(r'repeated value (.*?) the previous repeated value(.*)$', body)
    if not m:
        return None
    rel, tail = m.group(1).strip(), m.group(2).strip()
    mod = None
    mm = re.search(r'mod(?:ulo)?\s+(\d+)\s*\+\s*1', tail) or re.search(r'mod(?:ulo)?\s+(\d+)', tail)
    if mm:
        mod = int(mm.group(1)) + 1 if '+ 1' in tail or '+1' in tail else int(mm.group(1))
        tail = tail[:mm.start()].strip()
    plus = 0
    pm = re.match(r'plus\s+(?:one|1)\b', tail)
    if pm:
        plus = 1
        tail = tail[pm.end():].strip()
    if tail not in ('', '.'):
        return None

    def diff(v, r):
        d = v - r
        if mod:
            d %= mod
            if d > mod // 2:
                d -= mod
        return d

    if rel in ('equal to', 'equal to plus one'):
        base = lambda v, r: (v - r - plus) % mod == 0 if mod else v == r + plus
    elif rel == 'unequal to':
        base = lambda v, r: ((v - r - plus) % mod != 0) if mod else v != r + plus
    elif rel == 'greater than':
        base = lambda v, r: v > r
    elif rel == 'greater than or equal to':
        base = lambda v, r: v >= r
    elif rel == 'less than':
        base = lambda v, r: v < r
    elif rel == 'less than or equal to':
        base = lambda v, r: v <= r
    elif rel.startswith('differing from'):
        how = rel[len('differing from'):].strip()
        how = re.sub(r'^by\s+', '', how) if how.startswith('by') else None
        return None
    else:
        return None
    return (lambda v, r: not base(v, r)) if neg else (lambda v, r: base(v, r))


def _diffcond(text, K):
    """the `differing from the previous repeated value by ...' conditions."""
    t = ' '.join(text.lower().split())
    neg = t.startswith('no ')
    body = t[3:] if neg else (t[6:] if t.startswith('every ') else None)
    if body is None:
        return None
    m = re.match(r'repeated value differing from the previous repeated value by (.*?)\s*\.?$',
                 body)
    if not m:
        return None
    spec = m.group(1).strip()
    mod = None
    mm = re.search(r'modulo\s+(\d+)\s*\+\s*1', spec)
    if mm:
        mod = int(mm.group(1)) + 1
        spec = spec[:mm.start()].strip()
    other = False
    if spec.startswith('other than'):
        other = True
        spec = spec[len('other than'):].strip()

    def parse_set(s):
        """the set of differences the phrase names, or None."""
        if s in ('one', '1'):
            return {1, -1}
        if s in ('plus or minus one', 'plus or minus 1'):
            return {1, -1}
        if s in ('more than one', 'more than 1'):
            return None          # a range, handled below
        if s in ('one or less', '1 or less'):
            return None
        words = {'plus two': 2, 'plus 2': 2, 'zero': 0, 'minus 1': -1, 'minus one': -1,
                 'plus one': 1, 'plus 1': 1, 'minus 2': -2, 'minus two': -2, 'two': 2}
        parts = [p.strip() for p in re.split(r',| or ', s) if p.strip()]
        out = set()
        for p in parts:
            if p not in words:
                return None
            out.add(words[p])
        return out or None

    rng = None
    if spec in ('more than one', 'more than 1'):
        rng = ('gt', 1)
    elif spec in ('one or less', '1 or less'):
        rng = ('le', 1)
    else:
        s = parse_set(spec)
        if s is None:
            return None

    def d(v, r):
        x = v - r
        if mod:
            x %= mod
            if x > mod // 2:
                x -= mod
        return x

    if rng:
        kind, b = rng
        base = (lambda v, r: abs(d(v, r)) > b) if kind == 'gt' else (lambda v, r: abs(d(v, r)) <= b)
    else:
        base = lambda v, r: d(v, r) in s
    if other:
        inner = base
        base = lambda v, r: not inner(v, r)
    return (lambda v, r: not base(v, r)) if neg else (lambda v, r: base(v, r))


def parse_name(nm):
    m = NAME.match(' '.join(nm.split()))
    if not m:
        return None
    off = m.group(1).replace(' ', '')
    base = int(off.split('+')[1]) if '+' in off else 0
    K = int(m.group(2))
    if K > 9:
        return None
    text = m.group(3)
    kind, extra = None, {}
    low = ' '.join(text.lower().split())
    if 'following elements' in low:
        mm = re.match(r'no following elements (larger than|greater than or equal to) '
                      r'the first repeated value', low)
        if not mm:
            return None
        kind = 'first'
        extra['strict'] = mm.group(1) == 'greater than or equal to'
    elif low == 'new repeated values introduced in sequential order starting with zero':
        kind = 'seqrep'
    elif low == ('new values introduced in sequential order, and with new repeated values '
                 'introduced in sequential order, both starting with zero'):
        kind = 'seqboth'
    else:
        canon = False
        if low.endswith(', with new values introduced in sequential order'):
            canon = True
            text = text[:text.lower().rfind(', with new values')]
        f = _cond(text, K) or _diffcond(text, K)
        if f is None:
            return None
        kind = 'prev'
        extra['f'] = f
        extra['canon'] = canon
    return {'engine': 'repval', 'K': K, 'base': base, 'kind': kind, **extra}


def build(p, cap=200000):
    K, kind = p['K'], p['kind']
    states, index = [], {}

    def sid(s):
        if s not in index:
            index[s] = len(states)
            states.append(s)
        return index[s]

    start = []
    if kind == 'prev':
        if p.get('canon'):
            start = [sid((0, None, 0))]
        else:
            start = [sid((c, None)) for c in range(K + 1)]
    elif kind == 'first':
        start = [sid((c, None)) for c in range(K + 1)]
    elif kind == 'seqrep':
        start = [sid((c, 0)) for c in range(K + 1)]
    elif kind == 'seqboth':
        start = [sid((0, 0, 0))]
    adj = {}
    i = 0
    while i < len(states):
        s = states[i]
        row = []
        for t in range(K + 1):
            if kind == 'prev' and p.get('canon'):
                last, r, mx = s
                if t > mx + 1:
                    continue
                nmx = max(mx, t)
                if t == last:
                    if r is not None and not p['f'](t, r):
                        continue
                    row.append(sid((t, t, nmx)))
                else:
                    row.append(sid((t, r, nmx)))
            elif kind == 'prev':
                last, r = s
                if t == last:
                    if r is not None and not p['f'](t, r):
                        continue
                    row.append(sid((t, t)))
                else:
                    row.append(sid((t, r)))
            elif kind == 'first':
                last, first = s
                if first is not None and (t >= first if p['strict'] else t > first):
                    continue
                if t == last and first is None:
                    row.append(sid((t, t)))
                else:
                    row.append(sid((t, first)))
            elif kind == 'seqrep':
                last, m = s
                if t == last:
                    if t > m:
                        continue
                    row.append(sid((t, m + 1 if t == m else m)))
                else:
                    row.append(sid((t, m)))
            elif kind == 'seqboth':
                last, mx, m = s
                if t > mx + 1:
                    continue
                nmx = max(mx, t)
                if t == last:
                    if t > m:
                        continue
                    row.append(sid((t, nmx, m + 1 if t == m else m)))
                else:
                    row.append(sid((t, nmx, m)))
        adj[i] = row
        i += 1
        if len(states) > cap:
            return None
    return {'adj': [adj[j] for j in range(len(states))], 'start': start, 'S': len(states)}


def terms(b, N):
    """the number of arrays of each length, from length 1 up."""
    v = [0] * b['S']
    for s in b['start']:
        v[s] += 1
    out = [sum(v)]
    for _ in range(N + 2):
        w = [0] * b['S']
        for i, c in enumerate(v):
            if c:
                for j in b['adj'][i]:
                    w[j] += c
        v = w
        out.append(sum(v))
    return out


def threshold(b, coeffs, order):
    """the last walk index at which the conjectured recurrence fails, or None.

    The count is iota^T M^j tau for an S-state matrix, so it satisfies the recurrence of M's
    characteristic polynomial, of order S. If the conjectured residual vanishes at S + order
    consecutive indices it vanishes for ever: the two sequences satisfy a common monic
    recurrence of that order and agree on that many consecutive terms.
    """
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
