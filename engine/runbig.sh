for w in 0 1 2 3; do python3 src/audit_big.py $1 $2 $3 $w 4 > /dev/null 2>&1 & done; wait
