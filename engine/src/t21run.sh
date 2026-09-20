#!/bin/sh
# The 78 capped off-roster transfer21 entries, now that uniform.build dispatches transfer21 to
# transfer17's pair-free construction instead of its pair build.
#
# transfer21 was the only caller of transfer17.build, whose vertices are ordered PAIRS of lines
# and which refuses a priori on (alpha+1)^(2W) > cap. Everything else already came through
# uniform to build_pairfree, which has no such refusal. That one test is what refuses all 15 of
# these entries that carry a conjecture, and nothing else refuses any of them.
# (78 capped, 15 of them carrying a conjecture. An earlier note said 120; that was
# transfer17's count, not transfer21's.)
#
# The swap is verified: same terms as the pair build on 243 shapes -- 99 entries and 144 of the
# parameter grid -- zero mismatches, with the state counts differing throughout (65793 against
# 11717 at W=4 K=4), which is what shows the comparison ran.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10; do
  ANUMS_FILE=deep-check/t21cap.txt BUDGET=900 TAG=t21 MEMGB=6 \
    timeout 1700 python3 src/sweep_shard.py 2000000 0 1 >> /tmp/t21_run.log 2>&1
done
