#!/bin/sh
# The standing rule made real: every sweep restarts for ever, and when its pool empties the
# pools are rebuilt from the clone so it has something to run on the next round.
#
# The `wait` at the end of each round is not optional. An earlier edit inserted the tail
# sweep AFTER the for-loop's `done` and left a second `done` behind, which closed the WHILE
# loop early and put the `wait` outside it. The loop then spun as fast as the shell could go,
# launching six background jobs per turn without ever waiting: it reached 470 copies of one
# sweep, all writing the same three files. Nothing was lost -- every file still parsed and the
# counts held -- but only by luck. Keep the structure below intact.
cd /home/user/Conjectures/engine
round=0
while true; do
  round=$((round + 1))
  for i in 0 1 2; do
    # the 1,590 entries with a readable conjecture AND a readable name that the cached
    # candidate list had never heard of -- 610 of them were not in it at all
    ANUMS_FILE=deep-check/namepool.txt BUDGET=90 TAG=np \
      timeout 1700 python3 src/sweep_shard.py 2000000 $i 3 >> /tmp/np_$i.log 2>&1 &
    ANUMS_FILE=deep-check/pool-rec.txt BUDGET=90 \
      timeout 1700 python3 src/sweep_shard.py 2000000 $i 3 >> /tmp/sw_$i.log 2>&1 &
    ANUMS_FILE=deep-check/pool-order.txt BUDGET=150 \
      timeout 1700 python3 src/sweep_ordwhole.py 2000000 $i 3 >> /tmp/ord_$i.log 2>&1 &
    ANUMS_FILE=deep-check/order-unproved.txt BUDGET=120 \
      timeout 1700 python3 src/ordtails.py 2000000 $i 3 >> /tmp/tails_$i.log 2>&1 &
  done
  wait
  HITS=tabnew_hits.json DONE=tabnew_done.json \
    timeout 900 python3 src/sweep_table.py 300000 >> /tmp/tab.log 2>&1
  TMODE=row HITS=rownew_hits.json DONE=rownew_done.json \
    timeout 900 python3 src/sweep_tablerow.py 300000 >> /tmp/row.log 2>&1
  TARGETS=cf_cands_all.json HITS=cfnew_hits.json DONE=cfnew_done.json \
    timeout 900 python3 src/sweep_cf.py 2000000 >> /tmp/cf.log 2>&1
  timeout 900 python3 src/falsify.py 300000 >> /tmp/fal.log 2>&1
  # every few rounds, rebuild the pools from the clone: new entries arrive daily and new
  # engines widen what counts as a candidate
  if [ $((round % 3)) -eq 0 ]; then
    timeout 1700 python3 src/keepgoing.py >> /tmp/keep.log 2>&1
  fi
done
