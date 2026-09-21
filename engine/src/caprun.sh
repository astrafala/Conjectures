#!/bin/sh
# The off-roster capped entries that actually CARRY a conjecture, in THREE shards.
#
# This used to run deep-check/capped2.txt -- every off-roster row of uniall_caps.json -- at
# MEMGB=1.5, and produced 0 proofs in 546 entries. Both halves were wrong: 1,255 of the 2,311
# rows carry no parsable conjecture at all, and 1.5 GB was the tightest memory budget in the
# project aimed at the population most likely to need memory, where until today every
# out-of-memory came back wearing the cap's name (IDEAS section AP, STATE.md defects 36-41).
#
# deep-check/realcap2.txt is the 734 entries that carry a conjecture and whose engine is not
# withdrawn, less the 255 latpoly/ca2d of realcap.txt. It has produced eight proofs.
#
# THREE shards, not one. On a single shard it managed one entry in an hour against 28 standing
# runners, which is 594 hours for what is left; the entries here are large by construction and
# each one holds its shard for minutes. Three shards write three sets of files and cannot
# overwrite each other -- that is the whole reason sweep_shard takes a shard index -- so the
# only cost is memory, and 5 GB each is chosen to fit three of them beside the rotation.
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
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/realcap2.txt BUDGET=600 TAG=rcap2 MEMGB=5 \
      timeout 2100 python3 src/sweep_shard.py 2000000 $i 3 >> /tmp/cap_run.log 2>&1 &
  done
  wait
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
