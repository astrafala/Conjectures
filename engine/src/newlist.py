#!/usr/bin/env python3
"""Write out the A-numbers of every result held but not yet installed.

status.py counts them; nothing wrote the list itself, so the live re-check that has to
happen before any of them is counted had nothing to read. One list, one place.

    python3 src/newlist.py > deep-check/new.txt
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def L(f):
    try:
        return json.load(open(f))
    except Exception:
        return None


roster = {v['anum'] for v in (L('paper-engines.json') or {}).values()}
new = set()
for pat in ('shard_hits_*.json', 'ordwhole_hits.json', 'tabnew_hits.json',
            'rownew_hits.json', 'cfnew_hits.json', 'shardt94_hits_*.json'):
    for f in glob.glob(pat):
        for h in (L(f) or []):
            if isinstance(h, dict) and h.get('anum') and h['anum'] not in roster:
                new.add(h['anum'])
new |= {x['anum'] for x in (L('ordtails.json') or {}).get('proved', [])
        if x['anum'] not in roster}
print('\n'.join(sorted(new)))
