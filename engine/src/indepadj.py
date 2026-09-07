#!/usr/bin/env python3
"""An independent check of the adjacent-elements family --- the largest in the corpus.

1,121 entries read "Number of n X W 0..m arrays with every element (un)equal to <counts>
<neighbourhood> adjacent elements, with upper left element zero". Like the other two
independent checks, this shares no code with any engine: it reads the name with its own
grammar, enumerates every array of the stated shape, and tests each cell directly.

The readings taken, written out so they can be argued with rather than trusted:

  * KING-MOVE adjacency is all eight surrounding cells; HORIZONTALLY is left and right,
    VERTICALLY up and down, DIAGONALLY the two cells on the falling diagonal (up-left and
    down-right), ANTIDIAGONALLY the two on the rising one (up-right and down-left);
  * a cell off the edge of the array is not a neighbour, so a corner cell simply has fewer;
  * "every element EQUAL TO k adjacent elements" counts the neighbours holding the SAME value
    as the cell and requires that count to be one of the listed numbers;
  * "every element UNEQUAL TO k adjacent elements" counts the neighbours holding a DIFFERENT
    value --- not the complement of the equal count against eight, but against however many
    neighbours the cell actually has;
  * "with upper left element zero" fixes A[0][0] = 0 and says nothing about any other cell.

The two readings of "unequal" matter: on an edge cell they differ, which is exactly the kind
of thing an engine and a second program can disagree about, and exactly why this exists.

    python3 src/indepadj.py [limit] [max_arrays]
"""
import itertools
import json
import os
import re
import sys

import localentry as LE

NAME = re.compile(
    r'(?i)^\s*Number of\s+(?:\(\s*n\s*\+\s*(\d+)\s*\)|n)\s*X\s*(\d+)\s+0\.\.(\d+)\s+arrays\s+'
    r'with\s+every element\s+(equal|unequal)\s+to\s+([\d,\sor]+?)\s+'
    r'(king-move|[a-z,\s]+?)\s+adjacent(?:\s+elements)?\s*,\s*'
    r'with upper left element zero\s*\.?\s*$')
DIRS = {'horizontally': [(0, -1), (0, 1)],
        'vertically': [(-1, 0), (1, 0)],
        'diagonally': [(-1, -1), (1, 1)],
        'antidiagonally': [(-1, 1), (1, -1)]}
KING = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]


def _dirs(text):
    t = text.strip().lower()
    if t == 'king-move':
        return KING
    words = [w for w in re.split(r'[,\s]+|\bor\b', t) if w]
    out = []
    for w in words:
        if w not in DIRS:
            return None
        out += DIRS[w]
    return out or None


def _counts(text):
    v = [int(x) for x in re.findall(r'\d+', text)]
    return set(v) if v else None


def parse(name):
    """(rows_add, cols, alpha, want_equal, allowed_counts, offsets) or None"""
    m = NAME.match(' '.join(name.split()))
    if not m:
        return None
    add = int(m.group(1) or 0)
    cols, alpha = int(m.group(2)), int(m.group(3))
    eq = m.group(4).lower() == 'equal'
    allowed = _counts(m.group(5))
    offs = _dirs(m.group(6))
    if allowed is None or offs is None:
        return None
    return add, cols, alpha, eq, allowed, offs


def count(rows, cols, alpha, eq, allowed, offs):
    """Every array with A[0][0] = 0, one at a time."""
    tot = 0
    rest = rows * cols - 1
    for tail in itertools.product(range(alpha + 1), repeat=rest):
        flat = (0,) + tail
        ok = True
        for i in range(rows):
            for j in range(cols):
                x = flat[i * cols + j]
                c = 0
                for di, dj in offs:
                    a, b = i + di, j + dj
                    if 0 <= a < rows and 0 <= b < cols:
                        c += (flat[a * cols + b] == x) if eq else (flat[a * cols + b] != x)
                if c not in allowed:
                    ok = False
                    break
            if not ok:
                break
        tot += ok
    return tot


def check(a, max_arrays=4 * 10 ** 6):
    e = LE.get(a)
    got = parse(e['name'])
    if not got:
        return 'not this family, or a shape this program does not read'
    add, cols, alpha, eq, allowed, offs = got
    off = int(e['offset'].split(',')[0])
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mine, k = [], 0
    while k < min(len(d), 8):
        rows = off + k + add
        if (alpha + 1) ** (rows * cols - 1) > max_arrays:
            break
        mine.append(count(rows, cols, alpha, eq, allowed, offs))
        k += 1
    if not mine:
        return 'the smallest array is already too big to enumerate'
    if mine == d[:len(mine)]:
        return f'OK on {len(mine)} terms'
    return f'DISAGREES: brute force {mine}, entry {d[:len(mine)]}'


def write_summary(out, family, path):
    """The tracked record of what this check established.

    The per-entry file is rewritten after every entry, so while a run is going it is dirty
    in the working tree every few seconds and no commit of it is ever current. That file is
    progress, not a result: it is left untracked. THIS is the result --- written once, when
    the run has nothing left to attempt --- and it is the one that is stored.
    """
    import collections
    kinds = collections.Counter(v.split(':')[0].split(' on ')[0] for v in out.values())
    json.dump({'family': family,
               'attempted': len(out),
               'confirmed': sum(1 for v in out.values() if v.startswith('OK')),
               'disagreeing': sorted(a for a, v in out.items() if v.startswith('DISAGREES')),
               'terms': {a: int(v.split()[2]) for a, v in out.items() if v.startswith('OK')},
               'outcomes': dict(kinds)},
              open(path, 'w'), indent=1, sort_keys=True)


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9
    mx = int(sys.argv[2]) if len(sys.argv) > 2 else 4 * 10 ** 6
    roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    out = json.load(open('indepadj_done.json')) if os.path.exists('indepadj_done.json') else {}
    n = 0
    for a in sorted(roster):
        if a in out:
            continue
        try:
            e = LE.get(a)
        except Exception:
            continue
        if 'adjacent elements, with upper left element zero' not in ' '.join(e['name'].split()):
            continue
        out[a] = check(a, mx)
        json.dump(out, open('indepadj_done.json', 'w'), indent=0)
        print(a, out[a], flush=True)
        n += 1
        if n >= limit:
            break
    ok = sum(1 for v in out.values() if v.startswith('OK'))
    bad = [a for a, v in out.items() if v.startswith('DISAGREES')]
    write_summary(out, 'adjacent-elements', 'deep-check/indep-adj.json')
    print(f'\n{len(out)} entries in the adjacent-elements family attempted, {ok} '
          f'independently confirmed, {len(bad)} disagreeing')
    for a in bad[:20]:
        print('  ', a, out[a])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
