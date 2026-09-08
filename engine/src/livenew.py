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
import re
import sys
import time

from verify_open import PROOF, fetch

targets = [a for a in open(sys.argv[1]).read().split() if a.startswith('A')]
OUT = 'deep-check/livenew.json'
state = json.load(open(OUT)) if os.path.exists(OUT) else {'kept': {}, 'dropped': {},
                                                          'flagged': {}}
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
    conj = [l for l in lines if re.search(r'conjectur|[Ee]mpirical', l)]
    if not conj:
        state['dropped'][a] = 'no conjectural or empirical line left on the entry'
    else:
        hits = [l[:160] for l in lines
                if PROOF.search(l) and re.search(r'conjectur|recurrence|empirical', l, re.I)]
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
