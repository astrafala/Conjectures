#!/bin/sh
# Papers for the generating-function vein, eight shards. Only entries the live re-check has
# confirmed still open are built.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2 3 4 5 6 7; do
    PAPER_DATE='8 September 2026' timeout 1700 python3 src/build_gfdef.py $i 8 \
      >> /tmp/gd_$i.log 2>&1 &
  done
  wait
done
