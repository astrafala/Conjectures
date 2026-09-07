#!/usr/bin/env python3
"""Deep check, Phase 7: caps, refusals, and everything not attempted.

*A cap is a setting, not a wall.* This phase does not re-run anything --- Phase 5 does that
--- it makes the untried visible. Three questions, answered from the sweep's own bookkeeping:

  1. what caps are in force, and how many entries were refused at each;
  2. what every refusal was, bucketed by reason, so a bucket that is not a mathematical
     obstruction can be seen and attacked rather than inherited;
  3. which entries an engine reads, which carry a conjecture, and which have never been
     processed at all --- the pool that costs nothing but attention, and that has been the
     largest single source of results on this project.

The output is a list, not a verdict. A phase that says "everything was tried" without saying
what "tried" meant is worth nothing.
"""
import collections
import json
import os
import re
import sys

import repopaths
import localentry as LE
import ratrec
import uniform

MARK = re.compile(r'onjectur|Empirical', re.I)
ORDER = re.compile(r'[Ee]mpirical recurrence of order (\d+)')
SC = ('/tmp/claude-0/-home-user-Conjectures/'
      'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/')


def main():
    names = json.load(open(SC + 'all_names.json'))
    roster = {v['anum'] for v in json.load(open(os.path.join(repopaths.ROOT, 'deep-check', 'frozen-roster.json'))).values()} \
        if os.path.exists(os.path.join(repopaths.ROOT, 'deep-check', 'frozen-roster.json')) else \
        {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    cands = json.load(open('uni_cands.json'))
    done = set(json.load(open('uniall_done.json')))
    hits = {h['anum'] for h in json.load(open('uniall_hits.json'))}
    caps = json.load(open('uniall_caps.json')) if os.path.exists('uniall_caps.json') else {}

    print(f'Phase 7: {len(names)} names known, {len(roster)} entries settled')

    bycap = collections.Counter()
    for a, c in caps.items():
        if a not in roster and a not in hits:
            bycap[c] += 1
    print('\n  caps under which entries stand refused:')
    for c in sorted(bycap):
        print(f'    {bycap[c]:6d} entries last tried at cap {c}')

    kinds = collections.Counter()
    never = []
    for a, en in cands.items():
        if a in roster or a in hits:
            continue
        try:
            e = LE.get(a)
        except Exception:
            kinds['entry unreadable'] += 1
            continue
        lines = [L for L in e['comment'] + e['formula'] if MARK.search(L)]
        if not lines:
            kinds['no unsettled conjecture on the entry'] += 1
        elif any(ratrec.parse_rec(L) for L in lines):
            kinds['recurrence stated; processed and unsettled' if a in done
                  else 'recurrence stated; NEVER PROCESSED'] += 1
            if a not in done:
                never.append(a)
        elif ORDER.search(' '.join(lines)):
            kinds['order line; processed and unsettled' if a in done
                  else 'order line; NEVER PROCESSED'] += 1
            if a not in done:
                never.append(a)
        else:
            kinds['conjecture of a kind no sweep tests'] += 1
    print('\n  every candidate an engine reads and that is not settled:')
    for k, v in kinds.most_common():
        print(f'    {v:6d}  {k}')

    unread = [a for a in names if a not in roster and a not in cands]
    live = 0
    for a in unread[:4000]:
        try:
            e = LE.get(a)
        except Exception:
            continue
        if any(MARK.search(L) for L in e['comment'] + e['formula']):
            live += 1
    print(f'\n  {len(unread)} names no engine reads; of the first 4000 sampled, '
          f'{live} carry something unsettled')
    if never:
        open(os.path.join(repopaths.ROOT, 'deep-check', 'phase7-never-processed.txt'), 'w').write(','.join(sorted(never)))
        print(f'\n  {len(never)} entries an engine reads, carrying a testable conjecture, '
              f'never processed at all -> deep-check/phase7-never-processed.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main())
