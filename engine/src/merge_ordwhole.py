#!/usr/bin/env python3
"""Fold the order-line sweep's shard files into the one file everything else reads.

Each shard rewrites its own hits and done files after every entry, so those are progress and
are not stored. `ordwhole_hits.json` is the result: the builder, the comment writer and two
check phases all read it and nothing else. Merging is by A-number, and a record already in
the merged file is kept rather than replaced, so a re-run at a different cap cannot quietly
change the claim a paper was built from.

    python3 src/merge_ordwhole.py
"""
# Written by rename, not by truncate: this file is read at startup by sweeps that are
# running while it is rewritten, and a plain json.dump truncates first. Defect 55 --
# nineteen shards died with JSONDecodeError on half-written unified files in one night,
# each one costing a round and each one invisible because the idle backoff read the
# instant death as an exhausted vein.
import atomicjson
import glob
import json
import os

merged = json.load(open('ordwhole_hits.json')) if os.path.exists('ordwhole_hits.json') else []
by = {h['anum']: h for h in merged}
added = 0
for f in sorted(glob.glob('ordwhole_hits_*.json')):
    for h in json.load(open(f)):
        if h['anum'] not in by:
            by[h['anum']] = h
            added += 1
out = [by[a] for a in sorted(by)]
atomicjson.dump(out, 'ordwhole_hits.json', indent=1)

done = set(json.load(open('ordwhole_done.json'))) if os.path.exists('ordwhole_done.json') else set()
for f in sorted(glob.glob('ordwhole_done_*.json')):
    done |= set(json.load(open(f)))
json.dump(sorted(done), open('ordwhole_done.json', 'w'))
print(f'{added} new order-line results folded in; {len(out)} in total, {len(done)} attempted')
