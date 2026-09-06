"""Berlekamp--Massey: the MINIMAL linear recurrence of a sequence, exactly.

Some entries do not print their conjectured recurrence at all --- they say "Empirical
recurrence of order 55 (see link above)", and the link is not in the local copy. The
recurrence itself cannot be read, but the conjecture can still be settled, because of a
uniqueness argument:

    a walk count on S vertices satisfies SOME monic recurrence of order at most S
    (Cayley--Hamilton), so Berlekamp--Massey applied to its first 2S terms returns the
    MINIMAL one exactly. If that minimal order equals the order the entry states, then any
    recurrence of that order the sequence satisfies has a characteristic polynomial that is a
    multiple of the minimal polynomial and of the same degree, hence equal to it. The entry's
    recurrence is therefore the one computed here, whatever its file says.

When the stated order is larger than the minimal one, no such uniqueness holds and the entry
is left alone: its recurrence is some multiple of the minimal polynomial, and which multiple
cannot be recovered without reading it.
"""
from fractions import Fraction


def bm(s):
    """(order, [c_1..c_L]) with s[n] = sum_i c_i s[n-i], over the rationals."""
    C = [Fraction(1)]
    B = [Fraction(1)]
    L, m, b = 0, 1, Fraction(1)
    for n in range(len(s)):
        d = s[n] + sum(C[i] * s[n - i] for i in range(1, L + 1))
        if d == 0:
            m += 1
            continue
        coef = d / b
        T = C[:]
        if len(C) < len(B) + m:
            C = C + [Fraction(0)] * (len(B) + m - len(C))
        for i in range(len(B)):
            C[i + m] -= coef * B[i]
        if 2 * L <= n:
            L = n + 1 - L
            B, b, m = T, d, 1
        else:
            m += 1
    return L, [-C[i] for i in range(1, L + 1)]


def bm_mod(s, p):
    """the order only, computed in Z/p: a cheap filter before the exact run."""
    C = [1]
    B = [1]
    L, m, b = 0, 1, 1
    for n in range(len(s)):
        d = (s[n] + sum(C[i] * s[n - i] for i in range(1, L + 1))) % p
        if d == 0:
            m += 1
            continue
        coef = d * pow(b, p - 2, p) % p
        T = C[:]
        if len(C) < len(B) + m:
            C = C + [0] * (len(B) + m - len(C))
        for i in range(len(B)):
            C[i + m] = (C[i + m] - coef * B[i]) % p
        if 2 * L <= n:
            L = n + 1 - L
            B, b, m = T, d, 1
        else:
            m += 1
    return L
