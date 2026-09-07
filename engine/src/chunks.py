#!/usr/bin/env python3
"""What to attack next, ranked by how many conjectures it would settle.

The standing rule is to work in chunks and to take the biggest approachable one first. A
rule like that decays into a preference unless something measures it, so this does the
measuring: it groups every open, conjecture-carrying entry that no engine reaches by the
shape of its clause, and prints the groups largest first. Run it before choosing anything.

It also prints the cheapest chunk of all, which is not a new family at all: entries an
engine already parses that were refused and never revisited. Raising a cap has recovered
real results four times on this project, so that pool is always worth its own line.

    python3 src/chunks.py            the ranking
    python3 src/chunks.py 40         the top 40 groups
"""
import collections
import json
import os
import re
import sys

import localentry as LE
import ratrec
import uniform

SC = ('/tmp/claude-0/-home-user-Conjectures/'
      'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad')
MARK = re.compile(r'onjectur|Empirical', re.I)


def clause(name):
    """the entry's condition with its sizes and letters removed, so a family shows as one"""
    s = ' '.join(name.split())
    m = (re.search(r'\barrays? with (.+?)\.?$', s, re.I)
         or re.search(r'\bmatrices with (.+?)\.?$', s, re.I))
    t = m.group(1) if m else s
    t = re.sub(r'\b\d+\.\.\d+\b', 'A', t)
    t = re.sub(r'\d+', '#', t)
    return ' '.join(re.sub(r'[^A-Za-z# ]', ' ', t.lower()).split())


def has_conjecture(a):
    try:
        e = LE.get(a)
    except Exception:
        return False
    return any(ratrec.parse_rec(L) for L in e['comment'] + e['formula'] if MARK.search(L))


def main(top=25):
    names = json.load(open(SC + '/all_names.json'))
    mine = {r['anum'] for r in json.load(open('rank-map.json'))}
    unreached = [a for a in names if a not in mine and not uniform.read(names[a])]
    live = [a for a in unreached if has_conjecture(a)]
    groups = collections.Counter()
    example = collections.defaultdict(list)
    for a in live:
        k = clause(names[a])
        groups[k] += 1
        if len(example[k]) < 3:
            example[k].append(a)

    print(f'{len(names)} names known, {len(mine)} settled, '
          f'{len(unreached)} unreached by any engine')
    print(f'{len(live)} of those carry a conjecture: that is the target list, '
          f'in {len(groups)} clause shapes\n')

    try:
        cands = json.load(open('uni_cands.json'))
        done = set(json.load(open('uniall_done.json')))
        hits = {h['anum'] for h in json.load(open('uniall_hits.json'))}
        caps = json.load(open('uniall_caps.json')) if os.path.exists('uniall_caps.json') else {}
        stale = [a for a in cands if a in done and a not in mine and a not in hits]
        # A refusal only means something next to the cap it was made at. Reporting the whole
        # refused pool as cheap work sends the next pass to redo what the last one just did.
        best = max(caps.values()) if caps else 0
        fresh = [a for a in stale if caps.get(a, 0) < best]
        print(f'REFUSED POOL: {len(stale)} entries an engine parses, processed and not '
              f'settled.')
        if caps:
            buckets = collections.Counter(caps.get(a, 0) for a in stale)
            for cap, n in sorted(buckets.items()):
                mark = '  <-- never tried above this' if cap < best else ''
                print(f'    {n:5d} last tried at cap {cap or "unrecorded"}{mark}')
            print(f'  {len(fresh)} of them have never been tried at the highest cap used '
                  f'({best}). A cap is a setting, not a wall.')
        else:
            print('  no caps recorded yet, so none of these can be told apart')
        print()
    except Exception as e:
        print(f'(could not size the refused pool: {e})\n')

    print(f'{"count":>6}  {"examples":<26}  clause')
    for k, n in groups.most_common(top):
        print(f'{n:6d}  {" ".join(example[k]):<26}  {k[:96]}')
    return groups


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 25)
