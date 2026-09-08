#!/bin/sh
# The 1,246 entries an engine already reads that carry an unsettled conjecture and are not in
# the roster. Built by intersecting the clone's conjecture wording with what uniform.read
# accepts, so it cannot go stale the way a hand-built pool does.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/readable-unsettled-trimmed.txt BUDGET=150 \
      timeout 1700 python3 src/sweep_shard.py 8000000 $i 3 >> /tmp/rd_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/readable-unsettled-trimmed.txt BUDGET=150 \
      timeout 1700 python3 src/sweep_ordwhole.py 8000000 $i 3 >> /tmp/rdo_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/readable-unsettled-trimmed.txt BUDGET=200 SCUT=20000 \
      timeout 1700 python3 src/ordtails.py 8000000 $i 3 >> /tmp/rdt_$i.log 2>&1 &
  done
  wait
done
