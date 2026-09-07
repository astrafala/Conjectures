#!/usr/bin/env python3
"""Rebuild uni_cands.json: every known name, asked of every engine, again.

The list is a cache --- asking eighty parsers about twenty-nine thousand names costs minutes,
and the sweep has to run in short pieces. But a cache of what is reachable goes stale the
moment an engine is written or a parser is widened, and a name missing from it is never asked
again by anything. That is a silent refusal of exactly the kind this project keeps finding,
so the list is rebuilt from scratch rather than appended to.

    python3 src/mkcands.py            rebuild, report what changed
"""
import json
import os

import uniform

SC = ('/tmp/claude-0/-home-user-Conjectures/'
      'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad')
names = json.load(open(SC + '/all_names.json'))
old = json.load(open('uni_cands.json')) if os.path.exists('uni_cands.json') else {}
new = {}
for a, nm in names.items():
    got = uniform.read(nm)
    if got:
        new[a] = got[0]
added = sorted(set(new) - set(old))
gone = sorted(set(old) - set(new))
moved = sorted(a for a in set(new) & set(old) if new[a] != old[a])
json.dump(new, open('uni_cands.json', 'w'), indent=0, sort_keys=True)
print(f'{len(new)} candidates ({len(old)} before): {len(added)} new, {len(gone)} no longer '
      f'parsed, {len(moved)} now read by a different engine')
for a in added[:20]:
    print('  new', a, new[a], names[a][:70])
if gone:
    print('  NO LONGER PARSED:', gone[:20])
