#!/bin/sh
# The 80 capped off-roster `transfer17' entries that carry a parsable conjectured recurrence.
#
# IDEAS AP.5 left this as a question rather than a target: transfer17 already HAS the merged
# pair-free build, so why do 82 of its entries still cap? Asked directly, eight of eight cap at
# 2,000,000, each taking 12-30 seconds to get there -- so this is real construction reaching the
# limit, not the a-priori (alpha+1)^(2W) refusal that transfer21's entries hit. And 79 of the 80
# had only ever been asked at 2,000,000.
#
# A204606 (alpha=2, W=9) BUILDS at 8,000,000. That is the whole case for this runner: the
# population was never refused by mathematics, only by the one cap every sweep happened to use.
#
# MEMGB=5 and a 900-second budget because the build that succeeded took seven minutes on a
# loaded machine and about 1.8 GB. Three shards, so the 80 are read in a night rather than a
# week; sweep_shard's shard index keeps their files apart.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  _t0=$(date +%s)
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/t17conj.txt BUDGET=900 TAG=t17c MEMGB=5 \
      timeout 1700 python3 src/sweep_shard.py 8000000 $i 3 >> /tmp/t17c_$i.log 2>&1 &
  done
  wait
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
