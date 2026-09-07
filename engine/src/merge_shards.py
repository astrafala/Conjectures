#!/usr/bin/env python3
"""Fold the shard sweeps' results back into the one set of files, under the sweep's lock.

Each shard writes its own hits, done and caps, so no shard can overwrite another's results.
This is the one place they come together, and it takes the same lock sweep_uni.py takes, for
the same reason: whoever writes uniall_hits.json last would otherwise drop what the others
found, silently and with a correct-looking count.
"""
import glob
import json
import os

HITS, DONE, CAPS = 'uniall_hits.json', 'uniall_done.json', 'uniall_caps.json'
LOCK = HITS + '.lock'

if os.path.exists(LOCK):
    try:
        other = int(open(LOCK).read().strip())
    except Exception:
        other = None
    if other is not None and os.path.exists(f'/proc/{other}'):
        raise SystemExit(f'a sweep (pid {other}) is writing {HITS}; refusing to merge')
open(LOCK, 'w').write(str(os.getpid()))
try:
    hits = json.load(open(HITS)) if os.path.exists(HITS) else []
    done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
    caps = json.load(open(CAPS)) if os.path.exists(CAPS) else {}
    have = {h['anum'] for h in hits}
    added = 0
    for f in sorted(glob.glob('shard_hits_*.json')):
        for h in json.load(open(f)):
            if h['anum'] in have:
                continue
            have.add(h['anum'])
            hits.append(h)
            added += 1
    ndone = 0
    for f in sorted(glob.glob('shard_done_*.json')):
        s = set(json.load(open(f)))
        ndone += len(s - done)
        done |= s
    for f in sorted(glob.glob('shard_caps_*.json')):
        for a, c in json.load(open(f)).items():
            caps[a] = max(caps.get(a, 0), c)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    json.dump(caps, open(CAPS, 'w'), indent=0, sort_keys=True)
    print(f'{added} new hits, {ndone} newly processed; {len(hits)} hits, {len(done)} done')
    for f in glob.glob('shard_hits_*.json') + glob.glob('shard_done_*.json') + \
             glob.glob('shard_caps_*.json'):
        os.remove(f)
finally:
    try:
        os.remove(LOCK)
    except OSError:
        pass
