"""Integrate the T(n,k) column papers: replace the 59 already held (their Verification
section quoted a digit count that was not theirs) and add the newly settled tables."""
import json, os, shutil
hits = json.load(open('table_hits.json'))
eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
by_anum = {v['anum']: k for k, v in eng.items()}
nxt = max(eng) + 1
added, replaced, skipped = [], [], []
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    src = f"build/tb2{a}/p.pdf"
    if not (os.path.exists(src) and os.path.getsize(src) > 50000):
        skipped.append(a); continue
    order = max(c['order'] for c in h['cols'])
    degree = max(c['S'] for c in h['cols'])
    if a in by_anum:
        w = by_anum[a]
        assert eng[w]['engine'] == 'table-column', (a, eng[w])
        shutil.copy(src, f"papers-old-numbering/{w}-PROOF.pdf")
        eng[w].update({'order': order, 'degree': degree})
        replaced.append((w, a)); continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt] = {'engine': 'table-column', 'order': order, 'degree': degree,
                'anum': a, 'disproof': False}
    added.append((nxt, a)); nxt += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
print('added', len(added), 'replaced', len(replaced), 'skipped', len(skipped), skipped[:5])
