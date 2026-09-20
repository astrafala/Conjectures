#!/bin/sh
# The off-roster capped entries that actually CARRY a conjecture, re-asked one shard at a time.
#
# This used to run deep-check/capped2.txt -- every off-roster entry in uniall_caps.json -- at
# MEMGB=1.5, and it produced 0 proofs in 546 entries. Both halves of that were wrong:
#
#   * 1,255 of the 2,311 rows in the caps file carry no parsable conjecture at all. `sweep_shard'
#     records "state space > cap" against any entry whose NAME an engine parses, and one of its
#     two cap points fires before the recurrence is looked for. Asking them proves nothing
#     because there is nothing in them to prove (IDEAS section AP).
#   * 1.5 GB was chosen when four concurrent shards were dying. One shard does not need it, and
#     until today `uniform.build' flattened MemoryError to None, which `sweep_shard' read as the
#     cap refusing -- so the tightest memory budget in the project was aimed at the population
#     most likely to need memory, and every failure came back wearing the cap's name.
#
# deep-check/realcap2.txt is the 734 entries that carry a conjecture and whose engine is not
# withdrawn, less the 255 latpoly/ca2d of realcap.txt. The first five entries of that sibling
# list gave two proofs, A184710 at S=353 and A188239 at S=41 -- both filed as too big for a cap
# of two million.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  ANUMS_FILE=deep-check/realcap2.txt BUDGET=600 TAG=rcap2 MEMGB=6 \
    timeout 1700 python3 src/sweep_shard.py 2000000 0 1 >> /tmp/cap_run.log 2>&1
done
