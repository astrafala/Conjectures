#!/usr/bin/env python3
"""Deep check, Phase 2: text that must not be in a paper.

A paper is a proof and stays a proof. It carries no proposed OEIS comment (those live in
comments/), it points at no other paper, and it carries no drafting residue and no
credential. Each pattern here is one that has actually been found in a published paper, or
one whose presence would be embarrassing in a way no reader would report.

Run over a slice: dc_phase2.py [lo hi]. With no arguments it does the whole corpus, which
takes a few minutes, so the usual use is four slices in parallel.
"""
import csv
import json
import os
import re
import sys

import pypdf

import dc_text
import repopaths

# (name, pattern, why it must not appear)
FORBIDDEN = [
    ('comment appendix', r'Suggested OEIS comment|house style|Proposed OEIS comment',
     'comments live in comments/, so that a paper is only ever a proof'),
    ('points at another paper',
     r'as in the companion|the same argument as in|see paper \d|elsewhere in this series'
     r'|this family of notes|as we did for A\d{6}',
     'every paper must stand alone: a reader has one paper, not the roster'),
    ('drafting residue', r'\bTODO\b|\bFIXME\b|\bXXX\b|\bTK\b|lorem ipsum|\?\?',
     'text that was never finished'),
    ('unresolved reference', r'\[\?\]|\bref\{|\bcite\{',
     'a LaTeX reference that did not resolve prints as a question mark'),
    ('credential', r'(?i)password|api[_ -]?key|secret[_ -]?key|ghp_[A-Za-z0-9]{20}',
     'nothing of the sort belongs in a published paper'),
    ('foreign email', r'[\w.+-]+@(?!nowhere)[\w-]+\.[\w.]+',
     'the only contact detail in a paper is the author, and these papers give none'),
]
NEEDED = [
    ('an abstract', r'Abstract'),
    ('a verification section', r'(?i)verification'),
    ('references', r'(?i)references'),
    ('the author', r'Adrian Perez Fontelles'),
]


def text(path):
    r = pypdf.PdfReader(path)
    return '\n'.join((p.extract_text() or '') for p in r.pages), len(r.pages)


def main(lo, hi):
    with open(os.path.join(repopaths.ROOT, 'papers', 'index.csv')) as f:
        idx = [r for r in csv.DictReader(f) if lo <= int(r['rank']) <= hi]
    defects = []
    for r in idx:
        try:
            t, pages = text(os.path.join(repopaths.ROOT, r['file']))
        except Exception as e:
            defects.append({'rank': int(r['rank']), 'check': 'opens', 'detail': str(e)})
            continue
        flat = dc_text.flat(t)
        for name, pat, _ in FORBIDDEN:
            m = re.search(pat, flat)
            if m:
                defects.append({'rank': int(r['rank']), 'check': name,
                                'detail': flat[max(0, m.start() - 40):m.end() + 40]})
        for name, pat in NEEDED:
            if not re.search(pat, flat):
                defects.append({'rank': int(r['rank']), 'check': f'missing {name}',
                                'detail': ''})
        if r['anum'] not in flat:
            defects.append({'rank': int(r['rank']), 'check': 'names its own entry',
                            'detail': f"paper does not contain {r['anum']}"})
        if pages < 2:
            defects.append({'rank': int(r['rank']), 'check': 'has a page count',
                            'detail': f'{pages} page'})
    out = os.path.join(repopaths.ROOT, 'deep-check', f'phase2-{lo}.json')
    json.dump(defects, open(out, 'w'), indent=1)
    print(f'{lo}..{hi}: {len(idx)} papers, {len(defects)} defects -> {os.path.basename(out)}')
    return defects


if __name__ == '__main__':
    lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 10 ** 9)
    main(lo, hi)
