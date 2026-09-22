#!/usr/bin/env python3
"""Is this runner's list a QUESTION, or the same answer again? Check all three refusals at once.

Five stale lists were found in one night, and the fifth was one I had built myself twenty
minutes earlier. The pattern never varies: a list is generated from a refusal file, the runner
is pointed at it with some cap, budget and memory limit, and nobody asks whether those settings
are the ones that produced the refusals in the first place. `caprun` asked at the cap that had
refused 727 of its 734; `tmorun` asked at the budget that had refused 39 of its 62; `oomlist`
held 41 rows against a file of 138.

The fifth is the instructive one. I rebuilt `t17small.txt`, checked it against `uniall_caps`
and `uniall_oom`, and announced 36 new questions. The runner reported 32 skips for BUDGET: 31
of the 57 carried a `uniall_tmo` row of exactly 420, which was that runner's own budget. Only
16 were askable. **A sweep has three refusals and a list is new only against all three** --
which is the whole reason defects 48, 49 and 53 went to the trouble of keeping them apart.

So this does it mechanically, the way `checkclaim` does the textual half of a by-hand check:
parse the runner's own settings out of its script, and report, per list, how many entries each
of the three files already refuses at or above that setting -- plus how many are settled or
carry no parsable conjecture, which is the fourth way a list wastes rounds.

    python3 src/listcheck.py              # every runner in restart_all.sh
    python3 src/listcheck.py t17run.sh    # one
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

J = lambda f: json.load(open(f)) if os.path.exists(f) else {}
CAPS, TMO, OOM = J('uniall_caps.json'), J('uniall_tmo.json'), J('uniall_oom.json')
DIED = J('uniall_died.json')
HITS = {h['anum'] for h in J('uniall_hits.json')} if os.path.exists('uniall_hits.json') else set()
# sweep_shard's FIRST skip is `if a in roster or a in GHITS: continue', and it is SILENT -- no
# counter, no log line. A list made of entries that already carry an installed paper therefore
# asks nothing while every refusal file says it is clear. t21run sat at 52 of 52 "askable" and
# an empty result dict for an hour because its list was filtered on uniall_hits alone and all
# 52 were on the roster. This tool existed to catch exactly that and had the same gap.
ROSTER = ({v['anum'] for v in J('paper-engines.json').values()}
          if os.path.exists('paper-engines.json') else set())
HITS |= ROSTER
DIEDMAX = 3

SET = re.compile(r'ANUMS_FILE=(\S+)[^\n]*?BUDGET=(\d+)[^\n]*?MEMGB=([\d.]+)', re.S)
CAP = re.compile(r'^\s+timeout \d+ python3 src/sweep_shard\.py (\d+)', re.M)


def check(script):
    s = open(script).read()
    m = SET.search(s)
    cm = CAP.search(s)
    if not m or not cm:
        return None
    lst, budget, memgb = m.group(1), int(m.group(2)), float(m.group(3))
    cap = int(cm.group(1))
    if not os.path.exists(lst):
        return (os.path.basename(script), lst, cap, budget, memgb, None, {})
    L = [x.strip() for x in open(lst) if x.strip()]
    r = {
        'proved already': sum(1 for a in L if a in HITS),
        'cap >= %d' % cap: sum(1 for a in L if a not in HITS and CAPS.get(a, 0) >= cap),
        'budget >= %d' % budget: sum(1 for a in L if a not in HITS and TMO.get(a, 0) >= budget),
        'memory >= %g' % memgb: sum(1 for a in L if a not in HITS and OOM.get(a, 0) >= memgb),
        'died %d+ times' % DIEDMAX: sum(1 for a in L if a not in HITS and DIED.get(a, 0) >= DIEDMAX),
    }
    askable = [a for a in L if a not in HITS and CAPS.get(a, 0) < cap and TMO.get(a, 0) < budget
               and OOM.get(a, 0) < memgb and DIED.get(a, 0) < DIEDMAX]
    return (os.path.basename(script), lst, cap, budget, memgb, len(L), r, len(askable))


def main():
    if len(sys.argv) > 1:
        names = sys.argv[1:]
    else:
        ra = open('src/restart_all.sh').read()
        mm = re.search(r'^for f in ([^;]+); do', ra, re.M)
        names = mm.group(1).split() if mm else []
    rows = []
    for n in names:
        p = n if os.path.exists(n) else os.path.join('src', n)
        if not os.path.exists(p):
            continue
        got = check(p)
        if got:
            rows.append(got)
    print('%-14s %-28s %9s %6s %5s %6s %8s' %
          ('runner', 'list', 'cap', 'budget', 'mem', 'rows', 'ASKABLE'))
    for got in rows:
        if got[5] is None:
            print('%-14s %-28s %9d %6d %5g   (list missing)' % (got[0], got[1], got[2], got[3], got[4]))
            continue
        name, lst, cap, budget, memgb, n, r, ask = got
        flag = '' if ask else '   <- ASKS NOTHING'
        print('%-14s %-28s %9d %6d %5g %6d %8d%s' % (name, lst, cap, budget, memgb, n, ask, flag))
        for k, v in r.items():
            if v:
                print('%-14s %-28s already refused / settled: %s = %d' % ('', '', k, v))


main()
