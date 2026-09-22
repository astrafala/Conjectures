#!/bin/sh
# The 1,110 entries defect 69 freed: they carry a conjecture and were refused at a cap of
# 2,000,000 by `np2run', whose refusal path then marked them `done' -- which is global and
# permanent, so they were excluded from every runner at every cap for ever. They are not hard:
# 21 of 25 build at 2,000,000 with state counts of 5, 20, 40, ..., 2560, and 29 of 40 put
# through the sweep's whole sequence prove outright.
#
# Asked here directly rather than waiting for the main sweep to reach them: the main sweep
# spends most of a round walking skip lists, and at CAP=2,000,000 the new cap skip would pass
# over these anyway, since that is exactly the cap their rows record. 8,000,000 is above every
# one of those rows, so the skip lets them through.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
  _t0=$(date +%s)
  _pids=""
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/cap-freed.txt BUDGET=300 TAG=freed MEMGB=5 \
      timeout 1700 python3 src/sweep_shard.py 8000000 $i 3 >> /tmp/freed_$i.log 2>&1 &
    _pids="$_pids $!"
  done
  _rc=0
  for _p in $_pids; do
    if wait "$_p"; then :; else _s=$?; [ $_s -ne 124 ] && _rc=$_s; fi
  done
  _el=$(( $(date +%s) - _t0 ))
  # defect 52: a crash ends in seconds and so does an empty vein; the exit code tells them apart
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- a crash, NOT an empty vein; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- the freed list is read out, stopping"
    # defect 65: say WHY this stopped, so restart_all does not undo an idle backoff.
    date +%s > "/tmp/$(basename "$0").readout"
    break
  fi
done
