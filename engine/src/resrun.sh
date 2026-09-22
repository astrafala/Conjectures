#!/bin/sh
# The 33 entries `uniall_done.json' calls finished that were never decided.
#
# `sweep_shard' records a build timeout, a terms timeout, an annihilation timeout, a build
# failure and a terms failure exactly as it records a settlement: `done.add(a)' and a counter
# that lives only as long as the process. Nothing durable is written, so an entry that merely
# ran out of BUDGET is marked done forever and cannot be told apart from one the sweep actually
# decided -- uniall_caps.json at least records that a cap was hit.
#
# These 33 are what is left after removing, from the 3,579 done-and-off-roster entries, every
# one that is capped, is a hit, carries no parsable conjecture, is not open, or belongs to a
# withdrawn engine. They are open, conjectural, live-engined and were never capped, so whatever
# ended them left no record at all. 20 are ca2d, 8 transfer96.
#
# Asked with BUDGET=1800 rather than the usual 40-600: if the reason was the clock, this is what
# finds out, and if it was not, the reason will now be written down.
#
# CHECKED WITH src/listcheck.py, WHICH IS THE POINT. That tool reports, per runner, how many of
# its list each of the three refusal files already refuses AT OR ABOVE this runner's own cap,
# budget and memory. It found this runner asking NOTHING -- 0 of 5 -- and `resrun' asking 5 of
# 33. Five stale lists were found by hand in one night before it existed, the fifth being one I
# had built myself twenty minutes earlier.
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
  ANUMS_FILE=deep-check/residue.txt BUDGET=1800 TAG=res MEMGB=5 \
    timeout 6000 python3 src/sweep_shard.py 8000000 0 1 >> /tmp/res_run.log 2>&1
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
    break
  fi
done
