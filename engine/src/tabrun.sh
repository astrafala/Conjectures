#!/bin/sh
# The T(n,k) column and row conjectures on the FULL pool: 1,729 entries carry an
# "Empirical for column k:" block and the sweep had asked about 11 of them, because it walked
# all 399,027 names in A-number order and never recorded the ones it skipped.
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
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
  _t0=$(date +%s)
  for i in 0 1 2 3; do
    TABPOOL=deep-check/tabpool.txt HITS=tabnew_hits_$i.json DONE=tabnew_done_$i.json \
      TABSHARD=$i TABNSHARD=4 BUDGET=30 ROWCAP=1024 ENTRY_BUDGET=90 \
      timeout 1700 python3 src/sweep_table.py 2000000 \
      >> /tmp/tab_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2 3; do
    TMODE=row TABPOOL=deep-check/rowpool.txt HITS=rownew_hits_$i.json \
      DONE=rownew_done_$i.json TABSHARD=$i TABNSHARD=4 BUDGET=30 ROWCAP=1024 \
      ENTRY_BUDGET=90 \
      timeout 1700 python3 src/sweep_tablerow.py 2000000 >> /tmp/row_$i.log 2>&1 &
  done
  wait
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
