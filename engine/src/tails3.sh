#!/bin/sh
# The order-line tail sweep, re-aimed. tails2.txt was exhausted (382 proved); this runs the
# 136 order-line entries never tried, then re-asks the 191 refused at a cap -- a cap is a
# setting, not a wall, and every earlier raise recovered real results.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/tails3.txt BUDGET=200 SCUT=20000 \
      timeout 900 python3 src/ordtails.py 40000000 $i 3 >> /tmp/tails3_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/tails-retry.txt BUDGET=300 SCUT=30000 \
      timeout 1200 python3 src/ordtails.py 60000000 $i 3 >> /tmp/tails3r_$i.log 2>&1 &
  done
  wait
done
