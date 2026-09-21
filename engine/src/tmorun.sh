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
# seen. MEMGB=6 and two shards, because this list spans every engine and nothing suggests it is
# memory-bound -- what refused it was the clock.
#
# BUDGET=300, and it started at 900. `signal.alarm(BUDGET)' is set THREE times per entry -- for
# the build, the terms and the threshold -- so BUDGET is a per-PHASE limit and an entry can
# consume three times it. At 900 that is forty-five minutes for one entry, most of a container
# generation, and in its first hour this runner recorded nothing at all: each shard started one
# entry and was killed by the restart before finishing it. At 300 the worst case is fifteen
# minutes, about four entries per shard per generation, and 300 is still more than three times
# the ninety seconds most of this list was refused at -- which is the whole point of asking
# again.
#
# sweep_shard skips an entry whose recorded budget is at least its own, and releases it when
# BUDGET is larger, so pointing a 900-second runner at this list re-asks all 62 with no
# bookkeeping. Whatever it cannot settle is recorded again, at 900, and stays honest.
#
# THE BUDGET THIS ASKS AT HAD ALREADY REFUSED MOST OF THE LIST. 39 of tmolist's 62 entries
# carry a uniall_tmo.json row saying the clock refused them at 300 seconds or more, and this
# asked at exactly 300 -- defect 54's shape, in the vein whose whole subject is the clock.
# Raised to 500, at which all 62 are a new question (the worst row is 420).
#
# 500 and not more because BUDGET is PER PHASE: build, terms and threshold each arm their own
# alarm, so one entry costs up to 3*BUDGET = 1500s, and the outer `timeout 1700' has to be
# larger than that or a slow entry is killed with its marker on disk and written down as
# something it is not (defect 50).
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  _t0=$(date +%s)
  _pids=""
  for i in 0 1; do
    ANUMS_FILE=deep-check/tmolist.txt BUDGET=500 TAG=tmo MEMGB=6 \
      timeout 1700 python3 src/sweep_shard.py 8000000 $i 2 >> /tmp/tmo_$i.log 2>&1 &
    _pids="$_pids $!"
  done
  # `wait' with no operands always returns zero, so per-pid is the only way to see a status.
  _rc=0
  for _p in $_pids; do
    if wait "$_p"; then :; else _s=$?; [ $_s -ne 124 ] && _rc=$_s; fi
  done
  _el=$(( $(date +%s) - _t0 ))
  # DEFECT 52. A round ending in seconds because the sweep CRASHED looks exactly like a round
  # ending in seconds because there was nothing to ask. bsweep.py died on its first entry on
  # 31 August and sat at 3,376 of 10,632 for three weeks looking like a half-read queue.
  # 0 is a clean round, 124 is `timeout' doing its job, anything else is a crash.
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- this is a crash, NOT an empty vein; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out at this budget, stopping"
    break
  fi
done
