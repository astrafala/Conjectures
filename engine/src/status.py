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
                'rownew_hits.json', 'cfnew_hits.json', 'shardt94_hits_*.json',
                'lexcf_hits.json'):
        for f in glob.glob(pat):
            for h in (L(f) or []):
                if isinstance(h, dict) and h.get('anum') and h['anum'] not in roster:
                    new.add(h['anum'])
    # the tail sweep's proofs are results too and belong in the total, not only in its own
    # line: a headline count that leaves out a whole sweep is the kind of number that drifts
    t = L('ordtails.json') or {}
    new |= {x['anum'] for x in t.get('proved', []) if x['anum'] not in roster}
    out = [f'NEW {len(new)}']
    # the shards overlap: three workers can each land on the same entry, so summing their
    # lengths counted some entries twice and once read past the total. Union by A-number.
    okset, badset, skset = set(), set(), set()

    def _anum(x):
        return x if isinstance(x, str) else (x.get('anum') if isinstance(x, dict) else str(x))

    for f in glob.glob(os.path.join(repopaths.DEEPCHECK, 'phase5-*.json')):
        s = L(f)
        if s:
            okset |= {_anum(x) for x in s['ok']}
            badset |= {_anum(x) for x in s['bad']}
            for v in s.get('skipped', {}).values():
                skset |= {_anum(x) for x in v}
    # the total was hard-coded at 3865 and the real pool is 3864; derive it instead so the
    # line cannot drift from what phase 5 actually iterates
    try:
        tot = len({h['anum'] for h in L('uniall_hits.json') or []
                   if not h.get('FAILS') and h.get('coeffs') and h.get('engine')})
    except Exception:
        tot = 0
    ok, bad, sk = len(okset), len(badset), len(skset - okset)
    out.append(f'phase5 {ok}/{tot} bad {bad} skip {sk} left {max(0, tot - ok - bad - sk)}')
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
