#!/usr/bin/env python3
"""The congruence and periodicity papers, checked numerically against the entry's own terms.

These prove statements of the form "a(n) mod k is eventually periodic with period dividing
phi(k)", "the Gauss congruences hold for the sequence and every shift", or "every term is
congruent to c modulo m". None of them is a recurrence, so the recurrence audits skip them; all
of them can be TESTED on the terms the entry publishes, which is independent of the algebra in
the paper and catches a misread of what the conjecture says.

A test over forty terms is not a proof and is not claimed to be one. It is the check that would
have caught a wrong reading, which is what the audit is for.
"""
import json, os, re, sys, collections
from math import gcd
import localentry as LE

OUT = 'audit_cong.json'
SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'


def totient(m):
    r, t = m, m
    p = 2
    while p * p <= t:
        if t % p == 0:
            while t % p == 0:
                t //= p
            r -= r // p
        p += 1
    if t > 1:
        r -= r // t
    return r


def periodic_with(d, k, per):
    """Is d eventually periodic mod k with period dividing per, over the range published?"""
    m = [x % k for x in d]
    if len(m) < 2 * per + 2:
        return None                       # not enough terms to say anything
    for start in range(0, len(m) - 2 * per):
        if all(m[i] == m[i + per] for i in range(start, len(m) - per)):
            return True
    return False


def check_periodicity(d, kmax=12):
    rows = {}
    for k in range(2, kmax + 1):
        rows[k] = periodic_with(d, k, totient(k))
    tested = [k for k, v in rows.items() if v is not None]
    bad = [k for k in tested if rows[k] is False]
    return {'moduli_tested': tested, 'failed': bad}


def check_gauss(d, off, pmax=13, rmax=3):
    """a_i(n p^r) == a_i(n p^(r-1)) mod p^r, for the sequence and its shifts."""
    bad, tested = [], 0
    primes = [p for p in range(2, pmax + 1) if all(p % q for q in range(2, p))]
    for i in range(0, 3):
        for p in primes:
            for r in range(1, rmax + 1):
                n = 1
                while True:
                    hi, lo = n * p ** r, n * p ** (r - 1)
                    if hi + i - off >= len(d):
                        break
                    tested += 1
                    if (d[hi + i - off] - d[lo + i - off]) % p ** r:
                        bad.append((i, p, r, n))
                    n += 1
    return {'tested': tested, 'failed': bad[:5]}


def check_residue(d, c, m, skip=0):
    bad = [i for i, x in enumerate(d[skip:], skip) if x % m != c % m]
    return {'tested': len(d) - skip, 'failed': bad[:5]}


TITLES = [
    (re.compile(r'The reduction of OEIS A\d{6} modulo \$?k'), 'periodicity'),
    (re.compile(r'Eventual periodicity modulo'), 'periodicity'),
    (re.compile(r'The Gauss congruences'), 'gauss'),
    (re.compile(r'The reduction of OEIS A\d{6} modulo \$?(\d+)'), 'reduction'),
    (re.compile(r'Every term of OEIS A\d{6} is congruent to \$?(\d+)\$? modulo \$?(\d+)'), 'residue'),
    (re.compile(r'Every term of OEIS A\d{6} is odd'), 'odd'),
    (re.compile(r'Every odd-indexed term of OEIS A\d{6} after the first is even'), 'oddindex'),
    (re.compile(r'Every term of OEIS A\d{6} after the second is divisible by \$?(\d+)'), 'divis'),
]


def classify(title):
    for rx, kind in TITLES:
        m = rx.search(title)
        if m:
            return kind, m
    return None, None


def main():
    tex = json.load(open(SC + '/texfacts.json'))
    st = json.load(open(SC + '/status.json'))
    pe = json.load(open('paper-engines.json'))
    live = {v['anum'] for v in pe.values()}
    out = {}
    for a in sorted(tex):
        if a not in live:
            continue
        for r in tex[a]:
            kind, m = classify(r['title'])
            if not kind:
                continue
            e = LE.get(a)
            d = [int(x) for x in e['data'].split(',') if x.strip()]
            off = int(e['offset'].split(',')[0])
            key = a + '|' + kind
            if kind == 'periodicity':
                res = check_periodicity(d)
                ok = not res['failed'] and res['moduli_tested']
            elif kind == 'gauss':
                res = check_gauss(d, off)
                ok = not res['failed'] and res['tested'] > 0
            elif kind == 'reduction':
                k = int(m.group(1))
                res = {'modulus': k, **{'periodic': periodic_with(d, k, totient(k))}}
                ok = res['periodic'] is not False
            elif kind == 'residue':
                res = check_residue(d, int(m.group(1)), int(m.group(2)))
                ok = not res['failed']
            elif kind == 'odd':
                res = check_residue(d, 1, 2)
                ok = not res['failed']
            elif kind == 'oddindex':
                idx = [x for i, x in enumerate(d) if (off + i) % 2 == 1][1:]
                res = {'tested': len(idx), 'failed': [x for x in idx if x % 2][:5]}
                ok = not res['failed']
            else:
                k = int(m.group(1))
                res = {'tested': len(d) - 2,
                       'failed': [i for i, x in enumerate(d[2:], 2) if x % k][:5]}
                ok = not res['failed']
            out[key] = {'v': 'ok' if ok else 'PROBLEM', 'kind': kind,
                        'title': r['title'][:90], 'nterms': len(d), **res}
    json.dump(out, open(OUT, 'w'), indent=1)
    print(len(out), dict(collections.Counter(v['v'] for v in out.values())))
    for k, v in out.items():
        if v['v'] != 'ok':
            print('  ', k, json.dumps(v)[:200])


if __name__ == '__main__':
    main()
