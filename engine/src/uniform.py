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

ENG = ['repval', 'permrow', 'ca2dcount', 'ca2d', 'ecarow', 'cuspdim', 'transfer96', 'transfer95', 'transfer94', 'transfer93', 'transfer92', 'transfer91', 'denumerant', 'transfer89', 'transfer87', 'transfer86', 'transfer85', 'transfer84', 'transfer83', 'transfer82', 'transfer81', 'transfer47', 'transfer77', 'transfer3', 'transfer46', 'transfer45', 'transfer44', 'transfer43', 'transfer42', 'transfer41', 'transfer40', 'transfer38', 'transfer37', 'transfer36', 'transfer35', 'transfer34', 'transfer33', 'transfer32', 'transfer31', 'transfer30', 'transfer29', 'transfer28', 'transfer27', 'transfer26', 'transfer25', 'transfer24', 'transfer23', 'transfer17', 'transfer22', 'transfer21', 'transfer20', 'transfer19', 'transfer18', 'transfer9', 'transfer6', 'transfer16', 'transfer12', 'transfer10', 'transfer8', 'transfer14', 'transfer11', 'transfer15', 'transfer13', 'transfer7', 'transfer48', 'transfer49', 'transfer50', 'transfer51', 'transfer52', 'transfer53', 'transfer54', 'transfer55', 'transfer56', 'transfer57', 'transfer58', 'transfer59', 'transfer60', 'transfer61', 'transfer62', 'transfer63', 'transfer64', 'transfer65', 'transfer66', 'transfer67', 'transfer68', 'transfer69', 'transfer70', 'transfer71', 'transfer72', 'transfer73', 'transfer74', 'transfer75']
M = {e: importlib.import_module(e) for e in ENG}
T2 = importlib.import_module('transfer2')
T19 = M['transfer19']
import lumpauto
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
PAIR = ('transfer94', 'transfer18', 'transfer19', 'transfer24', 'transfer26', 'transfer27',
        'transfer28', 'transfer32', 'transfer40', 'transfer41', 'transfer43',
        'transfer44', 'transfer46', 'transfer47',
        'transfer48', 'transfer50', 'transfer51', 'transfer52', 'transfer53',
        'transfer57', 'transfer58', 'transfer59', 'transfer60', 'transfer61', 'transfer63', 'transfer64', 'transfer65', 'transfer66', 'transfer67', 'transfer68', 'transfer69', 'transfer70', 'transfer71', 'transfer72', 'transfer73', 'transfer74', 'transfer75', 'transfer77', 'transfer81', 'transfer82', 'transfer83', 'transfer84', 'transfer85', 'transfer86', 'transfer87', 'transfer89', 'denumerant', 'transfer91', 'transfer92', 'transfer93')          # (adj, start, end, S)
DEN = ('transfer20', 'transfer21', 'transfer22', 'transfer25', 'transfer38',
       'transfer42', 'transfer45', 'transfer49', 'transfer54', 'transfer55', 'transfer56', 'transfer62')   # (adj, start, end, S, den)
PLAIN = ('transfer3', 'transfer6', 'transfer17', 'transfer23', 'transfer29', 'transfer30', 'transfer31', 'transfer33', 'transfer34', 'transfer35', 'transfer36', 'transfer37')   # (states, adj), all-ones vectors


# A parser that raises on a name it ought to read makes that name unreachable, and the
# `continue` below hides it: the name simply comes back as "no engine". That is the silent
# refusal this project has paid for five times, so the raises are counted and kept. Nothing
# stops --- one broken parser must not take down a sweep --- but nothing is invisible either.
RAISED = {}


def read(nm):
    for en in ENG:
        try:
            p = M[en].parse_name(nm)
        except Exception as exc:
            RAISED.setdefault(en, []).append((nm[:70], type(exc).__name__))
            continue
        if p:
            return en, p
    return None


IMAGE = ('transfer95', 'transfer96', 'cuspdim', 'ecarow', 'ca2d', 'ca2dcount', 'permrow',
         'repval')   # build returns a dict, terms are the engine's own


def build(en, p, cap):
    try:
        if en in IMAGE:
            return M[en].build(p, cap)
        if en == 'transfer3':
            cols, al, _, _ = p
            if (al + 1) ** cols > cap:
                return None
            return M[en].build(*p)
        if en == 'transfer17':
            # the pair state is (alpha+1)^(2W) and almost all of it is redundant; the
            # pair-free construction merges before the states exist and is both smaller and
            # faster, so it is what the sweep uses. Nothing falls back to the old build: if
            # this one passes the cap, the pair state passed it long ago.
            return M[en].build_pairfree(p, cap=cap)
        if en in ('transfer23', 'transfer29', 'transfer30', 'transfer31', 'transfer33', 'transfer34', 'transfer35', 'transfer36', 'transfer37', 'transfer6'):
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
            if b is None:
                return None
            # an engine that supplies its own terms and threshold need not be a digraph at
            # all: the test below exists to catch a transfer matrix that failed to build,
            # and applying it to a model that never had one would refuse it silently
            if hasattr(M[en], 'terms_p') and hasattr(M[en], 'threshold_p'):
                return b
            return b if b[0] else None
        b = M[en].build(p, cap=cap)
        return b if b else None
    except Exception:
        return None


def size(en, p, b):
    if en in IMAGE:
        return b['S']
    if en == 'transfer17':
        return b[3]
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
    if en in IMAGE:
        t = M[en].terms(b, N + p.get('base', 0) + 2)
        # transfer96 indexes by WORD LENGTH; the entry indexes by its own n, and a name reading
        # "length n+4" puts a(1) at length 5. Leaving the offset for the caller's shift search
        # to find made 32 of these look like "model does not match DATA" -- the search window
        # is only a few steps wide by design, because a wide one can fit a wrong model.
        b0 = p.get('base', 0) if en == 'transfer96' else 0
        return [Fraction(v) for v in t[b0:]]
    if en == 'transfer3':
        st, adj = b
        return [Fraction(v) for v in T2.terms(adj, len(st), N)]
    if en == 'transfer17':
        adj, start, end, S = b
        return [Fraction(v, p['frac']) for v in T19.terms(adj, start, end, N)]
    if en in ('transfer6', 'transfer23', 'transfer29', 'transfer30', 'transfer31', 'transfer33', 'transfer34', 'transfer35', 'transfer36', 'transfer37'):
        st, adj = b
        f = p['frac']
        return [Fraction(v, f) for v in M[en].terms(adj, len(st), N)]
    if en in PAIR:
        adj, start, end, S = b
        f = p['frac']
        # an engine whose model is exact only past some board size supplies its own terms,
        # so the exceptional sizes can be counted on their own boards instead of by the
        # matrix. Everything else keeps the plain walk count.
        if hasattr(M[en], 'terms_p'):
            return [Fraction(v, f) for v in M[en].terms_p(p, b, N)]
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
    if en in IMAGE:
        return M[en].threshold(b, coeffs, order)
    if en == 'transfer3':
        st, adj = b
        return T2.threshold(adj, len(st), coeffs, order)
    if en == 'transfer17':
        adj, start, end, S = b
        adj, start, end, S = lumpauto.lump(adj, start, end)
        return T19.threshold(adj, start, end, coeffs, order, S)
    if en in ('transfer6', 'transfer23', 'transfer29', 'transfer30', 'transfer31', 'transfer33', 'transfer34', 'transfer35', 'transfer36', 'transfer37'):
        st, adj = b
        # The annihilation test runs until S consecutive residuals vanish, so its cost is
        # governed by the state count, and these models are enormously redundant: the
        # 3 X 3 subblock families come out at 59049 states and merge to 60. Without this
        # the test is hopeless on anything but the narrowest widths, which is why a hundred
        # and forty entries an engine already read had never been settled. States with the
        # same future contribute identically to iota^T M^n tau, so merging changes no count;
        # the threshold returned is the threshold of the same sequence, and the unmerged S a
        # paper quotes as its Cayley--Hamilton bound is still a valid bound.
        S = len(st)
        adj2, start2, end2, S2 = lumpauto.lump(adj, [1] * S, [1] * S)
        return T19.threshold(adj2, start2, end2, coeffs, order, S2)
    if en in PAIR:
        if hasattr(M[en], 'threshold_p'):
            # the same engines raise their own floor: a residual reading a term the matrix
            # does not certify cannot be certified by it either, so the bound moves out
            return M[en].threshold_p(p, b, coeffs, order)
        adj, start, end, S = b
        # States with the same future contribute identically to iota^T M^n tau, so merging
        # them changes no count. The annihilation test's length is governed by the state
        # count -- it runs until S consecutive residuals vanish -- so this is not tidying, it
        # is what makes the larger models decidable at all. The threshold it returns is the
        # threshold of the same sequence, and a paper quoting the unmerged S as its
        # Cayley-Hamilton bound is still quoting a valid bound, merely a generous one.
        adj, start, end, S = lumpauto.lump(adj, start, end)
        return T19.threshold(adj, start, end, coeffs, order, S)
    if en == 'transfer25':
        adj, start, end, S, den = b
        return M[en].threshold(adj, start, end, coeffs, order, S)
    if en in DEN:
        adj, start, end, S, den = b
        # same as the pair engines: the test's length is governed by the state count, so
        # merging states with identical futures is what makes the larger models decidable
        adj, start, end, S = lumpauto.lump(adj, start, end)
        return T19.threshold(adj, start, end, coeffs, order, S)
    if en == 'transfer7':
        adj, start, _ = b
        return M[en].threshold(adj, start, coeffs, order)
    if en == 'transfer10':
        adj, start, _ = b
        return M[en].threshold(adj, start, coeffs, order, p)
    adj, start, end, _ = b
    return M[en].threshold(adj, start, end, coeffs, order, p)
