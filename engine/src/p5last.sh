#!/bin/sh
# The last transfer22 models: 65,536 to 1,048,576 states, whose BUILD alone runs past two
# minutes. Given a budget large enough to finish one, and left to run.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
  for i in 0 1 2; do
    P5CAP=8000000 timeout 1700 python3 src/dc_phase5.py $i 3 900 >> /tmp/p5last_$i.log 2>&1 &
  done
  wait
done
