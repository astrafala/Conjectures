#!/bin/sh
# The entries the CLOCK refused, asked again with a budget that fits a container generation.
#
# This vein did not exist yesterday. Until STATE.md defect 49 was fixed, a build that ran out of
# BUDGET was swallowed by `uniform.build''s `except Exception: return None' and recorded as
# `state space > cap' -- so every one of these entries sat in uniall_caps.json looking like a
# state space too large to reach, when what they had actually exceeded was a 90-second clock.
#
# 62 of them, every one off the roster, every one carrying a parsable conjecture, every one
# still open. The budgets they failed under:
#
#     90s   40
#     150s  20
#     420s   2
#
# Forty were refused at NINETY SECONDS, which is a seventh of the shortest container generation
# seen. BUDGET=900 is ten times that and still fits. MEMGB=6 and two shards, because this list
# spans every engine and nothing suggests it is memory-bound -- what refused it was the clock.
#
# sweep_shard skips an entry whose recorded budget is at least its own, and releases it when
# BUDGET is larger, so pointing a 900-second runner at this list re-asks all 62 with no
# bookkeeping. Whatever it cannot settle is recorded again, at 900, and stays honest.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  _t0=$(date +%s)
  for i in 0 1; do
    ANUMS_FILE=deep-check/tmolist.txt BUDGET=900 TAG=tmo MEMGB=6 \
      timeout 1700 python3 src/sweep_shard.py 8000000 $i 2 >> /tmp/tmo_$i.log 2>&1 &
  done
  wait
  _el=$(( $(date +%s) - _t0 ))
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out at this budget, stopping"
    break
  fi
done
