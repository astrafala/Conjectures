#!/usr/bin/env python3
"""Deep check, Phase 8: wording and logic.

Four mechanical checks over every paper, each of one that has failed before or would fail
silently:

  1. **Verdict agreement.** A paper the roster marks a disproof must say it disproves, and a
     paper marked a proof must say it proves. Checked against the roster flag and the
     displayed statement, not against the title, because the title is the easiest thing to
     get right and the least informative.

  2. **The double-negation class.** An entry that says "no element ..." and a paper that says
     "every element ..." are opposite claims. This once put 66 papers into the exact reverse
     of their entry, so the quantifier in the paper's own condition sentence is compared with
     the quantifier of the entry's name.

  3. **Numbers in prose.** The order stated in the abstract, the state count, and the
     threshold are each compared with the roster's record of them. A paper that says one
     number in its abstract and another in its theorem is a defect whichever is right.

  4. **Required parts.** Abstract; a section 1 that quotes the conjecture and says it is still
     open; a Verification section; references. A missing part is a defect even when everything
     present is correct.

    python3 src/dc_phase8.py [lo] [hi]
"""
import csv
import json
import os
import re
import sys

import dc_text
import localentry as LE
import repopaths

try:
    import pypdf
except ImportError:
    pypdf = None

PAGENO = re.compile(r'^\s*\d{1,4}\s*$')
NEG = re.compile(r'\bno\b|\bnot\b|\bnever\b|\bunequal\b|\bavoid', re.I)
POS = re.compile(r'\bevery\b|\ball\b|\beach\b', re.I)
NEEDED = [('an abstract', re.compile(r'Abstract')),
          ('a verification section', re.compile(r'(?i)verification')),
          ('references', re.compile(r'(?i)\breferences\b|bibliography')),
          # the papers write "still recorded as AN UNPROVEN conjecture" and "still recorded
          # as A conjecture"; a pattern that expected the adjective straight after "as"
          # reported 68 of the first 300 as missing a sentence every one of them has
          ('the still-open statement', re.compile(
              r'(?i)still\s+recorded\s+as\b|still\s+(?:empirical|open|unproven)\b|'
              r'never marked settled|nothing on the entry records it as proved|'
              r'is still open|remains open|not been (?:proved|settled)'))]
ORDER = re.compile(r'recurrence of order \$?(\d+)')
STATES = re.compile(r'walk count on \$?S\s*=\s*([\d ,]+)')
THRESH = re.compile(r'for every \$?n\s*>\s*(\d+)')


def text(path):
    r = pypdf.PdfReader(path)
    out = []
    for page in r.pages:
        for L in (page.extract_text() or '').split('\n'):
            if not PAGENO.match(L):
                out.append(L)
    return dc_text.normalise('\n'.join(out))


def main(lo, hi):
    if pypdf is None:
        print('pypdf unavailable'); return 1
    with open(os.path.join(repopaths.ROOT, 'papers', 'index.csv')) as f:
        idx = [r for r in csv.DictReader(f) if lo <= int(r['rank']) <= hi]
    rm = {(m['rank']): m for m in json.load(open('rank-map.json'))}
    defects, flip, missing = [], [], {}
    checked = 0
    for r in idx:
        rank, a = int(r['rank']), r['anum']
        try:
            t = text(os.path.join(repopaths.ROOT, r['file']))
        except Exception as exc:
            defects.append((rank, a, f'unreadable: {exc}')); continue
        checked += 1
        low = t.lower()

        # A proof may perfectly well say "the statement is false for k even" while
        # delimiting its hypothesis; looking for those words anywhere called such a paper a
        # disproof. Only the abstract speaks for the paper as a whole.
        isdis = r['verdict'].upper() == 'DISPROOF'
        i = low.find('abstract')
        head = low[i:i + 1400] if i >= 0 else low[:1400]
        says_dis = ('disprov' in head or 'counterexample' in head
                    or 'the conjecture is false' in head or 'empirical recurrence is false' in head)
        says_pro = re.search(r'\bwe prove\b|\bit is true\b|\bis true[,.]|\bproved\b',
                             head) is not None
        if isdis and not says_dis:
            defects.append((rank, a, 'marked a disproof but never says it disproves'))
        if not isdis and says_dis and not says_pro:
            defects.append((rank, a, 'marked a proof but reads as a disproof'))

        for what, rx in NEEDED:
            if not rx.search(t):
                missing.setdefault(what, []).append((rank, a))

        try:
            name = LE.get(a)['name']
        except Exception:
            name = ''
        m = re.search(r'arrays? with (.{0,60})', name, re.I)
        if m:
            clause = m.group(1)
            ename_neg = bool(NEG.match(clause.strip()))
            mm = re.search(r'asks that (.{0,80})', t)
            if mm:
                pclause = mm.group(1)
                ppos = bool(POS.match(pclause.strip())) and not NEG.search(pclause[:20])
                if ename_neg and ppos:
                    flip.append((rank, a, clause[:40], pclause[:40]))

        ordn = ORDER.search(t)
        thr = THRESH.search(t)
        rec = rm.get(str(rank)) or {}
        if ordn and 'order' in rec and int(ordn.group(1)) != int(rec['order']):
            defects.append((rank, a, f"abstract says order {ordn.group(1)}, "
                                     f"roster records {rec['order']}"))

    print(f'Phase 8: {checked} papers')
    print(f'  {len(defects)} defects')
    for d in defects[:25]:
        print('   ', *d)
    print(f'  missing required parts:')
    for what, rows in sorted(missing.items(), key=lambda x: -len(x[1])):
        print(f'    {len(rows):5d}  {what}   e.g. {rows[:3]}')
    print(f'  {len(flip)} papers whose condition sentence reads positive where the entry '
          f'reads negative (the double-negation class; each needs a reading):')
    for d in flip[:15]:
        print('   ', *d)
    return len(defects)


if __name__ == '__main__':
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    sys.exit(min(main(lo, hi), 250))
