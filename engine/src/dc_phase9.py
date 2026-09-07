#!/usr/bin/env python3
"""Deep check, Phase 9: length that follows content.

Papers must not be uniform. A result needing one lemma and a three-state model should be
short; one needing a reduction, an excluded misreading and a threshold argument should not.
Uniform length is itself a defect: it means the generator emitted a template rather than
explaining an object.

For every paper a content score is computed from things that genuinely demand explanation ---
how many lemmas it states, how large the model is, whether a misreading had to be excluded,
whether a threshold argument is needed, how many cases the verification reports --- and
compared with the page count. Both directions are flagged:

  * short paper, high score  -> under-explained;
  * long paper, low score    -> padded.

The output is a ranking, not a verdict: the top of each list is what a reader should look at.
"""
import csv
import json
import math
import os
import re
import sys

import dc_text
import repopaths

try:
    import pypdf
except ImportError:
    pypdf = None

PAGENO = re.compile(r'^\s*\d{1,4}\s*$')
LEMMA = re.compile(r'\bLemma\s+\d|\bTheorem\s+\d|\bProposition\s+\d|\bCorollary\s+\d')
STATES = re.compile(r'S\s*=\s*([\d ,]{1,12})')
MISREAD = re.compile(r'(?i)misread|another reading|the strict reading|does not say which|'
                     r'two readings|the reading was pinned')
THRESH = re.compile(r'(?i)threshold|for every \$?n\s*>')
CASES = re.compile(r'(?i)all \$?([\d ,]+)\$? terms')


def text_pages(path):
    r = pypdf.PdfReader(path)
    out = []
    for page in r.pages:
        for L in (page.extract_text() or '').split('\n'):
            if not PAGENO.match(L):
                out.append(L)
    return dc_text.normalise('\n'.join(out)), len(r.pages)


def main(lo, hi):
    if pypdf is None:
        print('pypdf unavailable'); return 1
    with open(os.path.join(repopaths.ROOT, 'papers', 'index.csv')) as f:
        idx = [r for r in csv.DictReader(f) if lo <= int(r['rank']) <= hi]
    rows = []
    for r in idx:
        try:
            t, pages = text_pages(os.path.join(repopaths.ROOT, r['file']))
        except Exception:
            continue
        lemmas = len(set(LEMMA.findall(t)))
        m = STATES.search(t)
        S = int(m.group(1).replace(' ', '').replace(',', '')) if m and m.group(1).strip() else 0
        score = (2.0 * lemmas
                 + (math.log10(S) if S > 1 else 0)
                 + (2.0 if MISREAD.search(t) else 0)
                 + (1.0 if THRESH.search(t) else 0)
                 + (1.0 if CASES.search(t) else 0))
        rows.append((int(r['rank']), r['anum'], pages, round(score, 2), len(t)))
    if not rows:
        print('no papers read'); return 0
    pg = [x[2] for x in rows]
    sc = [x[3] for x in rows]
    print(f'Phase 9: {len(rows)} papers')
    print(f'  pages: min {min(pg)}, median {sorted(pg)[len(pg)//2]}, max {max(pg)}')
    print(f'  score: min {min(sc)}, median {sorted(sc)[len(sc)//2]}, max {max(sc)}')
    # a paper is out of step when its page count sits far from what its score would predict
    import statistics
    ms, ss = statistics.mean(sc), (statistics.pstdev(sc) or 1)
    mp, sp = statistics.mean(pg), (statistics.pstdev(pg) or 1)
    off = []
    for rank, a, pages, score, chars in rows:
        z = (score - ms) / ss - (pages - mp) / sp
        off.append((round(z, 2), rank, a, pages, score))
    off.sort()
    print('\n  most likely PADDED (long for what they explain):')
    for z, rank, a, pages, score in off[:8]:
        print(f'    z={z:6.2f}  rank {rank:5d}  {a}  {pages} pages, score {score}')
    print('\n  most likely UNDER-EXPLAINED (short for what they explain):')
    for z, rank, a, pages, score in off[-8:][::-1]:
        print(f'    z={z:6.2f}  rank {rank:5d}  {a}  {pages} pages, score {score}')
    uniform_pages = sum(1 for x in pg if x == sorted(pg)[len(pg)//2])
    print(f'\n  {uniform_pages} of {len(pg)} papers ({100*uniform_pages//len(pg)}%) sit at '
          f'the median page count — the closer that is to 100%, the more the generators are '
          f'emitting a template rather than explaining an object')
    return 0


if __name__ == '__main__':
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    sys.exit(main(lo, hi))
