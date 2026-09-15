"""Find the minimal constant-coefficient recurrence of a sequence, exactly.

Used only to PROPOSE a recurrence; the proposal is then proved by the annihilation test
against the transfer matrix, so a wrong guess here cannot become a claim.
"""
from fractions import Fraction


def solve(rows, rhs):
    n = len(rows[0])
    m = [list(map(Fraction, r)) + [Fraction(v)] for r, v in zip(rows, rhs)]
    piv = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, len(m)) if m[i][c]), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        inv = m[r][c]
        m[r] = [x / inv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c]:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        piv.append(c)
        r += 1
        if r == len(m):
            break
    for i in range(r, len(m)):
        if not any(m[i][:n]) and m[i][n]:
            return None
    x = [Fraction(0)] * n
    for i, c in enumerate(piv):
        x[c] = m[i][n]
    return x


def minimal(terms, maxorder=None):
    """terms[0..] -> (order, [c_1..c_r]) with a(n) = sum c_i a(n-i), or None."""
    N = len(terms)
    maxorder = maxorder or (N - 1) // 2
    for r in range(1, maxorder + 1):
        rows = [[terms[n - i] for i in range(1, r + 1)] for n in range(r, N)]
        rhs = [terms[n] for n in range(r, N)]
        if len(rows) < r:
            break
        c = solve(rows, rhs)
        if c is None:
            continue
        if all(sum(ci * terms[n - i - 1] for i, ci in enumerate(c)) == terms[n]
               for n in range(r, N)):
            if all(x.denominator == 1 for x in c):
                return r, [int(x) for x in c]
            return r, c
    return None
