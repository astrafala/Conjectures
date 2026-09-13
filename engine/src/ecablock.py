#!/usr/bin/env python3
"""ON and OFF cell counts of the elementary automata whose row does NOT grow at its ends.

`ecacount' asks the row for

    w(n + p) = L_r + w(n) + R_r,

growth at the two ends only, and 56 of the 256 rules refuse it -- among them 109, 131, 133 and
141, none of them chaotic, and 67 entries sit on them.  `ecashape' replaces that with the block
template

    w(n0 + r + j*p) = B_0 . Q_1^j . B_1 . ... . Q_m^j . B_m,

which is where those rules actually live: rule 133 gains `1010' in the middle of a periodic
run and rule 141 gains `10' in one run and `11' in another.  The end-growth shape is the case
m = 2 with the outer fixed blocks empty, so nothing already certified is lost; this module
takes only the rules the older one refuses, so no entry is claimed twice.

The count is immediate.  sum |Q_i| = 2p because the row has width 2n+1, and

    on(n0 + r + j*p) = sum_i ones(B_i) + j * sum_i ones(Q_i)

is linear in j, hence quasi-linear in n with period p: annihilated by (z^p - 1)^2.  OFF is
2n + 1 - on and (z - 1)^2 divides (z^p - 1)^2, so it has the same annihilator; a running total
contributes one further factor (z - 1).  The numerator's degree is below n0 + 2p, so the
recurrence of order 2p + 1 is in force from index n0 + 2p + 1 and S = n0 + 2p + 6 covers all
four wordings with room to spare.

Why the template is a theorem rather than a fit is argued in `ecashape': p steps of a radius-1
map have radius p, so once the p-step map is verified by simulation at two consecutive j whose
periodic runs are longer than the dependence cone, locality carries it to every larger j.
"""
import ecacount
import ecarow
import ecashape

HEAD = ecacount.HEAD
_EDGE = {}
_SHAPE = {}


def _edge_shape(rule):
    """whether `ecacount' already has this rule; that engine keeps the ones it can."""
    if rule not in _EDGE:
        _EDGE[rule] = ecacount.build({'rule': rule, 'on': True, 'total': False}) is not None
    return _EDGE[rule]


def parse_name(nm):
    p = ecacount.parse_name(nm)
    if p is None or _edge_shape(p['rule']):
        return None
    return p


def build(p, cap=200000):
    # Four entries share a rule, and finding its template costs up to a minute; a
    # sweep that recomputes it per entry spends most of its budget on the same answer.
    rule = p['rule']
    if rule not in _SHAPE:
        ws = ecarow.rows(rule, 90)
        _SHAPE[rule] = (ws, ecashape.shape(ws, rule=rule))
    ws, sh = _SHAPE[rule]
    if sh is None:
        return None
    n0, per, tem = sh
    return {'rule': p['rule'], 'n0': n0, 'p': per, 'tem': tem, 'ws': ws,
            'on': p['on'], 'total': p['total'], 'S': n0 + 2 * per + 6}


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


def certify(b, upto=90):
    """how many steps past the settling point the template was checked before the proof."""
    ws = ecarow.rows(b['rule'], upto)
    n0, per, tem = b['n0'], b['p'], b['tem']
    k = 0
    for n in range(n0, len(ws)):
        r = (n - n0) % per
        j = (n - n0) // per
        if ecashape.render(tem[r], j) != ws[n]:
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
