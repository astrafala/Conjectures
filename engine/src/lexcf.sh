#!/bin/sh
# The lexicographic family's closed-form conjectures, four shards. Each shard keeps its own
# hits and done files: two writers on one file destroy each other's results.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2 3; do
    TARGETS=lex_cands.json HITS=lexcf_hits_$i.json DONE=lexcf_done_$i.json \
      CFSHARD=$i CFNSHARD=4 BUDGET=300 \
      timeout 1700 python3 src/sweep_cf.py 40000000 >> /tmp/lexcf_$i.log 2>&1 &
  done
  wait
done
