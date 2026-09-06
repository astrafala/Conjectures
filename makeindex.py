#!/usr/bin/env python3
"""Index files for papers/, so 8887 PDFs are something a person can actually navigate.

A folder of numbered PDFs is not readable. Every band gets a table naming the OEIS entry each
paper settles and what kind of argument settles it, the top level gets a contents page, and
index.csv carries the whole thing in machine-readable form.
"""
import json, csv, os, collections
import paperpath

rm = json.load(open('rank-map.json'))
desc = json.load(open('engine_desc.json'))
OEIS = 'https://oeis.org/'


def short(engine, verdict):
    d = desc.get(f'{engine}|{verdict}') or desc.get(f'{engine}|PROOF') or ''
    d = ' '.join(d.split())
    return d[:110] + ('...' if len(d) > 110 else '')


bands = collections.defaultdict(list)
for m in rm:
    bands[paperpath.band(m['rank'])].append(m)

with open('papers/index.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['rank', 'anum', 'verdict', 'engine', 'file'])
    for m in rm:
        w.writerow([m['rank'], m['anum'], m['verdict'], m['engine'],
                    paperpath.path(m['rank'], m['verdict'])])

npr = sum(1 for m in rm if m['verdict'] == 'PROOF')
ndis = len(rm) - npr
lines = [
    '# The papers',
    '',
    f'{len(rm)} papers: {npr} proofs and {ndis} disproofs of conjectures recorded as open in',
    'the On-Line Encyclopedia of Integer Sequences.',
    '',
    'Author: **Adrian Perez Fontelles**, independent researcher.',
    '',
    '## How these are ordered',
    '',
    '**The number IS the ranking. 1 is the hardest result, and the last is the easiest.**',
    'Ranking is by the depth of the argument the result needed, not by the size of the',
    'sequence or the length of the paper.',
    '',
    'The papers are filed in bands of 500 only because a web file browser will not list more',
    'than a thousand files in one folder. Rank numbers are zero padded so that a plain',
    'alphabetical listing is the hardness order.',
    '',
    'Each paper names its OEIS entry inside the document, states the conjecture verbatim with',
    'its contributor and date, and gives the range over which it has been settled.',
    '',
    '## Contents',
    '',
    '| Band | Papers | Hardest entry in the band |',
    '| --- | --- | --- |',
]
for b in sorted(bands):
    ms = sorted(bands[b], key=lambda m: m['rank'])
    lines.append(f"| [{b}]({b}/) | {len(ms)} | [{ms[0]['anum']}]({OEIS}{ms[0]['anum']}) |")
lines += ['', '`index.csv` lists every paper with its OEIS entry and the kind of argument used.']
open('papers/README.md', 'w').write('\n'.join(lines) + '\n')

for b in sorted(bands):
    ms = sorted(bands[b], key=lambda m: m['rank'])
    out = [f'# Papers {b}', '',
           f'Ranks {ms[0]["rank"]} to {ms[-1]["rank"]} of {len(rm)}, hardest first.',
           '', '| # | OEIS | Result | What settles it | Paper |', '| --- | --- | --- | --- | --- |']
    for m in ms:
        f = paperpath.name(m['rank'], m['verdict'])
        out.append(f"| {m['rank']} | [{m['anum']}]({OEIS}{m['anum']}) | {m['verdict'].title()} "
                   f"| {short(m['engine'], m['verdict'])} | [{f}]({f}) |")
    open(f'papers/{b}/README.md', 'w').write('\n'.join(out) + '\n')
print('index written for', len(rm), 'papers in', len(bands), 'bands')
