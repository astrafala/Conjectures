#!/bin/sh
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1 2; do
    P5CAP=8000000 timeout 1700 python3 src/dc_phase5.py $i 3 240 >> /tmp/p5cap_$i.log 2>&1 &
  done
  wait
done
echo P5CAP_DONE >> /tmp/p5cap.log
