#!/usr/bin/env python3
"""The Bala phi(k) periodicity conjectures on sequences with e.g.f. G(exp(x)-1).

Each entry is a(n) = Sum_j c_j * j! * S(n,j) for an integer series G(t) = Sum c_j t^j read
off the entry's own e.g.f. Modulo k only j < k survives, and the truncated Stirling state
evolves by a fixed matrix, so a(n) mod k is exactly computable and its eventual period is
found exactly by cycle detection on the state -- nothing is estimated from a tail.

Every G below is checked against the entry's published DATA before it is used.
"""
import entry
from sympy import totient, fibonacci, catalan, binomial, npartitions


def weights(k, coeff):
    fact = [1] * k
    for j in range(1, k):
        fact[j] = fact[j - 1] * j % k
    return [coeff(j) * fact[j] % k for j in range(k)]


def seq_mod(k, N, coeff):
    st = [1] + [0] * (k - 1)
    w = weights(k, coeff)
    out = []
    for _ in range(N):
        out.append(sum(w[j] * st[j] for j in range(k)) % k)
        st = [(j * st[j] + (st[j - 1] if j else 0)) % k for j in range(k)]
    return out


def exact_period(k, coeff, limit=2_000_000):
    """Exact (pre-period, period) of a(n) mod k, by cycle detection on the state."""
    st = tuple([1] + [0] * (k - 1))
    w = weights(k, coeff)
    seen = {st: 0}
    vals = [sum(w[j] * st[j] for j in range(k)) % k]
    n = 0
    while n < limit:
        st = tuple((j * st[j] + (st[j - 1] if j else 0)) % k for j in range(k))
        n += 1
        if st in seen:
            pre, per = seen[st], n - seen[st]
            tail = vals[pre:]
            for p in sorted(d for d in range(1, per + 1) if per % d == 0):
                if all(tail[i] == tail[(i + p) % per] for i in range(per)):
                    return pre, p
            return pre, per
        seen[st] = n
        vals.append(sum(w[j] * st[j] for j in range(k)) % k)
    return None, None


def check_G(anum, coeff, nmax=14):
    """Confirm the read-off G reproduces the entry's own published terms, exactly."""
    d = [int(x) for x in entry.get(anum)['data'].split(',')]
    n = min(nmax, len(d))
    st = [1] + [0] * (n + 1)                  # exact Stirling row, integers
    fact = [1] * (n + 2)
    for j in range(1, n + 2):
        fact[j] = fact[j - 1] * j
    got = []
    for _ in range(n):
        got.append(sum(coeff(j) * fact[j] * st[j] for j in range(n + 2)))
        st = [j * st[j] + (st[j - 1] if j else 0) for j in range(n + 2)]
    off = int(entry.get(anum)['offset'].split(',')[0])
    for shift in (0, 1, 2):                    # the entry may start at a(off) with off>0
        if got[shift:shift + n - shift] == d[:n - shift] and n - shift >= 8:
            return True, shift, got[:8]
    return False, None, (got[:8], d[:8])


FAMILY = {
    "A000670": ("G = 1/(1-t)", lambda j: 1),
    "A052895": ("G = (1-sqrt(1-4t))/(2t), Catalan", lambda j: int(catalan(j))),
    "A354242": ("G = 1/sqrt(1-4t)", lambda j: int(binomial(2 * j, j))),
    "A354253": ("G = 1/sqrt(1-8t)", lambda j: int(binomial(2 * j, j)) * 2 ** j),
    "A320352": ("G = t/(1-t-t^2), Fibonacci", lambda j: int(fibonacci(j))),
    "A167137": ("G = partition g.f.", lambda j: int(npartitions(j))),
}


def main(kmax=40):
    for anum, (desc, coeff) in FAMILY.items():
        ok, shift, detail = check_G(anum, coeff)
        if not ok:
            print(f"{anum}  {desc}\n    G REJECTED (does not reproduce DATA): {detail}")
            continue
        bad = []
        for k in range(2, kmax + 1):
            pre, p = exact_period(k, coeff)
            if p is None:
                bad.append((k, None, int(totient(k)), None))
                continue
            if int(totient(k)) % p:
                bad.append((k, p, int(totient(k)), pre))
        print(f"{anum}  {desc}  G verified on DATA")
        if bad:
            for k, p, phi, pre in bad:
                print(f"    *** k={k:3d} true period {p} does NOT divide phi(k)={phi}"
                      f"  (pre-period {pre})")
        else:
            print(f"    period divides phi(k) for every k up to {kmax}")


if __name__ == "__main__":
    main()
