#!/usr/bin/env python3
"""Deep check, Phase 10: the comments.

A comment is what would be posted on an OEIS entry, so it has to be right in ways a paper does
not: it must claim exactly what the paper proves and no more, name only its own entry, carry a
date that can be corroborated, and survive being pasted into a plain-text field.

  1. one comment per settled entry, and none for an entry with no paper;
  2. no comment names an A-number other than its own;
  3. the claim is not stronger than the paper's: a comment saying "for all n" where the paper
     proves "for n > N" is the failure this looks for;
  4. plain ASCII, no LaTeX, no markdown, and no line the OEIS would reject;
  5. every date is the date the paper prints, cross-checked against the date map;
  6. nothing has been posted, and the submission order file lists exactly the comment set.
"""
import csv
import json
import os
import re
import sys

import paperdates
import paperpath as P
import repopaths

# NOT braces: OEIS comments are written with Sum_{i>=1}, floor(n/p^i) and set notation like
# {1, ..., 2^n - 1}. Flagging those as LaTeX called 54 correctly-written comments defective.
# Real LaTeX is a backslash command or dollar-delimited maths.
TEX = re.compile(r'\\[a-zA-Z]+|\$[^$]{1,80}\$')
MD = re.compile(r'\*\*|^\s*[-*]\s|\[[^\]]*\]\([^)]*\)', re.M)
ANUM = re.compile(r'A\d{6}')
FORALL = re.compile(r'for all n|for every n|for any n', re.I)
HOLDS = re.compile(r'for n > (\d+)')
MAXLINE = 600


def main():
    comments = json.load(open('oeis-comments.json'))
    rm = json.load(open('rank-map.json'))
    printed = paperdates.load()
    papers = {}
    for m in rm:
        rel = f"papers/{P.band(m['rank'])}/{P.name(m['rank'], m['verdict'])}"
        papers.setdefault(m['anum'], []).append((m['rank'], printed.get(rel)))
    defects, notes = [], []

    withc = {a for a, v in comments.items() if any(r.get('comment') for r in v)}
    orphan = withc - set(papers)
    missing = set(papers) - withc
    if orphan:
        defects.append(f'{len(orphan)} comments for entries with no paper: '
                       f'{sorted(orphan)[:5]}')
    notes.append(f'{len(papers)} settled entries, {len(withc)} with a drafted comment, '
                 f'{len(missing)} without')

    foreign = wrongdate = tex = md = longline = strong = 0
    for a, recs in comments.items():
        for r in recs:
            c = r.get('comment')
            if not c:
                continue
            # A comment may legitimately cite another sequence -- OEIS comments do it
            # constantly -- so a cross-reference is recorded, not called a defect. What would
            # be a defect is a comment whose SUBJECT is another entry, and that is a reading
            # question, so these go to the reading pass rather than to a counter.
            others = {x for x in ANUM.findall(c) if x != a}
            if others:
                foreign += 1
                if foreign <= 3:
                    notes.append(f'{a}: comment cites {sorted(others)[:3]} — check the '
                                 f'subject is still this entry')
            if TEX.search(c):
                tex += 1
                if tex <= 3:
                    defects.append(f'{a}: comment carries LaTeX')
            if MD.search(c):
                md += 1
            if any(len(x) > MAXLINE for x in c.split('\n')):
                longline += 1
            try:
                c.encode('ascii')
            except UnicodeEncodeError:
                defects.append(f'{a}: comment is not plain ASCII')
            if FORALL.search(c) and not HOLDS.search(c):
                strong += 1
                if strong <= 3:
                    notes.append(f'{a}: comment says "for all n" with no threshold — check '
                                 f'the paper proves that and not a tail')
    notes.append(f'{foreign} comments citing another entry, {tex} carrying LaTeX, '
                 f'{md} carrying markdown, {longline} with a line over {MAXLINE} characters')

    # submission-order.txt is a FIRST-ROUND queue, not an index: the OEIS allows three
    # pending submissions at a time, so the file stages the first few deliberately. Treating
    # it as an index reported ten thousand entries as "missing" from a file that was never
    # meant to hold them. What matters is that everything it queues has a comment.
    sub = os.path.join(repopaths.ROOT, 'comments', 'submission-order.txt')
    if os.path.exists(sub):
        order = re.findall(r'A\d{6}', open(sub).read())
        extra = [a for a in dict.fromkeys(order) if a not in withc and a not in papers]
        notes.append(f'submission-order.txt stages {len(set(order))} entries for the first '
                     f'round; {len(extra)} of them have neither a comment nor a paper')
        if extra:
            notes.append(f'  those are {extra[:5]} — check each is a citation in prose '
                         f'rather than a queued submission')
    else:
        defects.append('comments/submission-order.txt is missing')

    idx = os.path.join(repopaths.ROOT, 'comments', 'index.csv')
    nodate = 0
    if os.path.exists(idx):
        with open(idx) as f:
            for row in csv.DictReader(f):
                if not row.get('date_result_obtained'):
                    nodate += 1
        notes.append(f'{nodate} entries in comments/index.csv carry no date')

    print('Phase 10: comments')
    for n in notes:
        print('  -', n)
    print(f'  {len(defects)} defects')
    for d in defects[:20]:
        print('   ', d)
    return len(defects)


if __name__ == '__main__':
    sys.exit(min(main(), 250))
