#!/usr/bin/env python3
"""Install every transfer89 paper into the roster."""
import json
import os
import shutil

hits = [h for h in json.load(open('uniall_hits.json'))
        if h.get('engine') == 'transfer89' and not h.get('FAILS')]
eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
where = {v['anum']: k for k, v in eng.items() if v['engine'] == 'white-squares'}
nxt = max(eng) + 1
have = {v['anum'] for v in eng.values()}
replaced, added = 0, 0
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    src = f"build/un{a}/p.pdf"
    if not (os.path.exists(src) and os.path.getsize(src) > 50000):
        print('  no pdf for', a)
        continue
    if a in where:
        n = where[a]
        replaced += 1
    elif a in have:
        print('  settled by another engine, left alone:', a)
        continue
    else:
        n = nxt
        nxt += 1
        added += 1
    shutil.copy(src, f"papers-old-numbering/{n}-PROOF.pdf")
    eng[n] = {'engine': 'white-squares', 'order': h['order'], 'degree': h['S'],
              'anum': a, 'disproof': False}
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
print(f'{replaced} replaced, {added} added')
