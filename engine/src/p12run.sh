#!/bin/sh
cd /home/user/Conjectures/engine
for round in 1 2 3 4 5 6 7 8; do
  timeout 1700 python3 src/dc_phase12.py 12 4 0 1 >> /tmp/p12.log 2>&1
done
echo P12_DONE >> /tmp/p12.log
