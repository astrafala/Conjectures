#!/bin/sh
# The active-cell counts: 168 entries, none readable before ca2dcount.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/b8.txt BUDGET=200 \
      timeout 1700 python3 src/sweep_shard.py 200000 $i 3 >> /tmp/b8_$i.log 2>&1 &
  done
  wait
  for i in 0 1; do
    TARGETS=b8_cands.json HITS=b8cf_hits_$i.json DONE=b8cf_done_$i.json \
      CFSHARD=$i CFNSHARD=2 BUDGET=200 \
      timeout 1700 python3 src/sweep_cf.py 200000 >> /tmp/b8cf_$i.log 2>&1 &
  done
  wait
done
