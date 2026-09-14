#!/bin/sh
# The Galebach coordination sequences: 379 entries, every one with a conjectured recurrence
# and a name no engine read until galcoord came into service. The chain is expensive and MOST
# of them refuse -- the distance is not a max of affine pieces on the majority of tilings --
# so this runs slowly and forever rather than in a batch.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1; do
    ANUMS_FILE=deep-check/galcoord.txt BUDGET=400 TAG=gal \
      timeout 1700 python3 src/sweep_shard.py 400000 $i 2 >> /tmp/gal_$i.log 2>&1 &
  done
  wait
done
