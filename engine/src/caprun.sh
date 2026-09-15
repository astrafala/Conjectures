#!/bin/sh
# The 688 off-roster entries of deep-check/capped.txt, re-asked ONE shard at a time.
#
# These are the entries `sweep_shard` refused as "state space > cap", and the refusal list has
# never been re-asked since the engines changed. Four concurrent shards over it died three times
# running: `uniform.build` allocates toward the cap, and four such processes plus the two dozen
# standing runners exceed the container, so the kernel kills whichever it likes. One shard with
# a 1.5 GB address-space limit fails the one entry instead of the whole run.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  ANUMS_FILE=deep-check/capped2.txt BUDGET=90 TAG=cap2 MEMGB=1.5 \
    timeout 1700 python3 src/sweep_shard.py 2000000 0 1 >> /tmp/cap_run.log 2>&1
done
