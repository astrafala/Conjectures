#!/bin/sh
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
    timeout 3000 python3 src/sweep_shard.py 2000000 0 1 >> /tmp/t21_run.log 2>&1
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
