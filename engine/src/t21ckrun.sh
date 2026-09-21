#!/bin/sh
# Accumulate the transfer21 line-set verification across container restarts. Two earlier
# attempts died with nothing kept -- one on a MemoryError, one on a restart that wiped /tmp --
# and the sample has to reach the 243 shapes this vein was held to before the dispatch can be
# switched. t21check.py records each entry as it goes and skips what is already recorded.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  _t0=$(date +%s)
  CAP=200000 BUDGET=240 timeout 1700 python3 src/t21check.py >> /tmp/t21ck.log 2>&1
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- every candidate recorded, stopping"
    break
  fi
done
