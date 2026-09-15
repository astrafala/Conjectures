import json, os, shutil
hits = [h for h in json.load(open('uniall_hits.json'))
        if h.get('engine') == 'transfer81' and not h.get('FAILS')]
eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
nxt = max(eng) + 1
added, skipped = [], []
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    src = f"build/un{a}/p.pdf"
    if a in have or not (os.path.exists(src) and os.path.getsize(src) > 50000):
        skipped.append(a)
        continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt] = {'engine': 'canonical-subblock', 'order': h['order'], 'degree': h['S'],
                'anum': a, 'disproof': False}
    have.add(a)
    added.append((nxt, a))
    nxt += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
d = json.load(open('engine_desc.json'))
d['canonical-subblock|PROOF'] = (
    "the entry asks two things at once: a condition on every subblock, which a window of "
    "consecutive rows decides, and that new values be introduced in row major order, which is "
    "not local at all -- it counts colourings up to renaming. The whole prefix enters only "
    "through how many values have been introduced so far, so one extra integer in the state "
    "carries it exactly, and the count is again a walk count")
json.dump(d, open('engine_desc.json', 'w'), indent=1, sort_keys=True)
print('added', len(added), 'skipped', len(skipped))
