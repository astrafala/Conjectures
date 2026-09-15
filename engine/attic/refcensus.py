#!/usr/bin/env python3
"""Every non-roster array entry with a conjectured recurrence that no engine reads.

Clustered by the opening of the CONDITION -- the part of the name after the array shape --
because that is what an engine has to understand. Openness is not re-checked here; the
sweep does that per entry. This is a target list, not a claim about any entry.
"""
import json, re, sys
import localentry as LE, ratrec, uniform

P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
MARK = re.compile(r'onjectur|Empirical', re.I)
ARR = re.compile(r'\barrays?\b|\bmatri(?:x|ces)\b|\btables?\b', re.I)
# the shape clause is boilerplate in every one of these names; stripping it leaves the
# condition, which is the only thing that decides whether an engine can be written
SHAPE = re.compile(r'^Number of\s+.*?\barrays?\b\s*(?:with\s+)?|^Number of\s+.*?\bmatrices\b\s*',
                   re.I)

out = {}
for a in sorted(names):
    if a in roster:
        continue
    nm = names[a]
    if not ARR.search(nm):
        continue
    if uniform.read(nm):
        continue
    try:
        e = LE.get(a)
    except Exception:
        continue
    if not any(ratrec.parse_rec(L) for L in e['comment'] + e['formula'] if MARK.search(L)):
        continue
    cond = SHAPE.sub('', nm).strip()
    out[a] = cond
json.dump(out, open('refcensus.json', 'w'), indent=1)
print('entries', len(out))

from collections import Counter
c = Counter()
key = {}
for a, cond in out.items():
    k = ' '.join(re.sub(r'\d+', '#', cond).split()[:5])
    c[k] += 1
    key.setdefault(k, []).append(a)
for k, n in c.most_common(45):
    print(f'{n:5d}  {k}   e.g. {key[k][0]}')
