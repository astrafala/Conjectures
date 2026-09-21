#!/bin/sh
# Accumulate the transfer21 line-set verification across container restarts. Two earlier
# attempts died with nothing kept -- one on a MemoryError, one on a restart that wiped /tmp --
# and the sample has to reach the 243 shapes this vein was held to before the dispatch can be
# switched. t21check.py records each entry as it goes and skips what is already recorded.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  _t0=$(date +%s)
  CAP=200000 BUDGET=240 timeout 1700 python3 src/t21check.py >> /tmp/t21ck.log 2>&1
  _rc=$?
  _el=$(( $(date +%s) - _t0 ))
  # DEFECT 52. A round ending in seconds because the sweep CRASHED looks exactly like a round
  # ending in seconds because there was nothing to ask. bsweep.py died on its first entry on
  # 31 August and sat at 3,376 of 10,632 for three weeks looking like a half-read queue.
  # 0 is a clean round, 124 is `timeout' doing its job, anything else is a crash.
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- this is a crash, NOT an empty vein; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- every candidate recorded, stopping"
    break
  fi
done
