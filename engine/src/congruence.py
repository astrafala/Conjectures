#!/usr/bin/env python3
"""Congruence and divisibility conjectures, decided exactly.

Until now this project has settled one kind of claim: that a sequence satisfies a particular
linear recurrence. That is 15,978 of the 32,629 OEIS entries carrying a conjecture. The other
16,651 -- congruences, divisibility, inequalities, asymptotics -- were never attempted, and
"decidable" was quietly being used to mean "reduces to linear algebra over Q".

Congruences are decidable too, and by a real theorem rather than by arithmetic on a matrix.

    If a satisfies a monic integer linear recurrence of order r, then the state vector
    (a(n), ..., a(n+r-1)) taken mod m evolves under a fixed matrix over Z/mZ. There are only
    m^r states, so the state sequence must repeat: a mod m is EVENTUALLY PERIODIC, and its
    pre-period and period are computed exactly by iterating until a state recurs.

Once the pre-period p and period L are known, every claim of the forms

    a(n) = c (mod m) for n > k        m | a(n) for all n > k
    a(n) is even / odd for n > k      a(n) = c (mod m) for n in some residue class

is settled by checking the finitely many residues in one period past the pre-period -- not
sampled, decided. A claim that fails inside that window is FALSE, and the failure is exhibited.

The recurrence is a premise, so it must be one the entry states as fact or one this project
has already proved; `witness` records which, and a claim resting on a conjectured recurrence
is refused rather than proved from an unproved premise.
"""
import re

CONG = re.compile(
    r'a\(\s*n\s*\)\s*(?:==|=|\bis\b\s+congruent\s+to)\s*(-?\d+)\s*'
    r'\(?\s*mod\s+(\d+)\s*\)?', re.I)
DIVBY = re.compile(r'(\d+)\s*(?:\||divides)\s*a\(\s*n\s*\)', re.I)
# The commonest phrasings name no a(n) at all -- "all terms are divisible by 18", "every term
# is divisible by 36" -- and a parser that insisted on a(n) read 40 of 294 such lines.
DIVIS = re.compile(r'(?:a\(\s*n\s*\)|all terms?|every term|each term|the terms?)\s+'
                   r'(?:are|is)\s+divisible\s+by\s+(\d+)', re.I)
TERMMOD = re.compile(r'(?:a\(\s*n\s*\)|all terms?|every term|each term|k)\s*'
                     r'(?:==|=|\bis\b)\s*(-?\d+)\s*\(?\s*mod\s+(\d+)\s*\)?', re.I)
PARITY = re.compile(r'(?:a\(\s*n\s*\)|all terms?|every term|each term)\s+(?:are|is)\s+'
                    r'(?:always\s+)?(even|odd)\b', re.I)
FROM = re.compile(r'for\s+n\s*(>=|>)\s*(\d+)', re.I)


# "a(n) == 10 (mod 84) for odd n. a(n) == 31 (mod 84) for even n > 0." A parser that drops
# the qualifier tests both congruences at every index, finds both false, and reports a TRUE
# conjecture as disproved -- which is exactly what happened on A237930. A claim now carries
# the residue class of n it is asserted for.
QUAL = re.compile(r"\bfor\s+(odd|even)\s+n\b", re.I)
NQUAL = re.compile(r"\bfor\s+n\s*==?\s*(\d+)\s*\(?\s*mod\s+(\d+)\s*\)?", re.I)


# the qualifier can carry its own lower bound too -- "for even n > 0" -- and dropping the
# bound put n = 0 inside a claim the entry excludes, which read as a counterexample
START = re.compile(r"\bn\s*(>=|>)\s*(\d+)")


def _nclass(seg):
    st = 0
    m = START.search(seg)
    if m:
        st = int(m.group(2)) + (1 if m.group(1) == ">" else 0)
    m = QUAL.search(seg)
    if m:
        return ((1, 2) if m.group(1).lower() == "odd" else (0, 2)) + (st,)
    m = NQUAL.search(seg)
    if m:
        return int(m.group(1)) % int(m.group(2)), int(m.group(2)), st
    return (0, 1, st)


def claims(line):
    """every claim on one line, as (residue, modulus, n-residue, n-modulus)"""
    out = []
    for m in CONG.finditer(line):
        out.append((int(m.group(1)), int(m.group(2))) + _nclass(line[m.end():m.end() + 60]))
    for m in DIVBY.finditer(line):
        out.append((0, int(m.group(1))) + _nclass(line[m.end():m.end() + 60]))
    for m in DIVIS.finditer(line):
        out.append((0, int(m.group(1))) + _nclass(line[m.end():m.end() + 60]))
    for m in TERMMOD.finditer(line):
        out.append((int(m.group(1)), int(m.group(2))) + _nclass(line[m.end():m.end() + 60]))
    for m in PARITY.finditer(line):
        out.append((0 if m.group(1).lower() == 'even' else 1, 2)
                   + _nclass(line[m.end():m.end() + 60]))
    seen, uniq = set(), []
    for c, mm, nr, nm, st in out:
        if not 2 <= mm <= 10 ** 6:
            continue
        k = (c % mm, mm, nr, nm, st)
        if k not in seen:
            seen.add(k)
            uniq.append(k)
    return uniq


def claimed_from(line):
    m = FROM.search(line)
    if not m:
        return None
    return int(m.group(2)) + (1 if m.group(1) == '>' else 0)


def period(coeffs, order, init, m):
    """(pre-period, period) of the sequence mod m, computed exactly.

    The state (a(n), ..., a(n+r-1)) mod m determines everything after it and there are m^r
    states, so a state must recur; the first recurrence gives both numbers.
    """
    st = tuple(v % m for v in init[:order])
    seen = {st: 0}
    seq = [st]
    n = 0
    limit = m ** order + 1
    while n < limit:
        nxt = tuple(list(st[1:]) + [sum(int(coeffs[i]) * st[order - i] for i in coeffs) % m])
        n += 1
        if nxt in seen:
            return seen[nxt], n - seen[nxt]
        seen[nxt] = n
        seq.append(nxt)
        st = nxt
    return None


def terms_mod(coeffs, order, init, m, upto):
    out = [v % m for v in init[:order]]
    while len(out) < upto:
        out.append(sum(int(coeffs[i]) * out[-i] for i in coeffs) % m)
    return out


def decide(coeffs, order, init, c, m, start, nres=0, nmod=1):
    """settle 'a(n) = c (mod m) for every n >= start'.

    Returns ('PROVED', pre, per) or ('FALSE', n, value) with a counterexample index, or None
    when the state space is too large to enumerate.
    """
    got = period(coeffs, order, init, m)
    if got is None:
        return None
    pre, per = got
    # everything from index `pre` on repeats with period `per`, so one window past
    # max(start, pre) decides the claim for every later index at once
    lo = max(start, pre)
    vals = terms_mod(coeffs, order, init, m, lo + per + order + 2)
    import math
    span = per * (nmod // math.gcd(per, nmod)) if nmod > 1 else per
    vals = terms_mod(coeffs, order, init, m, lo + span + order + 2)
    for j in range(start, lo + span):
        if j % nmod != nres % nmod:
            continue
        if j < len(vals) and vals[j] != c % m:
            return ('FALSE', j, vals[j])
    return ('PROVED', pre, per)
