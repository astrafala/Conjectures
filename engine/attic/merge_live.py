#!/usr/bin/env python3
"""Fold the live re-check's shard files into the one the builders read."""
import glob
import json
import os

OUT = 'deep-check/livenew.json'
d = json.load(open(OUT)) if os.path.exists(OUT) else {'kept': {}, 'dropped': {}, 'flagged': {}}
for f in sorted(glob.glob('deep-check/livenew_*.json')):
    try:
        s = json.load(open(f))
    except Exception:
        continue
    for k in ('kept', 'dropped', 'flagged'):
        d.setdefault(k, {}).update(s.get(k, {}))
json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print({k: len(v) for k, v in d.items()})
