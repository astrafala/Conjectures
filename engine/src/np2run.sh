#!/bin/sh
# The REBUILT name-readable pool. deep-check/namepool.txt held 1,446 entries and was fully
# exhausted -- every one left in it was already on the roster. Rebuilt from the clone on the
# same criterion (off the roster, a readable recurrence or closed form, and a name uniform.read
# models) it is 1,727 entries, 866 of which were never in the old file. See IDEAS section AE.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2 3; do
    ANUMS_FILE=deep-check/namepool2.txt BUDGET=90 TAG=np2 \
      timeout 1700 python3 src/sweep_shard.py 2000000 $i 4 >> /tmp/np2_$i.log 2>&1 &
  done
  wait
done
