#!/bin/sh
# The two-dimensional cellular automaton axes: 222 entries with a growth certificate, none
# readable by any engine before.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/ca2d.txt BUDGET=200 \
      timeout 1700 python3 src/sweep_shard.py 200000 $i 3 >> /tmp/ca2d_$i.log 2>&1 &
  done
  wait
  for i in 0 1; do
    TARGETS=ca2d_cands.json HITS=ca2dcf_hits_$i.json DONE=ca2dcf_done_$i.json \
      CFSHARD=$i CFNSHARD=2 BUDGET=200 \
      timeout 1700 python3 src/sweep_cf.py 200000 >> /tmp/ca2dcf_$i.log 2>&1 &
  done
  wait
done
