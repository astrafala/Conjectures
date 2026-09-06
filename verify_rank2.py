import paperpath
#!/usr/bin/env python3
"""Renumbering check, in two cheap pieces instead of one expensive one.

The full text-extraction pass over both trees reads 12000 PDFs and does not fit in one
foreground run here. It splits into (a) the renumbering itself, which is a copy and so is
settled exactly by comparing file digests against rank-map.json, and (b) whether a paper is
filed under the right A-number, which only has to be re-checked for papers newly added.
"""
import json, os, re, sys, hashlib
from collections import Counter
from pdfminer.high_level import extract_text


def dig(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


rm = json.load(open('rank-map.json'))
bad = []
for m in rm:
    a = paperpath.path(m['rank'], m['verdict'])
    b = f"papers-old-numbering/{m['was']}-{m['verdict']}.pdf"
    if not os.path.exists(a) or not os.path.exists(b) or dig(a) != dig(b):
        bad.append(m['rank'])
print('ranks whose file is not the master it claims:', bad or 'none')
import glob
print('papers/ file count:', len(glob.glob('papers/*/*.pdf')), 'map rows:', len(rm))
dup = Counter(m['anum'] for m in rm)
dup = sorted(a for a, n in dup.items() if n > 1)
# not an error: an entry can carry more than one conjecture, and each gets its own paper
print('entries holding more than one paper:', len(dup))

check = sys.argv[1:]
if check:
    byan = {m['anum']: m for m in rm}
    wrong = []
    for a in check:
        m = byan[a]
        t = extract_text(paperpath.path(m['rank'], m['verdict']), maxpages=2)
        found = re.findall(r'A\d{6}', t)
        if not found or found[0] != a:
            wrong.append((a, found[:2]))
    print('newly added papers whose PDF names another entry:', wrong or 'none',
          '(%d checked)' % len(check))
