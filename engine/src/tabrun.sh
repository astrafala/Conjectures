#!/bin/sh
# The T(n,k) column and row conjectures on the FULL pool: 1,729 entries carry an
# "Empirical for column k:" block and the sweep had asked about 11 of them, because it walked
# all 399,027 names in A-number order and never recorded the ones it skipped.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
  for i in 0 1 2 3; do
    TABPOOL=deep-check/tabpool.txt HITS=tabnew_hits_$i.json DONE=tabnew_done_$i.json \
      TABSHARD=$i TABNSHARD=4 timeout 1700 python3 src/sweep_table.py 2000000 \
      >> /tmp/tab_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2 3; do
    TMODE=row TABPOOL=deep-check/tabpool.txt HITS=rownew_hits_$i.json \
      DONE=rownew_done_$i.json TABSHARD=$i TABNSHARD=4 \
      timeout 1700 python3 src/sweep_tablerow.py 2000000 >> /tmp/row_$i.log 2>&1 &
  done
  wait
done
