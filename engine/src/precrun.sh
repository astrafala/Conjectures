#!/bin/sh
# Conjectured P-RECURSIVE recurrences: 459 open pool entries, 380 of them readable, and
# `ratrec` reads constant coefficients only so none was ever asked about. Where the entry
# states its generating function as fact and that function is algebraic, `holonomic` turns the
# claim into an identity of functions and settles it symbolically.
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
    ANUMS_FILE=deep-check/prec.txt ALARM=240 MEMGB=5 \
      timeout 1700 python3 src/sweep_prec.py $i 2 >> /tmp/prec_$i.log 2>&1 &
  done
  wait
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
