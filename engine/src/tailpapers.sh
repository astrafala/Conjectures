#!/bin/sh
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6; do
  for i in 0 1 2 3; do
    PAPER_DATE='8 September 2026' timeout 1700 python3 src/build_tails.py $i 4 \
      >> /tmp/tailpapers_$i.log 2>&1 &
  done
  wait
done
