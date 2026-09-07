#!/usr/bin/env python3
"""Fold the tail sweep's shards into one result file.

Same reason as merge_ordwhole: a shard rewrites its file after every entry, so the shards are
progress and the merge is the result. Records are keyed by A-number and an existing one is
kept, so a re-run at a different cap cannot change the claim a paper was built from.

    python3 src/merge_ordtails.py
"""
import glob
import json
import os

OUT = 'ordtails.json'
m = json.load(open(OUT)) if os.path.exists(OUT) else {'proved': [], 'disproved': [],
                                                      'not_unique': [], 'why': {}}
have = {x['anum'] for x in m['proved']} | {x['anum'] for x in m['disproved']}
add_p = add_d = 0
for f in sorted(glob.glob('ordtails_[0-9].json')):
    s = json.load(open(f))
    for x in s['proved']:
        if x['anum'] not in have:
            m['proved'].append(x); have.add(x['anum']); add_p += 1
    for x in s['disproved']:
        if x['anum'] not in have:
            m['disproved'].append(x); have.add(x['anum']); add_d += 1
    m['not_unique'] = sorted(set(m['not_unique']) | set(s['not_unique']))
    for k, v in s['why'].items():
        m['why'].setdefault(k, v)
json.dump(m, open(OUT, 'w'), indent=1)
print(f'{add_p} new proofs and {add_d} new candidate disproofs folded in; '
      f'{len(m["proved"])} proved, {len(m["disproved"])} disproof candidates, '
      f'{len(m["not_unique"])} not unique')
