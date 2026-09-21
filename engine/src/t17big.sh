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
