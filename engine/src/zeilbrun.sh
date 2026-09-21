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
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
