for w in 0 1 2 3; do python3 src/audit_regf.py $w 4 > /dev/null 2>&1 & done; wait
