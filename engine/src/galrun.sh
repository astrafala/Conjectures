#!/bin/sh
# The Galebach coordination sequences: 379 entries, every one with a conjectured recurrence
# and a name no engine read until galcoord came into service. The chain is expensive and MOST
# of them refuse -- the distance is not a max of affine pieces on the majority of tilings --
# so this runs slowly and forever rather than in a batch.
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
for r in 1 2 3 4 5 6 7 8; do
  _t0=$(date +%s)
  for i in 0 1; do
    ANUMS_FILE=deep-check/galcoord.txt BUDGET=400 TAG=gal \
      timeout 1700 python3 src/sweep_shard.py 400000 $i 2 >> /tmp/gal_$i.log 2>&1 &
  done
  wait
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
