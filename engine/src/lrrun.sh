#!/bin/sh
# The conjectures that are not in the entry: 192 entries saying only "Empirical recurrence of
# order k (see link above)", plus 36 saying "Empirical polynomial of degree d". Every one has a
# name an engine here already reads; the recurrence is in a linked a-file, which the local
# clone holds only as a Git LFS pointer. afiles/ has the fetched copies.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1 2 3; do
    ANUMS_FILE=deep-check/linkrec.txt BUDGET=300 \
      timeout 1700 python3 src/sweep_linkrec.py 200000 $i 4 >> /tmp/lr_$i.log 2>&1 &
  done
  wait
  TARGETS=linkpoly_cands.json HITS=linkpoly_hits.json DONE=linkpoly_done.json BUDGET=300 \
    timeout 1700 python3 src/sweep_cf.py 200000 >> /tmp/lp.log 2>&1
done
