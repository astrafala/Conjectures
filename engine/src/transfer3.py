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
import namecanon
from itertools import product

NAME = re.compile(
    r'Number of \(?n\s*\+\s*1\)?\s*X\s*\(?(\d+)(?:\s*\+\s*1)?\)?\s*0\.\.(\d+)\s*arrays?\s*'
    r'with every 2\s*X\s*2 subblock having its diagonal sum differing from its '
    r'antidiagonal sum by\s*(\d+)\s*(,\s*with no adjacent elements equal)?',
    re.I)


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
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
    """The row digraph, with each row's successors GENERATED rather than searched for.

    The old build compared every row with every other row, which is (alpha+1)^(2*cols) work:
    at width 7 over 0..4 that is 78,125 rows and six billion comparisons, and the entries of
    this family sat in the pool as "refused" when nothing about them was hard. The condition
    is linear, so it can be solved instead of tested. Writing the block condition as

        |r_j + s_{j+1} - r_{j+1} - s_j| = c   <=>   s_{j+1} - s_j = (r_{j+1} - r_j) +- c,

    the successor s is determined by its first entry and one sign per column, so a row has at
    most (alpha+1) * 2^(cols-1) candidates and they are written down directly. The digraph is
    the same digraph; only the way it is found has changed.
    """
    allrows = list(product(range(alpha + 1), repeat=cols))
    if noadj:
        st = [r for r in allrows if all(r[j] != r[j + 1] for j in range(cols - 1))]
    else:
        st = allrows
    index = {r: i for i, r in enumerate(st)}
    # c = 0 makes the two signs the same choice; the set keeps one of each
    signs = sorted(set(product((c, -c), repeat=cols - 1))) if cols > 1 else [()]
    adj = []
    for r in st:
        deltas = [r[j + 1] - r[j] for j in range(cols - 1)]
        out = set()
        for e in signs:
            step = [deltas[j] + e[j] for j in range(cols - 1)]
            for s0 in range(alpha + 1):
                if noadj and r[0] == s0:
                    continue
                v = s0
                sv = [s0]
                ok = True
                for j in range(cols - 1):
                    v += step[j]
                    if not 0 <= v <= alpha or (noadj and v == r[j + 1]):
                        ok = False
                        break
                    sv.append(v)
                if not ok:
                    continue
                i = index.get(tuple(sv))
                if i is not None:
                    out.add(i)
        adj.append(sorted(out))
    return st, adj
