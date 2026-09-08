#!/usr/bin/env python3
"""Fold any sweep's per-shard hits and done files into the one file the builders read.

The shard files are progress: every worker rewrites its own every few seconds, so tracking
them means the working tree is never clean and every commit races the next write. The repo
already ignores the order-line and tail sweeps' shard files for exactly this reason, and this
is the merge those two have and the newer sweeps did not.

A record already in the merged file is KEPT rather than replaced, so a re-run at a different
cap cannot quietly change the claim a paper was built from.

    python3 src/merge_sharded.py            # every known sweep
    python3 src/merge_sharded.py tabnew     # one of them
"""
import glob
import json
import os
import sys

SWEEPS = ['tabnew', 'rownew', 'lexcf', 'mfcf', 'gfonly', 'wordcf', 'cuspcf', 'ecacf']


def merge(stem):
    hits_f, done_f = f'{stem}_hits.json', f'{stem}_done.json'
    hits = json.load(open(hits_f)) if os.path.exists(hits_f) else []
    done = set(json.load(open(done_f))) if os.path.exists(done_f) else set()
    have = {h['anum'] for h in hits if isinstance(h, dict) and h.get('anum')}
    added = 0
    for f in sorted(glob.glob(f'{stem}_hits_*.json')):
        try:
            recs = json.load(open(f))
        except Exception:
            continue
        for h in recs:
            if not isinstance(h, dict) or not h.get('anum') or h['anum'] in have:
                continue
            have.add(h['anum'])
            hits.append(h)
            added += 1
    nd = 0
    for f in sorted(glob.glob(f'{stem}_done_*.json')):
        try:
            s = set(json.load(open(f)))
        except Exception:
            continue
        nd += len(s - done)
        done |= s
    json.dump(hits, open(hits_f, 'w'), indent=1)
    json.dump(sorted(done), open(done_f, 'w'))
    return added, len(hits), nd, len(done)


for stem in (sys.argv[1:] or SWEEPS):
    a, th, nd, td = merge(stem)
    if th or td:
        print(f'{stem}: {a} new hits ({th} total), {nd} newly asked ({td} total)')
