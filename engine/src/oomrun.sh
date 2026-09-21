#!/bin/sh
# The entries the CONTAINER refused, asked with memory the container can actually give.
#
# uniall_oom.json exists because until today an out-of-memory was flattened to None by
# uniform.build and read by sweep_shard as "state space > cap" -- a model too big for a cap it
# had never reached (STATE.md defects 36, 39, 41). These are the entries that fact was hiding.
# Every one of them BUILT; what exhausted the address space was lumpauto.lump inside
# uniform.threshold, which cannot be skipped: the annihilation test runs until S+1 consecutive
# residuals vanish, so its cost is governed by the state count and the merge is what makes it
# finishable at all.
#
# They failed at 5, 6 and 7 GB while 28 runners were up. One shard at MEMGB=11 on a 16 GB
# container is the honest test of whether the machine or the mathematics is the limit. A death
# now leaves an in-flight marker, is recorded, and is stepped past instead of looping.
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
  ANUMS_FILE=deep-check/oomlist.txt BUDGET=1500 TAG=oom MEMGB=11 \
    timeout 2400 python3 src/sweep_shard.py 2000000 0 1 >> /tmp/oom_run.log 2>&1
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
