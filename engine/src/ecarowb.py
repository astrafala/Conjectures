#!/usr/bin/env python3
"""The row of an elementary automaton read as a numeral, for the rules that grow in the middle.

`ecarow' asks the row to grow only at its ends, w(n+p) = L_r + w(n) + R_r, and 56 of the 256
rules refuse.  `ecashape' shows where those rules actually live: the row is a concatenation of
fixed and repeated blocks,

    w(n0 + r + j*p) = B_0 . Q_1^j . B_1 . ... . Q_m^j . B_m,

each Q_i gaining one copy every p steps.  Reading that as a numeral in base B is still an
exact linear recurrence.  Write s_i = |Q_i| + |Q_{i+1}| + ... + |Q_m| for the number of digits
to the right of the i-th run, so s_1 = 2p.  Then

    a(j) = v(B_0) B^{s_1 + c_0}
         + sum_i [ v(Q_i) (B^{|Q_i| j} - 1)/(B^{|Q_i|} - 1) B^{s_{i+1} + c_i}
                   + v(B_i) B^{s_{i+1} + c_i} ]
         + v(B_m),

where the c's are the fixed digit counts to the right and do not depend on j.  Every term is a
constant times B^{s_i j} or a constant, so along the class a is a Z-linear combination of
    B^{s_1 j}, B^{s_2 j}, ..., B^{s_m j}, 1,
and is annihilated by prod_i (T - B^{s_i}) (T - 1) with T the shift by p.  Taking the DISTINCT
roots that occur across the p residue classes and pulling each back to z^p - lambda gives a
monic annihilator; the pre-period raises the numerator's degree, so

    S = (number of distinct roots) * p + n0 + p.

The end-growth shape is the case m = 2 with B_0 and B_2 empty, where s_1 = |L|+|R| and
s_2 = |R| -- exactly the two roots `ecarow' already uses -- so this is a strict generalisation
and this module takes only the rules that engine refuses.
"""
import ecarow
import ecashape

HEAD = ecarow.HEAD
_EDGE = {}
_SHAPE = {}


def _edge_shape(rule):
    if rule not in _EDGE:
        ws = ecarow.rows(rule, 80)
        import ecacount
        _EDGE[rule] = ecarow.shape(ws) is not None or ecacount.shape_res(ws) is not None
    return _EDGE[rule]


def parse_name(nm):
    p = ecarow.parse_name(nm)
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
    B = p['base']
    lam = {1}
    for parts in tem.values():
        s = 0
        for kind, blk in reversed(parts):
            if kind == 'q':
                s += len(blk)
                lam.add(B ** s)
        if s != 2 * per:
            return None                 # the widths must add to 2p, or the row is not a cone
    return {'rule': p['rule'], 'B': B, 'n0': n0, 'p': per, 'tem': tem, 'ws': ws,
            'S': len(lam) * per + n0 + per}


def terms(b, N):
    return ecarow.terms(b, N)


def certify(b, upto=90):
    ws = ecarow.rows(b['rule'], upto)
    n0, per, tem = b['n0'], b['p'], b['tem']
    k = 0
    for n in range(n0, len(ws)):
        if ecashape.render(tem[(n - n0) % per], (n - n0) // per) != ws[n]:
            break
        k += 1
    return k


def threshold(b, coeffs, order):
    return ecarow.threshold(b, coeffs, order)
