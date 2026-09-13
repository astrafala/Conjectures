#!/usr/bin/env python3
"""Install every proved result that has a compiled paper and is not yet in the roster."""
import json, os, shutil
ENGNAME = {'transfer81': 'canonical-subblock', 'transfer82': 'subblock-condition',
           'transfer83': 'neighbour-condition', 'transfer84': 'column-domination',
           'transfer85': 'distance-repeat', 'transfer86': 'local-array-condition',
           'transfer87': 'parity-difference', 'transfer89': 'white-squares',
           'transfer91': 'neighbour-reach', 'transfer92': 'straight-line',
           'transfer93': 'subblock-multiset', 'denumerant': 'lattice-count',
           'transfer17': 'subblock-3x3', 'transfer38': 'edge-count-pattern',
           'transfer56': 'forbidden-run', 'transfer62': 'distance-inequality',
           'transfer23': 'subblock-matrix', 'transfer26': 'image-count',
           'transfer28': 'image-count', 'transfer30': 'subblock-coloring',
           'transfer31': 'monotone-subblock', 'transfer32': 'monotone-subblock',
           'transfer33': 'subblock-difference', 'transfer41': 'cell-condition',
           'transfer42': 'cell-condition-pattern', 'transfer45': 'consecutive-triple',
           'transfer53': 'modular-neighbour', 'transfer32': 'monotone-subblock',
           'transfer55': 'repeated-value', 'transfer60': 'capped-pair-count',
           # the engines whose model is not a walk: without these the default
           # 'transfer-matrix' label would be as false as unibuild's digraph was
           'latpoly': 'lattice-quasipolynomial', 'ordpoly': 'fixed-length-polynomial',
           'necklace': 'necklace-burnside', 'multiset': 'multiset-profile',
           'cuspdim': 'cusp-form-dimension', 'ca2d': 'automaton-axis',
           'ecarow': 'automaton-row', 'ecacount': 'automaton-cell-count', 'ecablock': 'automaton-block-count', 'permdisp': 'bounded-displacement',
           'window': 'window-condition', 'repval': 'repeated-value-chain'}
eng = {int(k): v for k, v in json.load(open('paper-engines.json')).items()}
have = {v['anum'] for v in eng.values()}
nxt = max(eng) + 1
added = 0
for h in sorted(json.load(open('uniall_hits.json')), key=lambda x: x.get('anum', '')):
    a = h.get('anum')
    if not a or h.get('FAILS') or a in have:
        continue
    src = f"build/un{a}/p.pdf"
    if not (os.path.exists(src) and os.path.getsize(src) > 50000):
        print('  no paper for', a, h.get('engine'))
        continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt] = {'engine': ENGNAME.get(h['engine'], 'transfer-matrix'),
                'order': h['order'], 'degree': h['S'], 'anum': a, 'disproof': False}
    have.add(a)
    nxt += 1
    added += 1
json.dump({str(k): v for k, v in eng.items()}, open('paper-engines.json', 'w'),
          indent=1, sort_keys=True)
print('added', added)
