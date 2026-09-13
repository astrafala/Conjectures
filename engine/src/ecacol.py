#!/usr/bin/env python3
"""The middle column of an elementary cellular automaton.

    Binary representation of the middle column of the "Rule 54" elementary cellular automaton
      starting with a single ON (black) cell.
    Middle column of the "Rule 25" elementary cellular automaton starting with a single ON
      (black) cell.

The middle column is the cell at the origin at each step: c(n) = w(n)[n], the centre of the
light cone. `Binary representation' concatenates c(0..n) and reads it as a decimal numeral,
`Decimal representation' as a binary one, and the bare wording lists the bits themselves. 25
entries of this shape carry a conjectured recurrence and no engine read one.

Observing that the column settles into a period is not a proof, and the row certificate
`ecarow' and `ecacount' already derive gives one in three cases. Write the certificate as
w(n+p) = L_r + w(n) + R_r for n >= n0 and r = n mod p. In ABSOLUTE coordinates, where the row
covers x in [-n, n] and w(n)[i] is the cell at x = i - n, the certificate says

    cell(x, n+p) = cell(x + d_r, n),     d_r = p - |L_r|,

so the column at the origin reads a diagonal that moves by d_r every p steps.

* **L_r empty for every r.** The row then grows only on the RIGHT and every prefix is frozen,
  so there is a single infinite word W with w(n)[i] = W[i], and cell(x, n) = W[x+n] gives
  c(n) = W[n] outright. W is w(n0) followed by R_{r_0} R_{r_1} ... , eventually periodic with
  period dividing sum_r |R_r|, so the column is eventually periodic with that period.
* **R_r empty for every r.** The mirror: the row grows only on the left, the word read from the
  right end is frozen, and c(n) = U[n] for that word.
* **sum_r d_r = 0.** The diagonal returns to the origin after a full cycle of residues, so
  cell(0, n + p^2) = cell(0, n) and the column has period dividing p^2.

In each case the period is a proved bound; the actual period is then found inside one window of
computed rows, which is a finite check and not a fit. A rule meeting none of the three is
refused with the reason -- its column may well be periodic, and saying so would be an
observation.

For the concatenated readings, c eventually periodic with period q gives
a(n+q) = a(n) B^q + v(the q new digits), the same constant in each residue class, so a is
annihilated by (z^q - B^q)(z^q - 1); the pre-period raises the numerator's degree.
"""
import re

import ecacount
import ecarow

HEAD = re.compile(
    r'^\s*(?:(Binary) representation of the|(Decimal) representation of the|)\s*'
    r'[Mm]iddle column of the "?Rule (\d+)"? elementary cellular automaton '
    r'starting with a single ON \(black\) cell\s*\.?\s*$', re.I)


def parse_name(nm):
    m = HEAD.match(' '.join(nm.split()))
    if not m:
        return None
    rule = int(m.group(3))
    if not 0 <= rule <= 255:
        return None
    base = 10 if m.group(1) else (2 if m.group(2) else None)
    return {'engine': 'ecacol', 'rule': rule, 'base': base, 'frac': 1}


def certificate(rule):
    """(n0, p, [(L_r, R_r)]) from whichever row engine has it, or None."""
    ws = ecarow.rows(rule, 80)
    sh = ecarow.shape(ws)
    if sh is not None:
        n0, p, L, R = sh
        return n0, p, [(L, R)]
    t = ecacount.shape_res(ws)
    if t is None:
        return None
    n0, p, pairs = t
    return n0, p, [pairs[i] for i in range(p)]


def column_period(rule):
    """(n0, q) with c(n+q) = c(n) proved for every n >= n0, or None."""
    cert = certificate(rule)
    if cert is None:
        return None
    n0, p, LR = cert
    if all(L == '' for L, _R in LR):
        q = sum(len(R) for _L, R in LR)
    elif all(R == '' for _L, R in LR):
        q = sum(len(L) for L, _R in LR)
    elif sum(p - len(L) for L, _R in LR) == 0:
        q = p * p
    else:
        return None
    return (n0 + p, q) if q else None


def build(p, cap=200000):
    rule = p['rule']
    got = column_period(rule)
    if got is None:
        return None
    n0, q = got
    if q > 64:
        return None
    ws = ecarow.rows(rule, 2 * (n0 + q) + 40)
    col = [int(ws[n][n]) for n in range(len(ws))]
    # the proved period is q from n0; the actual one is a divisor, found inside one window
    for m0 in range(n0 + 1):
        for d in sorted(x for x in range(1, q + 1) if q % x == 0):
            if all(col[n] == col[n + d] for n in range(m0, len(col) - d)):
                n0, q = m0, d
                break
        else:
            continue
        break
    B = p['base']
    S = (2 * q if B else q) + n0 + q + 4
    if S > 200:
        return None
    return {'rule': rule, 'base': B, 'n0': n0, 'q': q, 'col': col, 'S': S}


def terms(b, N):
    col = b['col']
    if N >= len(col):
        ws = ecarow.rows(b['rule'], N + 1)
        col = b['col'] = [int(ws[n][n]) for n in range(len(ws))]
    B = b['base']
    if B is None:
        return col[:N + 1]
    out, v = [], 0
    for n in range(N + 1):
        v = v * B + col[n]
        out.append(v)
    return out


def certify(b, upto=200):
    ws = ecarow.rows(b['rule'], upto)
    col = [int(ws[n][n]) for n in range(len(ws))]
    k = 0
    for n in range(b['n0'], len(col) - b['q']):
        if col[n] != col[n + b['q']]:
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
