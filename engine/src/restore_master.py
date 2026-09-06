#!/usr/bin/env python3
"""Rebuild papers-old-numbering/ from papers/ and rank-map.json.

papers-old-numbering/ is the `was`-keyed master the pipeline reads from: rank.py copies OUT of
it, so it has to exist on disk before anything can be re-ranked. It is not in the repository,
because it is the same 8887 PDFs a second time under different names and storing both doubles
the clone for nothing.

It does not need to be stored. rank-map.json records rank -> was for every paper, and the
mapping is a bijection, so the master is recoverable exactly from what IS stored. Run this
once after a fresh clone, before running rank.py.
"""
import json, os, shutil
import paperpath

rm = json.load(open('rank-map.json'))
os.makedirs('papers-old-numbering', exist_ok=True)
n = missing = 0
for m in rm:
    src = paperpath.path(m['rank'], m['verdict'])
    dst = f"papers-old-numbering/{m['was']}-{m['verdict']}.pdf"
    if not os.path.exists(src):
        missing += 1
        print('missing', src)
        continue
    shutil.copy(src, dst)
    n += 1
print('restored', n, 'papers', ('with %d missing' % missing) if missing else '')
