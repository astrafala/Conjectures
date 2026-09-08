#!/bin/sh
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/tails2.txt BUDGET=150 SCUT=9000 \
      timeout 1700 python3 src/ordtails.py 8000000 $i 3 >> /tmp/tails2_$i.log 2>&1 &
  done
  wait
done
