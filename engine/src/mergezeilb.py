#!/usr/bin/env python3
"""Fold the telescoping runner's live shards into the one file harvest reads.

`zeilb-3.json`, `-4` and `-5` are written by the running workers every few seconds, so they
are progress and are gitignored, exactly like every other sharded sweep here. But `harvest.py`
installs from the glob `zeilb-[0-9].json` and has no merge step of its own -- the August files
`zeilb-0` and `zeilb-1` were a one-off run that was simply left on disk.

So: the shards' records are folded into `zeilb-9.json`, which matches that glob and IS tracked.
A record already there is KEPT rather than replaced, so a re-run at a different order cannot
quietly change the claim a paper was built from -- the same rule `merge_sharded` follows.
"""
import glob
import json
import os

OUT = 'zeilb-9.json'
out = json.load(open(OUT)) if os.path.exists(OUT) else {}
added = 0
for f in sorted(glob.glob('zeilb-[3-8].json')):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    for k, v in d.items():
        if k not in out:
            out[k] = v
            added += 1
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
proved = sum(1 for v in out.values() if isinstance(v, dict) and v.get('status') == 'PROVED')
print(f'{OUT}: {added} new, {len(out)} records, {proved} PROVED')
