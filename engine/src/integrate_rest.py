#!/usr/bin/env python3
"""Install every proved result that has a compiled paper and is not yet in the roster."""
# Written by rename, not by truncate: this file is read at startup by sweeps that are
# running while it is rewritten, and a plain json.dump truncates first. Defect 55 --
# nineteen shards died with JSONDecodeError on half-written unified files in one night,
# each one costing a round and each one invisible because the idle backoff read the
# instant death as an exhausted vein.
import atomicjson
import refused
import withdrawnset
import json, os, shutil
from integrate_rest_names import ENGNAME

eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
nxt = max(eng) + 1
added = 0
for h in sorted(json.load(open('uniall_hits.json')), key=lambda x: x.get('anum', '')):
    a = h.get('anum')
    # a withdrawal blocks the ARGUMENT, not the entry: a different engine settling the
    # same open conjecture is a new result, not the withdrawn one returning
    if not a or h.get('FAILS') or a in have or withdrawnset.blocked(
            a, ENGNAME.get(h['engine'], 'transfer-matrix')):
        continue
    # the same guard `install_vein.py` applies, which this installer did not: an engine is
    # refused when its argument turns out not to be one, and a hit written before the refusal
    # is still sitting in the file. Zero records in `uniall_hits.json` are affected today.
    if not refused.ok(h.get('engine')):
        print('  refused engine', a, h.get('engine'))
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
atomicjson.dump({str(k): v for k, v in eng.items()}, 'paper-engines.json',
          indent=1, sort_keys=True)
print('added', added)
