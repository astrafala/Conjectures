#!/bin/sh
# Classify galcoord's 355 declines by the reason `galcoord.LAST_WHY' now records. A runner
# rather than a one-off because it wants a quiet machine: each build can take a minute, and the
# first attempt reached 20 of 355 before forty other jobs on four cores made the rest take
# hours. In the rotation it starts only when restart_all's MAXJOBS guard allows, which is
# exactly the condition it needs, and src/galwhy.py resumes from what is already classified.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8; do
  _t0=$(date +%s)
  timeout 1700 python3 -u src/galwhy.py >> /tmp/galwhy.log 2>&1
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
