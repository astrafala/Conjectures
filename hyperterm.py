#!/usr/bin/env python3
"""Settle a conjectured recurrence directly from a closed form for a(n).

No generating function is involved, which is the point: the largest remaining pile of
open conjectures sits on entries that post no g.f. at all, but many of them do post an
explicit formula --

    a(n) = binomial(2*n-1, n-3) - binomial(2*n-1, n-6)
    a(n) = n*(n-1)!*((n-2)*(n-1)! - 1)/2
    a(n) = (n+1)*(n+2)*(2*n+3)/6 * 2^n * n!

-- and each of those is a sum of finitely many hypergeometric terms. For such a term c,
the shift quotient c(n-i)/c(n) is a RATIONAL function of n, computable exactly. So for
a(n) = sum_j c_j(n),

    sum_i p_i(n) a(n-i)  =  sum_j c_j(n) * S_j(n),    S_j(n) = sum_i p_i(n) c_j(n-i)/c_j(n)

with every S_j rational. Terms are grouped into similarity classes -- c and d are similar
when c/d is rational -- and within a class the whole contribution collapses to one term
times one rational function, which cancel() decides exactly.

Pairwise dissimilar hypergeometric terms are linearly independent over the rational
functions (Petkovsek-Wilf-Zeilberger), so the recurrence holds identically if and only if
every class contributes zero. That makes the test a decision procedure, not a search: it
returns proved or refuted, never "maybe".

The excluded n are computed, not waved at: the identity is an identity of rational
functions, so it holds wherever no denominator vanishes and every term is defined.
"""
import sympy as sp

n = sp.Symbol('n')


def shift_ratio(c, i):
    """c(n-i)/c(n) as a rational function of n, or None if it is not one."""
    if i == 0:
        return sp.Integer(1)
    try:
        r = sp.simplify(sp.combsimp(sp.expand_func(c.subs(n, n - i) / c)))
    except Exception:
        return None
    r = sp.cancel(sp.together(r))
    if not r.is_rational_function(n):
        try:
            r = sp.cancel(sp.together(sp.simplify(sp.gammasimp(r))))
        except Exception:
            return None
    return r if r.is_rational_function(n) else None


def is_hyper(c, order):
    """A term is usable when every shift it needs has a rational quotient."""
    return all(shift_ratio(c, i) is not None for i in range(1, order + 1))


def terms_of(e):
    """The closed form as a list of summands, expanded just enough to separate them."""
    e = sp.expand(sp.powsimp(sp.together(e), force=False))
    out = sp.Add.make_args(sp.expand(e))
    return [t for t in out if t != 0]


def similar(a, b):
    """a and b are similar when a/b is a rational function of n."""
    try:
        r = sp.cancel(sp.together(sp.simplify(sp.combsimp(a / b))))
    except Exception:
        return None
    return r if r.is_rational_function(n) else None


def classes(ts):
    """Group the summands into similarity classes: (representative, [rational factors])."""
    out = []
    for t in ts:
        for cls in out:
            r = similar(t, cls[0])
            if r is not None:
                cls[1].append(r)
                break
        else:
            out.append([t, [sp.Integer(1)]])
    return out


def residual(ps, e):
    """Per-class residuals of sum_i p_i(n) a(n-i), or None if a term is not usable.

    Returns a list of (representative term, rational function). The recurrence holds
    identically iff every rational function is zero.
    """
    order = len(ps) - 1
    ts = terms_of(e)
    if not ts:
        return None
    cls = classes(ts)
    out = []
    for rep, facs in cls:
        rats = []
        for i in range(order + 1):
            if ps[i] == 0:
                continue
            rho = shift_ratio(rep, i)
            if rho is None:
                return None
            # every member of the class is rep times a rational function f(n);
            # its contribution is p_i(n) * f(n-i) * rep(n-i)
            for f in facs:
                fi = sp.cancel(sp.together(f.subs(n, n - i)))
                if not fi.is_rational_function(n):
                    return None
                rats.append(sp.cancel(ps[i] * fi * rho))
        S = sp.cancel(sp.together(sum(rats)))
        out.append((rep, S))
    return out


def excluded(out, ps):
    """The n where the argument does not apply: poles of the class residuals."""
    bad = set()
    for rep, S in out:
        den = sp.denom(sp.cancel(sp.together(S)))
        if den.free_symbols:
            try:
                for r in sp.solve(sp.Eq(den, 0), n):
                    if r.is_real:
                        bad.add(sp.nsimplify(r))
            except Exception:
                pass
    return sorted(bad, key=lambda t: sp.re(t) if t.is_number else 0)


def verdict(ps, e):
    """(True, classes) proved; (False, classes) refuted; (None, why) not applicable."""
    out = residual(ps, e)
    if out is None:
        return None, "a summand is not hypergeometric in n"
    if all(sp.cancel(S) == 0 for _, S in out):
        return True, out
    return False, out


def is_zero_sum(expr, var=None):
    """Decide whether a finite sum of hypergeometric terms is identically zero.

    Used where the expression is built explicitly rather than as sum_i p_i a(n-i): the
    two parity halves of a recurrence, for instance. Same argument as
    Proposition 1 -- group into similarity classes, and each class contributes its
    representative times the sum of its rational factors, which cancel() decides.

    Returns (True/False, classes) or (None, why).
    """
    v = var or n
    e = sp.expand(sp.together(expr))
    if e == 0:
        return True, []
    ts = [t for t in sp.Add.make_args(e) if t != 0]
    out = []
    for t in ts:
        for cls in out:
            try:
                r = sp.cancel(sp.together(sp.simplify(sp.combsimp(t / cls[0]))))
            except Exception:
                return None, "a quotient of summands could not be reduced"
            if r.is_rational_function(v):
                cls[1] = sp.cancel(cls[1] + r)
                break
        else:
            out.append([t, sp.Integer(1)])
    for rep, S in out:
        try:
            if not sp.cancel(sp.together(rep / rep)).is_rational_function(v):
                return None, "a summand is not hypergeometric"
        except Exception:
            return None, "a summand is not hypergeometric"
    if all(sp.cancel(S) == 0 for _, S in out):
        return True, out
    return False, out
