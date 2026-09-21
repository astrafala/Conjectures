#!/bin/sh
# "a(n) is a polynomial of degree 26 for n>13" -- seven entries whose claim names a degree and
# no coefficients, so nothing here read them. It is two linear recurrences: (z-1)^(d+1) must
# annihilate and (z-1)^d must not. The big degrees (127, 80) are slow, hence a runner.
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
  ANUMS_FILE=deep-check/degree.txt BUDGET=150 MEMGB=6 ALARMCAP=900 \
    timeout 1700 python3 src/sweep_degree.py 400000 0 1 >> /tmp/deg.log 2>&1
  sleep 5
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
