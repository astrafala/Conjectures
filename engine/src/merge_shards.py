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
import localentry as LE
import uniform
import glob
import json
import os

# A TAG'd run writes shard<TAG>_hits_*.json so two sweeps on different pools cannot overwrite
# each other. Nothing folded those back in, so a tagged run's results never reached the file
# the builders read: the same silent gap that left gfonly's 312 results uninstalled.
TAG = os.environ.get('TAG', '')
# DEFECT 68. The globs below are `shard{TAG}_kind_*.json', and with TAG unset that matches
# ONLY the untagged files -- the literal underscore sees to it. Every TAG'd runner
# (np, np2, cap, cap2, rcap, rcap2, gal, gal2, gal5, cg, oom, res, t17c, tmo, ...) therefore
# wrote its hits and its refusals to disk where nothing ever read them, because nothing runs
# this with their TAG.
#
# Measured: 468 cap rows for 396 entries sat in `shardnp2_caps_*' and `shardnp_caps_*', which
# is why a census of the merged files called those entries "asked, unsettled, NO refusal
# recorded" -- the record existed, under a tag nobody merges. Four HITS were sitting unmerged
# too. And the entries are not hard: np2run asks at a cap of 2,000,000 and the main sweep at
# 8,000,000, and 29 of 40 of them prove immediately at the larger cap.
#
# So an unset TAG now means EVERY tag, which is what "merge the shards" was always taken to
# mean. `TAG=np' still merges np alone, for when that is wanted. No tag in use contains an
# underscore, so the wildcard cannot straddle two of them.
PAT = TAG if TAG else '*'

HITS, DONE, CAPS = 'uniall_hits.json', 'uniall_done.json', 'uniall_caps.json'
# which PHASE exhausted the budget -- build, terms or threshold. Defect 62: all three
# wrote the same number into TMO and the distinction that decides what to fix was lost.
TMOPHASE = 'uniall_tmophase.json'
# a build that returned None from an engine that never reads the cap: a decline,
# not a size refusal (defect 70)
DECLINED = 'uniall_declined.json'
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
    tmoph = json.load(open(TMOPHASE)) if os.path.exists(TMOPHASE) else {}
    dieds = json.load(open(DIED)) if os.path.exists(DIED) else {}
    have = {h['anum'] for h in hits}
    added = 0
    for f in sorted(glob.glob(f'shard{PAT}_hits_*.json')):
        for h in json.load(open(f)):
            if h['anum'] in have:
                continue
            have.add(h['anum'])
            hits.append(h)
            added += 1
    ndone = 0
    for f in sorted(glob.glob(f'shard{PAT}_done_*.json')):
        s = set(json.load(open(f)))
        ndone += len(s - done)
        done |= s
    for f in sorted(glob.glob(f'shard{PAT}_caps_*.json')):
        for a, c in json.load(open(f)).items():
            caps[a] = max(caps.get(a, 0), c)
    for f in sorted(glob.glob(f'shard{PAT}_oom_*.json')):
        for a, g in json.load(open(f)).items():
            oom[a] = max(oom.get(a, 0), g)
    for f in sorted(glob.glob(f'shard{PAT}_tmo_*.json')):
        for a, b in json.load(open(f)).items():
            tmo[a] = max(tmo.get(a, 0), b)
    for f in sorted(glob.glob(f'shard{PAT}_tmophase_*.json')):
        for a, ph in json.load(open(f)).items():
            tmoph[a] = ph
    # deaths ADD rather than max: the question is how many separate generations died on this
    # entry, because one death is the machine and a run of them is the entry
    for f in sorted(glob.glob(f'shard{PAT}_died_*.json')):
        for a, c in json.load(open(f)).items():
            dieds[a] = dieds.get(a, 0) + int(c)
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)
    # CAPS is dumped BELOW the pruning, not above it. It was written here, before, and the
    # prune that followed deleted 1,004 rows from a dict nothing wrote again -- so the file
    # on disk kept every one of them and the run printed that it had retired them.
    # Prune the settled: an entry proved since it was recorded is not an entry the container
    # refuses, and a refusal list that is never retracted becomes exactly the thing this file
    # was written to stop uniall_caps.json being.
    roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    # DEFECT 61. This pruning was written once, for `oom', with a comment naming
    # `uniall_caps.json' as the thing it existed to stop --- and the other three files were
    # left exactly as described. Audited on 22 September: of 2,759 rows in uniall_caps.json,
    # 997 were already HITS of this very sweep and 1,004 were papered. Thirty-six percent of
    # the "refused at the cap" file was finished work, and every measurement built on it --
    # which engine deserves attention, how many entries a raised cap would open, what a list
    # is askable against -- was inflated by that much. None of the 2,759 was unasked.
    # `settled' is the union of what this sweep proved and what any engine papered: either
    # way the entry is no longer something the container refuses.
    # DEFECT 70. Keep `uniall_caps.json' meaning ONE thing. `sweep_shard' stopped writing a
    # cap row for the engines in `uniform.NO_SIZE_REFUSAL' -- whose build never reads the cap,
    # so a None from them means "this reading does not apply", not "too big" -- but the rows
    # written before that fix were never retracted. 843 of them were still there, galcoord's
    # 355 among them, and galcoord refuses in 0.3 seconds at a cap of 8,000,000 because it is
    # declining the tiling, not exploring a state space. They are moved to
    # `uniall_declined.json', which keeps the fact under its own name instead of losing it.
    try:
        declined = json.load(open(DECLINED)) if os.path.exists(DECLINED) else {}
        moved = 0
        for a in list(caps):
            try:
                r = uniform.read(LE.get(a)['name'])
            except Exception:
                continue
            if r and r[0] in uniform.NO_SIZE_REFUSAL:
                declined[a] = r[0]
                del caps[a]
                moved += 1
        if moved:
            atomicjson.dump(declined, DECLINED, indent=0, sort_keys=True)
            print(f'  {moved} cap rows moved to {DECLINED}: written by an engine whose build '
                  f'never reads the cap')
    except Exception as _exc:
        print('  could not separate the engine declines: %s' % _exc)

    settled = roster | have
    for nm, f in (('cap', caps), ('out-of-memory', oom), ('out-of-budget', tmo),
                  ('out-of-budget phase', tmoph), ('shard-death', dieds)):
        gone = [a for a in f if a in settled]
        for a in gone:
            del f[a]
        if gone:
            print(f'  {len(gone)} {nm} rows retired: settled since they were recorded')
    # (the separate roster-only prunes for tmo and dieds that used to stand here are covered
    # by the loop above, which uses the wider `settled' set)
    atomicjson.dump(caps, CAPS, indent=0, sort_keys=True)
    if oom:
        atomicjson.dump(oom, OOM, indent=0, sort_keys=True)
    elif os.path.exists(OOM):
        os.remove(OOM)
    if tmo:
        atomicjson.dump(tmo, TMO, indent=0, sort_keys=True)
    elif os.path.exists(TMO):
        os.remove(TMO)
    if tmoph:
        atomicjson.dump(tmoph, TMOPHASE, indent=0, sort_keys=True)
    elif os.path.exists(TMOPHASE):
        os.remove(TMOPHASE)
    if dieds:
        atomicjson.dump(dieds, DIED, indent=0, sort_keys=True)
    elif os.path.exists(DIED):
        os.remove(DIED)
    print(f'{added} new hits, {ndone} newly processed; {len(hits)} hits, {len(done)} done'
          + (f'; {len(oom)} out of memory, not capped' if oom else '')
          + (f'; {len(tmo)} out of budget, not capped' if tmo else '')
          + (f'; {len(dieds)} entries a shard died on' if dieds else ''))
# The why file is deleted with the rest now, and that is a correctness fix rather than tidying.
# Everything else here is consumed and removed on every merge, so a shard's hits, done, caps,
# oom, tmo and died files always describe the CURRENT generation. The why file was not, so it
# accumulated counters for ever and outlived the results it described. Reading `{"PROVED": 1}'
# in a tmo shard this morning meant a hit had been found -- five hours earlier, already merged
# and installed. Nothing reads these files but a human looking at what a vein is refusing right
# now, which is this project's central habit, and a counter that cannot be dated is no use for
# it. Nothing else in the codebase reads `shard*_why_*.json'.
    for f in glob.glob(f'shard{PAT}_hits_*.json') + glob.glob(f'shard{PAT}_done_*.json') + \
             glob.glob(f'shard{PAT}_caps_*.json') + glob.glob(f'shard{PAT}_oom_*.json') + \
             glob.glob(f'shard{PAT}_tmo_*.json') + glob.glob(f'shard{PAT}_tmophase_*.json') + \
             glob.glob(f'shard{PAT}_died_*.json') + \
             glob.glob(f'shard{PAT}_why_*.json'):
        os.remove(f)
finally:
    try:
        os.remove(LOCK)
    except OSError:
        pass
