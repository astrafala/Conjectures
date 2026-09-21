#!/usr/bin/env python3
"""What does an `out-of-memory' row actually mean? Measure the footprint instead of assuming it.

`uniall_oom.json' is written from two places. One is honest: `uniform.build' raises MemoryError
against the shard's RLIMIT_AS and the handler records MEMGB. The other is the in-flight marker
-- the shard died without recording anything, the boot stamp says the container did not
restart, so the next round writes the entry down as having died at MEMGB. That second path
cannot tell the entry's own footprint from the machine's: a shard killed by the cgroup while
twenty-eight other runners share 15 GB has learned nothing about the entry it happened to be
holding.

A183618 is the case that forced this. Its row said 6 GB refused it. Asked alone, it builds in
364 seconds with a peak RSS of 0.07 GB -- seventy megabytes. What had refused it was every
budget it was ever asked under, all of them shorter than 364 seconds. It was then skipped by
every runner at 6 GB or less, for ever, on a premise nothing had measured.

This asks each row alone, in its own process, with a generous clock and no memory limit, and
records the two numbers that decide which file it belongs in: seconds to build, and peak RSS.

    python3 src/oomtruth.py            # every row of uniall_oom.json not yet measured
"""
import json
import os
import subprocess
import sys
import time

OUT = 'deep-check/oomtruth.json'
BUDGET = int(os.environ.get('BUDGET', '900'))
CAP = int(os.environ.get('CAP', '2000000'))

CHILD = r'''
import sys, time, resource, json
# A guard, not a measurement. The point of this script is to ask each row with a generous clock
# and no memory limit -- but "no limit" on a 15 GB container shared with fifty runners means a
# single greedy build can have the CGROUP kill something else, and then the machine has taught
# me a fact about the wrong entry, which is the very mistake being investigated. 9 GB is above
# every limit any row was refused at (the worst is 7) and well below the container, so anything
# that hits it is genuinely large and says so by raising MemoryError, which the parent records.
resource.setrlimit(resource.RLIMIT_AS, (9 * 1024**3, 9 * 1024**3))
sys.path.insert(0, 'src')
import uniform, localentry as LE
import transfer17, transfer21  # noqa: F401
a = sys.argv[1]
e = LE.get(a)
got = uniform.read(e['name'])
if not got:
    print(json.dumps({'status': 'unreadable'})); raise SystemExit
t0 = time.time()
b = uniform.build(got[0], got[1], int(sys.argv[2]))
el = time.time() - t0
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576.0
print(json.dumps({'status': 'refused-at-cap' if b is None else 'built',
                  'engine': got[0], 'secs': round(el, 1), 'peak_gb': round(rss, 3),
                  'S': None if b is None else uniform.size(got[0], got[1], b)}))
'''


def main():
    rows = json.load(open('uniall_oom.json'))
    state = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [a for a in sorted(rows) if a not in state]
    print(f'{len(rows)} oom rows, {len(state)} measured, {len(todo)} to ask', flush=True)
    for a in todo:
        t0 = time.time()
        try:
            p = subprocess.run([sys.executable, '-c', CHILD, a, str(CAP)],
                               capture_output=True, text=True, timeout=BUDGET)
        except subprocess.TimeoutExpired:
            state[a] = {'status': f'over {BUDGET}s', 'recorded_gb': rows[a]}
            print(f'{a:<10} over {BUDGET}s', flush=True)
        else:
            line = (p.stdout or '').strip().splitlines()
            if p.returncode != 0 or not line:
                # A non-zero exit with no line is the child being KILLED -- the kernel, not the
                # entry. Named as such rather than folded back into a memory refusal, which is
                # the whole mistake this script exists to stop repeating.
                tail = (p.stderr or '').strip().splitlines()
                state[a] = {'status': 'child died', 'rc': p.returncode,
                            'stderr': tail[-1] if tail else '', 'recorded_gb': rows[a]}
                print(f'{a:<10} child died rc={p.returncode} {state[a]["stderr"][:70]}', flush=True)
            else:
                d = json.loads(line[-1])
                d['recorded_gb'] = rows[a]
                state[a] = d
                if d['status'] == 'built':
                    print(f'{a:<10} BUILT S={d["S"]:<9} {d["secs"]:>7.1f}s  peak '
                          f'{d["peak_gb"]:.2f} GB   (row said {rows[a]} GB)', flush=True)
                else:
                    print(f'{a:<10} {d["status"]:<15} {d["secs"]:>7.1f}s  peak '
                          f'{d["peak_gb"]:.2f} GB   (row said {rows[a]} GB)', flush=True)
        tmp = OUT + '.tmp'
        json.dump(state, open(tmp, 'w'), indent=0)
        os.replace(tmp, OUT)
    built = [v for v in state.values() if v.get('status') == 'built']
    small = [v for v in built if v['peak_gb'] < 1.0]
    print(f'\n{len(state)} measured: {len(built)} build alone; {len(small)} of those under 1 GB '
          f'-- rows that were never a memory refusal at all', flush=True)


main()
