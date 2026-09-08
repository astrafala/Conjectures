#!/bin/sh
# Conjectured recurrences that follow from a closed form the entry states as fact.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  timeout 900 python3 src/factscan.py >> /tmp/factscan.log 2>&1
  for i in 0 1 2 3; do
    TARGETS=deep-check/factcf.txt HITS=fcf_hits_$i.json DONE=fcf_done_$i.json \
      FSHARD=$i FNSHARD=4 BUDGET=40 \
      timeout 900 python3 src/sweep_factcf.py >> /tmp/fcf_$i.log 2>&1 &
  done
  wait
done
