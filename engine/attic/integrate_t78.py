import json, os, shutil
hits = [h for h in json.load(open('transfer78_hits.json')) if not h.get('FAILS')]
eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
nxt = max(eng) + 1
added, skipped = [], []
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    src = f"build/t78{a}/p.pdf"
    if a in have or not (os.path.exists(src) and os.path.getsize(src) > 50000):
        skipped.append(a)
        continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt] = {'engine': 'triangle-quasipolynomial', 'order': h['order'],
                'degree': h['T'], 'anum': a, 'disproof': False}
    have.add(a)
    added.append((nxt, a))
    nxt += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
d = json.load(open('engine_desc.json'))
d['triangle-quasipolynomial|PROOF'] = (
    "a triangle of FIXED shape over the alphabet 0..n: the alphabet grows, not the shape, so "
    "there is no digraph to walk; inclusion-exclusion over the adjacent pairs gives an exact "
    "quasi-polynomial of period 2 and the recurrence follows by polynomial division")
json.dump(d, open('engine_desc.json', 'w'), indent=1, sort_keys=True)
print('added', len(added), added)
print('skipped', len(skipped), skipped)
