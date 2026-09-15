#!/usr/bin/env python3
"""Ask `gridbase` about every entry carrying the cross-base identity; write gridbase_hits.json."""
import glob
import json
import os
import sys
import time

import atomicjson
import conjlines
import gridbase
import localentry as LE
import openness

OUT = 'gridbase_hits.json'
hits = json.load(open(OUT)) if os.path.exists(OUT) else []
seen = {h['anum'] for h in hits}
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}

cands = []
for p in glob.glob('/home/user/oeis/oeisdata/seq/*/*.seq'):
    a = os.path.basename(p)[:-4]
    if a in roster or a in seen:
        continue
    e = LE.get(a)
    if not e or not gridbase.parse_name(e.get('name', '')):
        continue
    if not gridbase.claim(a, e):
        continue
    if not openness.status(a)[0]:
        continue
    cands.append(a)
print('candidates:', len(cands), flush=True)
ok = bad = 0
for a in sorted(cands):
    t0 = time.time()
    try:
        r = gridbase.check(a)
    except Exception as ex:
        print('  %s ERROR %s' % (a, ex), flush=True)
        continue
    if r is None:
        continue
    if r.get('FAILS') or r.get('bad') or r.get('refbad') or r.get('sharp') is False:
        bad += 1
        print('  %s REFUSED %s' % (a, {k: v for k, v in r.items() if k in
                                       ('why', 'bad', 'refbad', 'sharp')}), flush=True)
        continue
    r['engine'] = 'gridbase'
    hits.append(r)
    ok += 1
    print('  %s OK b=%d d=%d nmax=%d terms=%d  %.0fs'
          % (a, r['b'], r['d'], r['nmax'], r['terms_checked'], time.time() - t0), flush=True)
    atomicjson.dump(hits, OUT)
atomicjson.dump(hits, OUT)
print('FINAL ok=%d refused=%d of %d' % (ok, bad, len(cands)), flush=True)
