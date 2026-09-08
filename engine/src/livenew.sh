#!/bin/sh
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  timeout 1700 python3 src/livenew.py deep-check/new.txt >> /tmp/livenew.log 2>&1
done
