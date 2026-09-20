#!/bin/sh
# The off-roster capped entries that actually CARRY a conjecture, in THREE shards.
#
# This used to run deep-check/capped2.txt -- every off-roster row of uniall_caps.json -- at
# MEMGB=1.5, and produced 0 proofs in 546 entries. Both halves were wrong: 1,255 of the 2,311
# rows carry no parsable conjecture at all, and 1.5 GB was the tightest memory budget in the
# project aimed at the population most likely to need memory, where until today every
# out-of-memory came back wearing the cap's name (IDEAS section AP, STATE.md defects 36-41).
#
# deep-check/realcap2.txt is the 734 entries that carry a conjecture and whose engine is not
# withdrawn, less the 255 latpoly/ca2d of realcap.txt. It has produced eight proofs.
#
# THREE shards, not one. On a single shard it managed one entry in an hour against 28 standing
# runners, which is 594 hours for what is left; the entries here are large by construction and
# each one holds its shard for minutes. Three shards write three sets of files and cannot
# overwrite each other -- that is the whole reason sweep_shard takes a shard index -- so the
# only cost is memory, and 5 GB each is chosen to fit three of them beside the rotation.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/realcap2.txt BUDGET=600 TAG=rcap2 MEMGB=5 \
      timeout 1700 python3 src/sweep_shard.py 2000000 $i 3 >> /tmp/cap_run.log 2>&1 &
  done
  wait
done
