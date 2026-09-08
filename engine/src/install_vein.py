#!/usr/bin/env python3
"""Install every compiled paper from one sweep's build directory into the roster.

`integrate_rest.py` does this for the unified sweep and reads `build/un<anum>`; every other
vein was installed by hand, which is why `build/ow` had no installer at all and 145 compiled
order-line papers were sitting uninstalled. One script, told which prefix and which record
list to walk, so a new vein needs no new integrator.

    python3 src/install_vein.py ow ordwhole_hits.json order-line
    python3 src/install_vein.py ot ordtails.json:proved order-line-tail

The engine name written into the roster is the third argument. A paper is installed only if
its PDF compiled to a plausible size and its entry is not already in the roster, so running
this twice is safe.
"""
import json
import os
import shutil
import sys

prefix, source, engname = sys.argv[1], sys.argv[2], sys.argv[3]
if ':' in source:
    f, key = source.split(':', 1)
    recs = json.load(open(f))[key]
else:
    recs = json.load(open(source))

eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
have |= {r['anum'] for r in json.load(open('rank-map.json'))}
nxt = max(eng) + 1
added, nopaper = 0, []
for h in sorted(recs, key=lambda x: x.get('anum', '')):
    a = h.get('anum')
    if not a or h.get('FAILS') or a in have:
        continue
    src = f'build/{prefix}{a}/p.pdf'
    if not (os.path.exists(src) and os.path.getsize(src) > 40000):
        nopaper.append(a)
        continue
    shutil.copy(src, f'papers-old-numbering/{nxt}-PROOF.pdf')
    eng[nxt] = {'engine': engname, 'order': h.get('order', h.get('stated', 0)),
                'degree': h.get('S', 0), 'anum': a,
                'disproof': bool(h.get('disproof'))}
    have.add(a)
    nxt += 1
    added += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
print(f'added {added}; {len(nopaper)} had no compiled paper')
for a in nopaper[:10]:
    print('  no paper for', a)
