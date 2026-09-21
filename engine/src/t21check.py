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


class Timeout(BaseException):
    """BaseException, not Exception, and that is the whole point.

    The alarm fires INSIDE `uniform.build', whose last clause is `except Exception: return
    None' -- so a Timeout derived from Exception was swallowed there and the build returned
    None, which every caller reads as "the state space exceeded the cap". Measured: a W=9 entry
    asked with a 2-second budget and a cap of 10^12 was recorded as `state space > cap'. Every
    build timeout in this project has been filed as a cap refusal, which is why
    `uniall_caps.json' over-reports and why the 33 entries of `residue.txt' were finished with
    no record of what finished them.

    `uniform.build' already re-raises MemoryError for exactly this reason, with the comment
    that an out-of-memory "is a different fact". A timeout is a different fact by the same
    argument. Deriving from BaseException makes it one no `except Exception' can absorb --
    the idiom Python itself uses for KeyboardInterrupt.
    """
    pass


signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Timeout()))
N = int(os.environ.get('NTERMS', '12'))
state = json.load(open(OUT)) if os.path.exists(OUT) else {'same': {}, 'opened': {},
                                                          'both_refused': [], 'skipped': {}}
# `lost' is the bucket this harness could not name until now, and the one it exists to catch.
# `uniform.build' ends in `except Exception: return None', so a genuine bug inside
# build_lineset -- a KeyError, a TypeError, an off-by-one in the Cmin key -- does not raise
# here. It comes back as None. And the test below read None from the lineset alone as
# `both_refused' WITHOUT asking what pairfree had done, so a lineset that had just lost a model
# pairfree builds would have been filed as the two of them agreeing. That is the exact shape of
# defect 46, and of the older harness on this very vein that compared its own TypeError with
# itself and reported 99 of 99 agreeing. Measured on the eleven entries already filed: all
# eleven have pairfree genuinely refusing, so nothing was hidden -- but the label could not
# have told me otherwise, and a label that cannot fail is not evidence.
state.setdefault('lost', {})


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
        | set(state['skipped']) | set(state['lost'])
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
        if tb is None and ta is None:
            state['both_refused'].append(a)
        elif tb is None:
            # pairfree BUILT and lineset did not. Never agreement: either the merge is wrong or
            # it is slower on this shape, and both are findings. Loud, because this is the one
            # outcome that would stop the switch.
            state['lost'][a] = Sa
            print(f'{a} LINESET LOST a model pairfree builds: pairfree S={Sa}', flush=True)
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
    print(f"\n{len(state['lost'])} LOST by the merge (must be 0 before switching)")
    print(f"{len(same)} compared, 0 mismatches, {diff} of them with DIFFERENT state counts; "
          f"{len(state['opened'])} the merge opens; {len(state['both_refused'])} both refuse; "
          f"{len(state['skipped'])} skipped", flush=True)


main()
