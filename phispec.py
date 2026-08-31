#!/usr/bin/env python3
"""For each entry, the series G with A(x) = G(exp(x)-1), and a check of G against DATA.

Every G here is obtained from the entry's OWN stated e.g.f. by the substitution
u = exp(x), t = u - 1, and is then checked coefficient by coefficient against the
coefficients that the entry's published terms force. Nothing is asserted unchecked.
"""
from fractions import Fraction as Fr
import gintegral as GI

N = 46


def zero():
    return [Fr(0)] * N


def one():
    c = zero(); c[0] = Fr(1); return c


def add(a, b):
    return [a[i] + b[i] for i in range(N)]


def sub(a, b):
    return [a[i] - b[i] for i in range(N)]


def mul(a, b):
    r = zero()
    for i in range(N):
        if a[i]:
            for j in range(N - i):
                r[i + j] += a[i] * b[j]
    return r


def inv(a):
    r = zero(); r[0] = 1 / a[0]
    for n in range(1, N):
        r[n] = -sum(a[k] * r[n - k] for k in range(1, n + 1)) / a[0]
    return r


def poly(*cs):
    c = zero()
    for i, v in enumerate(cs):
        c[i] = Fr(v)
    return c


def power(a, e):
    r = one()
    for _ in range(e):
        r = mul(r, a)
    return r


def sqrt_series(a):
    """square root of a series with a[0] = 1"""
    assert a[0] == 1
    r = zero(); r[0] = Fr(1)
    for n in range(1, N):
        s = sum(r[k] * r[n - k] for k in range(1, n))
        r[n] = (a[n] - s) / 2
    return r


def compose(f, g):
    """f(g(t)) with g[0] == 0"""
    assert g[0] == 0
    r = zero(); p = one()
    for j in range(N):
        if f[j]:
            r = add(r, [f[j] * p[i] for i in range(N)])
        p = mul(p, g)
    return r


T = poly(0, 1)


def catalan():
    # (1 - sqrt(1-4t)) / (2t)
    s = sqrt_series(poly(1, -4))
    num = sub(one(), s)
    return [num[i + 1] / 2 for i in range(N - 1)] + [Fr(0)]


def eulerprod(expo, powers):
    """Product over k>=1 of (1 - t^powers(k))^expo, as a series."""
    r = one()
    k = 1
    while powers(k) < N:
        f = zero(); f[0] = Fr(1); f[powers(k)] = Fr(-1)
        fi = inv(f) if expo < 0 else f
        for _ in range(abs(expo)):
            r = mul(r, fi)
        k += 1
    return r


def prod_form(fn):
    r = one(); k = 1
    while k < N:
        r = mul(r, fn(k)); k += 1
    return r


def partitions_g():
    return prod_form(lambda k: inv(poly(*([1] + [0] * (k - 1) + [-1]))) if k < N else one())


def cf_A301921():
    """1/(1 - t/(1 - t^2/(1 - t^3/(1 - ...)))), built from the inside out.

    R_k = 1/(1 - t^k * R_{k+1}); the answer is R_1. Levels with k >= N cannot affect
    coefficients below t^N, so the recursion is truncated there exactly.
    """
    r = one()
    for k in range(N - 1, 0, -1):
        tk = zero(); tk[k] = Fr(1)
        r = inv(sub(one(), mul(tk, r)))
    return r


def A138265(N):
    """The integer sequence A138265, read from the OEIS entry itself."""
    import entry
    return [int(x) for x in entry.get("A138265")["data"].split(",")][:N]


def cf_A079144():
    return poly(*A138265(N))


def G_A158690():
    """Sum_{n>=0} Prod_{k=1..n} (1 - (1+t)^-(2k-1)); each factor is an integer series
    with zero constant term, so the sum is a well-defined integer series."""
    total = zero(); term = one(); k = 1
    while k <= N:
        f = sub(one(), inv(power(poly(1, 1), 2 * k - 1)))
        term = mul(term, f)
        total = add(total, term)
        k += 1
    return add(one(), total)


SPEC = {
 "A000670": ("1/(2 - exp(x))", "1/(1-t)", lambda: inv(poly(1, -1))),
 "A002050": ("(exp(2*x) - exp(x))/(2 - exp(x))", "t*(1+t)/(1-t)",
             lambda: mul(mul(poly(0, 1), poly(1, 1)), inv(poly(1, -1)))),
 "A004123": ("1/(3 - 2*exp(x))", "1/(1-2t)", lambda: inv(poly(1, -2))),
 "A006531": ("C(1 - exp(-x)), C the Catalan g.f.", "C(t/(1+t))",
             lambda: compose(catalan(), mul(poly(0, 1), inv(poly(1, 1))))),
 "A052895": ("(1/2)/(exp(x)-1) * (1 - (5 - 4*exp(x))^(1/2))", "(1-sqrt(1-4t))/(2t)",
             catalan),
 "A064618": ("hypergeom([1,1],[],exp(x)-1)", "Sum j! t^j",
             lambda: poly(*[__import__('math').factorial(j) for j in range(N)])),
 "A080253": ("exp(x)/(2 - exp(2*x))", "(1+t)/(1-2t-t^2)",
             lambda: mul(poly(1, 1), inv(poly(1, -2, -1)))),
 "A162314": ("exp(2*x)/(2 - exp(2*x))", "(1+t)^2/(1-2t-t^2)",
             lambda: mul(power(poly(1, 1), 2), inv(poly(1, -2, -1)))),
 "A167137": ("P(exp(x)-1), P the partition g.f.", "Prod_{k>=1} 1/(1-t^k)",
             lambda: eulerprod(-1, lambda k: k)),
 "A259533": ("exp(3*x)/(2 - exp(x))", "(1+t)^3/(1-t)",
             lambda: mul(power(poly(1, 1), 3), inv(poly(1, -1)))),
 "A301921": ("continued fraction in exp(x)-1", "continued fraction in t", cf_A301921),
 "A305550": ("Prod_{k>=1} (1 + (exp(x)-1)^k)", "Prod_{k>=1} (1+t^k)",
             lambda: prod_form(lambda k: poly(*([1] + [0] * (k - 1) + [1])) if k < N else one())),
 "A306082": ("Prod_{k>=1} 1/(1 - (exp(x)-1)^(k^2))", "Prod_{k>=1} 1/(1-t^(k^2))",
             lambda: eulerprod(-1, lambda k: k * k)),
 "A316142": ("Prod_{k>=1} (1 + (exp(x)-1)^k)^2", "Prod_{k>=1} (1+t^k)^2",
             lambda: power(prod_form(lambda k: poly(*([1] + [0] * (k - 1) + [1])) if k < N else one()), 2)),
 "A316143": ("Prod_{k>=1} 1/(1 - (exp(x)-1)^k)^2", "Prod_{k>=1} 1/(1-t^k)^2",
             lambda: power(eulerprod(-1, lambda k: k), 2)),
 "A316144": ("Prod_{k>=1} ((1+(exp(x)-1)^k)/(1-(exp(x)-1)^k))^2",
             "Prod_{k>=1} ((1+t^k)/(1-t^k))^2",
             lambda: mul(power(prod_form(lambda k: poly(*([1] + [0] * (k - 1) + [1])) if k < N else one()), 2),
                         power(eulerprod(-1, lambda k: k), 2))),
 "A320352": ("(exp(x)-1)/(exp(x) - exp(2*x) + 1)", "t/(1-t-t^2)",
             lambda: mul(poly(0, 1), inv(poly(1, -1, -1)))),
 "A354242": ("1/sqrt(5 - 4*exp(x))", "1/sqrt(1-4t)",
             lambda: inv(sqrt_series(poly(1, -4)))),
 "A354253": ("1/sqrt(9 - 8*exp(x))", "1/sqrt(1-8t)",
             lambda: inv(sqrt_series(poly(1, -8)))),
 "A355409": ("1/(1 + exp(2*x) - exp(3*x))", "1/(1-t-2t^2-t^3)",
             lambda: inv(poly(1, -1, -2, -1))),
    "A079144": ("Sum_k k!*Stirling2(n,k)*A138265(k)", "Sum_k A138265(k) t^k", cf_A079144),
    "A158690": ("Sum_{n>=0} Prod_{k=1..n} (1 - exp(-(2k-1)x))",
                "Sum_{n>=0} Prod_{k=1..n} (1 - (1+t)^-(2k-1))", G_A158690),
}

if __name__ == "__main__":
    for a, (egf, gt, fn) in SPEC.items():
        try:
            g = fn()
        except Exception as ex:
            print(f"{a}  G BUILD ERROR {ex}"); continue
        shift, integral, first, n = GI.coeffs(a)
        want = [Fr(x) for x in first]
        got = g[:len(want)]
        ok = all(got[i] == want[i] for i in range(len(want)))
        allint = all(x.denominator == 1 for x in g)
        print(f"{a}  G = {gt:38s}  matches DATA: {ok}   G integral: {allint}")
        if not ok:
            print(f"      from G   : {[str(x) for x in got]}")
            print(f"      from DATA: {first}")
