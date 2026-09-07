#!/usr/bin/env python3
"""Install every proved result that has a compiled paper and is not yet in the roster."""
import json, os, shutil
ENGNAME = {'transfer85': 'distance-repeat', 'transfer86': 'local-array-condition',
           'transfer87': 'parity-difference'}
eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
nxt = max(eng) + 1
added = 0
for h in sorted(json.load(open('uniall_hits.json')), key=lambda x: x.get('anum', '')):
    a = h.get('anum')
    if not a or h.get('FAILS') or a in have:
        continue
    src = f"build/un{a}/p.pdf"
    if not (os.path.exists(src) and os.path.getsize(src) > 50000):
        print('  no paper for', a, h.get('engine'))
        continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt] = {'engine': ENGNAME.get(h['engine'], 'transfer-matrix'),
                'order': h['order'], 'degree': h['S'], 'anum': a, 'disproof': False}
    have.add(a)
    nxt += 1
    added += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
print('added', added)
