import json, os, shutil
hits = [h for h in json.load(open('transfer77_hits.json')) if not h.get('FAILS')]
eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
nxt = max(eng) + 1
added, skipped = [], []
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    src = f"build/t77{a}/p.pdf"
    if a in have or not (os.path.exists(src) and os.path.getsize(src) > 50000):
        skipped.append(a)
        continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt] = {'engine': 'rowmajor-across-columns', 'order': h['order'],
                'degree': h['S'], 'anum': a, 'disproof': False}
    have.add(a)
    added.append((nxt, a))
    nxt += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
d = json.load(open('engine_desc.json'))
d['rowmajor-across-columns|PROOF'] = (
    "a clause on the order of first occurrences in ROW major order, on an array the walk has "
    "to cross column by column: the state carries each named value's least row and the order "
    "those least rows were reached, and the clause is tested only at the end")
json.dump(d, open('engine_desc.json', 'w'), indent=1, sort_keys=True)
print('added', len(added), added)
print('skipped', len(skipped), skipped)
