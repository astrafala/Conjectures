#!/bin/sh
# "a(n) is a polynomial of degree 26 for n>13" -- seven entries whose claim names a degree and
# no coefficients, so nothing here read them. It is two linear recurrences: (z-1)^(d+1) must
# annihilate and (z-1)^d must not. The big degrees (127, 80) are slow, hence a runner.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  ANUMS_FILE=deep-check/degree.txt BUDGET=600 MEMGB=6 \
    timeout 1700 python3 src/sweep_degree.py 400000 0 1 >> /tmp/deg.log 2>&1
  sleep 5
done
