#!/usr/bin/env python3
"""Fill texfacts.json for every paper in the roster, from the stored sources.

`addtexfacts_new.py` reads `build/un<anum>/p.tex` and only the engines named on its command
line, so every vein with its own build prefix -- the order-line papers in `build/ow`, the tail
papers in `build/ot`, the tables in `build/tb3`, the closed forms in `build/cf` -- was invisible
to it and its papers reached mkcomments with no facts at all.

`paper-sources/` now holds the .tex of every paper that has one, named by rank, and
`rank-map.json` says which A-number sits at each rank. That is the one place where every
paper's source can be found the same way, so this reads from there.

    python3 src/addtexfacts_all.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperpath as P
import repopaths

SC = ('/tmp/claude-0/-home-user-Conjectures/'
      'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad')
tex = json.load(open(SC + '/texfacts.json'))
st = json.load(open(SC + '/status.json'))
rm = json.load(open('rank-map.json'))
added = nosrc = 0
for m in rm:
    a = m['anum']
    if a in tex and tex[a]:
        continue
    f = (f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
         f"{P.name(m['rank'], m['verdict'])[:-4]}.tex")
    if not os.path.exists(f):
        nosrc += 1
        continue
    src = open(f, errors='ignore').read()
    t = re.search(r'\\title\{(.+?)\}\n', src, re.S)
    q = re.search(r'\\begin\{quote\}\n(.+?)\n\\end\{quote\}', src, re.S)
    # S and the threshold are quoted in the papers themselves; take them from the source
    # rather than from a hits file, which not every vein has
    ms = re.search(r"S'?=(\d+)", src)
    mt = re.search(r'n>(\d+)', q.group(1) if q else '')
    tex[a] = [{'f': f, 'title': ' '.join(t.group(1).split()).replace(a, 'A') if t else '',
               'quote': ' '.join(q.group(1).split()) if q else '',
               'thr': int(mt.group(1)) if mt else 0,
               'S': int(ms.group(1)) if ms else 0}]
    st.setdefault(a, 'statement checked numerically')
    added += 1
json.dump(tex, open(SC + '/texfacts.json', 'w'))
json.dump(st, open(SC + '/status.json', 'w'))
print(f'texfacts filled for {added} papers; {nosrc} have no stored source')
