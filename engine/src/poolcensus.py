#!/usr/bin/env python3
"""What the pool actually is, per entry, from the files as they stand today.

    python3 src/poolcensus.py

Three counts have been quoted in planning this week and all three were wrong:
`uniall_caps.json` said 2,759 entries were refused at the cap when 1,004 were finished work
and another 1,109 carry no conjecture (the real figure is 645); `tabpool.txt` said 1,729
tables when 2,108 carry per-column lines; IDEAS.md section T's pool was derived from the first
of those. Rather than correct them one at a time, this classifies every entry the unified
sweep has ever considered, once, from the files rather than from memory.

The bucket that matters is the last one: an entry that carries a conjecture, has been asked,
was not settled, and has NO refusal row explaining why. Nothing counts those, and they are the
only entries where the reason for failure is unrecorded anywhere.
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conjlines
import localentry as LE
import ratrec
import uniform


def main():
    hits = {h['anum'] for h in json.load(open('uniall_hits.json'))}
    done = set(json.load(open('uniall_done.json')))
    roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    caps = json.load(open('uniall_caps.json'))
    tmo = json.load(open('uniall_tmo.json'))
    oom = json.load(open('uniall_oom.json'))
    died = json.load(open('uniall_died.json'))
    cands = json.load(open('uni_cands.json'))
    universe = set(cands) | done | hits
    print('entries the unified sweep has ever considered: %d' % len(universe))

    tally = collections.Counter()
    unexplained = []
    for a in sorted(universe):
        if a in hits or a in roster:
            tally['settled'] += 1
            continue
        try:
            e = LE.get(a)
        except Exception:
            tally['entry unreadable'] += 1
            continue
        if not uniform.read(e['name']):
            tally['no engine reads the name'] += 1
            continue
        recs = [x for x in (ratrec.parse_rec(L) for L in conjlines.claims(e)) if x]
        if not recs:
            tally['no conjecture to settle'] += 1
            continue
        if a in caps:
            tally['refused: cap'] += 1
        elif a in tmo:
            tally['refused: budget'] += 1
        elif a in oom:
            tally['refused: memory'] += 1
        elif a in died:
            tally['refused: shard death'] += 1
        elif a in done:
            tally['asked, unsettled, NO refusal recorded'] += 1
            unexplained.append(a)
        else:
            tally['never asked'] += 1
            unexplained.append(a)

    w = max(len(k) for k in tally)
    for k, v in tally.most_common():
        print('  %-*s %6d' % (w, k, v))
    json.dump(unexplained, open('deep-check/poolcensus-unexplained.json', 'w'), indent=1)
    print('-> deep-check/poolcensus-unexplained.json (%d)' % len(unexplained))


if __name__ == '__main__':
    main()
