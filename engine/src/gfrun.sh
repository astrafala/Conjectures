#!/bin/sh
# The conjectured-generating-function vein, on the full 1,328-entry pool rebuilt from the
# clone rather than the 135-entry snapshot list the sweep used to read.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2 3; do
    BUDGET=120 CAP=400000 timeout 1700 python3 src/sweep_gfonly.py $i 4 \
      >> /tmp/gf_$i.log 2>&1 &
  done
  wait
done
