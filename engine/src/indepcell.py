#!/usr/bin/env python3
"""An independent check of the cell-count family.

Like `indep2x2.py`, this shares no code with any engine. It reads the entry name with its own
grammar, enumerates every array of the stated shape, tests the condition cell by cell, and
counts.

The family: "Number of n X W 0..m arrays with each element x equal to the number its
horizontal and vertical neighbors equal to p(0),...,p(m) for x=0,...,m". The reading taken
here, written out so it can be argued with:

  * a cell's HORIZONTAL AND VERTICAL neighbours are the up to four cells sharing an edge with
    it --- corners are not neighbours, and cells off the edge of the array are not neighbours
    either, so a corner cell has two and an edge cell three;
  * the list after "equal to" is indexed by the cell's OWN value: a cell holding x must have
    exactly x neighbours holding p[x];
  * "n X W" means n rows and W columns, with n the sequence's argument.

    python3 src/indepcell.py [limit]
"""
import itertools
import json
import os
import re
import sys

import localentry as LE

NAME = re.compile(
    r'(?i)^\s*Number of\s+(?:\(\s*n\s*\+\s*(\d+)\s*\)|n)\s*X\s*(\d+)\s+0\.\.(\d+)\s+arrays\s+'
    r'(?:x\(i,j\)\s+)?with\s+each element x equal to the number (?:of )?its\s+'
    r'horizontal and vertical\s+neighbors equal to\s+([\d,\s]+?)\s+for x=\s*([\d,\s]+?)\s*\.?\s*$')


def parse(name):
    """(rows_add, cols, alpha, mapping) or None"""
    m = NAME.match(' '.join(name.split()))
    if not m:
        return None
    add = int(m.group(1) or 0)
    cols, alpha = int(m.group(2)), int(m.group(3))
    vals = [int(v) for v in m.group(4).split(',') if v.strip() != '']
    idx = [int(v) for v in m.group(5).split(',') if v.strip() != '']
    # the "for x=..." list says which value each entry of the mapping belongs to; if it is not
    # 0..alpha in order, this program does not know what the name means and says so
    if idx != list(range(alpha + 1)) or len(vals) != alpha + 1:
        return None
    if any(not 0 <= v <= alpha for v in vals):
        return None
    return add, cols, alpha, vals


def count(rows, cols, alpha, p):
    """Every array, one at a time."""
    tot = 0
    for flat in itertools.product(range(alpha + 1), repeat=rows * cols):
        ok = True
        for i in range(rows):
            for j in range(cols):
                x = flat[i * cols + j]
                want = p[x]
                c = 0
                if i:
                    c += flat[(i - 1) * cols + j] == want
                if i + 1 < rows:
                    c += flat[(i + 1) * cols + j] == want
                if j:
                    c += flat[i * cols + j - 1] == want
                if j + 1 < cols:
                    c += flat[i * cols + j + 1] == want
                if c != x:
                    ok = False
                    break
            if not ok:
                break
        tot += ok
    return tot


def check(a, max_arrays=4 * 10 ** 7):
    e = LE.get(a)
    got = parse(e['name'])
    if not got:
        return 'not this family, or a shape this program does not read'
    add, cols, alpha, p = got
    off = int(e['offset'].split(',')[0])
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mine, k = [], 0
    while k < min(len(d), 8):
        rows = off + k + add
        if (alpha + 1) ** (rows * cols) > max_arrays:
            break
        mine.append(count(rows, cols, alpha, p))
        k += 1
    if not mine:
        return 'the smallest array is already too big to enumerate'
    if mine == d[:len(mine)]:
        return f'OK on {len(mine)} terms'
    return f'DISAGREES: brute force {mine}, entry {d[:len(mine)]}'


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9
    roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    out = json.load(open('indepcell_done.json')) if os.path.exists('indepcell_done.json') else {}
    n = 0
    for a in sorted(roster):
        if a in out:
            continue
        try:
            e = LE.get(a)
        except Exception:
            continue
        if 'each element x equal to the number' not in e['name']:
            continue
        out[a] = check(a)
        json.dump(out, open('indepcell_done.json', 'w'), indent=0)
        print(a, out[a], flush=True)
        n += 1
        if n >= limit:
            break
    ok = sum(1 for v in out.values() if v.startswith('OK'))
    bad = [a for a, v in out.items() if v.startswith('DISAGREES')]
    print(f'\n{len(out)} entries in the cell-count family attempted, {ok} independently '
          f'confirmed, {len(bad)} disagreeing')
    for a in bad[:20]:
        print('  ', a, out[a])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
