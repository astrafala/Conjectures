#!/bin/sh
# The min-filter family: 134 entries no engine could read until transfer95. Every sweep reads
# them now, so they go through the recurrence, tail and closed-form sweeps together. The cap
# is high because 35 of them were refused at a DFA-state cap derived from 400,000.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/minfilter.txt BUDGET=300 \
      timeout 1700 python3 src/sweep_shard.py 4000000 $i 3 >> /tmp/mf_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2 3; do
    TARGETS=mf_cands.json HITS=mfcf_hits_$i.json DONE=mfcf_done_$i.json \
      CFSHARD=$i CFNSHARD=4 BUDGET=300 \
      timeout 1700 python3 src/sweep_cf.py 4000000 >> /tmp/mfcf_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/minfilter.txt BUDGET=300 SCUT=20000 \
      timeout 1700 python3 src/ordtails.py 4000000 $i 3 >> /tmp/mft_$i.log 2>&1 &
  done
  wait
done
