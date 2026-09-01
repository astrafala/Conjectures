#!/bin/bash
cd /home/user/Conjectures
for n in 6 15 11 13 10 8 16 12 14 7 9; do
  echo "=== sweep $n ==="
  case $n in
    6) timeout 3000 python3 sweep_transfer6.py 40000 ;;
    7) timeout 3000 python3 sweep_transfer7.py 4000 ;;
    8) timeout 3000 python3 sweep_transfer8.py 4000 ;;
    9) timeout 4000 python3 sweep_transfer9.py 6000 ;;
    10) timeout 2000 python3 sweep_transfer10.py 6000 ;;
    11) timeout 2000 python3 sweep_transfer11.py 8000 ;;
    12) timeout 2000 python3 sweep_transfer12.py 12000 ;;
    13) timeout 1500 python3 sweep_transfer13.py 20000 ;;
    14) timeout 2000 python3 sweep_transfer14.py 40000 ;;
    15) timeout 1500 python3 sweep_transfer15.py 60000 ;;
    16) timeout 2000 python3 sweep_transfer16.py 40000 ;;
  esac
  echo "--- sweep $n done ---"
done
echo ALLDONE
