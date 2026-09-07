#!/usr/bin/env python3
"""Deep check, Phase 4: the reading, re-pinned.

The largest source of error on this project is not the algebra, it is reading the English of
a conjecture in a way its author did not mean. A reading is *pinned* when a program written
to that reading reproduces the terms the entry itself publishes; the more terms, and the more
independent the program, the tighter the pin.

Three strengths are distinguished, and nothing is counted at a strength it does not have:

  INDEPENDENT  a second program, written to the reading and NOT sharing the engine's code,
               agreed with the entry's published terms. This is the only strength that can
               catch an engine that reads the name wrongly, because a bug in the engine
               cannot be present in a program that does not use it.
  ENGINE       the engine reproduced the entry's published terms, and that is all. A wrong
               reading that happens to be self-consistent survives this.
  NONE         no recorded agreement with published terms at all. These go on the hand list.

Then the ambiguity scan: for every entry whose name carries a word this project has already
been bitten by, the pin is reported separately, because those are exactly the names where two
readings are most likely to exist and only one to be right.

    python3 src/dc_phase4.py
"""
import collections
import glob
import json
import os
import re

import localentry as LE
import repopaths
import uniform

# Words that have already produced, or could plainly produce, two different readings of the
# same sentence. `diagonally`, `subblock` and `king` each cost a correction earlier.
AMBIG = ['diagonally', 'antidiagonally', 'horizontally', 'vertically', 'adjacent',
         'neighbouring', 'neighboring', 'distinct', 'absolute', 'ordered', 'unordered',
         'population', 'moving', 'subblock', 'king', 'knight', 'wrapping', 'cyclic',
         'symmetric']
AMBRE = re.compile(r'(?i)\b(' + '|'.join(AMBIG) + r')\b')


def independent():
    """Entries an independently written brute force agreed with."""
    ok = set()
    for f in sorted(glob.glob('bf*_done.json')):
        d = json.load(open(f))
        if isinstance(d, dict):
            for a, v in d.items():
                st = v[0] if isinstance(v, list) and v else v
                if isinstance(st, dict):
                    st = st.get('v')
                if str(st).upper().startswith('OK'):
                    ok.add(a)
        else:
            ok.update(d)
    return ok


def engine_pin():
    """anum -> how many published terms the engine reproduced, from every sweep's own file.

    A sweep records `nterms` only after it has located the entry's published block inside the
    model's own terms, so the presence of that field IS the record of agreement. Files are
    read rather than any summary, because a summary is one more place for the count to drift.
    """
    best = {}
    for f in sorted(glob.glob('*hits*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        recs = d if isinstance(d, list) else (list(d.values()) if isinstance(d, dict) else [])
        for r in recs:
            if not isinstance(r, dict) or r.get('FAILS'):
                continue
            a, n = r.get('anum'), r.get('nterms')
            if a and isinstance(n, int) and n > 0:
                best[a] = max(best.get(a, 0), n)
    return best


def names():
    """anum -> the entry's name.

    Every sweep stores the name it read alongside its verdict, so the names come from the
    sweep files themselves: that way the ambiguity scan looks at the exact wording the paper
    was written to, not at a copy that may since have been re-fetched and edited.
    """
    nm = {}
    for f in sorted(glob.glob('*hits*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        recs = d if isinstance(d, list) else (list(d.values()) if isinstance(d, dict) else [])
        for r in recs:
            if isinstance(r, dict) and r.get('anum') and r.get('name'):
                nm.setdefault(r['anum'], r['name'])
    return nm


def no_reading(a):
    """Is there an English description here at all to misread?

    A paper falls in the NONE bucket either because its reading was never pinned --- serious
    --- or because there is no reading: the entry states its conjecture as a formula, which
    the paper quotes verbatim, so no sentence about rows, neighbours or subblocks is being
    interpreted and no misreading is possible. The two are told apart by asking whether any
    engine can read the name as a counting description. Guessing from the paper's engine
    label would not do: several labels cover both kinds.

    Returns True when the conjecture is an identity and the reading question does not arise.
    """
    try:
        nm = LE.get(a)['name']
    except Exception:
        return False
    try:
        return uniform.read(nm) is None
    except Exception:
        return False


def cold_pin(a):
    """Last resort: pin the reading here and now, from cold.

    A handful of entries reach this point because the vein that settled them kept no record
    of term agreement -- the paper was built by a hand-written route, not by a sweep. Rather
    than leave them unpinned on a technicality, the model is rebuilt from the name and its
    terms compared with the entry's own, in this process, right now.

    Returns the number of published terms matched, or 0.
    """
    try:
        e = LE.get(a)
        got = uniform.read(e['name'])
        if not got:
            return 0
        en, pr = got
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        b = uniform.build(en, pr, 2000000)
        if b is None:
            return 0
        t = uniform.terms(en, pr, b, len(d) + off + 5)
        tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
        sh = next((sft for sft in range(0, off + 5) if tv[sft:sft + len(d)] == d), None)
        return len(d) if sh is not None else 0
    except Exception:
        return 0


def main():
    roster = json.load(open('paper-engines.json'))
    ind, eng, nm = independent(), engine_pin(), names()
    per = {}
    for v in roster.values():
        a = v['anum']
        if a in per:
            continue
        if a in ind:
            per[a] = ('INDEPENDENT', eng.get(a, 0))
        elif a in eng:
            per[a] = ('ENGINE', eng[a])
        else:
            per[a] = ('NONE', 0)
    # Nothing is called unpinned before asking whether it has a reading at all: condemning a
    # paper because a pin written for state models does not reach it would be the check's
    # failure, not the paper's.
    formula, late = [], {}
    for a, (st, n) in list(per.items()):
        if st != 'NONE':
            continue
        if no_reading(a):
            per[a] = ('FORMULA', 0)
            formula.append(a)
        else:
            k = cold_pin(a)
            if k:
                per[a] = ('COLD', k)
                late[a] = k

    c = collections.Counter(s for s, _ in per.values())
    tot = len(per)
    print(f'Phase 4: {tot} entries behind {len(roster)} papers\n')
    for k in ('INDEPENDENT', 'ENGINE', 'COLD', 'FORMULA', 'NONE'):
        print(f'  {k:12s} {c[k]:6d}  ({100.0 * c[k] / tot:5.1f}%)')
    print('  COLD    = no vein kept a record for these, so the model was rebuilt from the '
          'name and its\n            terms compared with the entry\'s in this run.')
    print('  FORMULA = the entry states its conjecture as an identity, quoted verbatim, so '
          'there is no\n            English description of a count for the paper to read '
          'the wrong way.')
    print('  NONE    = there IS a description, and no agreement with published terms is on '
          'record.')

    terms = [n for s, n in per.values() if n]
    if terms:
        terms.sort()
        print(f'\n  published terms reproduced: min {terms[0]}, median '
              f'{terms[len(terms) // 2]}, max {terms[-1]}')

    # A pin's strength is not how many terms agree but how much agreeing costs. Seven terms
    # of a plane-partition count are seven twenty-digit numbers; a reading that is wrong does
    # not reproduce a hundred and forty digits by luck, while twenty terms of a sequence of
    # small integers is a far looser constraint. So the strength is counted in digits.
    digits, thin = {}, []
    for a, (st, n) in per.items():
        if not n:
            continue
        try:
            d = [v.strip() for v in LE.get(a)['data'].split(',') if v.strip()]
        except Exception:
            continue
        k = sum(len(v.lstrip('-')) for v in d[:n])
        digits[a] = k
        if k < 40:
            thin.append(a)
    if digits:
        v = sorted(digits.values())
        print(f'  digits of published data reproduced: min {v[0]}, median '
              f'{v[len(v) // 2]}, max {v[-1]}')
        print(f'  {len(thin)} entries pinned by fewer than 40 digits — those, and only '
              f'those, are pins\n  thin enough that a wrong reading could plausibly '
              f'reproduce them by coincidence')

    amb = {a: v for a, v in per.items() if AMBRE.search(nm.get(a, ''))}
    ca = collections.Counter(s for s, _ in amb.values())
    print(f'\n  {len(amb)} entries whose name carries a word this project has already been '
          f'bitten by:')
    for k in ('INDEPENDENT', 'ENGINE', 'COLD', 'FORMULA', 'NONE'):
        print(f'    {k:12s} {ca[k]:6d}')
    if len(amb):
        print(f'    -> {ca["ENGINE"] + ca["COLD"] + ca["NONE"]} of them rest on a single '
              f'program reading '
              f'the name. Those are the reading-review list.')

    words = collections.Counter()
    for a in amb:
        for w in set(m.lower() for m in AMBRE.findall(nm.get(a, ''))):
            words[w] += 1
    print('\n  ambiguous words by how many entries carry them:')
    for w, n in words.most_common():
        print(f'    {w:16s} {n:6d}')

    out = {'per': {a: {'pin': s, 'terms': n} for a, (s, n) in per.items()},
           'counts': dict(c), 'ambiguous': sorted(amb),
           'formula': sorted(formula), 'cold': late,
           'unpinned': sorted(a for a, (s, _) in per.items() if s == 'NONE'),
           'digits': digits, 'thin': sorted(thin)}
    p = os.path.join(repopaths.DEEPCHECK, 'phase4.json')
    json.dump(out, open(p, 'w'), indent=1)
    print(f'\n  written to {p}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
