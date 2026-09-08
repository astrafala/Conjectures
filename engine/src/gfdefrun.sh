#!/bin/sh
# The largest settleable pool in the database: 2,817 entries not in the roster that carry a
# conjectured recurrence AND a generating function the entry states as fact. The conjecture
# follows from the stated g.f. by algebra alone -- no model, no engine, no name to parse.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2 3; do
    GFPOOL=deep-check/gfdef.txt HITS=gfdef_hits_$i.json DONE=gfdef_done_$i.json \
      GFSHARD=$i GFNSHARD=4 BUDGET=60 \
      timeout 1700 python3 src/sweep_gf.py >> /tmp/gfdef_$i.log 2>&1 &
  done
  wait
done
