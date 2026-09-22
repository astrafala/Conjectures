#!/bin/sh
# RETIRED 22 September. The transfer21 vein is read out, and the number I quoted for it was
# wrong in a way worth recording.
#
# I rebuilt this runner's list from the full candidate pool and reported "52 of 52 askable".
# All 52 were already on the ROSTER -- they carry an installed paper. sweep_shard's first skip
# is `if a in roster or a in GHITS: continue' and it is SILENT: no counter, no log line. So the
# runner returned an empty result dict every round while every refusal file said its list was
# clear, and `listcheck.py' agreed, because it too filtered on uniall_hits and not on
# paper-engines. Both are fixed; listcheck now reports this runner as ASKS NOTHING.
#
# The honest state of the vein, with the roster filter applied: 160 transfer21 candidates, 37
# already hits, 89 on the roster, 71 neither -- and only EIGHT of those 71 carry an open
# conjecture. All eight are refused by a cap of 8,000,000, three of them also by memory at
# 6 GB, and a cap of 32,000,000 was measured not to open this family. Nothing here is reachable
# by a setting.
#
# The build_lineset switch was still right: it was verified on 268 shapes and produced A204282
# and A204480, which are models the pair-free build refuses outright. It read the vein out.
# The 78 capped off-roster transfer21 entries, now that uniform.build dispatches transfer21 to
# transfer17's pair-free construction instead of its pair build.
#
# transfer21 was the only caller of transfer17.build, whose vertices are ordered PAIRS of lines
# and which refuses a priori on (alpha+1)^(2W) > cap. Everything else already came through
# uniform to build_pairfree, which has no such refusal. That one test is what refuses all 15 of
# these entries that carry a conjecture, and nothing else refuses any of them.
# (78 capped, 15 of them carrying a conjecture. An earlier note said 120; that was
# transfer17's count, not transfer21's.)
#
# The swap is verified: same terms as the pair build on 243 shapes -- 99 entries and 144 of the
# parameter grid -- zero mismatches, with the state counts differing throughout (65793 against
# 11717 at W=4 K=4), which is what shows the comparison ran.
#
# CHECKED WITH src/listcheck.py, WHICH IS THE POINT. That tool reports, per runner, how many of
# its list each of the three refusal files already refuses AT OR ABOVE this runner's own cap,
# budget and memory. It found this runner asking NOTHING -- 0 of 5 -- and `resrun' asking 5 of
# 33. Five stale lists were found by hand in one night before it existed, the fifth being one I
# had built myself twenty minutes earlier.
cd /home/user/Conjectures/engine
# IDLE BACKOFF (defect 44). A round of this loop that finds work takes minutes -- BUDGET
# alone is 90 seconds or more -- so a round that returns in seconds found nothing, and the
# only thing relaunching it achieves is another interpreter start. Thirteen veins were doing
# exactly that at once: /tmp was wiped by a container restart at 02:00 and by 02:05 the runner
# logs held about twenty-five thousand lines, almost all of them the empty result dict, while
# Phase 5 -- the one job with 1,904 entries of real work left -- wrote nothing for an hour.
# Reading the clock needs nothing from the sweep and so works for every script below, not just
# sweep_shard. Stopping is not retirement: restart_all.sh relaunches this an hour from now,
# which is when a changed engine could have reopened the vein.
for r in 1 2 3 4 5 6 7 8 9 10; do
  _t0=$(date +%s)
  ANUMS_FILE=deep-check/t21cap.txt BUDGET=900 TAG=t21 MEMGB=6 \
    timeout 3000 python3 src/sweep_shard.py 8000000 0 1 >> /tmp/t21_run.log 2>&1
  _rc=$?
  _el=$(( $(date +%s) - _t0 ))
  # DEFECT 52. A round that ends in seconds was read as "nothing left to ask". A round that
  # ends in seconds because the sweep CRASHED ends in seconds too, and said the same thing.
  # bsweep.py died on its first entry with AttributeError on 31 August and sat at 3,376 of
  # 10,632 for three weeks looking like a half-read queue; the moment it was put in a runner
  # the backoff would have called that queue read out. An exit code tells the two apart for
  # nothing: 0 is a clean round, 124 is `timeout' doing its job, anything else is a crash and
  # must never be mistaken for an empty vein.
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- this is a crash, NOT an empty vein; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
