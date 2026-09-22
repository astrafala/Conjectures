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
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bfile
import bsweep
from regf import entry

LAG = re.compile(r'a\(n-(\d+)\)')


def _line_order(line):
    """the order of a recurrence line, or 0 for a closed form or generating function"""
    lags = [int(x) for x in LAG.findall(line or '')]
    return max(lags) if lags else 0

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
    pe = json.load(open('paper-engines.json')).values()
    roster = sorted({v['anum'] for v in pe})
    # Six papers on this roster carry `disproof', and only THREE of them disprove the thing
    # this sweep tests. The distinction is the engine.
    #
    # `engine: disproof' (A076217, A141135, A197230) means the entry's own stated recurrence,
    # closed form or generating function is the thing shown false -- exactly what is tested
    # here -- so a b-file failure is the paper's assertion and a PASS is the alarm.
    #
    # `engine: quadratic' (A000364, A000040, A008365) disproves something else entirely.
    # Paper 28 refutes a trigonometric phi(k) periodicity claim on the Euler numbers, failing
    # at k = 27 and 54; paper 29 is on the primes. Neither says a word about those entries'
    # formula lines, which may hold perfectly well -- and do. Flagging them as "DISPROOF PAPER
    # BUT THE CONJECTURE HOLDS" was this sweep asserting something no paper had claimed.
    #
    # Caught by hand, which is the binding rule: check every apparent disproof against the
    # entry's own wording. Here it was the apparent FALSE disproof that had to be checked, and
    # the defect was in the checker's premise rather than in anybody's paper.
    DISPROOF = {v['anum'] for v in pe if v.get('disproof') and v.get('engine') == 'disproof'}
    # the order of the claim each paper settled, so a failing line can be told from our line
    PAPER_ORDER = {v['anum']: v.get('order') for v in pe}
    OTHERDIS = {v['anum'] for v in pe if v.get('disproof') and v.get('engine') != 'disproof'}
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
        # ALIGN BY OFFSET RATHER THAN DEMANDING IT MATCH. A b-file that starts earlier than the
        # DATA field is not a disagreement -- A193641's b-file begins at n=0 and its DATA at
        # n=1, and every overlapping term agrees. Comparing index by index and requiring
        # `off == doff' called that "b-file disagrees with DATA" and dropped the entry from the
        # check entirely. Rare -- zero cases in a 400-entry sample, so this unlocks almost
        # nothing -- but a false inconsistency reported against somebody else's entry is worth
        # more care than its frequency suggests.
        lo = max(off, doff)
        n = min(off + len(vals), doff + len(data)) - lo
        if n <= 0 or any(vals[lo - off + i] != data[lo - doff + i] for i in range(min(n, 20))):
            # the entry really does contradict itself; a failure below would be its fault
            state[a] = {'status': 'b-file disagrees with DATA'}
            continue

        # bsweep's own filter for a conjectural line. The entries on this roster were proved
        # FROM a conjecture, so the line is still marked as one; the recurrence test is
        # coeffs_of inside bsweep.check, which skips what it cannot parse.
        conjs = [l for l in F if bsweep.MARK.match(l)]
        bad = bsweep.check(a, conjs, vals, off)
        bad += bsweep.check_closed(F, vals, off) + bsweep.check_gf(F, vals, off)
        if a in DISPROOF:
            st = 'disproof confirmed: the entry fails, as its paper says' if bad else \
                 'DISPROOF PAPER BUT THE CONJECTURE HOLDS'
        elif a in OTHERDIS:
            st = ('formula lines fail, but this entry\'s disproof paper is about another claim'
                  if bad else 'holds on all b-file terms (its disproof paper is about another claim)')
        else:
            # A failure is a contradiction of OUR paper only if it is the claim our paper
            # proved. provedsweep tests every conjectural line on the entry, and an entry may
            # state several -- including lines that contradict each other.
            #
            # A286772 is the case. It states BOTH `a(n) = 1 for n>2' and
            # `a(n) = 2^(n+1) - 2 for n>2', which cannot both hold, because the OEIS entry lost
            # the words "even" and "odd" from two parity formulas (already recorded in
            # LEDGER.md as one of seven transcription defects). Both fail on the b-file, as they
            # must. The line this project proved is `a(n) = 5*a(n-2) - 4*a(n-4) for n>4', order
            # 4, and it holds at every term. Reporting that as CONTRADICTS A PROVED PAPER was
            # this sweep asserting something no paper claimed -- the same over-claim as the
            # A000040/A000364 alarm.
            #
            # paper-engines.json records the ORDER of the claim each paper settled. A failing
            # line whose order differs from it is a different claim, and the entry contradicting
            # itself is the entry's problem.
            ours = PAPER_ORDER.get(a)
            if bad and ours is not None and all(_line_order(b[0]) != ours for b in bad):
                st = ('other conjecture lines on this entry fail; the claim this paper proved '
                      'is not among them')
            else:
                st = 'CONTRADICTS A PROVED PAPER' if bad else 'holds on all b-file terms'
        state[a] = {'status': st, 'nterms': len(vals), 'ndata': len(data),
                    'nconj': len(conjs), 'bad': bad}
        if st.startswith('CONTRADICTS') or st.startswith('DISPROOF PAPER BUT'):
            print(f'*** {a} {st}: {bad[0] if bad else "no failing index"}', flush=True)
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
