#!/bin/sh
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10; do
  TARGETS=lex_cands.json HITS=lexcf_hits.json DONE=lexcf_done.json BUDGET=300 \
    timeout 1700 python3 src/sweep_cf.py 40000000 >> /tmp/lexcf.log 2>&1
done
