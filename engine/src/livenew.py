#!/usr/bin/env python3
"""Re-check every held result against the LIVE OEIS before any of it is counted.

The local clone is a snapshot and other people are working these same entries; a snapshot
is not good enough to stand behind a claim that a conjecture is still open. This fetches
each entry fresh, drops anything that no longer carries an unsettled conjecture, and prints
any settlement wording it finds so it can be judged rather than guessed at.

    python3 src/livenew.py deep-check/new.txt
"""
import json
import os
import zlib
import re
import sys
import time

from verify_open import PROOF, fetch

# Sharded: the check is one HTTP fetch per entry with a courtesy pause, so it is the slowest
# step in the whole pipeline and nothing about it needs to be sequential. Each shard keeps its
# own file; `merge` folds them into the one the builders read.
SHARD = int(os.environ.get('LSHARD', '0'))
NSHARD = int(os.environ.get('LNSHARD', '1'))
targets = [a for a in open(sys.argv[1]).read().split()
           if a.startswith('A') and zlib.crc32(a.encode()) % NSHARD == SHARD]
OUT = 'deep-check/livenew.json' if NSHARD == 1 else f'deep-check/livenew_{SHARD}.json'
state = json.load(open(OUT)) if os.path.exists(OUT) else {'kept': {}, 'dropped': {},
                                                          'flagged': {}}
if NSHARD > 1:
    # a shard starts from what the merged file already knows, or it re-fetches every entry
    # the earlier unsharded runs had already confirmed -- which is what six shards spent
    # their first windows doing
    try:
        base = json.load(open('deep-check/livenew.json'))
        for k in ('kept', 'dropped', 'flagged'):
            for a, v in base.get(k, {}).items():
                state[k].setdefault(a, v)
    except Exception:
        pass
for a in targets:
    if a in state['kept'] or a in state['dropped'] or a in state['flagged']:
        continue
    try:
        e = fetch(a)
    except Exception as ex:
        print(f'FETCH {a}: {ex}')
        continue
    lines = []
    for k in ('comment', 'formula', 'link', 'ext', 'example', 'maple', 'mathematica'):
        lines += e.get(k) or []
    # the same block defect a third time, and this one is the most dangerous of the three:
    # here it does not hide work, it THROWS AWAY finished results. A conjecture written as a
    # "Conjectures from X: (Start) ... (End)" block has no conjectural word on its formula
    # lines, so 23 proved entries were dropped as "no conjectural line left on the entry"
    # when the conjecture is plainly there. Blocks are read as a whole.
    inside = False
    conj = []
    for l in lines:
        if re.search(r'(?:conjectur\w*|empirical)\b.*\(Start\)', l, re.I):
            inside = True
            conj.append(l)
            continue
        if inside:
            conj.append(l)
            if '(End)' in l:
                inside = False
            continue
        if re.search(r'conjectur|[Ee]mpirical|It appears|Apparently', l, re.I):
            conj.append(l)
    if not conj:
        state['dropped'][a] = 'no conjectural or empirical line left on the entry'
    else:
        # A line saying a claim of correctness was REMOVED is evidence the conjecture stands,
        # not that it is settled. 41 entries were flagged on N. J. A. Sloane's
        # "Removed an unjustified claim that _Colin Barker_'s conjectures are correct",
        # which says the opposite of what the flag took it to mean.
        NEGATED = re.compile(r'\b(removed|deleted|withdrew|retracted|unjustified|'
                             r'not (?:been )?(?:proved|proven|verified)|no proof)\b', re.I)
        hits = [l[:160] for l in lines
                if PROOF.search(l) and re.search(r'conjectur|recurrence|empirical', l, re.I)
                and not NEGATED.search(l)]
        if hits:
            state['flagged'][a] = hits[0]
        else:
            state['kept'][a] = {'time': e['time'][:10], 'revision': e['revision'],
                                'name': e['name']}
    json.dump(state, open(OUT, 'w'), indent=1, sort_keys=True)
    time.sleep(0.3)
print(f"kept {len(state['kept'])}  dropped {len(state['dropped'])}  "
      f"flagged {len(state['flagged'])}")
for a, w in sorted(state['dropped'].items()):
    print(f'DROP {a}: {w}')
for a, w in sorted(state['flagged'].items()):
    print(f'FLAG {a}: {w}')
