#!/bin/sh
# The 25 capped `transfer17' entries at alpha=3, W=9 -- 262,144 rows, the expensive end of the
# vein t17run.sh reads. Sibling of that runner; see its header for why the split exists.
#
# ONE shard rather than three: at 262,144 rows the memory, not the CPU, is what limits how
# many can run at once.
#
# BUDGET=900, and it started at 2400. Forty minutes is longer than this container has ever
# lived between restarts, so that budget could not complete an entry -- it only guaranteed the
# shard would be killed mid-build for ever, which is what it did. A251844 was still building
# after eighteen minutes, so fifteen will still cut off most of these; the difference is that
# since defect 49 a build that runs out of budget is NAMED in uniall_tmo.json with the budget
# it failed under, instead of being counted anonymously in the why file (defect 40). That
# turns a silence into a list to re-ask on a quieter machine.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  _t0=$(date +%s)
  ANUMS_FILE=deep-check/t17big.txt BUDGET=900 TAG=t17b MEMGB=7 \
    timeout 3000 python3 src/sweep_shard.py 8000000 0 1 >> /tmp/t17b.log 2>&1
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
