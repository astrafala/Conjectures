#!/bin/sh
# Classify galcoord's "distance is not a max of affine pieces" declines into RAY and SCATTER.
# A ray correction to the ball count is quasi-linear in t, so the existing Ehrhart fit and
# certificate absorb it with one extra term (IDEAS A11); a scatter does not. The count decides
# how much of the 355 that route reaches. Resumable through deep-check/galrays.json, and in the
# rotation so it starts only when restart_all's MAXJOBS guard allows.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  _t0=$(date +%s)
  timeout 1700 python3 -u src/galrays.py >> /tmp/galrays.log 2>&1
  _rc=$?
  _el=$(( $(date +%s) - _t0 ))
  # defect 52: a crash and an empty queue both end in seconds; the exit code tells them apart
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- a crash, NOT an empty queue; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- every decline classified, stopping"
    # defect 65: say WHY this stopped, so restart_all does not undo an idle backoff.
    date +%s > "/tmp/$(basename "$0").readout"
    break
  fi
done
