#!/bin/sh
# The OTHER conjectures on entries this project has already proved C-finite. No model, no
# engine, no name to parse: the premise is a proof this project already owns.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12; do
  for i in 0 1 2 3; do
    TARGETS=deep-check/second.txt HITS=snd_hits_$i.json DONE=snd_done_$i.json \
      SSHARD=$i SNSHARD=4 BUDGET=30 \
      timeout 1700 python3 src/sweep_second.py >> /tmp/snd_$i.log 2>&1 &
  done
  wait
done
