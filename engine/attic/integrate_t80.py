import json, os, shutil
hits = [h for h in json.load(open('transfer80_hits.json')) if not h.get('FAILS')]
eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
nxt = max(eng) + 1
added, skipped = [], []
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    src = f"build/t80{a}/p.pdf"
    if a in have or not (os.path.exists(src) and os.path.getsize(src) > 50000):
        skipped.append(a)
        continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt] = {'engine': 'bounded-difference-triangle', 'order': len(h['settled']),
                'degree': h['bound'], 'anum': a, 'disproof': False}
    have.add(a)
    added.append((nxt, a))
    nxt += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
d = json.load(open('engine_desc.json'))
d['bounded-difference-triangle|PROOF'] = (
    "a fixed triangle over 0..n whose condition constrains differences only: translation "
    "splits the arrays into finitely many classes, a class of spread s holds max(0, n+1-s) of "
    "them, and the spread is bounded by the graph diameter, so the count is exactly linear "
    "from a point known in advance")
json.dump(d, open('engine_desc.json', 'w'), indent=1, sort_keys=True)
print('added', len(added), 'skipped', len(skipped))
