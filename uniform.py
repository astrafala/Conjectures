"""One interface over all the transfer engines.

Each engine grew its own shape: some return `(states, adj)` and count with an all-ones vector,
some return `(adj, start, end)`, some add a scaling denominator, some expose `avals` indexed by
the entry's own n. That was fine while each had its own sweep, but the table sweeps need to try
every engine on a rewritten name, and without a common interface the newer engines were simply
absent from them -- which is why the row sweep proved nothing at first while the names parsed
perfectly well.

`read` returns (engine, parsed); `terms` returns the model's counts indexed by walk step with
any scaling already divided out; `threshold` returns the last index at which the conjectured
recurrence fails, in that same walk index. Callers align the walk index to the entry's own n by
matching the published terms, exactly as before.
"""
import importlib
from fractions import Fraction
from math import factorial

ENG = ['transfer3', 'transfer47', 'transfer46', 'transfer45', 'transfer44', 'transfer43', 'transfer42', 'transfer41', 'transfer40', 'transfer38', 'transfer37', 'transfer36', 'transfer35', 'transfer34', 'transfer33', 'transfer32', 'transfer31', 'transfer30', 'transfer29', 'transfer28', 'transfer27', 'transfer26', 'transfer25', 'transfer24', 'transfer23', 'transfer17', 'transfer22', 'transfer21', 'transfer20', 'transfer19',
       'transfer18', 'transfer9', 'transfer6', 'transfer16', 'transfer12', 'transfer10',
       'transfer8', 'transfer14', 'transfer11', 'transfer15', 'transfer13', 'transfer7',
       'transfer48', 'transfer49', 'transfer50', 'transfer51', 'transfer52', 'transfer53', 'transfer54', 'transfer55', 'transfer56', 'transfer57', 'transfer58', 'transfer59', 'transfer60', 'transfer61', 'transfer62', 'transfer63', 'transfer64', 'transfer65', 'transfer66', 'transfer67', 'transfer68', 'transfer69', 'transfer70', 'transfer71', 'transfer72']
M = {e: importlib.import_module(e) for e in ENG}
T2 = importlib.import_module('transfer2')
T19 = M['transfer19']
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
PAIR = ('transfer18', 'transfer19', 'transfer24', 'transfer26', 'transfer27',
        'transfer28', 'transfer32', 'transfer40', 'transfer41', 'transfer43',
        'transfer44', 'transfer46', 'transfer47',
        'transfer48', 'transfer50', 'transfer51', 'transfer52', 'transfer53',
        'transfer57', 'transfer58', 'transfer59', 'transfer60', 'transfer61', 'transfer63', 'transfer64', 'transfer65', 'transfer66', 'transfer67', 'transfer68', 'transfer69', 'transfer70', 'transfer71', 'transfer72')          # (adj, start, end, S)
DEN = ('transfer20', 'transfer21', 'transfer22', 'transfer25', 'transfer38',
       'transfer42', 'transfer45', 'transfer49', 'transfer54', 'transfer55', 'transfer56', 'transfer62')   # (adj, start, end, S, den)
PLAIN = ('transfer3', 'transfer6', 'transfer17', 'transfer23', 'transfer29', 'transfer30', 'transfer31', 'transfer33', 'transfer34', 'transfer35', 'transfer36', 'transfer37')   # (states, adj), all-ones vectors


def read(nm):
    for en in ENG:
        try:
            p = M[en].parse_name(nm)
        except Exception:
            continue
        if p:
            return en, p
    return None


def build(en, p, cap):
    try:
        if en == 'transfer3':
            cols, al, _, _ = p
            if (al + 1) ** cols > cap:
                return None
            return M[en].build(*p)
        if en in ('transfer17', 'transfer23', 'transfer29', 'transfer30', 'transfer31', 'transfer33', 'transfer34', 'transfer35', 'transfer36', 'transfer37', 'transfer6'):
            b = M[en].build(p) if en == 'transfer6' else M[en].build(p, cap=cap)
            if b is None or not b[0]:
                return None
            if en == 'transfer6' and len(b[0]) > cap:
                return None
            return b
        if en == 'transfer7':
            # transfer7's build takes no cap and returns (adj, start, blocks); it was falling
            # through to the generic call, which passes cap= and raises TypeError -- swallowed
            # by the except below, so every transfer7 entry came back "too big" when the model
            # builds in seconds. A silent refusal, of the kind this file exists to prevent.
            b = M[en].build(p)
            if not b or not b[0] or len(b[0]) > cap:
                return None
            return b
        if en in PAIR or en in DEN:
            b = M[en].build(p, cap=cap)
            return b if b and b[0] else None
        b = M[en].build(p, cap=cap)
        return b if b else None
    except Exception:
        return None


def size(en, p, b):
    if en == 'transfer7':
        return len(b[0])
    if en in PLAIN:
        return len(b[0])
    if en in PAIR:
        return b[3]
    if en in DEN:
        return b[3]
    return len(b[0])


def terms(en, p, b, N):
    """model counts by walk step, scaling divided out; None where not an integer."""
    if en == 'transfer3':
        st, adj = b
        return [Fraction(v) for v in T2.terms(adj, len(st), N)]
    if en in ('transfer6', 'transfer17', 'transfer23', 'transfer29', 'transfer30', 'transfer31', 'transfer33', 'transfer34', 'transfer35', 'transfer36', 'transfer37'):
        st, adj = b
        f = p['frac']
        return [Fraction(v, f) for v in M[en].terms(adj, len(st), N)]
    if en in PAIR:
        adj, start, end, S = b
        f = p['frac']
        return [Fraction(v, f) for v in M[en].terms(adj, start, end, N)]
    if en == 'transfer25':
        adj, start, end, S, den = b        # weighted adjacency, its own matvec
        f = den * p.get('frac', 1)
        return [Fraction(v, f) for v in M[en].terms(adj, start, end, N)]
    if en in DEN:
        adj, start, end, S, den = b
        f = den * p.get('frac', 1)
        return [Fraction(v, f) for v in M[en].terms(adj, start, end, N)]
    if en == 'transfer7':
        adj, start, _ = b
        f = p['frac'] * factorial(p['K'])
        return [Fraction(v, f) for v in M[en].terms(adj, start, N)]
    if en == 'transfer10':
        adj, start, _ = b
        f = factorial(p['K']) * p['frac']
        return [None if q is None else Fraction(q, f)
                for q in M[en].avals(adj, start, p, N)]
    adj, start, end, _ = b
    f = p['frac'] * (factorial(p['K']) if en in SCALED else 1)
    return [None if q is None else Fraction(q, f)
            for q in M[en].avals(adj, start, end, p, N)]


def threshold(en, p, b, coeffs, order):
    if en == 'transfer3':
        st, adj = b
        return T2.threshold(adj, len(st), coeffs, order)
    if en in ('transfer6', 'transfer17', 'transfer23', 'transfer29', 'transfer30', 'transfer31', 'transfer33', 'transfer34', 'transfer35', 'transfer36', 'transfer37'):
        st, adj = b
        return M[en].threshold(adj, len(st), coeffs, order)
    if en in PAIR:
        adj, start, end, S = b
        return T19.threshold(adj, start, end, coeffs, order, S)
    if en == 'transfer25':
        adj, start, end, S, den = b
        return M[en].threshold(adj, start, end, coeffs, order, S)
    if en in DEN:
        adj, start, end, S, den = b
        return T19.threshold(adj, start, end, coeffs, order, S)
    if en == 'transfer7':
        adj, start, _ = b
        return M[en].threshold(adj, start, coeffs, order)
    if en == 'transfer10':
        adj, start, _ = b
        return M[en].threshold(adj, start, coeffs, order, p)
    adj, start, end, _ = b
    return M[en].threshold(adj, start, end, coeffs, order, p)
