#!/usr/bin/env python3
"""The x-axis and diagonal of a two-dimensional cellular automaton, read as a number.

    Binary representation of the x-axis, from the origin to the right edge, of the n-th stage
    of growth of the two-dimensional cellular automaton defined by "Rule 7", based on the
    5-celled von Neumann neighborhood.

387 entries, and no engine read one. Three things had to be read correctly, and the entries'
own published terms settled each of them rather than my guessing:

* **the rule encoding.** The automaton is outer-totalistic on the 5-cell von Neumann
  neighbourhood, so the new state depends on the cell and the number of live neighbours. Of the
  layouts tried only `bit(2*sum + own)` reproduces the data.
* **the direction.** The name says "from the left edge to the origin" or "from the origin to
  the right edge", and those are reverses of one another. Ignoring the phrase cost 21 of 60.
* **the background.** A rule taking an empty neighbourhood to a live cell flips the ENTIRE
  background, and a grid whose border stays 0 is not that background: it leaks inward one cell
  per step. A279028 was wrong from its third term until the padding exceeded the number of
  steps. The same defect appeared in the one-dimensional automata earlier the same day.

The row is then read as a word and, where it settles into w(n+p) = L + w(n) + R, the value
satisfies an exact linear recurrence -- the certificate `ecarow` uses, one dimension up.
"""
import re

HEAD = re.compile(
    r'^\s*(Binary|Decimal) representation of the (x-axis|diagonal)\b(.*?)'
    r'of the n-th stage of growth of the two-dimensional cellular automaton '
    r'defined by "?Rule (\d+)"?', re.I | re.S)


def parse_name(nm):
    m = HEAD.match(re.sub(r'\s+', ' ', nm).strip())
    if not m:
        return None
    rule = int(m.group(4))
    if not 0 <= rule <= 1023:
        return None
    mid = m.group(3) or ''
    if 'or from the origin' in mid:
        dirs = ('right', 'left')          # the name offers both; the data picks
    elif 'left edge to the origin' in mid:
        dirs = ('left',)
    else:
        dirs = ('right',)
    return {'rule': rule, 'base': 10 if m.group(1).lower() == 'binary' else 2,
            'axis': m.group(2).lower(), 'dirs': dirs, 'frac': 1}


def words(rule, steps, direction, axis='x-axis'):
    """the axis of each stage as a word, leading zeros stripped"""
    R = 2 * steps + 3                      # must exceed the steps: see the module docstring
    N = 2 * R + 1
    C = R
    g = [[0] * N for _ in range(N)]
    g[C][C] = 1
    out = []
    for n in range(steps + 1):
        if axis == 'x-axis':
            row = g[C][C:C + n + 1] if direction == 'right' else g[C][C - n:C + 1]
        else:
            row = ([g[C + k][C + k] for k in range(n + 1)] if direction == 'right'
                   else [g[C - k][C - k] for k in range(n + 1)][::-1])
        s = ''.join(map(str, row)).lstrip('0')
        out.append(s if s else '0')
        ng = [[0] * N for _ in range(N)]
        for i in range(1, N - 1):
            gi, gu, gd = g[i], g[i - 1], g[i + 1]
            ngi = ng[i]
            for j in range(1, N - 1):
                t = gu[j] + gd[j] + gi[j - 1] + gi[j + 1]
                ngi[j] = (rule >> (t * 2 + gi[j])) & 1
        g = ng
    return out


def shape(ws):
    """the growth shape, found on each residue class of n separately.

    Many of these automata alternate: the x-axis grows on even stages and is empty on odd ones,
    so the sequence of words is 1, 0, 101, 0, 10101, 0. Requiring w(n+p) to be LONGER than w(n)
    for every n found nothing at all in that case, because half the classes are constant. Each
    residue class of n mod p is now fitted on its own, and a class may grow or stay fixed.

    Returns (n0, p, [(L, R) per residue]) or None.
    """
    for p in range(1, 9):
        for n0 in range(0, 12):
            if n0 + 3 * p + 4 >= len(ws):
                continue
            per = []
            ok = True
            for r in range(p):
                idx = [n for n in range(n0 + r, len(ws) - p, p)]
                if len(idx) < 3:
                    ok = False
                    break
                a, b = ws[idx[0]], ws[idx[0] + p]
                fit = None
                for cut in range(len(b) - len(a) + 1) if len(b) >= len(a) else []:
                    if b[cut:cut + len(a)] != a:
                        continue
                    L, Rw = b[:cut], b[cut + len(a):]
                    if all(ws[n + p] == L + ws[n] + Rw for n in idx):
                        fit = (L, Rw)
                        break
                if fit is None:
                    ok = False
                    break
                per.append(fit)
            if ok:
                return n0, p, per
    return None


def value(word, base):
    v = 0
    for ch in word:
        v = v * base + (1 if ch == '1' else 0)
    return v


def build(p, cap=200000):
    """the reading that matches, with its growth certificate"""
    import localentry as LE
    for dr in p['dirs']:
        ws = words(p['rule'], 34, dr, p['axis'])
        sh = shape(ws)
        if sh is None:
            continue
        return {'rule': p['rule'], 'B': p['base'], 'axis': p['axis'], 'dir': dr,
                'n0': sh[0], 'p': sh[1], 'per': sh[2], 'ws': ws, 'S': sh[1] + 3}
    return None


def terms(b, N):
    ws = b['ws'] if N < len(b['ws']) else words(b['rule'], N + 1, b['dir'], b['axis'])
    return [value(w, b['B']) for w in ws[:N + 1]]


def certify(b, upto=34):
    """how far past the settling point the growth identity was checked"""
    ws = words(b['rule'], upto, b['dir'], b['axis'])
    n0, p, per = b['n0'], b['p'], b['per']
    k = 0
    for n in range(n0, len(ws) - p):
        L, R = per[(n - n0) % p]
        if ws[n + p] != L + ws[n] + R:
            break
        k += 1
    return k


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 30)
    last, run = None, 0
    # the scan starts at `order`, the first index at which a recurrence can be evaluated
    for j in range(order, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S + order:
        return None
    return last if last is not None else 0
