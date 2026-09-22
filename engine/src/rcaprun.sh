#!/bin/sh
# The 255 capped off-roster entries whose engine's capped population is real in full: 133
# `latpoly' and 122 `ca2d' (IDEAS section AP). Sibling of caprun.sh, which takes the other 734.
#
# Split in two rather than run as one list because these two engines are the ones where every
# capped entry carries a conjecture, and a runner that finishes is worth more than a runner that
# is still in its first tenth. Its first five entries gave two proofs.
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
  ANUMS_FILE=deep-check/realcap.txt BUDGET=600 TAG=rcap MEMGB=6 \
    timeout 2100 python3 src/sweep_shard.py 8000000 0 1 >> /tmp/rcap_run.log 2>&1
  _rc=$?
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
    # DEFECT 65. The backoff and the restarter were fighting, and the restarter won
    # once a turn: `restart_all.sh' relaunches every runner that is not currently up,
    # so a vein that had correctly stopped itself as read out came straight back. With
    # 33 runners doing that, the container reached a load average of 46 on 4 cores and
    # every wall-clock BUDGET was worth a fraction of itself (defect 64). The marker
    # says "this stopped because it had nothing to do", and restart_all honours it for
    # an hour -- long enough to stop the churn, short enough that a changed engine or a
    # widened pool is picked up on the next hour's firing. A CRASH writes no marker, so
    # a crashed runner is still restarted at once, which is the distinction defect 52
    # went to the trouble of making.
    date +%s > "/tmp/$(basename "$0").readout"
    break
  fi
done
