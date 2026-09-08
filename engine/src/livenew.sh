#!/bin/sh
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2 3 4 5; do
    LSHARD=$i LNSHARD=6 timeout 1700 python3 src/livenew.py deep-check/new.txt \
      >> /tmp/livenew_$i.log 2>&1 &
  done
  wait
done
