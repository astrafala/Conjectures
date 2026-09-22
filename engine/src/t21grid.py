#!/usr/bin/env python3
"""The parameter-grid half of verifying build_lineset, matching the standard the last switch met.

`uniform.py` records that `build_pairfree` was accepted for transfer21 on "243 shapes -- 99
entries and 144 of the parameter grid, over every body form the parser accepts crossed with
W=3..6 and K=2..4". `t21check.py` has now done the entry half for `build_lineset`: 160 of 160,
110 comparable, ZERO mismatches, ZERO lost, 19 opened, and 80 of the 110 with a strictly
smaller state space, which is what shows the comparison was running rather than comparing two
copies of a failure.

That is a bigger entry sample than the last switch had. What it does not have is the grid, and
the grid is the half that reaches shapes no entry happens to use. So: every distinct body form
among the transfer21 candidates, crossed with width 3..6 and K 2..4, terms from both builders
compared through `uniform.terms` so the scaling denominator is handled the way production
handles it.

Nothing is swallowed. A builder that raises is reported with its exception type, not counted as
agreement -- the defect that let an earlier harness compare its own TypeError with itself and
report 99 of 99 agreeing (STATE.md defect 38).

    python3 src/t21grid.py
"""
import json
import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import localentry as LE
import transfer17
import transfer21  # noqa: F401 -- registers the engine
import uniform

CAP = int(os.environ.get('CAP', '200000'))
NTERMS = int(os.environ.get('NTERMS', '10'))
BUDGET = int(os.environ.get('BUDGET', '90'))
WIDTHS = [3, 4, 5, 6]
KS = [2, 3, 4]


class Timeout(BaseException):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))


def run(builder, p):
    orig = transfer17.build_pairfree
    transfer17.build_pairfree = builder
    try:
        b = uniform.build('transfer21', p, CAP)
        if b is None:
            return None, None
        return uniform.terms('transfer21', p, b, NTERMS), b[3]
    finally:
        transfer17.build_pairfree = orig


def main():
    cands = [a for a, e in json.load(open('uni_cands.json')).items() if e == 'transfer21']
    forms = {}
    for a in sorted(cands):
        try:
            got = uniform.read(LE.get(a)['name'])
        except Exception:
            continue
        if not got or got[0] != 'transfer21':
            continue
        p = got[1]
        forms.setdefault(p.get('body'), p)
    print(f'{len(cands)} candidates, {len(forms)} distinct body forms', flush=True)

    PF, LS = transfer17.build_pairfree, transfer17.build_lineset
    same = diffstates = mismatch = lost = refused = skipped = 0
    shapes = 0
    for body, p0 in sorted(forms.items(), key=lambda x: (x[0] or '')):
        for wid in WIDTHS:
            for K in KS:
                p = dict(p0)
                p['fixed'] = wid
                p['K'] = K
                shapes += 1
                try:
                    signal.alarm(BUDGET)
                    ta, Sa = run(PF, p)
                    tb, Sb = run(LS, p)
                    signal.alarm(0)
                except Timeout:
                    signal.alarm(0); skipped += 1; continue
                except BaseException as exc:
                    signal.alarm(0)
                    print(f'  RAISED on width={wid} K={K}: {type(exc).__name__}: {exc}',
                          flush=True)
                    skipped += 1
                    continue
                if ta is None and tb is None:
                    refused += 1
                elif ta is None:
                    print(f'  OPENED width={wid} K={K}: pairfree refused, lineset S={Sb}',
                          flush=True)
                elif tb is None:
                    lost += 1
                    print(f'*** LOST width={wid} K={K}: pairfree S={Sa} built, lineset did not',
                          flush=True)
                elif ta != tb:
                    mismatch += 1
                    print(f'*** MISMATCH width={wid} K={K}\n    pairfree S={Sa} {ta}\n'
                          f'    lineset  S={Sb} {tb}', flush=True)
                else:
                    same += 1
                    if Sb < Sa:
                        diffstates += 1
    print(f'\n{shapes} shapes asked: {same} agree ({diffstates} of them with a SMALLER state '
          f'space), {mismatch} MISMATCH, {lost} LOST, {refused} both refuse, {skipped} skipped',
          flush=True)
    print('the switch is justified only if MISMATCH and LOST are both 0 and `agree with a '
          'smaller state space` is large', flush=True)


main()
