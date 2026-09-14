#!/bin/sh
# The closed-form pool, rebuilt from the clone. polyclosed_cands.json held 137 entries chosen
# by hand on 1 September; the refusal census found 274 more whose ONLY readable claim is a
# closed form `closedform` reads outright and whose name an engine already reads, and 5 of
# them were in that file. Ninth stale filter in this project.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1; do
    TARGETS=cfpool_cands.json HITS=cfpool_hits_$i.json DONE=cfpool_done_$i.json \
      CFSHARD=$i CFNSHARD=2 BUDGET=200 \
      timeout 1700 python3 src/sweep_cf.py 200000 >> /tmp/cfpool_$i.log 2>&1 &
  done
  wait
done
