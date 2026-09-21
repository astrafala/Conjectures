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
#
# THE CAP THIS ASKS AT WAS THE CAP THAT ALREADY REFUSED THE LIST. 727 of realcap2.txt's 734
# entries, and all 255 of realcap.txt's, carry a row in uniall_caps.json saying they were
# refused at 2,000,000 or more -- and both runners asked at exactly 2,000,000. A refusal is
# only meaningful next to the cap it was made at, and re-asking at the same cap is not a
# question, it is the same answer again. Raised to 8,000,000: measured, that is a NEW question
# for 375 of realcap2's 603 open entries and for 242 of realcap's 243.
#
# The memory is deliberately NOT raised with it. Three shards at MEMGB=5 already reach the
# whole container if they all peak; an entry whose state space needs more than that at the new
# cap will raise MemoryError and be recorded honestly, which is information rather than a loss.
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
  _pids=""
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/realcap2.txt BUDGET=600 TAG=rcap2 MEMGB=5 \
      timeout 2100 python3 src/sweep_shard.py 8000000 $i 3 >> /tmp/cap_run.log 2>&1 &
    _pids="$_pids $!"
  done
  # `wait' with NO OPERANDS is specified to return zero, always -- so reading $? after it
  # tells you nothing about the shards, and the defect-52 check was inert in every runner
  # that launches more than one. Waiting on each pid in turn is the portable way to get a
  # status back. 124 is `timeout' doing its job, not a crash.
  _rc=0
  for _p in $_pids; do
    if wait "$_p"; then :; else _s=$?; [ $_s -ne 124 ] && _rc=$_s; fi
  done
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
