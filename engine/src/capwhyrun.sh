#!/bin/sh
# Audit uniall_caps.json. 2,759 rows, each one a rebuild, so it is sharded and resumable:
# the first run was killed by a restart and lost every row it had.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  _t0=$(date +%s)
  _pids=""
  for i in 0 1 2 3 4 5; do
    CWSHARD=$i CWNSHARD=6 BUDGET=60 timeout 1700 python3 src/capwhy.py \
      >> /tmp/capwhy_$i.log 2>&1 &
    _pids="$_pids $!"
  done
  _rc=0
  for _p in $_pids; do
    if wait "$_p"; then :; else _s=$?; [ $_s -ne 124 ] && _rc=$_s; fi
  done
  _el=$(( $(date +%s) - _t0 ))
  # defect 52: a round ending in seconds because the script CRASHED looks exactly like a
  # round ending in seconds because there is nothing left. The exit code tells them apart.
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- a crash, NOT an empty queue; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- every cap row audited, stopping"
    # defect 65: say WHY this stopped, so restart_all does not undo an idle backoff.
    date +%s > "/tmp/$(basename "$0").readout"
    break
  fi
done
