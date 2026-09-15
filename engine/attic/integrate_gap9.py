"""Nine proofs found by the unified sweep that never reached the per-engine paper builders.

The builders read transfer<N>_hits.json; the unified sweep writes uniall_hits.json. Nine
entries were proved only by the second, at a cap the first had refused, so they sat in
uniall_hits.json with no paper. Re-run through their own engines, they are papers like any
other."""
import json, os, shutil

SRC = {'A228666': ('t9', 'transfer-matrix'), 'A228688': ('t9', 'transfer-matrix'),
       'A228759': ('t9', 'transfer-matrix'), 'A229753': ('tg', 'defective'),
       'A255089': ('t17', 'subblock-3x3'), 'A255226': ('t17', 'subblock-3x3'),
       'A255790': ('t17', 'subblock-3x3'), 'A255799': ('t17', 'subblock-3x3'),
       'A256746': ('t17', 'subblock-3x3')}
HITS = {'t9': 'transfer9_hits.json', 'tg': 'transfer16_hits.json',
        't17': 'transfer17_hits.json'}
info = {}
for f in set(HITS.values()):
    for h in json.load(open(f)):
        if h['anum'] in SRC and not h.get('FAILS'):
            info[h['anum']] = h

eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
nxt = max(eng) + 1
added, skipped = [], []
for a in sorted(SRC):
    pre, label = SRC[a]
    src = f'build/{pre}{a}/p.pdf'
    if a in have or not (os.path.exists(src) and os.path.getsize(src) > 50000):
        skipped.append(a)
        continue
    h = info[a]
    shutil.copy(src, f'papers-old-numbering/{nxt}-PROOF.pdf')
    eng[nxt] = {'engine': label, 'order': h['order'], 'degree': h['S'], 'anum': a,
                'disproof': False}
    have.add(a)
    added.append((nxt, a))
    nxt += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
print('added', len(added), added)
print('skipped', len(skipped), skipped)
