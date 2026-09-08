#!/bin/sh
# The one-dimensional word family: 101 entries verified against their own published terms and
# unreadable by any engine before transfer96, because every array engine looks for a second
# dimension that is not there.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2 3; do
    TARGETS=word_cands.json HITS=wordcf_hits_$i.json DONE=wordcf_done_$i.json \
      CFSHARD=$i CFNSHARD=4 BUDGET=200 \
      timeout 1700 python3 src/sweep_cf.py 300000 >> /tmp/wordcf_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/words.txt BUDGET=200 \
      timeout 1700 python3 src/sweep_shard.py 300000 $i 3 >> /tmp/word_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/words.txt BUDGET=200 SCUT=20000 \
      timeout 1700 python3 src/ordtails.py 300000 $i 3 >> /tmp/wordt_$i.log 2>&1 &
  done
  wait
done
