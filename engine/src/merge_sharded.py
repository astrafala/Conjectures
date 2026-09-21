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
# EVERY UNIFIED FILE HERE IS READ BY SEVENTY SHARDS AND WRITTEN BY THIS. A plain
# `json.dump(open(f, 'w'))' truncates first and writes second, so a shard starting during a
# merge reads a file that is half-written and dies with JSONDecodeError before its first
# entry. Nineteen such deaths are in tonight's runner logs -- uniall_done.json at char
# 3,646,799, uniall_hits.json at 3,203,111 -- and each one cost a whole round. Until defect 52
# they were invisible: the round came back in under a second and the idle backoff called the
# vein read out. The merge runs every hour, on the hour, against every runner at once.
import atomicjson
import glob
import json
import os
import sys

SWEEPS = ['tabnew', 'rownew', 'lexcf', 'mfcf', 'gfonly', 'wordcf', 'cuspcf', 'ecacf', 'gfdef', 'fcf', 'snd', 'cong', 'ca2dcf', 'b8cf', 'shardnp', 'linkrec', 'cfpool', 'prec']


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
    atomicjson.dump(hits, hits_f, indent=1)
    atomicjson.dump(sorted(done), done_f)
    return added, len(hits), nd, len(done)


for stem in (sys.argv[1:] or SWEEPS):
    a, th, nd, td = merge(stem)
    if th or td:
        print(f'{stem}: {a} new hits ({th} total), {nd} newly asked ({td} total)')
