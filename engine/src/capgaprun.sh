#!/bin/sh
# The 145 entries that carry an open conjecture, were refused by a CAP, and are on no other
# runner's list.
#
# Found by measuring the whole capped population against every runner's settings rather than
# by looking at any one list. uniall_caps.json holds 3,366 rows; 2,367 are off-roster and
# unsettled; 1,255 of those carry no parsable recurrence at all and 117 are already settled,
# which leaves 995 real questions, 956 of them not also blocked by the clock, memory or a run
# of deaths. Of those 956: 480 can be asked by some sweep_shard runner right now, 165 are on a
# runner's list but blocked by that runner's own cap or budget, and 311 are on no sweep_shard
# list at all. 145 of the 311 are askable at 8,000,000.
#
# 142 of the 145 carry a cap row of 200,000 -- they were refused at a cap forty times smaller
# than the one this asks at, and nothing has asked them since. That is the same fact as the
# other stale lists tonight, one level up: not a list asked at the wrong setting, but a
# population no list covers.
#
# Checked with src/listcheck.py after writing, which is the point of having it.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10; do
  _t0=$(date +%s)
  _pids=""
  for i in 0 1; do
    ANUMS_FILE=deep-check/capgap.txt BUDGET=900 TAG=capgap MEMGB=5 \
      timeout 3000 python3 src/sweep_shard.py 8000000 $i 2 >> /tmp/capgap_$i.log 2>&1 &
    _pids="$_pids $!"
  done
  # `wait' with no operands always returns zero, so per-pid is the only way to see a status.
  _rc=0
  for _p in $_pids; do
    if wait "$_p"; then :; else _s=$?; [ $_s -ne 124 ] && _rc=$_s; fi
  done
  _el=$(( $(date +%s) - _t0 ))
  # DEFECT 52. A round ending in seconds because the sweep CRASHED looks exactly like a round
  # ending in seconds because there was nothing to ask. 0 is clean, 124 is `timeout' doing its
  # job, anything else is a crash and must never be read as an empty vein.
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- this is a crash, NOT an empty vein; stopping"
    break
  fi
  # IDLE BACKOFF (defect 44). BUDGET alone is 900s, so a round back in seconds found nothing.
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out at these settings, stopping"
    break
  fi
done
