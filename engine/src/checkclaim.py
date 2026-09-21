#!/usr/bin/env python3
"""Check a held result against the entry's OWN recurrence line, character by character.

The binding rule is "check every apparent proof and disproof by hand against the entry's own
wording". Done by eye that is slow and it degrades: eleven results were checked that way in one
night and the eleventh got the same attention as the first only by luck. This does the textual
comparison mechanically, which is not a replacement for judgement about WHETHER a claim is the
entry's conjecture -- that still needs reading -- but it removes the part where a coefficient is
misread.

For each held, un-installed hit carrying `coeffs' it parses the entry's own formula line and
compares:

  * the coefficient SET, lag by lag, against `coeffs';
  * the threshold the entry states (`for n > N') against both the claimed and the computed one.

A record that disagrees is printed loudly and is NOT written to the output list. A record whose
entry has no parsable recurrence line is also withheld, named, and left for a human read --
absence of a line is not evidence the claim is wrong, only that this tool cannot speak to it.

    python3 src/checkclaim.py transfer17 > deep-check/verified.txt
    python3 src/checkclaim.py            # every engine with held results
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import localentry as LE

ENGINE = sys.argv[1] if len(sys.argv) > 1 else None
LAG = re.compile(r'([+-]?)\s*(\d*)\s*\*?\s*a\(n-(\d+)\)')


def entry_claim(e):
    """the entry's own recurrence line, as {lag: coefficient}, plus its stated threshold"""
    for l in (e.get('formula') or []):
        if 'a(n)' not in l or 'a(n-' not in l or '=' not in l:
            continue
        body = l.split('a(n) =', 1)[-1].split(' for ')[0]
        got = {int(m.group(3)): int((m.group(1) or '+') + (m.group(2) or '1'))
               for m in LAG.finditer(body)}
        if got:
            thr = re.search(r'for n\s*>\s*(\d+)', l)
            return got, (int(thr.group(1)) if thr else None), l
    return None, None, None


def main():
    roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    hits = [h for h in json.load(open('uniall_hits.json'))
            if isinstance(h, dict) and h.get('coeffs') and not h.get('FAILS')
            and h.get('anum') not in roster
            and (ENGINE is None or h.get('engine') == ENGINE)]
    ok, bad, mute = [], [], []
    for h in hits:
        a = h['anum']
        try:
            e = LE.get(a)
        except Exception as exc:
            mute.append((a, f'entry unreadable: {type(exc).__name__}')); continue
        ent, thr, line = entry_claim(e)
        if ent is None:
            mute.append((a, 'no recurrence line on the entry this tool can parse')); continue
        claim = {int(k): int(v) for k, v in h['coeffs'].items()}
        if ent != claim:
            bad.append((a, 'COEFFICIENTS DIFFER',
                        {k: v for k, v in ent.items() if claim.get(k) != v},
                        {k: v for k, v in claim.items() if ent.get(k) != v})); continue
        if thr is None:
            mute.append((a, 'entry states no threshold')); continue
        if not (thr == h.get('claimed') == h.get('nthr')):
            bad.append((a, 'THRESHOLD DIFFERS',
                        f'entry {thr}', f"claimed {h.get('claimed')} computed {h.get('nthr')}"))
            continue
        ok.append(a)
    for a, why, x, y in bad:
        print(f'!! {a} {why}: {x} vs {y}', file=sys.stderr)
    for a, why in mute:
        print(f'?? {a} withheld: {why}', file=sys.stderr)
    print(f'{len(ok)} verified, {len(bad)} DISAGREE, {len(mute)} withheld for a human read',
          file=sys.stderr)
    for a in sorted(ok):
        print(a)


main()
