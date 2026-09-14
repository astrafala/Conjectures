#!/bin/sh
# Conjectured P-RECURSIVE recurrences: 459 open pool entries, 380 of them readable, and
# `ratrec` reads constant coefficients only so none was ever asked about. Where the entry
# states its generating function as fact and that function is algebraic, `holonomic` turns the
# claim into an identity of functions and settles it symbolically.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  for i in 0 1; do
    ANUMS_FILE=deep-check/prec.txt ALARM=240 MEMGB=5 \
      timeout 1700 python3 src/sweep_prec.py $i 2 >> /tmp/prec_$i.log 2>&1 &
  done
  wait
done
