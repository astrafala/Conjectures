#!/usr/bin/env python3
"""Cell conditions counted up to relabelling of the alphabet.

    Number of n X K 0..m arrays with no element equal to more than one of its horizontal
    and vertical neighbors, and new values 0..m introduced in row major order.

The clause "new values 0..m introduced in row major order" says the array is the canonical
representative of its EQUALITY PATTERN: what is counted is patterns using at most m+1
letters, not arrays. Patterns are not a walk count directly, but they are a fixed integer
combination of walk counts, and that is enough.

Write N_j for the number of admissible patterns using exactly j letters and L_i for the
number of admissible arrays over an alphabet of size i. Since an array over i letters is a
pattern together with an injection of its letters into the alphabet,

    L_i  =  sum_j N_j * i(i-1)...(i-j+1),

a triangular system with unit diagonal, hence invertible over the rationals. The entry counts
a = N_1 + ... + N_{m+1}, so a is the fixed rational combination  a = (1^T F^{-1}) L  of the
L_i, where F is the matrix of falling factorials. Each L_i is a walk count on its own transfer
graph, so a is a walk count on the disjoint union of those graphs with a weighted starting
vector -- the weights being where the negative rational coefficients live. Everything after
that is the usual residual test.

This is only legitimate when the condition itself is invariant under permuting the alphabet,
which is exactly what `transfer19` records in its `inv` flag: a condition stated through
equality qualifies, one naming a literal value or comparing sizes does not.
"""
import re
from fractions import Fraction
import transfer19 as T19

# the clause appears as ", and new values 0..2 introduced in row major order" as well as
# ", with new values ... "; requiring the word "with" silently refused the first form
REL = re.compile(r',?\s*(?:and\s+)?(?:with\s+)?new\s+values(?:\s+0\.\.\d+)?\s+introduced'
                 r'\s+in\s+row\s+major\s+order\s*', re.I)
REL2 = re.compile(r',?\s*(?:and\s+)?(?:with\s+)?values\s+0\.\.\d+\s+introduced\s+in\s+row'
                  r'\s+major\s+order\s*', re.I)
REL3 = re.compile(r',?\s*(?:and\s+)?(?:with\s+)?new\s+values\s+introduced\s+in\s+order\s+0'
                  r'\s+sequentially\s+upwards?\s*', re.I)
LEAD = re.compile(r'^\s*new\s+values(?:\s+0\.\.\d+)?\s+introduced\s+in\s+row\s+major\s+order'
                  r'\s+and\s+', re.I)


def strip_relabel(nm):
    """(name with the relabelling clause removed, True) or (name, False)."""
    out = nm
    hit = False
    for rx in (REL, REL2, REL3):
        if rx.search(out):
            out = rx.sub(' ', out)
            hit = True
    m = re.search(r'arrays?\s+with\s+', out, re.I)
    if m and LEAD.match(out[m.end():]):
        out = out[:m.end()] + LEAD.sub('', out[m.end():])
        hit = True
    out = re.sub(r'\s+,', ',', re.sub(r'\s+', ' ', out)).strip()
    # the clause is sometimes the FIRST thing after "arrays with", and the pattern eats the
    # "with" along with it, leaving "arrays and no element ..." -- which no engine reads.
    out = re.sub(r'(arrays?)\s+(?:and|,)\s+', r'\1 with ', out, flags=re.I)
    out = re.sub(r'(arrays?)\s+(?=no |every |each |all |with )', r'\1 ', out, flags=re.I)
    out = re.sub(r'(arrays?) (no |every |each |all )', r'\1 with \2', out, flags=re.I)
    out = re.sub(r'\s*,\s*\.', '.', out)
    out = out.rstrip().rstrip(',')
    if not out.endswith('.'):
        out += '.'
    return out, hit


def falling_weights(K):
    """the rational c with a = sum_i c_i L_i, for patterns of at most K letters."""
    F = [[Fraction(1)] * (K + 1) for _ in range(K + 1)]      # F[i][j], 1-based in i and j
    for i in range(1, K + 1):
        for j in range(1, K + 1):
            v = Fraction(1)
            for t in range(j):
                v *= (i - t)
            F[i][j] = v
    # solve c^T F = 1^T, i.e. F^T c = 1
    A = [[F[i][j] for i in range(1, K + 1)] + [Fraction(1)] for j in range(1, K + 1)]
    n = K
    for col in range(n):
        piv = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        d = A[col][col]
        A[col] = [x / d for x in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
    return [A[r][n] for r in range(n)]                        # c_1 .. c_K


def parse_name(nm):
    plain, hit = strip_relabel(nm)
    if not hit:
        return None
    p = T19.parse_name(plain)
    if not p or not p['inv']:
        return None
    m = re.search(r'0\.\.(\d+)\s*arrays?|(binary)\s*arrays?', nm, re.I)
    K = (1 if (m and m.group(2)) else int(m.group(1))) + 1 if m else None
    if K is None:
        return None
    p['K'] = K                       # at most K letters
    p['plain'] = plain
    return p


def build(p, cap=40000):
    """block-diagonal union of the models over alphabets of size 1..K, weighted."""
    K = p['K']
    c = falling_weights(K)
    den = 1
    for x in c:
        den = den * x.denominator // _gcd(den, x.denominator)
    w = [int(x * den) for x in c]
    total = 0
    parts = []
    for i in range(1, K + 1):
        q = dict(p)
        q['alpha'] = i - 1
        b = T19.build(q, cap=cap)
        if b is None:
            return None
        parts.append(b)
        total += b[3]
        if total > cap:
            return None
    adj, start, end = [], [], []
    base = 0
    for (a_i, s_i, e_i, S_i), wi in zip(parts, w):
        adj.extend([[k + base for k in row] for row in a_i])
        start.extend([wi * x for x in s_i])
        end.extend(e_i)
        base += S_i
    return adj, start, end, base, den


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


matvec = T19.matvec
terms = T19.terms
threshold = T19.threshold
