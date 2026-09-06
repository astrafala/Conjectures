#!/usr/bin/env python3
"""Read a congruence or divisibility conjecture into something decidable.

Only the shapes a decision procedure can actually settle, and only with a FIXED modulus:

    a(n) == c (mod k)                       for all n, or for n > n0
    a(n) == c mod k                         same, without the parentheses
    a(n) is divisible by k                  c = 0
    k divides a(n)                          c = 0
    a(n) is divisible by k when n is congruent to r1, r2, ... modulo m

A modulus depending on n ("a(n) == 2 (mod n^3)") is refused: the state space is then not
finite and the argument does not apply. So is anything quantified over primes.
"""
import re

MOD = r"\(?\s*mod\s+(\d+)\s*\)?"


def parse(line):
    """(c, k, n_from, residues, m) or None. residues/m restrict n to n = r (mod m)."""
    b = re.sub(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*", "", line, flags=re.I)
    b = b.split(" - _")[0].strip().rstrip(".").strip()
    if re.search(r"\bprime\b|\bp\b\s*\)|a\(p\)|iff|if and only if", b, re.I):
        return None
    if re.search(r"mod\s+[a-zA-Z]", b):          # modulus depends on n
        return None

    n_from, residues, m = None, None, None
    mm = re.search(r"for\s+n\s*>=\s*(\d+)", b)
    if mm:
        n_from = int(mm.group(1))
    mm = re.search(r"for\s+n\s*>\s*(\d+)", b)
    if mm:
        n_from = int(mm.group(1)) + 1
    mm = re.search(r"when\s+n\s+is\s+congruent\s+to\s+([\d,\s]+(?:(?:and|or)[\d,\s]+)*)"
                   r"\s*modulo\s+(\d+)", b, re.I)
    if mm:
        residues = [int(t) for t in re.findall(r"\d+", mm.group(1))]
        m = int(mm.group(2))
        b = b[:mm.start()]

    mm = re.match(r"\s*a\(n\)\s*(?:==|=|\\equiv)\s*(-?\d+)\s*" + MOD, b)
    if mm:
        return int(mm.group(1)), int(mm.group(2)), n_from, residues, m
    mm = re.match(r"\s*a\(n\)\s+is\s+divisible\s+by\s+(\d+)\b", b, re.I)
    if mm:
        return 0, int(mm.group(1)), n_from, residues, m
    mm = re.match(r"\s*(\d+)\s+divides\s+a\(n\)", b, re.I)
    if mm:
        return 0, int(mm.group(1)), n_from, residues, m
    return None
