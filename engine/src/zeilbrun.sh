#!/bin/sh
# Boundary-corrected creative telescoping. The machinery was written in August, run once, and
# never given a runner -- zeilb-0.json and zeilb-1.json are dated 30 August and nothing has
# asked it anything since. Its own recorded skips are stale: 19 entries were refused with
# "SympifyError ... could not parse 'D-finite with recurrence'" and `prove_rec.parse_conj`
# reads every one of them now.
#
# Shards 3, 4 and 5 so `harvest.py`'s zeilb-[0-9].json glob picks the results up, and so the
# August files' own `done` set does not suppress the re-ask.
#
# PER is the per-entry alarm and must stay well under the timeout -- defect 25.
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
  for i in 3 4 5; do
    RES=zeilb-$i.json SHARD=$((i-3)) NSHARD=3 PER=240 MAXORDER=3 \
      timeout 1700 python3 src/zeilb_run.py >> /tmp/zeilb_$i.log 2>&1 &
  done
  wait
  # the shards are progress and are gitignored; harvest installs from zeilb-[0-9].json, so
  # they are folded into the tracked zeilb-9.json after each wave
  python3 src/mergezeilb.py >> /tmp/zeilb_merge.log 2>&1
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
