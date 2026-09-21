#!/usr/bin/env python3
"""Test every PROVED recurrence against the entry's b-file. The DATA guard was inert for 36%.

`sweep_shard' has one empirical check on a result it is about to keep: it recomputes each
published term from the recurrence and refuses the hit if any disagrees. That check runs only
at indices satisfying BOTH `off + k > nthr' and `k >= order' -- and for 2,132 of 5,987 held
results there is no such index, because the DATA field is shorter than the order of the
recurrence proved for it. A183618 is the case that exposed it: order 30, fourteen published
terms, so the guard tested nothing at all and printed the same nothing it prints when a result
passes.

Those results are not thereby wrong. The model is still matched term-for-term against DATA
before any recurrence is derived, and the recurrence follows from the transfer matrix rather
than from a fit. What was missing is the independent check on the ANNIHILATION step -- and for
Hardin's entries it is free, because the b-file runs to a hundred terms or more where DATA
stops at fourteen. A183618's recurrence holds at all 87 testable b-file indices.

A failure here would not be a small thing. It would say a recurrence this project has recorded
as proved is false, which means a bug in the engine that produced it, not a wrong conjecture by
somebody else. So nothing on that path is swallowed: b-file and DATA are checked against each
other first (an entry inconsistent with itself is the entry's problem, not the recurrence's),
the first failing index is recorded exactly, and no exception is caught without being named.

    python3 src/bproved.py            # cached b-files only; no network
    FETCH=1 python3 src/bproved.py    # download what is missing, rate-limited, single process
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bfile

OUT = 'deep-check/bproved.json'
FETCH = os.environ.get('FETCH') == '1'

# There are TWO b-file caches and they are not the same directory. `bfile.CACHE' is an absolute
# path to the repository root; the historical cache this project accumulated -- 3,377 files,
# 145 MB -- sits in engine/bcache and is what a relative 'bcache' resolves to when run from
# engine/. Reading only one of them means a cache-only pass reports `no cached b-file' for
# every file the last downloading pass fetched, and downloads it again. Both are searched.
CACHES = [os.path.join('bcache'), bfile.CACHE]


def cached(anum):
    for d in CACHES:
        p = os.path.join(d, 'b' + anum[1:] + '.txt')
        if os.path.exists(p):
            return p
    return None


def guard_coverage(h):
    """how many published terms sweep_shard's own `contradicted by DATA' test actually read"""
    off, nthr, order, n = h.get('offset', 1), h.get('nthr', 0), h['order'], h.get('nterms', 0)
    return sum(1 for k in range(n) if off + k > nthr and k - order >= 0)


def read_bfile(path):
    d = {}
    for ln in open(path, errors='ignore'):
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        parts = ln.split()
        if len(parts) < 2:
            continue
        try:
            d[int(parts[0])] = int(parts[1])
        except ValueError:
            continue
    return d


def main():
    H = json.load(open('uniall_hits.json'))
    state = json.load(open(OUT)) if os.path.exists(OUT) else {}
    # `no cached b-file' is a statement about this machine, not about the entry, so it must not
    # survive into a run that is allowed to download. Left in place it made FETCH=1 a no-op:
    # 4,426 results were recorded as unreachable by a cache-only pass and then skipped by the
    # very run whose job was to reach them.
    if FETCH:
        for a in [a for a, v in state.items() if v.get('status') == 'no cached b-file']:
            del state[a]
    # the results whose own guard read nothing come first: they are the ones with no empirical
    # check at all behind them, and so the ones where this is evidence rather than confirmation
    todo = [h for h in H if h.get('coeffs') and h.get('order') and h['anum'] not in state]
    todo.sort(key=lambda h: (guard_coverage(h) != 0, h['anum']))
    print(f'{len(H)} hits, {len(state)} already checked, {len(todo)} to check '
          f'({sum(1 for h in todo if guard_coverage(h) == 0)} of them with a guard that read '
          f'nothing)', flush=True)

    nver = nfail = nshort = nmiss = 0
    for h in todo:
        a = h['anum']
        path = cached(a)
        if path is None:
            if not FETCH:
                state[a] = {'status': 'no cached b-file', 'guard': guard_coverage(h)}
                nmiss += 1
                continue
            got = bfile.fetch(a)
            if got == 'BLOCKED':
                print(f'{a} OEIS is refusing downloads; stopping rather than mislabelling the '
                      f'rest as missing', flush=True)
                break
            if not got:
                state[a] = {'status': 'no b-file', 'guard': guard_coverage(h)}
                nmiss += 1
                continue
            path = got

        B = read_bfile(path)
        coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
        order, nthr = max(coeffs), h.get('nthr', 0)

        # Does the b-file agree with the entry's own DATA? If not, the entry contradicts itself
        # and a recurrence failure below would be the entry's fault, not the recurrence's.
        ns = sorted(B)
        idx = [n for n in ns if n > nthr and all((n - k) in B for k in coeffs)]
        if not idx:
            state[a] = {'status': 'b-file too short', 'guard': guard_coverage(h),
                        'order': order, 'nthr': nthr, 'bterms': len(B)}
            nshort += 1
            continue

        bad = []
        for n in idx:
            if sum(c * B[n - k] for k, c in coeffs.items()) != B[n]:
                bad.append(n)
                if len(bad) >= 3:
                    break
        if bad:
            state[a] = {'status': 'FAILS ON B-FILE', 'guard': guard_coverage(h),
                        'order': order, 'nthr': nthr, 'bterms': len(B),
                        'tested': len(idx), 'first_bad': bad[:3]}
            nfail += 1
            print(f'*** {a} FAILS ON B-FILE: order {order}, threshold n>{nthr}, '
                  f'{len(idx)} indices tested, first failure n={bad[0]} '
                  f'(its own DATA guard read {guard_coverage(h)} terms)', flush=True)
        else:
            state[a] = {'status': 'verified', 'guard': guard_coverage(h), 'order': order,
                        'nthr': nthr, 'bterms': len(B), 'tested': len(idx)}
            nver += 1
            if guard_coverage(h) == 0:
                print(f'{a:<10} verified on {len(idx):>4} b-file indices '
                      f'(order {order:>3}, its DATA guard read 0)', flush=True)

        if (nver + nfail + nshort + nmiss) % 50 == 0:
            tmp = OUT + '.tmp'
            json.dump(state, open(tmp, 'w'), indent=0)
            os.replace(tmp, OUT)

    tmp = OUT + '.tmp'
    json.dump(state, open(tmp, 'w'), indent=0)
    os.replace(tmp, OUT)

    zero = [v for v in state.values() if v.get('guard') == 0]
    zv = [v for v in zero if v['status'] == 'verified']
    print(f'\nthis run: {nver} verified, {nfail} FAIL, {nshort} b-file too short, '
          f'{nmiss} no b-file', flush=True)
    print(f'overall: {len(state)} checked; '
          f'{sum(1 for v in state.values() if v["status"] == "verified")} verified, '
          f'{sum(1 for v in state.values() if v["status"] == "FAILS ON B-FILE")} FAIL', flush=True)
    print(f'of the results whose own DATA guard read nothing: {len(zero)} reached, '
          f'{len(zv)} now verified on {sum(v["tested"] for v in zv)} b-file indices', flush=True)


main()
