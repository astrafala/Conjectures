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
#
# A LIST MUST BE CHECKED AGAINST ALL THREE SETTINGS, NOT ONE. t17small.txt was rebuilt as the
# 57 transfer17 entries that are capped, unsettled and carry an open conjecture -- checked
# against the CAP and against memory, and I called 36 of them a new question. The runner then
# reported 32 skips of "out of budget on an earlier pass": 31 of the 57 carry a uniall_tmo.json
# row of exactly 420, which is this runner's own budget. Only 16 were askable at all.
#
# A sweep has three refusals and a list is only new against all three. Raised to 550, at which
# nothing on the list is budget-skipped (the worst row is 500) and 36 become askable; the other
# 21 are refused by the cap at 8,000,000 and need a bigger one, not a longer clock.
#
# 550 and not more because BUDGET is per phase: 3*550 = 1650 must stay under `timeout 1700'
# or a slow entry is killed with its marker on disk and recorded as something it is not.
#
# BUDGET DOUBLED, AND THE OUTER TIMEOUT WITH IT. Measured: the clock is what holds this vein --
# "out of budget on an earlier pass" is the dominant refusal across every runner -- and the two
# budget raises made so far are the only setting changes that have produced anything. tmorun
# 300 -> 500 gave A253494; t17run 420 -> 550 gave A252102, A252128 and A252145. Every cap raise
# has given nothing.
#
# The raise that fits inside the old timeout was 8 percent, which will not convert an entry that
# already exhausted the budget; the two that paid were 67 and 31 percent. So the outer timeout
# rises too, and it must, because BUDGET is per phase: 3*BUDGET has to stay under it or an entry
# is killed with its marker on disk and recorded as something it is not (defect 50).
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  _t0=$(date +%s)
  _pids=""
  for i in 0 1; do
    ANUMS_FILE=deep-check/t17small.txt BUDGET=1100 TAG=t17c MEMGB=7 \
      timeout 3400 python3 src/sweep_shard.py 8000000 $i 2 >> /tmp/t17c_$i.log 2>&1 &
    _pids="$_pids $!"
  done
  # `wait' with NO OPERANDS is specified to return zero, always -- so reading $? after it
  # tells you nothing about the shards, and the defect-52 check was inert in every runner
  # that launches more than one. Waiting on each pid in turn is the portable way to get a
  # status back. 124 is `timeout' doing its job, not a crash.
  _rc=0
  for _p in $_pids; do
    if wait "$_p"; then :; else _s=$?; [ $_s -ne 124 ] && _rc=$_s; fi
  done
  _el=$(( $(date +%s) - _t0 ))
  # DEFECT 52. A round that ends in seconds was read as "nothing left to ask". A round that
  # ends in seconds because the sweep CRASHED ends in seconds too, and said the same thing.
  # bsweep.py died on its first entry with AttributeError on 31 August and sat at 3,376 of
  # 10,632 for three weeks looking like a half-read queue; the moment it was put in a runner
  # the backoff would have called that queue read out. An exit code tells the two apart for
  # nothing: 0 is a clean round, 124 is `timeout' doing its job, anything else is a crash and
  # must never be mistaken for an empty vein.
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- this is a crash, NOT an empty vein; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
