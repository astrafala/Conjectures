#!/usr/bin/env python3
"""Right division in the Ore algebra Q(n)[N], and what it proves.

Some entries state a recurrence that is NOT labelled a conjecture -- contributed as
"Recurrence: ..." and derived by whoever posted it -- alongside a separate one that IS
still conjectured. Nothing about generating functions is needed to connect them.

Write a recurrence as an operator in the shift N, where N f(n) = f(n+1). If the proven
operator P annihilates the sequence and the conjectured operator C factors as C = Q*P
for some Q in the algebra, then

    C(a) = Q(P(a)) = Q(0) = 0,

so the conjecture holds too. Finding Q is right division: exactly polynomial division,
except that moving N past a coefficient shifts it, N*q(n) = q(n+1)*N. Every step is
rational-function arithmetic in n, so a zero remainder is a proof.

Two things the division does not by itself give, and both are checked separately:

  * the coefficients of Q have denominators, and the argument says nothing at the
    finitely many n where one of them vanishes;
  * P itself is only asserted from some index onwards.

So the conclusion is a statement about all sufficiently large n, with the exceptional
set computed explicitly rather than waved at.
"""
import sympy as sp

n = sp.Symbol('n')


def to_operator(ps):
    """[p_0, ..., p_r] for sum_i p_i(n) a(n-i) = 0  ->  coefficients of N^0..N^r.

    Substituting n -> n + r turns a(n-i) into a(n + r - i), so the coefficient of N^j
    is p_{r-j}(n + r).
    """
    r = len(ps) - 1
    return [sp.cancel(sp.expand(ps[r - j].subs(n, n + r))) for j in range(r + 1)]


def _trim(c):
    c = [sp.cancel(t) for t in c]
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return c


def shift_mul(c, d):
    """N^d * (operator c): every coefficient shifts by d and the degree rises by d."""
    return [sp.Integer(0)] * d + [sp.cancel(t.subs(n, n + d)) for t in c]


def right_divide(C, P, maxsteps=40):
    """C = Q*P + R in Q(n)[N]. Returns (Q, R) as coefficient lists."""
    C, P = _trim(list(C)), _trim(list(P))
    if len(P) == 1 and P[0] == 0:
        raise ValueError("divisor is zero")
    R = list(C)
    Q = [sp.Integer(0)] * max(1, len(C) - len(P) + 1)
    steps = 0
    while True:
        R = _trim(R)
        if len(R) < len(P) or (len(R) == 1 and R[0] == 0):
            break
        steps += 1
        if steps > maxsteps:
            raise ValueError("division did not terminate")
        d = len(R) - len(P)
        lead_P = P[-1].subs(n, n + d)
        if sp.cancel(lead_P) == 0:
            raise ValueError("leading coefficient of the divisor vanishes after shifting")
        c = sp.cancel(R[-1] / lead_P)
        Q[d] = sp.cancel(Q[d] + c)
        sub = shift_mul(P, d)
        for i, t in enumerate(sub):
            R[i] = sp.cancel(R[i] - c * t)
        R[-1] = sp.Integer(0)
    return _trim(Q), _trim(R)


def is_zero(R):
    return all(sp.cancel(t) == 0 for t in R)


def exceptional_set(Q):
    """The n at which some coefficient of Q is undefined: the argument skips those."""
    bad = set()
    for t in Q:
        den = sp.denom(sp.cancel(sp.together(t)))
        if den.free_symbols:
            for r in sp.solve(sp.Eq(den, 0), n):
                if r.is_real:
                    bad.add(sp.nsimplify(r, rational=True))
    return sorted(bad, key=lambda t: sp.re(t) if t.is_number else 0)


def trivial(Q):
    """Q of degree 0 means the two recurrences are the same one rescaled."""
    return len(Q) == 1


def mul(a, b):
    """Product a*b in Q(n)[N], both given as coefficient lists of N^0..N^r."""
    out = [sp.Integer(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, t in enumerate(shift_mul(b, i)):
            out[j] = sp.cancel(out[j] + ai * t)
    return _trim(out)


def to_backward(q):
    """Coefficients of N^0..N^r  ->  p_0..p_r for sum_i p_i(n) a(n-i) = 0.

    The two conventions are related by n -> n - r: sum_j q_j(n) a(n+j) = 0 becomes
    sum_j q_j(n-r) a(n-r+j) = 0, and setting i = r - j gives p_i = q_{r-i}(n-r).
    """
    r = len(q) - 1
    return [sp.expand(sp.cancel(q[r - i].subs(n, n - r))) for i in range(r + 1)]
