#!/usr/bin/env python3
"""One line saying where everything stands. Written as a script so no shell quoting sits
between the numbers and whoever is reading them --- an inline monitor script that got its
quoting wrong reported the literal text "$cur" instead of a status for a whole cycle.

    python3 src/status.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repopaths


def L(f):
    try:
        return json.load(open(f))
    except Exception:
        return None


def main():
    roster = {v['anum'] for v in (L('paper-engines.json') or {}).values()}
    new = set()
    for pat in ('shard_hits_*.json', 'ordwhole_hits.json', 'tabnew_hits.json',
                'rownew_hits.json', 'cfnew_hits.json', 'shardt94_hits_*.json'):
        for f in glob.glob(pat):
            for h in (L(f) or []):
                if isinstance(h, dict) and h.get('anum') and h['anum'] not in roster:
                    new.add(h['anum'])
    out = [f'NEW {len(new)}']
    ok = bad = sk = 0
    for f in glob.glob(os.path.join(repopaths.DEEPCHECK, 'phase5-*.json')):
        s = L(f)
        if s:
            ok += len(s['ok'])
            bad += len(s['bad'])
            sk += sum(len(v) for v in s.get('skipped', {}).values())
    out.append(f'phase5 {ok}/3865 bad {bad} left {max(0, 3865 - ok - sk)}')
    p = L(os.path.join(repopaths.DEEPCHECK, 'phase12-0.json'))
    if p:
        out.append(f'phase12 {len(p["ok"])} fail {len(p["bad"])}')
    out.append(f'disproofs {len(L("falsify.json") or [])}')
    t = L('ordtails.json')
    if t:
        out.append(f'tails {len(t["proved"])} proved {len(t["disproved"])} disproof-cand')
    for lbl, f in (('i2x2', 'indep2x2_done.json'), ('iadj', 'indepadj_done.json')):
        d = L(f)
        if d:
            out.append(f'{lbl} {sum(1 for v in d.values() if v[:2] == "OK")} ok '
                       f'{sum(1 for v in d.values() if v[:3] == "DIS")} BAD')
    print(' | '.join(out))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
