#!/bin/sh
# The 255 capped off-roster entries whose engine's capped population is real in full: 133
# `latpoly' and 122 `ca2d' (IDEAS section AP). Sibling of caprun.sh, which takes the other 734.
#
# Split in two rather than run as one list because these two engines are the ones where every
# capped entry carries a conjecture, and a runner that finishes is worth more than a runner that
# is still in its first tenth. Its first five entries gave two proofs.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  ANUMS_FILE=deep-check/realcap.txt BUDGET=600 TAG=rcap MEMGB=6 \
    timeout 1700 python3 src/sweep_shard.py 2000000 0 1 >> /tmp/rcap_run.log 2>&1
done
