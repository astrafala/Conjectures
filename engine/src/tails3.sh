#!/bin/sh
# The order-line tail sweep, re-aimed. tails2.txt was exhausted (382 proved); this runs the
# 136 order-line entries never tried, then re-asks the 191 refused at a cap -- a cap is a
# setting, not a wall, and every earlier raise recovered real results.
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
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  _t0=$(date +%s)
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/tails3.txt BUDGET=200 SCUT=20000 \
      timeout 900 python3 src/ordtails.py 40000000 $i 3 >> /tmp/tails3_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/tails-retry.txt BUDGET=300 SCUT=30000 \
      timeout 1200 python3 src/ordtails.py 60000000 $i 3 >> /tmp/tails3r_$i.log 2>&1 &
  done
  wait
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
