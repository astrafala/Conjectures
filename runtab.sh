for w in 0 1 2 3; do python3 audit_tabrec.py $1 $2 $w 4 > /dev/null 2>&1 & done; wait
