#!/usr/bin/env python3
"""The hand-written number-theory papers, checked numerically from their own statements.

These are the results that are not recurrences and not walk counts: Detlefs' primorial
characterisation, Bala's strong divisibility and gcd-product valuations, Karttunen's GF(2)
divisibilities, Layman's nim-factorial, Schulte's gcd sums, and the rest. No parser covers
them and no engine rebuilds them, so what is done here is the thing that would catch a
misreading: each claim is computed directly, over as much range as is cheap, and compared
with what the paper says.

A finite check is not the proof. It is the check that the statement being proved is the
statement the entry makes, which is the error this project has actually made.
"""
import json, sys, collections
from math import gcd, comb, factorial
from fractions import Fraction
from sympy import primerange, factorint, primefactors, isprime, mobius, totient

OUT = 'audit_bespoke.json'
res = {}


def rec(key, ok, **kw):
    res[key] = {'v': 'ok' if ok else 'PROBLEM', **kw}


# ---------------------------------------------------------------- A000040 (Detlefs, proof)
def detlefs_primorial(nmax=5):
    from math import lcm
    bad = []
    ps = list(primerange(2, 100))
    for n in range(1, nmax + 1):
        P = 1
        for p in ps[:n]:
            P *= p
        f = 1
        for p in ps[:n]:
            f = lcm(f, p - 1)
        for k in range(1, min(P, 4000) + 1):
            lhs = pow(k, f, P) == 1
            rhs = gcd(k, P) == 1
            if lhs != rhs:
                bad.append((n, k))
    return not bad, {'checked_n': nmax, 'counterexamples': bad[:5]}


# ------------------------------------------------------- A000040 (Detlefs Fibonacci, disproof)
def detlefs_fib(limit=250000):
    def fibmod(k, m):
        a, b = 0, 1
        for bit in bin(k)[2:]:
            c = (a * ((2 * b - a) % m)) % m
            d = (a * a + b * b) % m
            a, b = (d, c + d) if bit == '1' else (c, d)
        return a
    hits = []
    n = 3
    while n < limit:
        if not isprime(n):
            f = fibmod(n, n)
            if (f == 1 or f == n - 1) and pow(2, n - 1, n) == 1:
                hits.append(n)
        n += 2
    return (219781 in hits), {'composites_passing_below_%d' % limit: hits[:6]}


# ----------------------------------------------------------- A000071 (Bala strong divisibility)
def bala_strong(K=(3, 5, 7, 9), M=4):
    """The index runs over POWERS of k -- gcd(a(k^n), a(k^m)) = a(k^gcd(n,m)).

    Read from the paper's PDF text this came out as "kn", because pdfminer drops the
    superscript, and the check built on that reading failed at once: a itself is not a strong
    divisibility sequence, which the paper says in its own first paragraph. The claim is about
    a fixed odd geometric progression, and k = 1 is not in it.
    """
    top = max(k ** M for k in K)
    F = [0, 1]
    for i in range(2, top + 4):
        F.append(F[-1] + F[-2])
    a = lambda j: F[j] - 1
    bad = []
    for k in K:
        for n in range(1, M + 1):
            for m in range(1, M + 1):
                if k ** max(n, m) >= len(F):
                    continue
                if gcd(a(k ** n), a(k ** m)) != a(k ** gcd(n, m)):
                    bad.append((k, n, m))
    return not bad, {'k_tested': list(K), 'exponent_max': M, 'counterexamples': bad[:5]}


# ------------------------------------------------------------------ A000139 (Bala parity)
def bala_parity(N=300):
    def fibbinary(x):
        return (x & (x >> 1)) == 0
    bad = []
    for n in range(0, N):
        a = 2 * factorial(3 * n) // (factorial(2 * n + 1) * factorial(n + 1))
        odd = a % 2 == 1
        want = fibbinary(n) and n % 2 == 1
        if odd != want:
            bad.append(n)
    return not bad, {'n_max': N, 'counterexamples': bad[:6]}


# ------------------------------------------------------------- A000364 (Bala periodicity, disproof)
def euler_periodicity():
    N = 60
    E = [0] * (2 * N + 1)
    E[0] = 1
    for n in range(1, N + 1):
        s = 0
        for k in range(n):
            s += comb(2 * n, 2 * k) * E[2 * k]
        E[2 * n] = -s
    a = [abs(E[2 * n]) for n in range(N + 1)]          # a(n) = |E_2n|, n >= 0
    k = 27
    got = (a[1] % k, a[19] % k)
    return got == (1, 10), {'a1_mod_27': got[0], 'a19_mod_27': got[1],
                            'phi27': int(totient(27))}


# ----------------------------------------------------------------- A008365 (Detlefs, disproof)
def detlefs_rough():
    M = 2310
    img = {pow(u, 24, M) for u in range(1, M) if gcd(u, M) == 1}
    return (pow(17, 24, M) == 1681 and len(img) == 5 and img == {1, 421, 631, 841, 1681}), \
           {'image_of_24th_powers': sorted(img), '17^24 mod 2310': pow(17, 24, M)}


# ---------------------------------------------------------- A092287 / A129364 / A129365 / A129454
def gcd_products(N=26):
    P = list(primerange(2, N + 1))

    def vp(x, p):
        e = 0
        while x % p == 0:
            x //= p; e += 1
        return e

    bad = collections.defaultdict(list)
    # Kaydalov: ord_p f(n,m) = sum_i floor(n/p^i) floor(m/p^i)
    for n in range(1, 16):
        for m in range(1, 16):
            f = 1
            for j in range(1, n + 1):
                for k in range(1, m + 1):
                    f *= gcd(j, k)
            for p in P:
                want = 0
                i = 1
                while p ** i <= max(n, m):
                    want += (n // p ** i) * (m // p ** i); i += 1
                if vp(f, p) != want:
                    bad['A092287'].append((n, m, p))
    # Bala on A129454: ord_p a(n) = sum_t floor((n-1)/p^t)^3
    for n in range(2, 13):
        a = 1
        for i in range(1, n):
            for j in range(1, n):
                for k in range(1, n):
                    a *= gcd(gcd(i, j), k)
        for p in P:
            want = 0
            t = 1
            while p ** t <= n:
                want += ((n - 1) // p ** t) ** 3; t += 1
            if vp(a, p) != want:
                bad['A129454'].append((n, p))
    # Bala on A129365: ord_p a(n) = sum_i B(floor(n/p^i)),  B(M) = sum_{k<=M} (M mod k)
    B = lambda M: sum(M % k for k in range(1, M + 1))
    for n in range(1, 17):
        num = 1
        for j in range(1, n + 1):
            for k in range(1, n + 1):
                num *= gcd(j, k)
        den = 1
        for k in range(1, n + 1):
            den *= factorial(n // k) ** k
        if num % den:
            bad['A129365-integrality'].append(n)
            continue
        a = num // den
        for p in P:
            want = 0
            i = 1
            while p ** i <= n:
                want += B(n // p ** i); i += 1
            if vp(a, p) != want:
                bad['A129365'].append((n, p))
    # Bala on A129364: A129364(n) divides A092287(n). The first version of this check had the
    # division the other way round, which is not what either the entry or the paper says.
    for n in range(1, 15):
        G = 1                                   # A092287(n) = prod_{j,k<=n} gcd(j,k)
        for j in range(1, n + 1):
            for k in range(1, n + 1):
                G *= gcd(j, k)
        d = 1                                   # A129364(n) = prod_{k<=n} prod_{e|k} e^(k/e)
        for k in range(1, n + 1):
            for e in range(1, k + 1):
                if k % e == 0:
                    d *= e ** (k // e)
        if G % d:
            bad['A129364'].append(n)
    return {k: (not v, {'counterexamples': v[:4]}) for k, v in
            [('A092287', bad['A092287']), ('A129454', bad['A129454']),
             ('A129365', bad['A129365'] + bad['A129365-integrality']),
             ('A129364', bad['A129364'])]}


# ------------------------------------------------------------------- A059970 (nim-factorial)
def nim():
    memo = {}

    def nimmul(a, b):
        if a < 2 or b < 2:
            return a * b
        if (a, b) in memo:
            return memo[(a, b)]
        # split at the largest Fermat 2-power below max(a,b)
        k = 1
        while (1 << (2 * k)) <= max(a, b):
            k *= 2
        F = 1 << k
        ah, al = a // F, a % F
        bh, bl = b // F, b % F
        c = nimmul(ah, bh)
        d = nimmul(al, bl)
        e = nimmul(ah ^ al, bh ^ bl)
        r = ((e ^ d) * F) ^ d ^ nimmul(c, F // 2)
        # F//2 times c in nim arithmetic: nimmul(c, F//2) handled recursively
        memo[(a, b)] = r
        return r

    def nimfact(n):
        r = 1
        for i in range(1, n + 1):
            r = nimmul(r, i)
        return r
    bad1 = [n for n in range(1, 9) if nimfact(2 ** n - 1) != 1]
    bad2 = [n for n in range(1, 9) if nimfact(2 ** n + 2 ** (n - 1) - 1) != 2]
    return (not bad1 and not bad2), {'a(2^n-1)!=1 at': bad1, 'a(3*2^(n-1)-1)!=2 at': bad2}


# ---------------------------------------------------------------------- A087726 (Branman)
def branman(N=40):
    bad = []
    for n in range(1, N + 1):
        c = 0
        for a in range(n):
            for b in range(n):
                for cc in range(n):
                    for d in range(n):
                        if ((a * a + b * cc) % n == 0 and (a * b + b * d) % n == 0
                                and (cc * a + d * cc) % n == 0 and (cc * b + d * d) % n == 0):
                            c += 1
        sf = all(e == 1 for e in factorint(n).values())
        if (c == n * n) != sf:
            bad.append((n, c))
    return not bad, {'n_max': N, 'counterexamples': bad[:5]}


# --------------------------------------------------------- A358272 / A358319 (Schulte gcd sums)
def schulte(N=200):
    def lam(x):
        return (-1) ** sum(factorint(x).values()) if x > 1 else 1

    def rad(x):
        r = 1
        for p in primefactors(x):
            r *= p
        return r
    bad1, bad2 = [], []
    for n in range(1, N + 1):
        s = sum(gcd(k, n) * lam(gcd(k, n)) for k in range(1, n + 1))
        a = 1
        for p, e in factorint(n).items():
            a *= (-1) ** e * p ** (2 * (e // 2))
        if s != a:
            bad1.append(n)
        t = sum(gcd(k, n) * mobius(rad(gcd(k, n))) for k in range(1, n + 1))
        b = 1
        for p, e in factorint(n).items():
            b *= ((p - 2) - (p - 1) * e) * p ** (e - 1)
        if t != b:
            bad2.append(n)
    return (not bad1 and not bad2), {'A358272 fails at': bad1[:5], 'A358319 fails at': bad2[:5]}





# ============================ second batch ============================================
def layman_binomial(N=14):
    """A005329 is the inverse binomial transform of A075272."""
    import localentry as LE
    a = [int(x) for x in LE.get('A005329')['data'].split(',') if x.strip()]
    b = [int(x) for x in LE.get('A075272')['data'].split(',') if x.strip()]
    M = min(len(a), len(b), N)
    bad = [n for n in range(M)
           if a[n] != sum((-1) ** (n - k) * comb(n, k) * b[k] for k in range(n + 1))]
    return not bad, {'tested': M, 'failed_at': bad[:5]}


def _gf2div(u, v):
    """u divisible by v over GF(2)[x], both as integers with bit i = coefficient of x^i."""
    if v == 0:
        return False
    dv = v.bit_length() - 1
    while u.bit_length() - 1 >= dv and u:
        u ^= v << (u.bit_length() - 1 - dv)
    return u == 0


def _gf2pow(base, e):
    r = 1
    for _ in range(e):
        # multiply r by base over GF(2)
        acc, b = 0, base
        rr = r
        while rr:
            if rr & 1:
                acc ^= b
            rr >>= 1
            b <<= 1
        r = acc
    return r


def karttunen(anum, poly, expo, lo, N=9):
    """Each term, read as a GF(2)[x] polynomial, is divisible by poly^expo(n)."""
    import localentry as LE
    d = [int(x) for x in LE.get(anum)['data'].split(',') if x.strip()]
    off = int(LE.get(anum)['offset'].split(',')[0])
    bad, tested = [], 0
    for i, v in enumerate(d[:N]):
        n = off + i
        if n < lo:
            continue
        e = expo(n)
        if e < 0:
            continue
        tested += 1
        if not _gf2div(v, _gf2pow(poly, e)):
            bad.append(n)
    return (not bad and tested > 0), {'tested': tested, 'failed_at': bad[:5]}


def seidov(N=5):
    """A047926(n) counts a^2+b^2+c^2 = 3^(2n) with 0 < a <= b <= c."""
    import localentry as LE
    d = [int(x) for x in LE.get('A047926')['data'].split(',') if x.strip()]
    off = int(LE.get('A047926')['offset'].split(',')[0])
    rows = []
    for n in range(1, N + 1):
        t = 9 ** n
        c = 0
        a = 1
        while 3 * a * a <= t:
            b = a
            while a * a + 2 * b * b <= t:
                r = t - a * a - b * b
                s = int(r ** 0.5)
                while s * s < r:
                    s += 1
                if s * s == r and s >= b:
                    c += 1
                b += 1
            a += 1
        # the entry's indexing is off by one against Seidov's wording, which the paper
        # states and corrects: the count for 9^k is A047926(k-1), not A047926(k)
        j = n - 1 - off
        rows.append((n, c, d[j] if 0 <= j < len(d) else None))
    bad = [r for r in rows if r[2] is not None and r[1] != r[2]]
    return not bad, {'rows': rows, 'mismatch': bad[:3]}


def detlefs_harmonic(pmax=60):
    """denominator(H(p)/H(p-1)) / numerator(H(p-1)/p^2) = p^3 for primes p > 3."""
    H = [Fraction(0)]
    for k in range(1, pmax + 2):
        H.append(H[-1] + Fraction(1, k))
    bad = []
    for p in primerange(5, pmax):
        lhs = Fraction(H[p], H[p - 1]).denominator
        rhs = Fraction(H[p - 1], p * p).numerator
        if lhs % rhs or lhs // rhs != p ** 3:
            bad.append(p)
    return not bad, {'primes_tested': [p for p in primerange(5, pmax)][:12],
                     'failed_at': bad[:5]}


def mathar_mobius(N=200):
    """A062368 is the third inverse Mobius transform of 4^omega(n)."""
    def omega(x):
        return len(primefactors(x))
    f = [0] + [4 ** omega(n) for n in range(1, N + 1)]
    for _ in range(3):                            # three inverse Mobius transforms
        g = [0] * (N + 1)
        for n in range(1, N + 1):
            g[n] = sum(f[d] for d in range(1, n + 1) if n % d == 0)
        f = g
    bad = []
    for n in range(1, N + 1):
        a = 1
        for p, e in factorint(n).items():
            a *= (e + 1) * (e + 2) * (4 * e + 3) // 6
        if a != f[n]:
            bad.append(n)
    return not bad, {'tested': N, 'failed_at': bad[:5]}


def luschny(N=40):
    import localentry as LE
    e = LE.get('A063321')
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    off = int(e['offset'].split(',')[0])
    bad = []
    for i, v in enumerate(d[:N]):
        n = off + i
        if n <= 2:
            continue
        if 13 * (n + (n - 1) % 2) + 14 * (n + n % 2) - 72 != v:
            bad.append(n)
    return not bad, {'tested': min(len(d), N), 'failed_at': bad[:5]}


def series_claims(terms=9, K=4000):
    """A305404 and A352117: the conjectured convergent series against the entry's terms."""
    import localentry as LE
    from mpmath import mp, mpf, binomial as mpbin, sqrt as mpsqrt, power
    mp.dps = 40
    out = {}
    d = [int(x) for x in LE.get('A305404')['data'].split(',') if x.strip()]
    bad = []
    for n in range(1, min(terms, len(d))):
        s = mp.nsum(lambda k: power(k, n) * mpbin(2 * k, k) /
                    (power(2, k) * power(3, k + mpf(1) / 2)), [0, mp.inf])
        if abs(s - d[n]) > mpf('1e-8') * max(1, abs(d[n])):
            bad.append((n, str(s)[:24], d[n]))
    out['A305404'] = (not bad, {'failed': bad[:3], 'tested': min(terms, len(d)) - 1})
    e = LE.get('A352117')
    d2 = [int(x) for x in e['data'].split(',') if x.strip()]
    off2 = int(e['offset'].split(',')[0])
    bad2 = []
    for n in range(1, min(terms, len(d2))):
        s = mp.nsum(lambda k: power(2, n - 3 * k - mpf(1) / 2) * power(k, n) * mpbin(2 * k, k),
                    [1, mp.inf])
        want = d2[n - off2]
        if abs(s - want) > mpf('1e-8') * max(1, abs(want)):
            bad2.append((n, str(s)[:24], want))
    out['A352117'] = (not bad2, {'failed': bad2[:3], 'tested': min(terms, len(d2)) - 1})
    return out


def yanev_kotesovec(N=300):
    """A327123: a(n) = Sum_{k=1..n} sin(gcd(k,n)*Pi/2), which is the character mod 4."""
    import localentry as LE
    e = LE.get('A327123')
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    off = int(e['offset'].split(',')[0])
    chi = {1: 1, 3: -1, 0: 0, 2: 0}
    bad = []
    for i, v in enumerate(d[:N]):
        n = off + i
        if n < 1:
            continue
        if sum(chi[gcd(k, n) % 4] for k in range(1, n + 1)) != v:
            bad.append(n)
    return not bad, {'tested': min(len(d), N), 'failed_at': bad[:5]}


def run_second():
    from sympy import Integer
    A000225 = lambda n: 2 ** n - 1
    A055010 = lambda n: (3 * 2 ** (n - 1) - 1) if n >= 1 else 0
    checks = [
        ('A005329-layman', layman_binomial),
        ('A036284-karttunen1', lambda: karttunen('A036284', 0b1001, lambda n: A000225(n - 1), 1)),
        ('A037096-karttunen', lambda: karttunen('A037096', 0b11, lambda n: A055010(n - 1), 3)),
        ('A037097-karttunen', lambda: karttunen('A037097', 0b11, lambda n: A000225(n - 2), 3)),
        ('A047926-seidov', seidov),
        ('A061002-detlefs-harmonic', detlefs_harmonic),
        ('A062368-mathar-mobius', mathar_mobius),
        ('A063321-luschny', luschny),
        ('A327123-yanev-kotesovec', yanev_kotesovec),
    ]
    for name, fn in checks:
        try:
            ok, info = fn()
        except Exception as ex:
            rec(name, False, error='%s: %s' % (type(ex).__name__, str(ex)[:90]))
            print(name, 'ERROR', type(ex).__name__, str(ex)[:80], flush=True)
            continue
        rec(name, ok, **info)
        print(name, res[name]['v'], json.dumps(info, default=str)[:150], flush=True)
    try:
        for k, (ok, info) in series_claims().items():
            rec(k + '-series', ok, **info)
            print(k, res[k + '-series']['v'], json.dumps(info, default=str)[:120], flush=True)
    except Exception as ex:
        rec('series', False, error='%s: %s' % (type(ex).__name__, str(ex)[:90]))
        print('series ERROR', type(ex).__name__, str(ex)[:90], flush=True)


if __name__ == '__main__':
    checks = [
        ('A000040-primorial', detlefs_primorial),
        ('A000040-fibonacci-disproof', detlefs_fib),
        ('A000071-strong-divisibility', bala_strong),
        ('A000139-parity', bala_parity),
        ('A000364-periodicity-disproof', euler_periodicity),
        ('A008365-disproof', detlefs_rough),
        ('A059970-nim', nim),
        ('A087726-branman', branman),
        ('A358272/A358319-schulte', schulte),
    ]
    for name, fn in checks:
        try:
            ok, info = fn()
        except Exception as ex:
            rec(name, False, error='%s: %s' % (type(ex).__name__, str(ex)[:90]))
            print(name, 'ERROR', type(ex).__name__, str(ex)[:80], flush=True)
            continue
        rec(name, ok, **info)
        print(name, res[name]['v'], json.dumps(info)[:150], flush=True)
    for k, (ok, info) in gcd_products().items():
        rec(k + '-valuation', ok, **info)
        print(k, res[k + '-valuation']['v'], json.dumps(info)[:120], flush=True)
    run_second()
    json.dump(res, open(OUT, 'w'), indent=1)
    print(dict(collections.Counter(v['v'] for v in res.values())))