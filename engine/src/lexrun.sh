#!/bin/sh
# The lexicographic-subblock family, unlocked by one clause added to transfer17's vocabulary.
# Every sweep reads it now, so it goes through all three at a cap high enough for the wider
# boards (the first pass refused 6 of 27 at 400,000).
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/lexpool.txt BUDGET=300 \
      timeout 1700 python3 src/sweep_shard.py 20000000 $i 3 >> /tmp/lex_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/lexpool.txt BUDGET=300 SCUT=20000 \
      timeout 1700 python3 src/ordtails.py 20000000 $i 3 >> /tmp/lext_$i.log 2>&1 &
  done
  wait
done
