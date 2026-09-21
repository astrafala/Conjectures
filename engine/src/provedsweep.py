#!/usr/bin/env python3
"""Test the conjecture each INSTALLED paper claims to have proved, against the entry's b-file.

`bsweep.py` does this for conjectures nobody has settled, and found A076217 false that way.
Its queue is built from `open_index.json["open"]`, so the 13,782 entries this project says it
has PROVED are precisely the ones it never asks. That is the wrong way round for finding a
mistake of our own: a false conjecture in the open pool costs a paper that was never written,
while a false conjecture in the roster is a paper that says it is proved.

`bproved.py` covers part of this already, but only the 5,987 records of `uniall_hits.json` and
only the recurrence the ENGINE derived. This asks the other question, on the whole roster and
in the entry's own words: take the conjectured recurrence, closed form and generating function
as the entry states them, and test them against every b-file term. If the project proved the
entry, the entry's own line must hold at every index -- so a failure here is either a proof
that is wrong or an entry that contradicts itself, and both are worth more than a day's sweeping.

The checks are bsweep's own, imported rather than reimplemented, so the two sweeps cannot drift
apart in what they consider a failure.

    python3 src/provedsweep.py            # cached b-files only; no network
    FETCH=1 python3 src/provedsweep.py    # download what is missing -- NEVER while another
                                          # fetcher runs; bfile.fetch is single-process
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bfile
import bsweep
from regf import entry

OUT = 'deep-check/provedsweep.json'
FETCH = os.environ.get('FETCH') == '1'
BUDGET = int(os.environ.get('BUDGET', '1200'))


def cached(anum):
    for d in ('bcache', bfile.CACHE):
        p = os.path.join(d, 'b' + anum[1:] + '.txt')
        if os.path.exists(p):
            return p
    return None


def main():
    roster = sorted({v['anum'] for v in json.load(open('paper-engines.json')).values()})
    state = json.load(open(OUT)) if os.path.exists(OUT) else {}
    # a cache-only pass records a fact about this machine; a downloading pass must be allowed
    # to overturn it, or FETCH=1 is a no-op (the mistake bproved made first)
    if FETCH:
        for a in [a for a, v in state.items() if v.get('status') == 'no cached b-file']:
            del state[a]
    todo = [a for a in roster if a not in state]
    print(f'{len(roster)} entries on the roster, {len(state)} checked, {len(todo)} to ask',
          flush=True)

    t0 = time.time()
    n = 0
    for a in todo:
        if time.time() - t0 > BUDGET:
            print(f'budget {BUDGET}s spent; {len(todo) - n} left for the next round', flush=True)
            break
        n += 1
        path = cached(a)
        if path is None:
            if not FETCH:
                state[a] = {'status': 'no cached b-file'}
                continue
            got = bfile.fetch(a)
            if got == 'BLOCKED':
                print('OEIS is refusing downloads; stopping rather than mislabelling the rest',
                      flush=True)
                break
            if not got:
                state[a] = {'status': 'no b-file'}
                continue

        off, vals = bfile.contiguous(a)
        if len(vals) < 12:
            state[a] = {'status': 'b-file too short'}
            continue
        try:
            F, data, doff, nm = entry(a)
        except Exception as exc:
            # named, never swallowed: "no entry" hid a reader bug once already (defect 46)
            state[a] = {'status': f'entry unreadable: {type(exc).__name__}'}
            continue
        m = min(len(data), len(vals))
        if off != doff or any(vals[i] != data[i] for i in range(min(m, 20))):
            # the entry contradicts itself; a failure below would be its fault, not the proof's
            state[a] = {'status': 'b-file disagrees with DATA'}
            continue

        # bsweep's own filter for a conjectural line. The entries on this roster were proved
        # FROM a conjecture, so the line is still marked as one; the recurrence test is
        # coeffs_of inside bsweep.check, which skips what it cannot parse.
        conjs = [l for l in F if bsweep.MARK.match(l)]
        bad = bsweep.check(a, conjs, vals, off)
        bad += bsweep.check_closed(F, vals, off) + bsweep.check_gf(F, vals, off)
        state[a] = {'status': 'CONTRADICTS A PROVED PAPER' if bad else 'holds on all b-file terms',
                    'nterms': len(vals), 'ndata': len(data), 'nconj': len(conjs), 'bad': bad}
        if bad:
            print(f'*** {a} CONTRADICTS A PROVED PAPER: {bad[0]}', flush=True)
        if n % 25 == 0:
            tmp = OUT + '.tmp'
            json.dump(state, open(tmp, 'w'), indent=0)
            os.replace(tmp, OUT)

    tmp = OUT + '.tmp'
    json.dump(state, open(tmp, 'w'), indent=0)
    os.replace(tmp, OUT)
    import collections
    c = collections.Counter(v['status'] for v in state.values())
    print(f'\n{len(state)} of {len(roster)} roster entries checked', flush=True)
    for k, v in c.most_common():
        print(f'  {k:<34} {v}', flush=True)


main()
