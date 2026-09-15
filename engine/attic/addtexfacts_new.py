#!/usr/bin/env python3
"""Fold every paper built in this run into texfacts.json, which mkcomments reads."""
import json, os, re, sys
SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'
tex = json.load(open(SC + '/texfacts.json'))
st = json.load(open(SC + '/status.json'))
engines = set(sys.argv[1:]) or {'transfer82', 'transfer83', 'transfer84', 'transfer85'}
hits = [h for h in json.load(open('uniall_hits.json'))
        if h.get('engine') in engines and not h.get('FAILS')]
n = 0
for h in hits:
    a = h['anum']
    f = f"build/un{a}/p.tex"
    if not os.path.exists(f):
        continue
    src = open(f, errors='ignore').read()
    m = re.search(r'\\title\{(.+?)\}\n', src, re.S)
    title = ' '.join(m.group(1).split()).replace(a, 'A') if m else ''
    q = re.search(r'\\begin\{quote\}\n(.+?)\n\\end\{quote\}', src, re.S)
    tex[a] = [{'f': f, 'title': title, 'quote': ' '.join(q.group(1).split()) if q else '',
               'thr': h['nthr'], 'S': h['S']}]
    st.setdefault(a, 'statement checked numerically')
    n += 1
json.dump(tex, open(SC + '/texfacts.json', 'w'))
json.dump(st, open(SC + '/status.json', 'w'))
print('texfacts updated for', n, 'papers')
