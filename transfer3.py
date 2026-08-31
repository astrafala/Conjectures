#!/usr/bin/env python3
"""Transfer matrix for the Hardin "constant-stress tiling" families.

    Number of (n+1) X (K+1) 0..m arrays with every 2 X 2 subblock having its diagonal sum
    differing from its antidiagonal sum by c [, with no adjacent elements equal].

For a 2 x 2 block with top row (r_j, r_{j+1}) and bottom row (s_j, s_{j+1}) the diagonal
sum is r_j + s_{j+1} and the antidiagonal sum is r_{j+1} + s_j, so the condition reads
|r_j + s_{j+1} - r_{j+1} - s_j| = c. "No adjacent elements equal" is r_j != r_{j+1} within
a row (a condition on the vertex) and r_j != s_j between rows (a condition on the edge).
Both are local to a consecutive pair of rows, so the row digraph applies unchanged.
"""
import re
from itertools import product

NAME = re.compile(
    r'Number of \(?n\s*\+\s*1\)?\s*X\s*\(?(\d+)(?:\s*\+\s*1)?\)?\s*0\.\.(\d+)\s*arrays?\s*'
    r'with every 2\s*X\s*2 subblock having its diagonal sum differing from its '
    r'antidiagonal sum by\s*(\d+)\s*(,\s*with no adjacent elements equal)?',
    re.I)


def parse_name(nm):
    norm = re.sub(r'(?<=[\d)])\s*[xX]\s*(?=[\d(])', ' X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    if re.search(r'X\s*\(\s*n', norm):          # square (n+1) X (n+1): not a walk in n
        return None
    m = NAME.search(norm)
    if not m:
        return None
    k = int(m.group(1))
    cols = k + 1 if re.search(r'X\s*\(\s*\d+\s*\+\s*1\s*\)', norm) else k
    alpha = int(m.group(2))
    c = int(m.group(3))
    noadj = bool(m.group(4))
    return cols, alpha, c, noadj


def build(cols, alpha, c, noadj):
    allrows = list(product(range(alpha + 1), repeat=cols))
    if noadj:
        st = [r for r in allrows if all(r[j] != r[j + 1] for j in range(cols - 1))]
    else:
        st = allrows
    adj = []
    for r in st:
        row = []
        for si, s in enumerate(st):
            ok = True
            if noadj and any(r[j] == s[j] for j in range(cols)):
                ok = False
            if ok:
                for j in range(cols - 1):
                    if abs(r[j] + s[j + 1] - r[j + 1] - s[j]) != c:
                        ok = False; break
            if ok:
                row.append(si)
        adj.append(row)
    return st, adj
