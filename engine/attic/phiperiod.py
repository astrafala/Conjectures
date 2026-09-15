#!/usr/bin/env python3
"""Exact eventual period of a(n) mod k for sequences a(n) = Sum_j c_j * j! * S(n,j).

Every entry in the Bala phi(k) family has e.g.f. G(exp(x)-1) for some integer series G,
so a(n) = Sum_j c_j j! S(n,j). Modulo k the terms with j >= k vanish because k | j!, and
the truncated Stirling state (S(n,0),...,S(n,k-1)) evolves by the fixed matrix
S(n,j) = j*S(n-1,j) + S(n-1,j-1). The state therefore runs into a cycle, and the cycle is
found exactly by storing every state seen -- no guessing at a period from a tail.
"""
from sympy import totient


def stirling_states(k, limit=200000):
    """Yield the exact pre-period and period of the truncated Stirling state mod k."""
    st = tuple([1] + [0] * (k - 1))          # n = 0: S(0,0)=1
    seen = {st: 0}
    states = [st]
    n = 0
    while n < limit:
        prev = states[-1]
        nxt = tuple((j * prev[j] + (prev[j - 1] if j else 0)) % k for j in range(k))
        n += 1
        if nxt in seen:
            return seen[nxt], n - seen[nxt], states, seen
        seen[nxt] = n
        states.append(nxt)
    raise RuntimeError("no cycle found within limit")


def series_period(k, coeff):
    """Eventual period of a(n) mod k where a(n) = sum_j coeff(j)*j!*S(n,j)."""
    pre, per, states, _ = stirling_states(k)
    fact = [1] * k
    for j in range(1, k):
        fact[j] = fact[j - 1] * j % k
    w = [coeff(j) * fact[j] % k for j in range(k)]
    seq = [sum(w[j] * s[j] for j in range(k)) % k for s in states]
    # the state cycle gives period `per`; the sequence's own period divides it
    tail = seq[pre:]
    for p in sorted(d for d in range(1, per + 1) if per % d == 0):
        if all(tail[i] == tail[i + p] for i in range(len(tail) - p)):
            # confirm p really is a period by walking the cycle
            cyc = states[pre:pre + per]
            vals = [sum(w[j] * s[j] for j in range(k)) % k for s in cyc]
            if all(vals[i] == vals[(i + p) % per] for i in range(per)):
                return pre, p
    return pre, per


def report(name, coeff, kmax=80):
    bad = []
    for k in range(2, kmax + 1):
        pre, p = series_period(k, coeff)
        phi = int(totient(k))
        if phi % p:
            bad.append((k, p, phi, pre))
    print(f"{name}: k where the true period does NOT divide phi(k):")
    for k, p, phi, pre in bad:
        print(f"    k={k:3d}  true period {p:6d}  phi(k)={phi:4d}  pre-period {pre}")
    if not bad:
        print("    none up to k =", kmax)
    return bad


if __name__ == "__main__":
    report("A000670 Fubini (G=1/(1-t))", lambda j: 1)
