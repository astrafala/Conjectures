#!/usr/bin/env python3
"""Make every number in the repository agree with paper-engines.json.

The roster count appears in six places -- the ledger's roster line, the README, the
methodology, the citation record, the Zenodo record and the papers index. Editing them by hand
after every batch is how they drift apart, and drift is the kind of error a reader notices
first. This does all six from the one source of truth.
"""
import json, re, collections

pe = json.load(open('paper-engines.json'))
n = len(pe)
dis = sum(1 for v in pe.values() if v['disproof'])
pro = n - dis
anums = len({v['anum'] for v in pe.values()})
args = len(collections.Counter(v['engine'] for v in pe.values()))

NUM = r'[\d,]+'
SUBS = [
    ('LEDGER.md', [
        (rf'Roster: \*\*{NUM} papers\*\* \({NUM} proofs, {NUM} disproofs\)',
         f'Roster: **{n} papers** ({pro} proofs, {dis} disproofs)')]),
    ('README.md', [
        (rf'\*\*{NUM} papers\*\* settling conjectures across \*\*{NUM} entries\*\*',
         f'**{n} papers** settling conjectures across **{anums} entries**'),
        (rf'\*\*{NUM} proofs\*\* and\s+\*\*{NUM} disproofs\*\*, by \*\*{NUM} distinct arguments\*\*',
         f'**{pro} proofs** and\n**{dis} disproofs**, by **{args} distinct arguments**'),
        (rf'All {NUM} papers\.', f'All {n} papers.')]),
    ('METHODOLOGY.md', [
        (rf'{NUM} distinct arguments across {NUM} entries',
         f'{args} distinct arguments across {anums} entries')]),
    ('CITATION.cff', [
        (rf'{NUM} papers settling conjectures across {NUM} entries',
         f'{n} papers settling conjectures across {anums} entries'),
        (rf'{NUM} proofs and {NUM} disproofs', f'{pro} proofs and {dis} disproofs')]),
    ('.zenodo.json', [
        (rf'{NUM} papers settling conjectures across {NUM} entries',
         f'{n} papers settling conjectures across {anums} entries'),
        (rf'{NUM} proofs and {NUM} disproofs', f'{pro} proofs and {dis} disproofs')]),
]

changed = []
for path, subs in SUBS:
    try:
        s = open(path).read()
    except FileNotFoundError:
        continue
    before = s
    for pat, rep in subs:
        s2, k = re.subn(pat, rep, s)
        if k == 0:
            print(f'  WARNING: no match in {path} for {pat[:50]}...')
        s = s2
    if s != before:
        open(path, 'w').write(s)
        changed.append(path)
print(f'roster {n} = {pro} proofs + {dis} disproofs, {anums} entries, {args} arguments')
print('updated:', ', '.join(changed) if changed else 'nothing (already in sync)')
