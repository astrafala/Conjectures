#!/bin/sh
# The 25 capped `transfer17' entries at alpha=3, W=9 -- 262,144 rows, the expensive end of the
# vein t17run.sh reads. Sibling of that runner; see its header for why the split exists.
#
# A251844 was still building after eighteen minutes, so a 900-second budget would record every
# one of these as a timeout -- and a timeout is a count in the why file, not a named entry
# (STATE.md defect 40), so the whole group would become unidentifiable. BUDGET=2400 with a
# 3000-second timeout gives each one a real chance to finish, and ONE shard rather than three
# because at 262,144 rows the memory, not the CPU, is what limits how many can run at once.
#
# If these still do not build, that is a fact about this shape and belongs in IDEAS AP.5 --
# but it will be a fact, not a budget.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  _t0=$(date +%s)
  ANUMS_FILE=deep-check/t17big.txt BUDGET=2400 TAG=t17b MEMGB=7 \
    timeout 3000 python3 src/sweep_shard.py 8000000 0 1 >> /tmp/t17b.log 2>&1
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
