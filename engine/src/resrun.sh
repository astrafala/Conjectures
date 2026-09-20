#!/bin/sh
# The 33 entries `uniall_done.json' calls finished that were never decided.
#
# `sweep_shard' records a build timeout, a terms timeout, an annihilation timeout, a build
# failure and a terms failure exactly as it records a settlement: `done.add(a)' and a counter
# that lives only as long as the process. Nothing durable is written, so an entry that merely
# ran out of BUDGET is marked done forever and cannot be told apart from one the sweep actually
# decided -- uniall_caps.json at least records that a cap was hit.
#
# These 33 are what is left after removing, from the 3,579 done-and-off-roster entries, every
# one that is capped, is a hit, carries no parsable conjecture, is not open, or belongs to a
# withdrawn engine. They are open, conjectural, live-engined and were never capped, so whatever
# ended them left no record at all. 20 are ca2d, 8 transfer96.
#
# Asked with BUDGET=1800 rather than the usual 40-600: if the reason was the clock, this is what
# finds out, and if it was not, the reason will now be written down.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  ANUMS_FILE=deep-check/residue.txt BUDGET=1800 TAG=res MEMGB=5 \
    timeout 2400 python3 src/sweep_shard.py 2000000 0 1 >> /tmp/res_run.log 2>&1
done
