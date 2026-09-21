#!/bin/sh
# The 80 capped off-roster `transfer17' entries that carry a parsable conjectured recurrence.
#
# IDEAS AP.5 left this as a question rather than a target: transfer17 already HAS the merged
# pair-free build, so why do 82 of its entries still cap? Asked directly, eight of eight cap at
# 2,000,000, each taking 12-30 seconds to get there -- so this is real construction reaching the
# limit, not the a-priori (alpha+1)^(2W) refusal that transfer21's entries hit. And 79 of the 80
# had only ever been asked at 2,000,000.
#
# A204606 (alpha=2, W=9) BUILDS at 8,000,000. That is the whole case for this runner: the
# population was never refused by mathematics, only by the one cap every sweep happened to use.
#
# SPLIT BY ROW SPACE, because the 80 are not one population. Their shapes:
#
#     alpha=2 W=9    19,683 rows     1
#     alpha=3 W=6     4,096 rows     1
#     alpha=3 W=7    16,384 rows    26
#     alpha=3 W=8    65,536 rows    27
#     alpha=3 W=9   262,144 rows    25
#
# A204606 (19,683 rows) built in 215 seconds; A251844 (262,144 rows) was still building after
# eighteen minutes, which is past this runner's whole budget. Left in one list the 25 largest
# would hold the shards for the entire night and the 55 cheap ones would never be reached --
# and a build that runs out of BUDGET is recorded as a COUNT in the why file, not per entry,
# so they would not even be identifiable afterwards (STATE.md defect 40). This runner takes
# the 55 that fit; t17big.sh takes the 25 that do not, with a budget that suits them.
#
# MEMGB=5 and a 900-second budget: the build that succeeded took 215s and about 1.8 GB.
# BUDGET=420, not 900. The container restarts on no schedule and has been as close as
# eleven minutes apart, so a 900-second budget is longer than a generation: all three shards
# sat in a restart loop on A252318, A252421 and A252146, each starting the same entry again
# every time, recording nothing, while 35 entries of this list had never been asked at
# 8,000,000 at all. Defect 47's stamp is what makes the loop correct rather than destructive --
# it re-asks instead of retiring -- but correct is not the same as progressing.
#
# Seven minutes fits inside almost every generation seen, and since defect 49 a build that
# runs out of budget is NAMED in uniall_tmo.json with the budget it failed under. So the
# entries this cuts off become a list to re-ask at a longer budget on a quieter machine,
# rather than the silence they were before.
# TWO shards at 7 GB, not three at 5. Memory is what refuses this list, not the cap and not
# the clock: of its 55 entries, 11 are proved and 13 exceeded MEMGB=5 -- more than were refused
# for any other reason. Three shards at 5 GB already claim 15 GB on a 15 GB machine, so the
# only way to raise the limit is to run fewer of them.
#
# This costs a third of the parallelism and re-opens 13 entries, because sweep_shard skips an
# out-of-memory row only while MEMGB is no larger than the limit it failed under (defect 48) --
# so raising the limit releases them with no bookkeeping at all. t17big.sh is stopped to pay
# for it: its 25 entries have produced nothing in three hours while holding 7 GB, and moving
# memory from the population that has produced nothing to the one that has produced eleven is
# the whole of the argument.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  _t0=$(date +%s)
  for i in 0 1; do
    ANUMS_FILE=deep-check/t17small.txt BUDGET=420 TAG=t17c MEMGB=7 \
      timeout 1700 python3 src/sweep_shard.py 8000000 $i 2 >> /tmp/t17c_$i.log 2>&1 &
  done
  wait
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
