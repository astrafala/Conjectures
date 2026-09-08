#!/bin/sh
# The cusp-form dimension family: 51 entries settled by a classical closed formula rather than
# by any transfer matrix. Every sweep reads them now.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/cusp.txt BUDGET=120 \
      timeout 1700 python3 src/sweep_shard.py 200000 $i 3 >> /tmp/cusp_$i.log 2>&1 &
  done
  wait
  for i in 0 1; do
    TARGETS=cusp_cands.json HITS=cuspcf_hits_$i.json DONE=cuspcf_done_$i.json \
      CFSHARD=$i CFNSHARD=2 BUDGET=120 \
      timeout 1700 python3 src/sweep_cf.py 200000 >> /tmp/cuspcf_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/cusp.txt BUDGET=120 SCUT=20000 \
      timeout 1700 python3 src/ordtails.py 200000 $i 3 >> /tmp/cuspt_$i.log 2>&1 &
  done
  wait
done
