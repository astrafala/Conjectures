#!/bin/sh
# The 255 capped off-roster entries whose engine's capped population is real in full: 133
# `latpoly' and 122 `ca2d' (IDEAS section AP). Sibling of caprun.sh, which takes the other 734.
#
# Split in two rather than run as one list because these two engines are the ones where every
# capped entry carries a conjecture, and a runner that finishes is worth more than a runner that
# is still in its first tenth. Its first five entries gave two proofs.
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
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  _t0=$(date +%s)
  ANUMS_FILE=deep-check/realcap.txt BUDGET=600 TAG=rcap MEMGB=6 \
    timeout 1700 python3 src/sweep_shard.py 2000000 0 1 >> /tmp/rcap_run.log 2>&1
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
