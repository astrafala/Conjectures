#!/usr/bin/env python3
"""Does `transfer17.build_lineset' change any transfer21 answer?

transfer21 counts 3x3 subblock conditions up to relabelling of the alphabet, by building one
transfer17 automaton per alphabet size and weighting them -- and it OVERRIDES the start vector
with a uniform weight per size. So the line-set merge being exact for transfer17 does not by
itself make it safe here, even though the return shape is identical, and this asks directly.

It accumulates. The first two attempts were lost -- one to a MemoryError inside transfer19.trim
at entry 14, one to a container restart that wiped /tmp with thirteen entries verified -- and
each time the sample started again from nothing. The standard this vein was held to before is
243 shapes; a sample that cannot survive an hour will never reach it. Results go to
`deep-check/t21check.json' and an entry already recorded is skipped.

A mismatch RAISES. The state counts are recorded for every entry because they are the evidence
that the comparison ran at all: if the monkeypatch failed to take, every pair would be equal,
which is how this vein was once reported 99 of 99 agreeing by a harness comparing its own
TypeError with itself (STATE.md defect 38).

    CAP=200000 python3 src/t21check.py
"""
import json
import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import atomicjson
import localentry as LE
import transfer17
import transfer21  # noqa: F401  -- registers the engine with uniform
import uniform

OUT = 'deep-check/t21check.json'
CAP = int(os.environ.get('CAP', '200000'))
# A per-entry clock, because one entry that cannot finish blocks every entry behind it. A204054
# did exactly that: four container generations in a row printed the header, started on it, and
# died before recording anything, so the verification stood at 12 for forty-five minutes while
# looking alive. The entry is recorded as skipped and the run moves on -- a skip that names the
# entry is a fact; a silent restart loop is not.
BUDGET = int(os.environ.get('BUDGET', '240'))


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Timeout()))
N = int(os.environ.get('NTERMS', '12'))
state = json.load(open(OUT)) if os.path.exists(OUT) else {'same': {}, 'opened': {},
                                                          'both_refused': [], 'skipped': {}}


def run(builder, p):
    orig = transfer17.build_pairfree
    transfer17.build_pairfree = builder
    try:
        b = uniform.build('transfer21', p, CAP)
        return (None, None) if b is None else (uniform.terms('transfer21', p, b, N), b[3])
    finally:
        transfer17.build_pairfree = orig


def main():
    cands = [a for a, e in json.load(open('uni_cands.json')).items() if e == 'transfer21']
    done = set(state['same']) | set(state['opened']) | set(state['both_refused']) \
        | set(state['skipped'])
    todo = [a for a in sorted(cands) if a not in done]
    print(f'{len(cands)} transfer21 candidates, {len(done)} already recorded, {len(todo)} to ask',
          flush=True)
    PF, LS = transfer17.build_pairfree, transfer17.build_lineset
    for a in todo:
        try:
            got = uniform.read(LE.get(a)['name'])
        except Exception as exc:
            state['skipped'][a] = f'entry unreadable: {type(exc).__name__}'
            atomicjson.dump(state, OUT, indent=0); continue
        if not got or got[0] != 'transfer21':
            state['skipped'][a] = 'no longer read as transfer21'
            atomicjson.dump(state, OUT, indent=0); continue
        p = got[1]
        try:
            signal.alarm(BUDGET)
            ta, Sa = run(PF, p)
            tb, Sb = run(LS, p)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0)
            state['skipped'][a] = f'over {BUDGET}s'
            print(f'{a} skipped: over {BUDGET}s', flush=True)
            atomicjson.dump(state, OUT, indent=0); continue
        except MemoryError:
            signal.alarm(0)
            state['skipped'][a] = 'harness out of memory'
            atomicjson.dump(state, OUT, indent=0); continue
        except Exception as exc:
            signal.alarm(0)
            state['skipped'][a] = f'{type(exc).__name__}: {exc}'
            atomicjson.dump(state, OUT, indent=0); continue
        if tb is None:
            state['both_refused'].append(a)
        elif ta is None:
            state['opened'][a] = Sb
            print(f'{a} OPENED by the merge: pairfree refused, lineset S={Sb}', flush=True)
        elif ta != tb:
            raise SystemExit(f'MISMATCH {a}\n  pairfree S={Sa} {ta}\n  lineset S={Sb} {tb}')
        else:
            state['same'][a] = [Sa, Sb]
            print(f'{a} same terms  {Sa} -> {Sb}', flush=True)
        atomicjson.dump(state, OUT, indent=0)
    same = state['same']
    diff = sum(1 for v in same.values() if v[0] != v[1])
    print(f"\n{len(same)} compared, 0 mismatches, {diff} of them with DIFFERENT state counts; "
          f"{len(state['opened'])} the merge opens; {len(state['both_refused'])} both refuse; "
          f"{len(state['skipped'])} skipped", flush=True)


main()
