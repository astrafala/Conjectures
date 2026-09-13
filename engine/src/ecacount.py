#!/usr/bin/env python3
"""ON and OFF cell counts of an elementary cellular automaton.

    Number of ON (black) cells in the n-th iteration of the "Rule 7" elementary cellular
      automaton starting with a single ON (black) cell.
    Total number of OFF (white) cells after n iterations of the "Rule 1" ...

`ecarow' already models the ROW of an elementary automaton and derives the shape

    w(n+p) = L + w(n) + R

for every n past a settling point n0, verified over every available step. Nothing about that
certificate is specific to reading the row as a numeral. Counting its ON cells uses the same
identity and gives a shorter recurrence:

    on(n+p) = on(n) + ones(L) + ones(R),

so `on' is annihilated by (z^p - 1)(z - 1). The row at step n is the light cone, of width
2n+1, so off(n) = 2n + 1 - on(n) and (z-1)^2 kills the width; a running total adds one more
(z-1). The pre-period raises the numerator's degree, exactly as it does for the row, so
S = p + 4 + n0 covers all four wordings.

87 entries carry these four names and no engine read any of them: the row engine wanted the
word "representation" on the line. That is the same silent refusal this project keeps paying
for -- machinery already built, hidden by how a sweep chose what to look at.

`ecarow' asks for ONE pair (L, R) serving every n past the settling point, and that is too
rigid. Rule 1 alternates between 1^k 000 1^k and 0^k 1 0^k: the identity holds with
L = R = "11" on the odd n and with L = R = "00" on the even, and no single pair serves both,
so the row engine reports no shape at all. `ca2d' already allows a different pair per residue
class of n and says so in its bound; the one-dimensional engine never did. Asking per class
is what brings these rules into range, and for the COUNT the bound stays simple: on(n+p) =
on(n) + ones(L_r) + ones(R_r) is quasi-linear with period p whatever the L_r and R_r are.
"""
import re

import ecarow

HEAD = re.compile(
    r'^\s*(Total number|Number) of (ON \(black\)|OFF \(white\)) cells '
    r'(?:in the n-th iteration|after n iterations) of the '
    r'"Rule (\d+)" elementary cellular automaton starting with a single ON \(black\) cell'
    r'\s*\.?\s*$', re.I)


def parse_name(nm):
    m = HEAD.match(re.sub(r'\s+', ' ', nm).strip())
    if not m:
        return None
    rule = int(m.group(3))
    if not 0 <= rule <= 255:
        return None
    return {'rule': rule, 'on': m.group(2).lower().startswith('on'),
            'total': m.group(1).lower().startswith('total'), 'frac': 1}


def shape_res(ws, maxp=17, maxn0=28):
    """w(n+p) = L_r + w(n) + R_r for every n >= n0 in the class r = n mod p."""
    for per in range(1, maxp):
        for n0 in range(0, maxn0):
            if n0 + 2 * per + 6 >= len(ws):
                continue
            pairs = {}
            ok = True
            for n in range(n0, len(ws) - per):
                a, b = ws[n], ws[n + per]
                if len(b) != len(a) + 2 * per:
                    ok = False
                    break
                r = n % per
                if r in pairs:
                    L, R = pairs[r]
                    if b != L + a + R:
                        ok = False
                        break
                    continue
                cuts = [c for c in range(2 * per + 1) if b[c:c + len(a)] == a]
                if not cuts:
                    ok = False
                    break
                c = cuts[0]
                pairs[r] = (b[:c], b[c + len(a):])
            if ok and len(pairs) == per:
                return n0, per, pairs
    return None


def build(p, cap=200000):
    ws = ecarow.rows(p['rule'], 80)
    s = shape_res(ws)
    if s is None:
        return None
    n0, per, pairs = s
    return {'rule': p['rule'], 'n0': n0, 'p': per, 'pairs': pairs, 'ws': ws,
            'on': p['on'], 'total': p['total'], 'S': per + 4 + n0}


def terms(b, N):
    """a(n) for n = 0, 1, 2, ... -- the entry's own index."""
    ws = b['ws'] if N < len(b['ws']) else ecarow.rows(b['rule'], N + 1)
    out, run = [], 0
    for n in range(N + 1):
        w = ws[n]
        v = w.count('1') if b['on'] else w.count('0')
        run += v
        out.append(run if b['total'] else v)
    return out


def certify(b, upto=80):
    """how far past the settling point the per-class identity was checked."""
    ws = ecarow.rows(b['rule'], upto)
    n0, per, pairs = b['n0'], b['p'], b['pairs']
    k = 0
    for n in range(n0, len(ws) - per):
        L, R = pairs[n % per]
        if ws[n + per] != L + ws[n] + R:
            break
        k += 1
    return k


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
