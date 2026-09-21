#!/usr/bin/env python3
"""Fold the shard sweeps' results back into the one set of files, under the sweep's lock.

Each shard writes its own hits, done and caps, so no shard can overwrite another's results.
This is the one place they come together, and it takes the same lock sweep_uni.py takes, for
the same reason: whoever writes uniall_hits.json last would otherwise drop what the others
found, silently and with a correct-looking count.
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

# A TAG'd run writes shard<TAG>_hits_*.json so two sweeps on different pools cannot overwrite
# each other. Nothing folded those back in, so a tagged run's results never reached the file
# the builders read: the same silent gap that left gfonly's 312 results uninstalled.
TAG = os.environ.get('TAG', '')
HITS, DONE, CAPS = 'uniall_hits.json', 'uniall_done.json', 'uniall_caps.json'
# entries whose build outgrew the shard's MEMGB. They are NOT caps -- what they exceeded is
# the container -- and folding them into uniall_caps.json is how A186012 came to be recorded
# as refused for size when it builds at S=900096 under a cap of 2,000,000. Kept as its own
# list, holding the largest limit each has failed under, so it stays re-askable.
OOM = 'uniall_oom.json'
# entries the CLOCK refused, holding the largest budget each has failed under. Not the same
# fact as an out-of-memory and not the same fact as a cap, so not the same file.
TMO = 'uniall_tmo.json'
# how many times a shard has died holding each entry. Separate from OOM on purpose: OOM is
# `uniform.build' raising MemoryError against a limit, which is the entry's appetite; this is a
# shard that vanished, which is the machine's state at that moment and says nothing certain
# about the entry (STATE.md, the out-of-memory section).
DIED = 'uniall_died.json'
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
    oom = json.load(open(OOM)) if os.path.exists(OOM) else {}
    tmo = json.load(open(TMO)) if os.path.exists(TMO) else {}
    dieds = json.load(open(DIED)) if os.path.exists(DIED) else {}
    have = {h['anum'] for h in hits}
    added = 0
    for f in sorted(glob.glob(f'shard{TAG}_hits_*.json')):
        for h in json.load(open(f)):
            if h['anum'] in have:
                continue
            have.add(h['anum'])
            hits.append(h)
            added += 1
    ndone = 0
    for f in sorted(glob.glob(f'shard{TAG}_done_*.json')):
        s = set(json.load(open(f)))
        ndone += len(s - done)
        done |= s
    for f in sorted(glob.glob(f'shard{TAG}_caps_*.json')):
        for a, c in json.load(open(f)).items():
            caps[a] = max(caps.get(a, 0), c)
    for f in sorted(glob.glob(f'shard{TAG}_oom_*.json')):
        for a, g in json.load(open(f)).items():
            oom[a] = max(oom.get(a, 0), g)
    for f in sorted(glob.glob(f'shard{TAG}_tmo_*.json')):
        for a, b in json.load(open(f)).items():
            tmo[a] = max(tmo.get(a, 0), b)
    # deaths ADD rather than max: the question is how many separate generations died on this
    # entry, because one death is the machine and a run of them is the entry
    for f in sorted(glob.glob(f'shard{TAG}_died_*.json')):
        for a, c in json.load(open(f)).items():
            dieds[a] = dieds.get(a, 0) + int(c)
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)
    atomicjson.dump(caps, CAPS, indent=0, sort_keys=True)
    # Prune the settled: an entry proved since it was recorded is not an entry the container
    # refuses, and a refusal list that is never retracted becomes exactly the thing this file
    # was written to stop uniall_caps.json being.
    roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    gone = [a for a in oom if a in roster]
    for a in gone:
        del oom[a]
    if gone:
        print(f'  {len(gone)} out-of-memory rows retired: proved since they were recorded')
    gonet = [a for a in tmo if a in roster]
    for a in gonet:
        del tmo[a]
    if gonet:
        print(f'  {len(gonet)} timed-out rows retired: proved since they were recorded')
    goned = [a for a in dieds if a in roster]
    for a in goned:
        del dieds[a]
    if goned:
        print(f'  {len(goned)} death rows retired: proved since they were recorded')
    if oom:
        atomicjson.dump(oom, OOM, indent=0, sort_keys=True)
    elif os.path.exists(OOM):
        os.remove(OOM)
    if tmo:
        atomicjson.dump(tmo, TMO, indent=0, sort_keys=True)
    elif os.path.exists(TMO):
        os.remove(TMO)
    if dieds:
        atomicjson.dump(dieds, DIED, indent=0, sort_keys=True)
    elif os.path.exists(DIED):
        os.remove(DIED)
    print(f'{added} new hits, {ndone} newly processed; {len(hits)} hits, {len(done)} done'
          + (f'; {len(oom)} out of memory, not capped' if oom else '')
          + (f'; {len(tmo)} out of budget, not capped' if tmo else '')
          + (f'; {len(dieds)} entries a shard died on' if dieds else ''))
    for f in glob.glob(f'shard{TAG}_hits_*.json') + glob.glob(f'shard{TAG}_done_*.json') + \
             glob.glob(f'shard{TAG}_caps_*.json') + glob.glob(f'shard{TAG}_oom_*.json') + \
             glob.glob(f'shard{TAG}_tmo_*.json') + glob.glob(f'shard{TAG}_died_*.json'):
        os.remove(f)
finally:
    try:
        os.remove(LOCK)
    except OSError:
        pass
